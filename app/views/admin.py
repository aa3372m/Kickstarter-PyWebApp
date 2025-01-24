from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc
from functools import wraps
from datetime import datetime, timedelta
import csv
import io
import json
import os
from werkzeug.utils import secure_filename
from email.utils import parsedate_to_datetime
import traceback

from ..models import db
from ..models.user import User
from ..models.user_preferences import UserPreferences
from ..models.master_data import MasterData
from ..utils.logging import log_operation
from ..forms.admin import MasterDataForm, MasterDataImportForm, SystemSettingsForm, UserEditForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            log_operation(
                current_app.logger,
                'Admin Access Attempt',
                'failure',
                {'user_id': getattr(current_user, 'id', None), 'path': request.path}
            )
            flash('You do not have permission to access this area.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    # Get user statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Get recent logins (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_logins = User.query.filter(User.last_login >= yesterday).count()
    
    # Get recent activity from logs (if available)
    recent_activity = []  # This would be populated from your logging system
    
    log_operation(
        current_app.logger,
        'Admin Dashboard Access',
        'success',
        {'user_id': current_user.id}
    )
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        active_users=active_users,
        recent_logins=recent_logins,
        recent_activity=recent_activity
    )

@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    log_operation(
        current_app.logger,
        'User List View',
        'success',
        {'page': page, 'total_users': users.total}
    )
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user page"""
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # Update user from form data
            form.populate_obj(user)
            
            # Update preferences
            if not user.preferences:
                user.preferences = UserPreferences(user_id=user.id)
            user.preferences.theme = form.theme.data
            
            db.session.commit()
            
            log_operation(
                current_app.logger,
                'User Update',
                'success',
                {
                    'user_id': user_id,
                    'updated_fields': {
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_active': user.is_active,
                        'is_admin': user.is_admin,
                        'theme': user.preferences.theme
                    }
                }
            )
            
            flash('User updated successfully.', 'success')
            return redirect(url_for('admin.user_list'))
            
        except Exception as e:
            db.session.rollback()
            log_operation(
                current_app.logger,
                'User Update',
                'error',
                {
                    'user_id': user_id,
                    'error': str(e)
                }
            )
            flash('Error updating user. Please try again.', 'danger')
    
    # Pre-populate theme field
    if user.preferences:
        form.theme.data = user.preferences.theme
    
    log_operation(
        current_app.logger,
        'User Edit View',
        'success',
        {'user_id': user_id}
    )
    return render_template('admin/edit_user.html', user=user, form=form)

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user == current_user:
        log_operation(
            current_app.logger,
            'User Status Toggle',
            'failure',
            {'user_id': user_id, 'reason': 'Cannot deactivate self'}
        )
        return jsonify({'error': 'You cannot deactivate your own account'}), 400
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        log_operation(
            current_app.logger,
            'User Status Toggle',
            'success',
            {'user_id': user_id, 'new_status': user.is_active}
        )
        
        return jsonify({
            'status': 'success',
            'is_active': user.is_active,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        log_operation(
            current_app.logger,
            'User Status Toggle',
            'error',
            {'user_id': user_id, 'error': str(e)}
        )
        return jsonify({'error': 'Failed to update user status'}), 500

@admin_bp.route('/master-data')
@login_required
@admin_required
def master_data():
    """Master data management page"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    per_page = 10
    
    query = MasterData.query
    if category:
        query = query.filter_by(category=category)
    
    data = query.order_by(MasterData.category, MasterData.sort_order).paginate(
        page=page, per_page=per_page, error_out=False)
    categories = db.session.query(MasterData.category).distinct().all()
    
    return render_template('admin/master_data.html',
                         master_data=data,
                         categories=categories,
                         current_category=category)

