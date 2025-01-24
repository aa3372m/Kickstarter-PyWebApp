from datetime import datetime
from ..extensions import db

class MasterData(db.Model):
    """Master data model"""
    __tablename__ = 'master_data'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    icon = db.Column(db.String(50))
    tags = db.Column(db.String(100))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_master_data_created_by'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    # Unique constraint for category and code combination
    __table_args__ = (
        db.UniqueConstraint('category', 'code', name='uq_master_data_category_code'),
    )
    
    def __init__(self, category, code, name, description=None, icon=None, tags=None, sort_order=0, is_active=True, created_by_id=None):
        self.category = category
        self.code = code
        self.name = name
        self.description = description
        self.icon = icon
        self.tags = tags
        self.sort_order = sort_order
        self.is_active = is_active
        self.created_by_id = created_by_id
    
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'tags': self.tags,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MasterData {self.category}:{self.code}>' 