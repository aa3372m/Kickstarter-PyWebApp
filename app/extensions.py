from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
jwt = JWTManager()
csrf = CSRFProtect() 