import os
import json
from datetime import timedelta

# Load configuration from JSON file
with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
    config_data = json.load(f)

class Config:
    """Base configuration class"""
    
    # Application settings
    APP_NAME = config_data['app_name']
    CLIENT_NAME = config_data['client_name']
    VERBOSE = True
    
    # Security settings
    SECRET_KEY = config_data['security'].get('secret_key', os.urandom(32))
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=config_data['security']['session_lifetime'])
    PASSWORD_MIN_LENGTH = config_data['security']['password_min_length']
    
    # CSRF settings
    WTF_CSRF_ENABLED = config_data['security'].get('csrf_enabled', True)
    WTF_CSRF_TIME_LIMIT = config_data['security'].get('csrf_time_limit', 3600)
    WTF_CSRF_SSL_STRICT = False  # Allow CSRF token with HTTP during development
    
    # Theme settings
    DEFAULT_THEME = config_data['theme']['default']
    AVAILABLE_THEMES = config_data['theme']['available']
    
    # Mail settings
    MAIL_SERVER = config_data['mail_server']['smtp_host']
    MAIL_PORT = config_data['mail_server']['smtp_port']
    MAIL_USE_TLS = config_data['mail_server']['use_tls']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config_data['database']['development']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    VERBOSE = False
    SQLALCHEMY_DATABASE_URI = config_data['database']['production']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_SSL_STRICT = True  # Enforce HTTPS for CSRF tokens in production

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 