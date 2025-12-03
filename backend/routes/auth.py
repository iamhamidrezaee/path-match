from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database import db
from models import User, Mentor, Mentee
import json
import os
from werkzeug.utils import secure_filename

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user (Base User only - Legacy)"""
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['net_id', 'email', 'password', 'name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(net_id=data['net_id']).first():
        return jsonify({'error': 'NetID already registered'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user = User(
        net_id=data['net_id'],
        email=data['email'],
        name=data['name'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create access tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201

@bp.route('/register-mentee', methods=['POST'])
def register_mentee():
    """Register a new Mentee with profile"""
    data = request.get_json()
    
    # 1. Create User
    if User.query.filter_by(net_id=data.get('net_id')).first():
        return jsonify({'error': 'NetID already registered'}), 409
        
    user = User(
        net_id=data.get('net_id'),
        email=data.get('email'),
        name=data.get('name'),
        role='mentee'
    )
    user.set_password(data.get('password'))
    
    try:
        db.session.add(user)
        db.session.flush() # Get user ID
        
        # 2. Create Mentee Profile
        # Extract lists and serialize to JSON
        seeking = json.dumps(data.get('seeking', []))
        fields = json.dumps(data.get('fields', []))
        
        # Parse careers string into list
        careers_str = data.get('careers', '')
        careers_list = [c.strip() for c in careers_str.split(',') if c.strip()]
        careers_json = json.dumps(careers_list)
        
        mentee = Mentee(
            user_id=user.id,
            graduating_year=int(data.get('gradYear', 0)) if data.get('gradYear') else 0,
            info_concentration=data.get('concentration'),
            preferred_communication=json.dumps(data.get('correspondence', [])), # Storing as JSON string
            advising_needs=seeking,
            field_interests=fields,
            careers_interested_in=careers_json,
            bio=data.get('bio')
            # careers_interested_in is mapped to seeking/fields in survey? 
            # The survey asks "seeking advice on" and "field of interest". 
            # Mentee model has advising_needs, careers_interested_in, field_interests.
            # I'll map 'seeking' to advising_needs and 'fields' to field_interests.
        )
        
        db.session.add(mentee)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'message': 'Mentee registered successfully', 'access_token': access_token}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error registering mentee: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/register-mentor', methods=['POST'])
def register_mentor():
    """Register a new Mentor with profile and image upload"""
    # handle FormData
    form = request.form
    files = request.files
    
    # 1. Create User
    if User.query.filter_by(net_id=form.get('net_id')).first():
        return jsonify({'error': 'NetID already registered'}), 409
        
    user = User(
        net_id=form.get('net_id'),
        email=form.get('email'),
        name=form.get('name'),
        role='mentor'
    )
    user.set_password(form.get('password'))
    
    try:
        db.session.add(user)
        db.session.flush()
        
        # 2. Handle Image Upload
        if 'profileImage' in files:
            file = files['profileImage']
            if file.filename != '':
                # Save to frontend/images as Firstname.jpeg (per instructions)
                # Instructions: "create a placeholder image with <firstname>.jpeg... Then, when a mentor signs up, then SHOULD upload an image"
                # I'll use the uploaded file and save it as firstname.jpeg to match the convention.
                # Or better, save as user_id.jpeg to avoid collisions, but instructions said <firstname>.jpeg.
                # I'll stick to instructions but sanitize.
                
                firstname = form.get('name').split(' ')[0]
                filename = secure_filename(f"{firstname}.jpeg")
                
                # Determine path: Go up one level from backend/routes -> backend -> root -> frontend/images
                # current_app.root_path is usually backend/
                base_path = os.path.dirname(os.path.dirname(current_app.root_path)) # path-match/
                # Wait, current_app.root_path in flask is where app is instantiated (backend).
                # So dirname(backend) is path-match.
                
                # Let's try relative path from CWD (which is workspace root)
                upload_path = os.path.join('frontend', 'images')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                    
                file.save(os.path.join(upload_path, filename))
        
        # 3. Create Mentor Profile
        topics = json.dumps(request.form.getlist('topics[]'))
        correspondence = json.dumps(request.form.getlist('correspondence[]')) # Note: FormData might send as 'correspondence'
        if not correspondence or correspondence == '[]':
             # Try getting single key if only one selected or different naming
             correspondence = json.dumps(request.form.getlist('correspondence'))

        mentor = Mentor(
            user_id=user.id,
            graduating_year=int(form.get('gradYear', 0)) if form.get('gradYear') else 0,
            info_concentration=form.get('concentration'),
            preferred_communication=correspondence,
            advising_topics=topics,
            career_pursuing=form.get('career'),
            bio=form.get('bio'),
            calendly_link=form.get('calendly'),
            availability_status='available'
        )
        
        db.session.add(mentor)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'message': 'Mentor registered successfully', 'access_token': access_token}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error registering mentor: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('net_id') or not data.get('password'):
        return jsonify({'error': 'NetID and password required'}), 400
    
    user = User.query.filter_by(net_id=data['net_id']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({'access_token': access_token}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200
