"""
PathMatch Backend API
=====================
A Flask-based REST API for the PathMatch mentorship platform.
Connects Cornell CIS underclassmen with graduating seniors.
"""

import os
import json
from datetime import timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from database import db
from models import User, Mentor, Mentee, Match

load_dotenv()

# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = Flask(__name__)

# Database configuration - Use SQLite for simplicity (demo mode)
# Always use SQLite with an absolute path to the instance folder
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, 'instance')

# Ensure instance directory exists
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

db_path = os.path.join(instance_path, 'pathmatch.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# CORS configuration - allow frontend origins
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:8000,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8000').split(',')
CORS(app, origins=cors_origins, supports_credentials=True)

# =============================================================================
# MATCHING ALGORITHM
# =============================================================================

# Keyword synonyms for semantic matching
KEYWORD_SYNONYMS = {
    'ml': ['machine learning', 'deep learning', 'ai', 'artificial intelligence'],
    'ai': ['artificial intelligence', 'machine learning', 'ml', 'deep learning'],
    'ux': ['user experience', 'ui', 'design', 'user interface', 'hci'],
    'ui': ['user interface', 'ux', 'design', 'user experience'],
    'pm': ['product management', 'product manager', 'product'],
    'swe': ['software engineering', 'software engineer', 'developer', 'programming'],
    'ds': ['data science', 'data scientist', 'analytics', 'data analysis'],
    'quant': ['quantitative', 'finance', 'trading', 'quantitative finance'],
    'phd': ['doctorate', 'doctoral', 'research', 'academia', 'academic'],
    'mba': ['business', 'management', 'consulting'],
    'startup': ['entrepreneurship', 'founder', 'business', 'venture'],
    'research': ['academia', 'academic', 'phd', 'graduate school'],
}

def extract_keywords(text):
    """Extract meaningful keywords from text."""
    if not text:
        return set()
    
    # Common words to ignore
    stopwords = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your', 'he', 'she',
        'it', 'they', 'them', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
        'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but',
        'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
        'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
        't', 'can', 'will', 'just', 'don', 'should', 'now', 'would', 'could', 'also',
        'really', 'want', 'looking', 'interested', 'help', 'learn', 'like', 'get',
        'im', "i'm", 'ive', "i've", 'im', 'currently', 'working', 'work', 'experience'
    }
    
    # Clean and tokenize
    text = text.lower()
    # Keep alphanumeric and spaces
    cleaned = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
    words = cleaned.split()
    
    # Filter stopwords and short words
    keywords = {w for w in words if w not in stopwords and len(w) > 2}
    
    return keywords


def expand_keywords(keywords):
    """Expand keywords with synonyms."""
    expanded = set(keywords)
    for keyword in keywords:
        if keyword in KEYWORD_SYNONYMS:
            expanded.update(KEYWORD_SYNONYMS[keyword])
        # Check if keyword matches any synonym values
        for key, synonyms in KEYWORD_SYNONYMS.items():
            if keyword in synonyms:
                expanded.add(key)
                expanded.update(synonyms)
    return expanded


