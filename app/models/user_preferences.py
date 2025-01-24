from datetime import datetime
from . import db

class UserPreferences(db.Model):
    """User preferences model for storing user-specific settings"""
    
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_preferences_user_id'), unique=True, nullable=False)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(5), default='en')
    sidebar_pinned = db.Column(db.Boolean, default=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', name='uq_user_preferences_user_id'),
    )
    
    def __init__(self, user_id, theme='light', language='en'):
        self.user_id = user_id
        self.theme = theme
        self.language = language
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'sidebar_pinned': self.sidebar_pinned,
            'notifications_enabled': self.notifications_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserPreferences {self.user_id}>' 