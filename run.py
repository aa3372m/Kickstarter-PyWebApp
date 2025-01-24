import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    ) 