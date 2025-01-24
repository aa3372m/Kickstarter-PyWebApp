import os
import sys
import csv
from datetime import datetime
import logging

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, MasterData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_datetime(datetime_str):
    """Parse datetime string in ISO 8601 format"""
    try:
        logger.info(f"Parsing datetime string: {datetime_str}")
        return datetime.fromisoformat(datetime_str)
    except ValueError as e:
        logger.error(f"Error parsing datetime: {str(e)}")
        return datetime.utcnow()

def import_master_data(csv_file):
    """Import master data from CSV file"""
    logger.info(f"Starting master data import from file: {csv_file}")
    app = create_app()
    
    with app.app_context():
        # Get admin user
        logger.info("Looking for admin user...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            logger.error("Admin user not found")
            return
        logger.info(f"Found admin user with ID: {admin_user.id}")
        
        try:
            if not os.path.exists(csv_file):
                logger.error(f"CSV file not found: {csv_file}")
                return
                
            logger.info("Reading CSV file...")
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                row_count = 0
                success_count = 0
                skip_count = 0
                error_count = 0
                
                for row in reader:
                    row_count += 1
                    try:
                        logger.info(f"Processing row {row_count}: {row['category']}:{row['code']}")
                        
                        # Check if record already exists
                        existing = MasterData.query.filter_by(
                            category=row['category'],
                            code=row['code']
                        ).first()
                        
                        if existing:
                            logger.info(f"Skipping existing record: {row['category']}:{row['code']}")
                            skip_count += 1
                            continue
                        
                        # Create new master data record
                        master_data = MasterData(
                            category=row['category'],
                            code=row['code'],
                            name=row['description'],  # Using description as name
                            description=row['description'],
                            icon=row['icon'],
                            tags=row['tags'],
                            is_active=row['is_active'].upper() == 'TRUE',
                            created_by_id=admin_user.id
                        )
                        
                        db.session.add(master_data)
                        logger.info(f"Added: {row['category']}:{row['code']}")
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing row {row_count}: {str(e)}")
                        continue
                
                # Commit all changes
                db.session.commit()
                logger.info(f"""
                Import completed:
                - Total rows processed: {row_count}
                - Successfully added: {success_count}
                - Skipped (existing): {skip_count}
                - Errors: {error_count}
                """)
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fatal error during import: {str(e)}")
            raise

if __name__ == '__main__':
    csv_file = 'mydoc/sampledata/masterdata.csv'
    import_master_data(csv_file) 