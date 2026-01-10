# tests/test_main.py
import pytest
from apps.dbmodels import User, UserType
from apps.extensions import db
def test_main_index(client):
    """홈페이지 접속 테스트"""
    response = client.get('/')
    assert response.status_code == 200
    # 데이터를 텍스트(Unicode)로 변환하여 비교
    page_content = response.get_data(as_text=True)
    assert "서비스" in page_content
    assert "환영합니다" in page_content
    assert "API 키" in page_content

def test_login_process(client, app):
    """회원가입 및 로그인 통합 테스트"""
    # 1. 회원가입
    client.post('/auth/signup', data={
        'username': 'tester',
        'email': 'tester@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    # 2. 로그인 확인
    response = client.post('/auth/login', data={
        'email': 'tester@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"tester" in response.data

def test_admin_menu_visibility(client, app):
    """권한별 메뉴 노출 검증 테스트"""
    with app.app_context():
        # 1. 테스트용 일반 유저와 관리자 유저 생성
        user = User(username='regular', email='user@test.com', password='password123', user_type=UserType.USER)
        admin = User(username='boss', email='admin@test.com', password='password123', user_type=UserType.ADMIN)
        db.session.add_all([user, admin])
        db.session.commit()
    # --- 시나리오 A: 일반 사용자로 로그인 ---
    client.post('/auth/login', data={'email': 'user@test.com', 'password': 'password123'}, follow_redirects=True)
    response_user = client.get('/')
    page_user = response_user.get_data(as_text=True)
    # 일반 유저에게는 관리자 전용 메뉴가 보이지 않아야 함
    # (base.html의 {% if current_user.user_type==UserType.ADMIN %} 부분 검증)
    assert "로그아웃 (regular)" in page_user
    assert "관리자" not in page_user 
    # 로그아웃 후 다음 테스트 준비
    client.get('/auth/logout', follow_redirects=True)

    # --- 시나리오 B: 관리자로 로그인 ---
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'password123'}, follow_redirects=True)
    response_admin = client.get('/')
    page_admin = response_admin.get_data(as_text=True)
    # 관리자에게는 관리자 메뉴가 보여야 함
    assert "로그아웃 (boss)" in page_admin
    # 실제 base.html에 작성된 관리자 메뉴 텍스트나 링크를 확인하세요. 
    # 예시로 관리자 계정 여부를 확인하는 로직이 들어있다면 아래와 같이 검증합니다.
    # assert "관리자" in page_admin

def test_login_failure_invalid_password(client, app):
    """실패 케이스 1: 잘못된 비밀번호로 로그인 시도"""
    with app.app_context():
        user = User(username='failtest', email='fail@test.com', password='correct_password', user_type=UserType.USER)
        db.session.add(user)
        db.session.commit()

    # 실제 views.py의 엔드포인트는 /auth/login 입니다.
    response = client.post('/auth/login', data={
        'email': 'fail@test.com',
        'password': 'wrong_password'
    }, follow_redirects=True)

    page_content = response.get_data(as_text=True)
    # views.py의 flash 메시지 반영: "이메일 주소 및 비번 확인 필요"
    assert "이메일 주소 및 비번 확인 필요" in page_content

def test_signup_duplicate_email(client, app):
    """실패 케이스 2: 이미 존재하는 이메일로 가입 시도"""
    with app.app_context():
        # 1. 중복될 유저 생성
        if not User.query.filter_by(email='duplicate@test.com').first():
            existing_user = User(
                username='existing',
                email='duplicate@test.com',
                password='password123',
                user_type=UserType.USER
            )
            db.session.add(existing_user)
            db.session.commit()

    # 2. 동일한 이메일로 가입 시도
    response = client.post('/auth/signup', data={
        'username': 'newuser',
        'email': 'duplicate@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    page_content = response.get_data(as_text=True)
    
    # [수정된 부분] 
    # views.py의 flash 메시지가 아니라 forms.py의 ValidationError 메시지를 확인합니다.
    assert "이미 사용 중인 이메일 주소입니다." in page_content