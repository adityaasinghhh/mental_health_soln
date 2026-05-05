from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    
    def get_id(self):
        return str(self.id)

class Assessment(db.Model):
    """Store mental health assessment results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    anxiety_score = db.Column(db.Integer)
    depression_score = db.Column(db.Integer)
    stress_score = db.Column(db.Integer)
    general_score = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    overall_status = db.Column(db.String(20))
    
    nlp_sentiment_score = db.Column(db.Float)
    nlp_sentiment_tone = db.Column(db.String(50))
    nlp_subjectivity = db.Column(db.Float)
    nlp_polarity = db.Column(db.Float)
    
    combined_status = db.Column(db.String(20))
    psychometric_responses = db.Column(db.Text)
    nlp_responses = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.assessment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'anxiety_score': self.anxiety_score,
            'depression_score': self.depression_score,
            'stress_score': self.stress_score,
            'general_score': self.general_score,
            'total_score': self.total_score,
            'overall_status': self.overall_status,
            'nlp_sentiment_score': self.nlp_sentiment_score,
            'combined_status': self.combined_status
        }