def calculate_compatibility(mentee, mentor):
    """
    Calculate compatibility score between mentee and mentor.
    
    Returns a dict with:
    - score: 0-100 compatibility score
    - breakdown: detailed scoring breakdown
    - reasons: human-readable match explanations
    """
    score = 0
    max_score = 100
    breakdown = {}
    reasons = []
    
    # Parse JSON fields
    try:
        mentee_needs = json.loads(mentee.advising_needs) if mentee.advising_needs else []
        mentee_careers = json.loads(mentee.careers_interested_in) if mentee.careers_interested_in else []
        mentor_topics = json.loads(mentor.advising_topics) if mentor.advising_topics else []
    except json.JSONDecodeError:
        mentee_needs = []
        mentee_careers = []
        mentor_topics = []
    
    # =========================================================================
    # DETERMINISTIC MATCHING (60 points)
    # =========================================================================
    
    # 1. Advising Topics Alignment (30 points)
    topic_score = 0
    matched_topics = []
    if mentee_needs and mentor_topics:
        mentee_needs_lower = {n.lower().strip() for n in mentee_needs}
        mentor_topics_lower = {t.lower().strip() for t in mentor_topics}
        matches = mentee_needs_lower.intersection(mentor_topics_lower)
        
        if mentee_needs_lower:
            topic_score = (len(matches) / len(mentee_needs_lower)) * 30
            matched_topics = list(matches)
            if matches:
                reasons.append(f"Can help with: {', '.join(matched_topics)}")
    
    breakdown['advising_topics'] = round(topic_score, 1)
    score += topic_score
    
    # 2. Career Path Alignment (20 points)
    career_score = 0
    if mentee_careers and mentor.career_pursuing:
        mentor_career = mentor.career_pursuing.lower().strip()
        mentee_careers_lower = [c.lower().strip() for c in mentee_careers]
        
        # Direct match
        if mentor_career in mentee_careers_lower:
            career_score = 20
            reasons.append(f"Pursuing career in {mentor.career_pursuing}")
        else:
            # Partial match - check for keyword overlap
            mentor_keywords = extract_keywords(mentor_career)
            for mc in mentee_careers_lower:
                mentee_keywords = extract_keywords(mc)
                if mentor_keywords & mentee_keywords:
                    career_score = 15
                    reasons.append(f"Related career path: {mentor.career_pursuing}")
                    break
    
    breakdown['career_path'] = round(career_score, 1)
    score += career_score
    
    # 3. Concentration Alignment (10 points)
    concentration_score = 0
    if mentee.info_concentration and mentor.info_concentration:
        mentee_conc = mentee.info_concentration.lower().strip()
        mentor_conc = mentor.info_concentration.lower().strip()
        
        if mentee_conc == mentor_conc:
            concentration_score = 10
            if mentee_conc != "i don't know":
                reasons.append(f"Same concentration: {mentor.info_concentration}")
        elif mentee_conc == "i don't know":
            # Neutral - mentee is exploring
            concentration_score = 5
    
    breakdown['concentration'] = round(concentration_score, 1)
    score += concentration_score
    
    # =========================================================================
    # SEMANTIC MATCHING (40 points)
    # =========================================================================
    
    # Extract and compare bio keywords
    mentee_bio_keywords = extract_keywords(mentee.bio or '')
    mentee_fields_keywords = extract_keywords(mentee.field_interests or '')
    mentee_all_keywords = expand_keywords(mentee_bio_keywords | mentee_fields_keywords)
    
    mentor_bio_keywords = extract_keywords(mentor.bio or '')
    mentor_exp_keywords = extract_keywords(mentor.experiences or '')
    mentor_all_keywords = expand_keywords(mentor_bio_keywords | mentor_exp_keywords)
    
    # Add career keywords
    if mentor.career_pursuing:
        mentor_all_keywords.update(expand_keywords(extract_keywords(mentor.career_pursuing)))
    
    # Calculate semantic overlap
    semantic_score = 0
    if mentee_all_keywords and mentor_all_keywords:
        overlap = mentee_all_keywords & mentor_all_keywords
        
        # Score based on overlap ratio
        if overlap:
            # Use Jaccard-like similarity but weighted toward mentee's interests
            overlap_ratio = len(overlap) / max(len(mentee_all_keywords), 1)
            semantic_score = min(overlap_ratio * 60, 40)  # Cap at 40 points
            
            # Add reason for significant keyword matches
            important_matches = overlap - {'data', 'science', 'engineering', 'technology', 'tech'}
            if important_matches:
                top_matches = list(important_matches)[:3]
                reasons.append(f"Shared interests: {', '.join(top_matches)}")
    
    breakdown['semantic'] = round(semantic_score, 1)
    score += semantic_score
    
    # =========================================================================
    # FINAL SCORE
    # =========================================================================
    
    # Ensure score is within bounds
    final_score = max(0, min(100, score))
    
    # Add quality indicator
    if final_score >= 80:
        quality = "Excellent Match"
    elif final_score >= 60:
        quality = "Good Match"
    elif final_score >= 40:
        quality = "Moderate Match"
    else:
        quality = "Low Match"
    
    return {
        'score': round(final_score, 1),
        'quality': quality,
        'breakdown': breakdown,
        'reasons': reasons if reasons else ["General mentorship available"]
    }


def get_top_matches(mentee, mentors, limit=10):
    """Get top N mentor matches for a mentee."""
    matches = []
    
    for mentor in mentors:
        if mentor.availability_status == 'available':
            result = calculate_compatibility(mentee, mentor)
            matches.append({
                'mentor': mentor,
                'score': result['score'],
                'quality': result['quality'],
                'breakdown': result['breakdown'],
                'reasons': result['reasons']
            })
    
    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return matches[:limit]


# =============================================================================
# HEALTH CHECK ROUTES
# =============================================================================

