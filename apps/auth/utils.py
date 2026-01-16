# apps/auth/utils.py
from flask import current_app, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from apps.extensions import mail
#from threading import Thread
#
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
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"비동기 메일 전송 실패: {e}")

def send_email(subject, to, template, **kwargs):
    app = current_app._get_current_object()
    
    # 발신자 정보 보강
    sender = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')
    msg = Message(subject, recipients=[to], sender=sender)
    
    msg.body = render_template(template + '.html', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    try:
        # [수정] Render에서 메일이 올 때까지 기다리도록 동기 방식으로 전송
        # 이렇게 하면 에러가 발생할 경우 로그에 즉시 찍힙니다.
        mail.send(msg)
        app.logger.info(f"이메일 발송 성공: {to}")
    except Exception as e:
        app.logger.error(f"이메일 발송 실패: {str(e)}")
        # 실패하더라도 회원가입 프로세스는 유지됨

"""
#def send_email(subject, to, template, **kwargs):
#    app = current_app._get_current_object()
    
    # 발신자 설정 확인
#    sender = app.config.get('MAIL_DEFAULT_SENDER')
#    msg = Message(subject, recipients=[to], sender=sender)
    
#    msg.body = render_template(template + '.html', **kwargs)
#    msg.html = render_template(template + '.html', **kwargs)

    # Render 배포 환경에서 Network Unreachable이 계속된다면 
    # 아래 Thread 부분을 주석처리하고 mail.send(msg)를 직접 호출해 보세요.
#    if app.config.get('TESTING'):
#        mail.send(msg)
#    else:
        # 비동기 전송 시도
#        Thread(target=send_async_email, args=[app, msg]).start()
"""