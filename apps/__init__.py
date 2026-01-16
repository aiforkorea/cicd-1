import os, logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from werkzeug.security import generate_password_hash
from .extensions import db, migrate, login_manager, csrf, mail
from .config import Config # 기본 설정

def create_app(config_class=Config): # 설정 클래스를 인자로 받음(테스트를 위해 추가 필요함)
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 로깅 설정
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    elif not app.testing: 
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # 확장 기능 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    from .dbmodels import User, UserType

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import flash, redirect, url_for, request
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('auth.login', next=request.path))

    @app.context_processor
    def inject_user_type():
        return {'UserType': UserType}

    from .main import main
    from .auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    with app.app_context():
        # 테스트 시에는 drop_all을 conftest에서 관리하므로 여기서는 create_all만 보장
        db.create_all()
        admin_username = app.config.get('ADMIN_USERNAME')
        admin_password = app.config.get('ADMIN_PASSWORD')
        if admin_username and admin_password:
            if not User.query.filter_by(username=admin_username).first():
                new_admin = User(
                    username=admin_username, 
                    email=app.config.get('ADMIN_EMAIL'), 
                    password=admin_password, # dbmodels의 password 세터 사용 가정
                    user_type=UserType.ADMIN,
                    confirmed=True # 관리자는 자동 인증
                )
                db.session.add(new_admin)
                db.session.commit()
    return app