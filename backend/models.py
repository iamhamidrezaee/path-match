from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(db.Model):
    """Base user model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    net_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'mentor' or 'mentee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mentor_profile = db.relationship('Mentor', backref='user', uselist=False, cascade='all, delete-orphan')
    mentee_profile = db.relationship('Mentee', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'net_id': self.net_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Mentor(db.Model):
    """Mentor profile and availability"""
    __tablename__ = 'mentors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    graduating_year = db.Column(db.Integer, nullable=False)
    info_concentration = db.Column(db.String(100)) 
    preferred_communication = db.Column(db.String(50)) # e.g., 'email', 'zoom', 'in-person'
    advising_topics = db.Column(db.Text) # JSON array of topics
    career_pursuing = db.Column(db.String(100))
    experiences = db.Column(db.Text)  # JSON string of experiences/roles
    bio = db.Column(db.Text) # JSON string of personal bio
    calendly_link = db.Column(db.String(255))
    availability_status = db.Column(db.String(20), default='available')  # 'available', 'dnd', 'unavailable'
    ratings_feedback = db.Column(db.Text)  # JSON array of feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    survey_responses = db.relationship('SurveyResponse', backref='mentor', lazy=True, 
                                      foreign_keys='SurveyResponse.mentor_id')
    matches = db.relationship('Match', backref='mentor', lazy=True, 
                            foreign_keys='Match.mentor_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'graduating_year': self.graduating_year,
            'info_concentration': self.info_concentration,
            'preferred_communication': self.preferred_communication,
            'advising_topics': self.advising_topics,
            'career_pursuing': self.career_pursuing,
            'bio': self.bio,
            'calendly_link': self.calendly_link,
            'availability_status': self.availability_status
        }


class Mentee(db.Model):
    """Mentee profile and needs"""
    __tablename__ = 'mentees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    graduating_year = db.Column(db.Integer, nullable=False)
    info_concentration = db.Column(db.String(100))
    preferred_communication = db.Column(db.String(50))  # e.g., 'email', 'zoom', 'in-person'
    advising_needs = db.Column(db.Text)  # JSON array of needs/topics
    # looking_for_career_advice = db.Column(db.Boolean, default=False)
    careers_interested_in = db.Column(db.Text)  # JSON array of career paths
    # looking_for_major_advice = db.Column(db.Boolean, default=False)
    field_interests = db.Column(db.Text)
    bio = db.Column(db.Text)  # JSON string of personal bio
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    survey_responses = db.relationship('SurveyResponse', backref='mentee', lazy=True,
                                      foreign_keys='SurveyResponse.mentee_id')
    matches = db.relationship('Match', backref='mentee', lazy=True,
                            foreign_keys='Match.mentee_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'graduating_year': self.graduating_year,
            'info_concentration': self.info_concentration,
            'preferred_communication': self.preferred_communication,
            'advising_needs': self.advising_needs,
            'careers_interested_in': self.careers_interested_in,
            'field_interests': self.field_interests,
            'bio': self.bio
        }


class SurveyResponse(db.Model):
    """Survey responses for matching algorithm"""
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=True)
    mentee_id = db.Column(db.Integer, db.ForeignKey('mentees.id'), nullable=True)
    question_id = db.Column(db.String(50), nullable=False)
    response_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'response_data': self.response_data,
            'created_at': self.created_at.isoformat()
        }


class Match(db.Model):
    """Mentor-mentee matches with compatibility scores"""
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('mentees.id'), nullable=False)
    compatibility_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'completed', 'cancelled'
    meeting_scheduled = db.Column(db.Boolean, default=False)
    meeting_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate matches
    __table_args__ = (db.UniqueConstraint('mentor_id', 'mentee_id', name='unique_mentor_mentee'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'mentor': self.mentor.to_dict() if self.mentor else None,
            'mentee': self.mentee.to_dict() if self.mentee else None,
            'compatibility_score': self.compatibility_score,
            'status': self.status,
            'meeting_scheduled': self.meeting_scheduled,
            'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None,
            'created_at': self.created_at.isoformat()
        }

