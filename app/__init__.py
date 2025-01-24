import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template
from flask_wtf.csrf import CSRFError
from datetime import datetime

from config.config import config
from .extensions import db, login_manager, migrate, mail, jwt, csrf
from .utils.logging import configure_logging

def create_app(config_name=None):
    """Create Flask application."""
    if not config_name:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure the logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    log_file = os.path.join(logs_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))
    
    # Register error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/csrf_error.html', reason=e.description), 400
    
    # Register context processors
    @app.context_processor
    def utility_processor():
        return {'now': datetime.utcnow()}
    
    # Register blueprints
    from .views.main import main_bp
    from .views.auth import auth_bp
    from .views.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    return app 