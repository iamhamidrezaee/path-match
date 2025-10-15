from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Mentor

bp = Blueprint('mentors', __name__, url_prefix='/api/mentors')

@bp.route('/', methods=['GET'])
def get_mentors():
    """Get all available mentors"""
    mentors = Mentor.query.filter_by(availability_status='available').all()
    return jsonify({'mentors': [mentor.to_dict() for mentor in mentors]}), 200

@bp.route('/<int:mentor_id>', methods=['GET'])
def get_mentor(mentor_id):
    """Get specific mentor by ID"""
    mentor = Mentor.query.get_or_404(mentor_id)
    return jsonify({'mentor': mentor.to_dict()}), 200

@bp.route('/profile', methods=['POST'])
@jwt_required()
def create_mentor_profile():
    """Create or update mentor profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'mentor':
        return jsonify({'error': 'User is not registered as a mentor'}), 403
    
    data = request.get_json()
    
    # Check if profile exists
    mentor = Mentor.query.filter_by(user_id=current_user_id).first()
    
    if mentor:
        # Update existing profile
        mentor.graduating_year = data.get('graduating_year', mentor.graduating_year)
        mentor.professional_experiences = data.get('professional_experiences', mentor.professional_experiences)
        mentor.postgrad_plans = data.get('postgrad_plans', mentor.postgrad_plans)
        mentor.info_concentration = data.get('info_concentration', mentor.info_concentration)
        mentor.technical_courses = data.get('technical_courses', mentor.technical_courses)
        mentor.calendly_link = data.get('calendly_link', mentor.calendly_link)
        mentor.availability_status = data.get('availability_status', mentor.availability_status)
    else:
        # Create new profile
        mentor = Mentor(
            user_id=current_user_id,
            graduating_year=data.get('graduating_year'),
            professional_experiences=data.get('professional_experiences'),
            postgrad_plans=data.get('postgrad_plans'),
            info_concentration=data.get('info_concentration'),
            technical_courses=data.get('technical_courses'),
            calendly_link=data.get('calendly_link'),
            availability_status=data.get('availability_status', 'available')
        )
        db.session.add(mentor)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Mentor profile updated successfully',
        'mentor': mentor.to_dict()
    }), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_my_mentor_profile():
    """Get current user's mentor profile"""
    current_user_id = get_jwt_identity()
    mentor = Mentor.query.filter_by(user_id=current_user_id).first()
    
    if not mentor:
        return jsonify({'error': 'Mentor profile not found'}), 404
    
    return jsonify({'mentor': mentor.to_dict()}), 200

@bp.route('/availability', methods=['PUT'])
@jwt_required()
def update_availability():
    """Update mentor availability status"""
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
    
    return jsonify({
        'message': 'Availability updated',
        'status': status
    }), 200

