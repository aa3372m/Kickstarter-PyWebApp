from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask import current_app

from ..models.user import User

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    full_name = StringField('Full Name', validators=[
        Length(max=100)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, field):
        """Check if username is already taken"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already taken.')

    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already registered.')

    def validate_password(self, field):
        """Validate password complexity"""
        password = field.data
        if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
            raise ValidationError(f'Password must be at least {current_app.config["PASSWORD_MIN_LENGTH"]} characters long')
        if not any(c.isupper() for c in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in password):
            raise ValidationError('Password must contain at least one number')

class RequestPasswordResetForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, field):
        """Check if email exists"""
        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError('Email address not found.')

class ResetPasswordForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

    def validate_password(self, field):
        """Validate password complexity"""
        password = field.data
        if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
            raise ValidationError(f'Password must be at least {current_app.config["PASSWORD_MIN_LENGTH"]} characters long')
        if not any(c.isupper() for c in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in password):
            raise ValidationError('Password must contain at least one number')

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

    def validate_new_password(self, field):
        """Validate password complexity"""
        password = field.data
        if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
            raise ValidationError(f'Password must be at least {current_app.config["PASSWORD_MIN_LENGTH"]} characters long')
        if not any(c.isupper() for c in password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in password):
            raise ValidationError('Password must contain at least one number') 