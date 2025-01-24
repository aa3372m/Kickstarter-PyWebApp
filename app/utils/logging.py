import os
import logging
from logging.handlers import RotatingFileHandler
from flask import request

def configure_logging(app):
    """Configure application logging with detailed formatting"""
    
    # Set logging level based on configuration
    log_level = logging.DEBUG if app.config['VERBOSE'] else logging.INFO
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n'
        'Remote IP: %(remote_ip)s\n'
        'Method: %(http_method)s\n'
        'Path: %(path)s\n'
        'Message: %(message)s\n'
        'Additional Data: %(extra_data)s\n'
        '----------------------'
    )
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Add custom filter to include request information
    class RequestFilter(logging.Filter):
        def filter(self, record):
            record.remote_ip = request.remote_addr if request else 'N/A'
            record.http_method = request.method if request else 'N/A'
            record.path = request.path if request else 'N/A'
            record.extra_data = getattr(record, 'extra_data', 'None')
            return True
    
    # Apply filter to file handler
    file_handler.addFilter(RequestFilter())
    
    # Remove existing handlers and add new one
    del app.logger.handlers[:]
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    # Log application startup
    app.logger.info(
        'Application started',
        extra={'extra_data': {
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'debug': app.debug,
            'testing': app.testing,
            'secret_key_set': bool(app.secret_key),
            'csrf_enabled': app.config['WTF_CSRF_ENABLED']
        }}
    )

def log_operation(logger, operation, status, details=None):
    """Utility function to log operations with consistent formatting
    
    Args:
        logger: The application logger instance
        operation: String describing the operation (e.g., 'User Login', 'Database Update')
        status: String indicating the outcome ('success', 'failure', 'error')
        details: Dictionary containing additional operation details
    """
    log_data = {
        'operation': operation,
        'status': status,
        'details': details or {}
    }
    
    if status == 'success':
        logger.info(f'{operation} completed successfully', extra={'extra_data': log_data})
    elif status == 'failure':
        logger.warning(f'{operation} failed', extra={'extra_data': log_data})
    else:
        logger.error(f'{operation} encountered an error', extra={'extra_data': log_data}) 