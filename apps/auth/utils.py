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
    # current_app 대신 실제 앱 객체 참조
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[to])
    # 템플릿 렌더링
    msg.body = render_template(template + '.html', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    # [수정] 테스트 모드라면 스레드를 생성하지 않고 즉시 전송 (가로채기 가능하도록)
    if app.config.get('TESTING'):
        with app.app_context():
            mail.send(msg)
    else:
        # 실제 운영/개발 환경에서는 비동기 전송
        Thread(target=send_async_email, args=[app, msg]).start()