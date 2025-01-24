import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import MasterData

def delete_all_master_data():
    """Delete all master data records from the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get count of records before deletion
            count = MasterData.query.count()
            
            if count == 0:
                print("No master data records found to delete.")
                return
            
            # Ask for confirmation
            confirm = input(f"Are you sure you want to delete all {count} master data records? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("Operation cancelled.")
                return
            
            # Delete all records
            MasterData.query.delete()
            db.session.commit()
            
            print(f"Successfully deleted {count} master data records.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting master data: {str(e)}")
            raise

if __name__ == '__main__':
    delete_all_master_data() 