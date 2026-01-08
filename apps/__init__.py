# app/__init__.py
import os,logging
from logging.handlers import RotatingFileHandler   # logging 추가
from flask import Flask
from .config import Config
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # 로깅 설정
    if app.debug:  # 개발 환경에서는 콘솔에만 로깅 (디버그 모드에서만)
        app.logger.setLevel(logging.DEBUG)
    else: # 프로덕션 환경에서는 파일에 로깅
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter( '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]' )) 
        file_handler.setLevel(logging.INFO) 
        app.logger.addHandler(file_handler) 
        app.logger.setLevel(logging.INFO)
# main 블루프린트 등록
    from .main import main 
    app.register_blueprint(main)
    return app
