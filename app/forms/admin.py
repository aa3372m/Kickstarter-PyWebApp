from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, URL, Email, ValidationError

class MasterDataForm(FlaskForm):
    """Form for managing master data"""
    category = StringField('Category', validators=[
        DataRequired(),
        Length(max=50)
    ])
    code = StringField('Code', validators=[
        DataRequired(),
        Length(max=50)
    ])
    name = StringField('Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    icon = StringField('Icon', validators=[
        Optional(),
        Length(max=50)
    ])
    tags = StringField('Tags', validators=[
        Optional(),
        Length(max=100)
    ])
    sort_order = IntegerField('Sort Order', default=0)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save')

class MasterDataImportForm(FlaskForm):
    """Form for importing master data from CSV"""
    file = FileField('CSV File', validators=[
        DataRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Import')

class SystemSettingsForm(FlaskForm):
    """Form for managing system settings"""
    app_name = StringField('Application Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    client_name = StringField('Client Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    default_theme = SelectField('Default Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark')
    ])
    smtp_host = StringField('SMTP Host', validators=[Optional(), Length(max=200)])
    smtp_port = IntegerField('SMTP Port', validators=[Optional()])
    smtp_user = StringField('SMTP User', validators=[Optional(), Length(max=100)])
    smtp_password = StringField('SMTP Password', validators=[Optional(), Length(max=100)])
    smtp_use_tls = BooleanField('Use TLS', default=True)
    admin_email = StringField('Admin Email', validators=[Optional(), Email()])
    session_lifetime = IntegerField('Session Lifetime (seconds)', default=86400)
    password_min_length = IntegerField('Minimum Password Length', default=8)
    backup_config = SubmitField('Backup Configuration')
    restore_config = FileField('Restore Configuration', validators=[
        Optional(),
        FileAllowed(['json'], 'JSON files only!')
    ])
    submit = SubmitField('Save Changes')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    theme = SelectField('Theme', choices=[('light', 'Light'), ('dark', 'Dark')])
    is_active = BooleanField('Active')
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Save Changes') 