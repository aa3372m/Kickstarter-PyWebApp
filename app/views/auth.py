from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime

from ..models import db
from ..models.user import User
from ..models.user_preferences import UserPreferences
from ..forms.auth import LoginForm, RegistrationForm, RequestPasswordResetForm, ResetPasswordForm, ChangePasswordForm
from ..utils.email import send_password_reset_email
from ..utils.logging import log_operation

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            current_app.logger.warning(f'Failed login attempt for username: {form.username.data}')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('This account has been deactivated. Please contact an administrator.', 'error')
            current_app.logger.warning(f'Deactivated account login attempt: {user.username}')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()

        if current_app.config['VERBOSE']:
            current_app.logger.info(f'User logged in: {user.username}')

        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    if current_app.config['VERBOSE']:
        current_app.logger.info(f'User logged out: {current_user.username}')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            full_name=form.full_name.data
        )
        
        db.session.add(user)
        db.session.flush()  # Flush to get user id
        
        # Create user preferences with default theme
        preferences = UserPreferences(
            user_id=user.id,
            theme=current_app.config['DEFAULT_THEME']
        )
        
        db.session.add(preferences)
        db.session.commit()

        if current_app.config['VERBOSE']:
            current_app.logger.info(f'New user registered: {user.username}')

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Password reset request route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            if current_app.config['VERBOSE']:
                current_app.logger.info(f'Password reset requested for user: {user.username}')
        flash('Check your email for instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        if current_app.config['VERBOSE']:
            current_app.logger.info(f'Password reset completed for user: {user.username}')
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route for authenticated users"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        log_operation(
            current_app.logger,
            'Password Change',
            'success',
            {'user_id': current_user.id}
        )
        
        flash('Your password has been changed successfully.', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/change_password.html', title='Change Password', form=form) 