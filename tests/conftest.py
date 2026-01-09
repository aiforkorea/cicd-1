#tests/conftest.py
import pytest, sys, os
# 현재 폴더의 한 단계 위(프로젝트 루트)를 파이썬 경로에 추가합니다.
# ModuleNotFoundError: No module named 'apps' 에러 예방
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps import create_app
from apps.extensions import db
from apps.dbmodels import User, UserType
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",  # 이 부분이 누락되어 세션 오류가 발생했습니다.
        "ADMIN_USERNAME": "admin",        # 환경 변수 대신 테스트용 값 직접 주입
        "ADMIN_PASSWORD": "1234",
        "ADMIN_EMAIL": "admin@example.com"
    })
    with app.app_context():
        # create_app 내부에 이미 db.create_all()과 관리자 생성이 있다면, 추가 작업 없이 yield만 입력
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """일반 사용자로 로그인된 클라이언트를 반환합니다."""
    with app.app_context():
        user = User(username='testuser', email='test@test.com', password='password123', user_type=UserType.USER)
        db.session.add(user)
        db.session.commit()
    client.post('/auth/login', data={'email': 'test@test.com', 'password': 'password123'}, follow_redirects=True)
    return client

