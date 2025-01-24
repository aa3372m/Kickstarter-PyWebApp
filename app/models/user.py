from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
import jwt
from flask import current_app
from time import time

class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100))
    profile_picture = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    last_password_change = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, full_name=None, is_admin=False):
        self.username = username
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.is_admin = is_admin
        self.last_password_change = datetime.utcnow()
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_in=3600):
        """Generate password reset token"""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_token(token):
        """Verify password reset token"""
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except:
            return None
        return User.query.get(id)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 