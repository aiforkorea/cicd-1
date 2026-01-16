# apps/extensions.py      apps/__init__.py에서 일부 이동
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf=CSRFProtect()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message = '로그인이 필요합니다.'