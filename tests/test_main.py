# tests/test_main.py
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