@app.route('/')
def index():
    """API root endpoint."""
    return jsonify({
        'message': 'PathMatch API',
        'version': '2.0.0',
        'status': 'running'
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user (base registration)."""
    data = request.get_json()
    
    required_fields = ['net_id', 'email', 'password', 'name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(net_id=data['net_id']).first():
        return jsonify({'error': 'NetID already registered'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        net_id=data['net_id'],
        email=data['email'],
        name=data['name'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@app.route('/api/auth/register-mentee', methods=['POST'])
def register_mentee():
    """Register a new mentee with profile."""
    data = request.get_json()
    
    if User.query.filter_by(net_id=data.get('net_id')).first():
        return jsonify({'error': 'NetID already registered'}), 409
    
    try:
        # Create user
        user = User(
            net_id=data.get('net_id'),
            email=data.get('email'),
            name=data.get('name'),
            role='mentee'
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.flush()
        
        # Serialize list fields
        seeking = json.dumps(data.get('seeking', []))
        fields = json.dumps(data.get('fields', []))
        
        # Parse careers
        careers_str = data.get('careers', '')
        careers_list = [c.strip() for c in careers_str.split(',') if c.strip()]
        careers_json = json.dumps(careers_list)
        
        correspondence = json.dumps(data.get('correspondence', []))
        
        # Create mentee profile
        mentee = Mentee(
            user_id=user.id,
            graduating_year=int(data.get('gradYear', 0)) if data.get('gradYear') else 0,
            info_concentration=data.get('concentration'),
            preferred_communication=correspondence,
            advising_needs=seeking,
            field_interests=fields,
            careers_interested_in=careers_json,
            bio=data.get('bio')
        )
        
        db.session.add(mentee)
        db.session.commit()
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Mentee registered successfully',
            'access_token': access_token,
            'mentee_id': mentee.id,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register-mentor', methods=['POST'])
def register_mentor():
    """Register a new mentor with profile and optional image upload."""
    # Handle both JSON and FormData
    if request.content_type and 'multipart/form-data' in request.content_type:
        form = request.form
        files = request.files
    else:
        form = request.get_json() or {}
        files = {}
    
    net_id = form.get('net_id')
    if User.query.filter_by(net_id=net_id).first():
        return jsonify({'error': 'NetID already registered'}), 409
    
    try:
        # Create user
        user = User(
            net_id=net_id,
            email=form.get('email'),
            name=form.get('name'),
            role='mentor'
        )
        user.set_password(form.get('password'))
        
        db.session.add(user)
        db.session.flush()
        
        # Handle image upload
        if 'profileImage' in files:
            file = files['profileImage']
            if file.filename:
                firstname = form.get('name', 'User').split(' ')[0]
                filename = secure_filename(f"{firstname}.jpeg")
                upload_path = os.path.join('..', 'frontend', 'images')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                file.save(os.path.join(upload_path, filename))
        
        # Parse list fields
        if request.content_type and 'multipart/form-data' in request.content_type:
            topics = json.dumps(request.form.getlist('topics[]') or request.form.getlist('topics'))
            correspondence = json.dumps(request.form.getlist('correspondence[]') or request.form.getlist('correspondence'))
        else:
            topics = json.dumps(form.get('topics', []))
            correspondence = json.dumps(form.get('correspondence', []))
        
        # Create mentor profile
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
        
        return jsonify({
            'message': 'Mentor registered successfully',
            'access_token': access_token,
            'mentor_id': mentor.id,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user."""
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


@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


# =============================================================================
# MENTOR ROUTES
# =============================================================================

@app.route('/api/mentors', methods=['GET'])
def get_mentors():
    """Get all available mentors."""
    mentors = Mentor.query.filter_by(availability_status='available').all()
    return jsonify({'mentors': [mentor.to_dict() for mentor in mentors]}), 200


@app.route('/api/mentors/<int:mentor_id>', methods=['GET'])
def get_mentor(mentor_id):
    """Get specific mentor by ID."""
    mentor = Mentor.query.get_or_404(mentor_id)
    return jsonify({'mentor': mentor.to_dict()}), 200


@app.route('/api/mentors/profile', methods=['POST'])
@jwt_required()
def update_mentor_profile():
    """Create or update mentor profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'mentor':
        return jsonify({'error': 'User is not registered as a mentor'}), 403
    
    data = request.get_json()
    mentor = Mentor.query.filter_by(user_id=current_user_id).first()
    
    if mentor:
        mentor.graduating_year = data.get('graduating_year', mentor.graduating_year)
        mentor.info_concentration = data.get('info_concentration', mentor.info_concentration)
        mentor.advising_topics = data.get('advising_topics', mentor.advising_topics)
        mentor.career_pursuing = data.get('career_pursuing', mentor.career_pursuing)
        mentor.bio = data.get('bio', mentor.bio)
        mentor.calendly_link = data.get('calendly_link', mentor.calendly_link)
        mentor.availability_status = data.get('availability_status', mentor.availability_status)
    else:
        mentor = Mentor(
            user_id=current_user_id,
            graduating_year=data.get('graduating_year'),
            info_concentration=data.get('info_concentration'),
            advising_topics=data.get('advising_topics'),
            career_pursuing=data.get('career_pursuing'),
            bio=data.get('bio'),
            calendly_link=data.get('calendly_link'),
            availability_status=data.get('availability_status', 'available')
        )
        db.session.add(mentor)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Mentor profile updated successfully',
        'mentor': mentor.to_dict()
    }), 200


@app.route('/api/mentors/profile', methods=['GET'])
@jwt_required()
def get_my_mentor_profile():
    """Get current user's mentor profile."""
    current_user_id = get_jwt_identity()
    mentor = Mentor.query.filter_by(user_id=current_user_id).first()
    
    if not mentor:
        return jsonify({'error': 'Mentor profile not found'}), 404
    
    return jsonify({'mentor': mentor.to_dict()}), 200


@app.route('/api/mentors/availability', methods=['PUT'])
@jwt_required()
def update_availability():
    """Update mentor availability status."""
    current_user_id = get_jwt_identity()
    mentor = Mentor.query.filter_by(user_id=current_user_id).first()
    
    if not mentor:
        return jsonify({'error': 'Mentor profile not found'}), 404
    
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['available', 'dnd', 'unavailable']:
        return jsonify({'error': 'Invalid status'}), 400
    
    mentor.availability_status = status
    db.session.commit()
    
    return jsonify({'message': 'Availability updated', 'status': status}), 200


# =============================================================================
# MENTEE ROUTES
# =============================================================================

@app.route('/api/mentees/profile', methods=['POST'])
@jwt_required()
def update_mentee_profile():
    """Create or update mentee profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'mentee':
        return jsonify({'error': 'User is not registered as a mentee'}), 403
    
    data = request.get_json()
    mentee = Mentee.query.filter_by(user_id=current_user_id).first()
    
    if mentee:
        mentee.graduating_year = data.get('graduating_year', mentee.graduating_year)
        mentee.info_concentration = data.get('info_concentration', mentee.info_concentration)
        mentee.advising_needs = data.get('advising_needs', mentee.advising_needs)
        mentee.careers_interested_in = data.get('careers_interested_in', mentee.careers_interested_in)
        mentee.field_interests = data.get('field_interests', mentee.field_interests)
        mentee.bio = data.get('bio', mentee.bio)
    else:
        mentee = Mentee(
            user_id=current_user_id,
            graduating_year=data.get('graduating_year'),
            info_concentration=data.get('info_concentration'),
            advising_needs=data.get('advising_needs'),
            careers_interested_in=data.get('careers_interested_in'),
            field_interests=data.get('field_interests'),
            bio=data.get('bio')
        )
        db.session.add(mentee)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Mentee profile updated successfully',
        'mentee': mentee.to_dict()
    }), 200


@app.route('/api/mentees/profile', methods=['GET'])
@jwt_required()
def get_my_mentee_profile():
    """Get current user's mentee profile."""
    current_user_id = get_jwt_identity()
    mentee = Mentee.query.filter_by(user_id=current_user_id).first()
    
    if not mentee:
        return jsonify({'error': 'Mentee profile not found'}), 404
    
    return jsonify({'mentee': mentee.to_dict()}), 200


# =============================================================================
# MATCHING ROUTES
# =============================================================================

@app.route('/api/matches/find', methods=['POST'])
@jwt_required()
def find_matches():
    """Find compatible mentors for a mentee."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'mentee':
        return jsonify({'error': 'Only mentees can search for mentors'}), 403
    
    mentee = Mentee.query.filter_by(user_id=current_user_id).first()
    if not mentee:
        return jsonify({'error': 'Mentee profile not found'}), 404
    
    available_mentors = Mentor.query.filter_by(availability_status='available').all()
    matches = get_top_matches(mentee, available_mentors)
    
    return jsonify({
        'matches': [{
            'mentor': m['mentor'].to_dict(),
            'compatibility_score': m['score'],
            'quality': m['quality'],
            'breakdown': m['breakdown'],
            'reasons': m['reasons']
        } for m in matches]
    }), 200


@app.route('/api/matches/find-for-mentee/<int:mentee_id>', methods=['GET'])
def find_matches_for_mentee(mentee_id):
    """Find compatible mentors for a specific mentee (public endpoint for demo)."""
    mentee = Mentee.query.get_or_404(mentee_id)
    available_mentors = Mentor.query.filter_by(availability_status='available').all()
    matches = get_top_matches(mentee, available_mentors)
    
    return jsonify({
        'mentee': mentee.to_dict(),
        'matches': [{
            'mentor': m['mentor'].to_dict(),
            'compatibility_score': m['score'],
            'quality': m['quality'],
            'breakdown': m['breakdown'],
            'reasons': m['reasons']
        } for m in matches]
    }), 200


@app.route('/api/matches/calculate', methods=['POST'])
def calculate_match():
    """Calculate match score between a mentee and mentor (for demo/testing)."""
    data = request.get_json()
    
    mentee_id = data.get('mentee_id')
    mentor_id = data.get('mentor_id')
    
    if not mentee_id or not mentor_id:
        return jsonify({'error': 'Both mentee_id and mentor_id required'}), 400
    
    mentee = Mentee.query.get_or_404(mentee_id)
    mentor = Mentor.query.get_or_404(mentor_id)
    
    result = calculate_compatibility(mentee, mentor)
    
    return jsonify({
        'mentee': mentee.to_dict(),
        'mentor': mentor.to_dict(),
        'compatibility': result
    }), 200


@app.route('/api/matches', methods=['POST'])
@jwt_required()
def create_match():
    """Create a match between mentor and mentee."""
    data = request.get_json()
    
    mentor_id = data.get('mentor_id')
    mentee_id = data.get('mentee_id')
    
    if not mentor_id or not mentee_id:
        return jsonify({'error': 'Mentor ID and Mentee ID required'}), 400
    
    mentor = Mentor.query.get(mentor_id)
    mentee = Mentee.query.get(mentee_id)
    
    if not mentor or not mentee:
        return jsonify({'error': 'Mentor or mentee not found'}), 404
    
    existing = Match.query.filter_by(mentor_id=mentor_id, mentee_id=mentee_id).first()
    if existing:
        return jsonify({'error': 'Match already exists'}), 409
    
    result = calculate_compatibility(mentee, mentor)
    
    match = Match(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        compatibility_score=result['score'],
        status='pending'
    )
    
    db.session.add(match)
    db.session.commit()
    
    return jsonify({
        'message': 'Match created successfully',
        'match': match.to_dict(),
        'compatibility': result
    }), 201


@app.route('/api/matches/my-matches', methods=['GET'])
@jwt_required()
def get_my_matches():
    """Get all matches for current user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'mentor':
        mentor = Mentor.query.filter_by(user_id=current_user_id).first()
        if not mentor:
            return jsonify({'matches': []}), 200
        matches = Match.query.filter_by(mentor_id=mentor.id).all()
    else:
        mentee = Mentee.query.filter_by(user_id=current_user_id).first()
        if not mentee:
            return jsonify({'matches': []}), 200
        matches = Match.query.filter_by(mentee_id=mentee.id).all()
    
    return jsonify({
        'matches': [match.to_dict() for match in matches]
    }), 200


@app.route('/api/matches/<int:match_id>/status', methods=['PUT'])
@jwt_required()
def update_match_status(match_id):
    """Update match status."""
    match = Match.query.get_or_404(match_id)
    data = request.get_json()
    
    status = data.get('status')
    if status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    match.status = status
    db.session.commit()
    
    return jsonify({
        'message': 'Match status updated',
        'match': match.to_dict()
    }), 200


@app.route('/api/matches/test', methods=['GET'])
def test_match():
    """Test endpoint for frontend connectivity."""
    return jsonify({
        'message': 'Backend matching API is connected!',
        'status': 'success'
    }), 200


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Initialize database on first run
    with app.app_context():
        db.create_all()
        print(f"Database ready at: {db_path}")
    
    print("Starting PathMatch API server...")
    print("API available at: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # Demo mode - always enable debug
    )
