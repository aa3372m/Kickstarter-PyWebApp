from datetime import datetime
from ..extensions import db

class People(db.Model):
    """People model"""
    __tablename__ = 'people'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(1))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_people_created_by'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    # Unique constraint for email
    __table_args__ = (
        db.UniqueConstraint('email', name='uq_people_email'),
    )
    
    def __init__(self, first_name, last_name=None, email=None, phone=None, address=None, birth_date=None, gender=None, notes=None, is_active=True, created_by_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.birth_date = birth_date
        self.gender = gender
        self.notes = notes
        self.is_active = is_active
        self.created_by_id = created_by_id
    
    @property
    def full_name(self):
        """Return the full name of the person"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def to_dict(self):
        """Convert object to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': self.gender,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<People {self.full_name}>' 