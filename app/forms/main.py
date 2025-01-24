from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ProfileForm(FlaskForm):
    """User profile form"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    full_name = StringField('Full Name', validators=[
        Length(max=100)
    ])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    theme = SelectField('Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark')
    ])
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French')
    ])
    notifications_enabled = BooleanField('Enable Notifications')
    submit = SubmitField('Save Changes') 