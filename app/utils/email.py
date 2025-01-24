from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from .. import mail

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            if app.config['VERBOSE']:
                app.logger.info(f'Email sent successfully to {msg.recipients}')
        except Exception as e:
            app.logger.error(f'Failed to send email to {msg.recipients}: {str(e)}')

def send_email(subject, recipients, text_body, html_body, attachments=None):
    """Send email with optional attachments"""
    msg = Message(
        subject=f"{current_app.config['APP_NAME']} - {subject}",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=recipients
    )
    msg.body = text_body
    msg.html = html_body

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)

    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def send_password_reset_email(user):
    """Send password reset email to user"""
    token = user.get_reset_password_token()
    send_email(
        'Password Reset',
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            user=user,
            token=token
        ),
        html_body=render_template(
            'email/reset_password.html',
            user=user,
            token=token
        )
    ) 