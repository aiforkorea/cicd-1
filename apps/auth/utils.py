# apps/auth/utils.py
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
    
    # [수정] sender를 설정에서 가져오거나 기본값을 명시하여 AssertionError 해결
    sender = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')
    
    msg = Message(subject, recipients=[to], sender=sender)
    msg.body = render_template(template + '.html', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    # 테스트 모드라면 동기 방식으로 전송 (가로채기용)
    if app.config.get('TESTING'):
        with app.app_context():
            mail.send(msg)
    else:
        Thread(target=send_async_email, args=[app, msg]).start()