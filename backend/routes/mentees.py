from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Mentee

bp = Blueprint('mentees', __name__, url_prefix='/api/mentees')

@bp.route('/profile', methods=['POST'])
@jwt_required()
def create_mentee_profile():
    """Create or update mentee profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'mentee':
        return jsonify({'error': 'User is not registered as a mentee'}), 403
    
    data = request.get_json()
    
    # Check if profile exists
    mentee = Mentee.query.filter_by(user_id=current_user_id).first()
    
    if mentee:
        # Update existing profile
        mentee.graduating_year = data.get('graduating_year', mentee.graduating_year)
        mentee.looking_for_career_advice = data.get('looking_for_career_advice', mentee.looking_for_career_advice)
        mentee.careers_interested_in = data.get('careers_interested_in', mentee.careers_interested_in)
        mentee.looking_for_major_advice = data.get('looking_for_major_advice', mentee.looking_for_major_advice)
        mentee.concentrations_interested_in = data.get('concentrations_interested_in', mentee.concentrations_interested_in)
        mentee.technical_courses_taken = data.get('technical_courses_taken', mentee.technical_courses_taken)
    else:
        # Create new profile
        mentee = Mentee(
            user_id=current_user_id,
            graduating_year=data.get('graduating_year'),
            looking_for_career_advice=data.get('looking_for_career_advice', False),
            careers_interested_in=data.get('careers_interested_in'),
            looking_for_major_advice=data.get('looking_for_major_advice', False),
            concentrations_interested_in=data.get('concentrations_interested_in'),
            technical_courses_taken=data.get('technical_courses_taken')
        )
        db.session.add(mentee)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Mentee profile updated successfully',
        'mentee': mentee.to_dict()
    }), 200

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_my_mentee_profile():
    """Get current user's mentee profile"""
    current_user_id = get_jwt_identity()
    mentee = Mentee.query.filter_by(user_id=current_user_id).first()
    
    if not mentee:
        return jsonify({'error': 'Mentee profile not found'}), 404
    
    return jsonify({'mentee': mentee.to_dict()}), 200

