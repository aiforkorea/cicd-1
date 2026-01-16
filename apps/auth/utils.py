from flask import current_app, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from apps.extensions import mail
from threading import Thread

def generate_token(email, salt):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=salt)

def confirm_token(token, salt, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(token, salt=salt, max_age=expiration)
    except:
        return False

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, to, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + '.html', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    Thread(target=send_async_email, args=[app, msg]).start()