@admin_bp.route('/master-data/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_master_data():
    """Add master data page"""
    form = MasterDataForm()
    import_form = MasterDataImportForm()
    
    if form.validate_on_submit():
        try:
            data = MasterData(
                category=form.category.data,
                code=form.code.data,
                name=form.name.data,
                description=form.description.data,
                icon=form.icon.data,
                tags=form.tags.data,
                sort_order=form.sort_order.data,
                is_active=form.is_active.data,
                created_by_id=current_user.id
            )
            db.session.add(data)
            db.session.commit()
            
            log_operation(
                current_app.logger,
                'Master Data Creation',
                'success',
                {
                    'user_id': current_user.id,
                    'category': data.category,
                    'code': data.code
                }
            )
            
            flash('Master data added successfully.', 'success')
            return redirect(url_for('admin.master_data'))
            
        except Exception as e:
            db.session.rollback()
            log_operation(
                current_app.logger,
                'Master Data Creation',
                'error',
                {
                    'user_id': current_user.id,
                    'error': str(e)
                }
            )
            flash('Error adding master data.', 'danger')
    
    return render_template('admin/edit_master_data.html', form=form, import_form=import_form, data=None)

@admin_bp.route('/master-data/<int:data_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_master_data(data_id):
    """Edit master data page"""
    data = MasterData.query.get_or_404(data_id)
    form = MasterDataForm(obj=data)
    import_form = MasterDataImportForm()
    
    if form.validate_on_submit():
        try:
            form.populate_obj(data)
            db.session.commit()
            
            log_operation(
                current_app.logger,
                'Master Data Update',
                'success',
                {
                    'user_id': current_user.id,
                    'data_id': data_id,
                    'category': data.category,
                    'code': data.code
                }
            )
            
            flash('Master data updated successfully.', 'success')
            return redirect(url_for('admin.master_data'))
            
        except Exception as e:
            db.session.rollback()
            log_operation(
                current_app.logger,
                'Master Data Update',
                'error',
                {
                    'user_id': current_user.id,
                    'data_id': data_id,
                    'error': str(e)
                }
            )
            flash('Error updating master data.', 'danger')
    
    return render_template('admin/edit_master_data.html', form=form, import_form=import_form, data=data)

@admin_bp.route('/master-data/import', methods=['POST'])
@login_required
@admin_required
def import_master_data():
    """Import master data from CSV"""
    form = MasterDataImportForm()
    
    if form.validate_on_submit():
        try:
            # Read CSV file
            csv_file = form.file.data
            stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Process each row
            success_count = 0
            error_count = 0
            
            for row in csv_reader:
                try:
                    # Convert string to boolean
                    is_active = row['is_active'].upper() == 'TRUE'
                    
                    # Parse created_on date using ISO format
                    try:
                        created_on = datetime.fromisoformat(row['created_on'])
                    except ValueError:
                        created_on = datetime.utcnow()
                    
                    # Find or create user by email
                    user = User.query.filter_by(email=row['created_by']).first()
                    if not user:
                        user = current_user
                    
                    # Check if record already exists
                    existing = MasterData.query.filter_by(
                        category=row['category'],
                        code=row['code']
                    ).first()
                    
                    if existing:
                        current_app.logger.info(f"Skipping existing record: {row['category']}:{row['code']}")
                        continue
                    
                    # Create master data entry
                    data = MasterData(
                        category=row['category'],
                        code=row['code'],
                        name=row['description'],  # Using description as name
                        description=row['description'],
                        icon=row['icon'],
                        tags=row['tags'],
                        is_active=is_active,
                        created_by_id=user.id
                    )
                    data.created_at = created_on
                    db.session.add(data)
                    success_count += 1
                    current_app.logger.info(f"Added: {row['category']}:{row['code']}")
                    
                except Exception as row_error:
                    error_count += 1
                    current_app.logger.error(f"Error processing row: {str(row_error)}")
                    continue
            
            db.session.commit()
            
            log_operation(
                current_app.logger,
                'Master Data Import',
                'success',
                {
                    'user_id': current_user.id,
                    'success_count': success_count,
                    'error_count': error_count
                }
            )
            
            flash(f'Master data imported successfully. Added: {success_count}, Errors: {error_count}', 'success')
            
        except Exception as e:
            db.session.rollback()
            log_operation(
                current_app.logger,
                'Master Data Import',
                'error',
                {
                    'user_id': current_user.id,
                    'error': str(e)
                }
            )
            flash(f'Error importing master data: {str(e)}', 'danger')
    
    return redirect(url_for('admin.master_data'))

@admin_bp.route('/master-data/<int:data_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_master_data(data_id):
    """Delete master data entry"""
    data = MasterData.query.get_or_404(data_id)
    
    try:
        db.session.delete(data)
        db.session.commit()
        
        log_operation(
            current_app.logger,
            'Master Data Deletion',
            'success',
            {
                'user_id': current_user.id,
                'data_id': data_id,
                'category': data.category,
                'code': data.code
            }
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Master data deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        log_operation(
            current_app.logger,
            'Master Data Deletion',
            'error',
            {
                'user_id': current_user.id,
                'data_id': data_id,
                'error': str(e)
            }
        )
        return jsonify({
            'status': 'error',
            'error': 'Failed to delete master data'
        }), 500

@admin_bp.route('/systemsettings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    """System settings management page"""
    current_app.logger.info("Accessing system settings page")
    form = SystemSettingsForm()
    config_file = os.path.join(current_app.root_path, '..', 'config', 'config.json')
    current_app.logger.info(f"Config file path: {config_file}")
    
    if request.method == 'GET':
        current_app.logger.info("Processing GET request")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                current_app.logger.info("Current configuration loaded successfully")
                
            # Populate form with current settings
            form.app_name.data = config.get('app_name', '')
            form.client_name.data = config.get('client_name', '')
            form.default_theme.data = config.get('theme', {}).get('default', 'light')
            
            # Mail settings
            mail_config = config.get('mail_server', {})
            form.smtp_host.data = mail_config.get('smtp_host', '')
            form.smtp_port.data = mail_config.get('smtp_port', 587)
            form.smtp_user.data = mail_config.get('smtp_user', '')
            form.smtp_password.data = mail_config.get('smtp_password', '')
            form.smtp_use_tls.data = mail_config.get('use_tls', True)
            
            # Security settings
            security = config.get('security', {})
            form.session_lifetime.data = security.get('session_lifetime', 86400)
            form.password_min_length.data = security.get('password_min_length', 8)
            form.admin_email.data = config.get('admin_email', '')
            
            current_app.logger.info("Form populated with current settings")
            
        except Exception as e:
            current_app.logger.error(f"Error loading configuration: {str(e)}")
            log_operation(
                current_app.logger,
                'System Settings Load',
                'error',
                {'error': str(e)}
            )
            flash('Error loading configuration. Please check the logs.', 'danger')
    
    if form.validate_on_submit():
        current_app.logger.info("Form submitted and validated")
        try:
            # Create backup before saving
            backup_file = os.path.join(
                current_app.root_path, '..', 'config',
                f'config_backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            )
            current_app.logger.info(f"Backup file path: {backup_file}")
            
            # Read current config first
            with open(config_file, 'r') as f:
                current_config = json.load(f)
                current_app.logger.info("Current configuration loaded for backup")
            
            # Create backup
            with open(backup_file, 'w') as f:
                json.dump(current_config, f, indent=2)
                current_app.logger.info("Backup created successfully")
            
            # Log form data
            current_app.logger.info("Form data:")
            current_app.logger.info(f"app_name: {form.app_name.data}")
            current_app.logger.info(f"client_name: {form.client_name.data}")
            current_app.logger.info(f"default_theme: {form.default_theme.data}")
            current_app.logger.info(f"smtp_host: {form.smtp_host.data}")
            
            # Update configuration
            new_config = {
                'app_name': form.app_name.data,
                'client_name': form.client_name.data,
                'theme': {
                    'default': form.default_theme.data,
                    'available': current_config.get('theme', {}).get('available', ['light', 'dark'])
                },
                'mail_server': {
                    'smtp_host': form.smtp_host.data,
                    'smtp_port': form.smtp_port.data,
                    'smtp_user': form.smtp_user.data,
                    'smtp_password': form.smtp_password.data,
                    'use_tls': form.smtp_use_tls.data
                },
                'security': {
                    'session_lifetime': form.session_lifetime.data,
                    'password_min_length': form.password_min_length.data
                },
                'admin_email': form.admin_email.data,
                'database': current_config.get('database', {})  # Preserve database settings
            }
            
            current_app.logger.info("New configuration prepared")
            
            # Save new configuration
            with open(config_file, 'w') as f:
                json.dump(new_config, f, indent=2)
                current_app.logger.info("New configuration saved successfully")
            
            log_operation(
                current_app.logger,
                'System Settings Update',
                'success',
                {
                    'user_id': current_user.id,
                    'backup_file': os.path.basename(backup_file)
                }
            )
            
            flash('Configuration updated successfully. Backup created.', 'success')
            return redirect(url_for('admin.system_settings'))
            
        except Exception as e:
            current_app.logger.error(f"Error updating configuration: {str(e)}")
            current_app.logger.error(f"Exception type: {type(e)}")
            current_app.logger.error(f"Exception traceback: {traceback.format_exc()}")
            log_operation(
                current_app.logger,
                'System Settings Update',
                'error',
                {
                    'user_id': current_user.id,
                    'error': str(e)
                }
            )
            flash(f'Error updating configuration: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            current_app.logger.error("Form validation failed")
            current_app.logger.error(f"Form errors: {form.errors}")
    
    return render_template('admin/system_settings.html', form=form)

@admin_bp.route('/systemsettings/backup', methods=['POST'])
@login_required
@admin_required
def backup_config():
    """Create and download a backup of the configuration"""
    try:
        config_file = os.path.join(current_app.root_path, '..', 'config', 'config.json')
        backup_name = f'config_backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        
        log_operation(
            current_app.logger,
            'Configuration Backup',
            'success',
            {'filename': backup_name}
        )
        
        return send_file(
            config_file,
            mimetype='application/json',
            as_attachment=True,
            download_name=backup_name
        )
        
    except Exception as e:
        log_operation(
            current_app.logger,
            'Configuration Backup',
            'error',
            {'error': str(e)}
        )
        flash(f'Error creating backup: {str(e)}', 'danger')
        return redirect(url_for('admin.system_settings'))

@admin_bp.route('/systemsettings/restore', methods=['POST'])
@login_required
@admin_required
def restore_config():
    """Restore configuration from a backup file"""
    if 'config_file' not in request.files:
        flash('No file provided', 'danger')
        return redirect(url_for('admin.system_settings'))
    
    file = request.files['config_file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin.system_settings'))
    
    try:
        # Read and validate the uploaded config
        config_data = json.load(file)
        required_keys = ['app_name', 'client_name', 'theme', 'mail_server', 'security']
        if not all(key in config_data for key in required_keys):
            raise ValueError('Invalid configuration file format')
        
        # Create backup of current config
        current_config_file = os.path.join(current_app.root_path, '..', 'config', 'config.json')
        backup_name = f'config_backup_before_restore_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        backup_path = os.path.join(current_app.root_path, '..', 'config', backup_name)
        
        with open(current_config_file, 'r') as f:
            current_config = json.load(f)
        with open(backup_path, 'w') as f:
            json.dump(current_config, f, indent=2)
        
        # Save the new config
        with open(current_config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        log_operation(
            current_app.logger,
            'Configuration Restore',
            'success',
            {
                'backup_file': backup_name,
                'restored_from': file.filename
            }
        )
        
        flash('Configuration restored successfully. Backup of previous configuration created.', 'success')
        
    except ValueError as e:
        log_operation(
            current_app.logger,
            'Configuration Restore',
            'error',
            {'error': 'Invalid configuration format'}
        )
        flash('Invalid configuration file format', 'danger')
    except Exception as e:
        log_operation(
            current_app.logger,
            'Configuration Restore',
            'error',
            {'error': str(e)}
        )
        flash(f'Error restoring configuration: {str(e)}', 'danger')
    
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/viewlogs')
@login_required
@admin_required
def view_logs():
    """View application logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    log_file = os.path.join(current_app.root_path, '..', 'logs', 'app.log')
    
    try:
        # Read the log file
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                # Read all lines and reverse them to show newest first
                log_entries = f.readlines()
                log_entries.reverse()
                
                # Simple pagination
                total_entries = len(log_entries)
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                current_entries = log_entries[start_idx:end_idx]
                
                # Parse log entries
                parsed_entries = []
                for entry in current_entries:
                    try:
                        # Assuming log format: timestamp level message
                        parts = entry.split(' ', 2)
                        if len(parts) >= 3:
                            timestamp, level, message = parts
                            parsed_entries.append({
                                'timestamp': timestamp,
                                'level': level.strip('[]'),
                                'message': message.strip()
                            })
                        else:
                            parsed_entries.append({
                                'timestamp': '',
                                'level': 'UNKNOWN',
                                'message': entry.strip()
                            })
                    except Exception as e:
                        current_app.logger.error(f"Error parsing log entry: {str(e)}")
                        parsed_entries.append({
                            'timestamp': '',
                            'level': 'ERROR',
                            'message': entry.strip()
                        })
                
                total_pages = (total_entries + per_page - 1) // per_page
        else:
            parsed_entries = []
            total_pages = 1
            flash('Log file not found.', 'warning')
        
        log_operation(
            current_app.logger,
            'View Logs',
            'success',
            {'page': page, 'entries_count': len(parsed_entries)}
        )
        
        return render_template(
            'admin/view_logs.html',
            logs=parsed_entries,
            page=page,
            total_pages=total_pages,
            per_page=per_page
        )
        
    except Exception as e:
        log_operation(
            current_app.logger,
            'View Logs',
            'error',
            {'error': str(e)}
        )
        flash(f'Error reading logs: {str(e)}', 'danger')
        return redirect(url_for('admin.admin_dashboard')) 