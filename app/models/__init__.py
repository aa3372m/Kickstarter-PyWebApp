"""Models package initialization"""
from ..extensions import db

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .user_preferences import UserPreferences
from .master_data import MasterData
from .people import People

__all__ = ['db', 'User', 'UserPreferences', 'MasterData', 'People'] 