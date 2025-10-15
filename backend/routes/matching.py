from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Mentor, Mentee, Match
from services.matching_algorithm import calculate_compatibility

bp = Blueprint('matching', __name__, url_prefix='/api/matches')

@bp.route('/find', methods=['POST'])
@jwt_required()
def find_matches():
    """Find compatible mentors for a mentee"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role != 'mentee':
        return jsonify({'error': 'Only mentees can search for mentors'}), 403
    
    mentee = Mentee.query.filter_by(user_id=current_user_id).first()
    if not mentee:
        return jsonify({'error': 'Mentee profile not found'}), 404
    
    # Get all available mentors
    available_mentors = Mentor.query.filter_by(availability_status='available').all()
    
    # Calculate compatibility scores
    matches = []
    for mentor in available_mentors:
        score = calculate_compatibility(mentee, mentor)
        matches.append({
            'mentor': mentor.to_dict(),
            'compatibility_score': score
        })
    
    # Sort by compatibility score
    matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
    
    return jsonify({
        'matches': matches[:10]  # Return top 10 matches
    }), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_match():
    """Create a match between mentor and mentee"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    mentor_id = data.get('mentor_id')
    mentee_id = data.get('mentee_id')
    
    if not mentor_id or not mentee_id:
        return jsonify({'error': 'Mentor ID and Mentee ID required'}), 400
    
    # Verify mentor and mentee exist
    mentor = Mentor.query.get(mentor_id)
    mentee = Mentee.query.get(mentee_id)
    
    if not mentor or not mentee:
        return jsonify({'error': 'Mentor or mentee not found'}), 404
    
    # Check if match already exists
    existing_match = Match.query.filter_by(mentor_id=mentor_id, mentee_id=mentee_id).first()
    if existing_match:
        return jsonify({'error': 'Match already exists'}), 409
    
    # Calculate compatibility
    score = calculate_compatibility(mentee, mentor)
    
    # Create match
    match = Match(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        compatibility_score=score,
        status='pending'
    )
    
    db.session.add(match)
    db.session.commit()
    
    return jsonify({
        'message': 'Match created successfully',
        'match': match.to_dict()
    }), 201

@bp.route('/my-matches', methods=['GET'])
@jwt_required()
def get_my_matches():
    """Get all matches for current user"""
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

@bp.route('/<int:match_id>/status', methods=['PUT'])
@jwt_required()
def update_match_status(match_id):
    """Update match status"""
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

