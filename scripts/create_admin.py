# conda activate kickstarter101 && export FLASK_APP=run.py && python scripts/create_admin.py
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.user_preferences import UserPreferences

def create_admin_user():
    """Create an admin user if it doesn't exist"""
    app = create_app('development')
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password='admin123',  # This will be hashed by the User model
                full_name='Administrator',
                is_admin=True
            )
            
            db.session.add(admin)
            db.session.flush()  # Get the user id
            
            # Create user preferences
            preferences = UserPreferences(
                user_id=admin.id,
                theme=app.config['DEFAULT_THEME']
            )
            
            db.session.add(preferences)
            db.session.commit()
            
            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print("Admin user already exists!")

if __name__ == '__main__':
    load_dotenv()  # Load environment variables
    create_admin_user() 