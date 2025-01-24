from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from ..models import db
from ..models.user import User
from ..models.user_preferences import UserPreferences
from ..utils.logging import log_operation
from ..forms.main import ProfileForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    """Home page route"""
    log_operation(
        current_app.logger,
        'Home Page Access',
        'success',
        {'user_id': current_user.id}
    )
    return render_template('main/index.html', title='Home')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    form = ProfileForm()
    
    # Set form choices from config
    form.theme.choices = [(theme, theme.title()) for theme in current_app.config['AVAILABLE_THEMES']]
    
    if request.method == 'GET':
        # Pre-populate form with current user data
        form.email.data = current_user.email
        form.full_name.data = current_user.full_name
        if current_user.preferences:
            form.theme.data = current_user.preferences.theme
            form.language.data = current_user.preferences.language
            form.notifications_enabled.data = current_user.preferences.notifications_enabled
    
    if form.validate_on_submit():
        try:
            # Update user information
            current_user.email = form.email.data
            current_user.full_name = form.full_name.data
            
            # Handle profile picture upload
            if form.profile_picture.data:
                file = form.profile_picture.data
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    if file_ext not in current_app.config['ALLOWED_EXTENSIONS']:
                        flash('Invalid file type. Please upload a valid image.', 'danger')
                        return redirect(url_for('main.profile'))
                    
                    # Save the file
                    upload_path = os.path.join(current_app.static_folder, 'uploads')
                    os.makedirs(upload_path, exist_ok=True)
                    
                    # Remove old profile picture if it exists
                    if current_user.profile_picture:
                        old_file = os.path.join(upload_path, current_user.profile_picture)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    
                    # Save new profile picture
                    new_filename = f'profile_{current_user.id}{file_ext}'
                    file.save(os.path.join(upload_path, new_filename))
                    current_user.profile_picture = new_filename
            
            # Update or create user preferences
            if not current_user.preferences:
                current_user.preferences = UserPreferences(user_id=current_user.id)
            
            current_user.preferences.theme = form.theme.data
            current_user.preferences.language = form.language.data
            current_user.preferences.notifications_enabled = form.notifications_enabled.data
            
            db.session.commit()
            
            log_operation(
                current_app.logger,
                'Profile Update',
                'success',
                {
                    'user_id': current_user.id,
                    'updated_fields': {
                        'email': current_user.email,
                        'full_name': current_user.full_name,
                        'theme': current_user.preferences.theme,
                        'language': current_user.preferences.language,
                        'notifications': current_user.preferences.notifications_enabled
                    }
                }
            )
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            log_operation(
                current_app.logger,
                'Profile Update',
                'error',
                {
                    'user_id': current_user.id,
                    'error': str(e)
                }
            )
            flash('Error updating profile. Please try again.', 'danger')
    
    log_operation(
        current_app.logger,
        'Profile Page Access',
        'success',
        {'user_id': current_user.id}
    )
    return render_template('main/profile.html', title='Profile Settings', form=form)

@main_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        # Remove profile picture if it exists
        if current_user.profile_picture:
            upload_path = os.path.join(current_app.static_folder, 'uploads')
            file_path = os.path.join(upload_path, current_user.profile_picture)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Store user info for logging
        user_id = current_user.id
        username = current_user.username
        
        # Delete user (cascade will handle related records)
        db.session.delete(current_user)
        db.session.commit()
        
        log_operation(
            current_app.logger,
            'Account Deletion',
            'success',
            {
                'user_id': user_id,
                'username': username
            }
        )
        
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        log_operation(
            current_app.logger,
            'Account Deletion',
            'error',
            {
                'user_id': current_user.id,
                'error': str(e)
            }
        )
        flash('Error deleting account. Please try again.', 'danger')
        return redirect(url_for('main.profile'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route"""
    return redirect(url_for('main.index'))  # For now, redirect to index 