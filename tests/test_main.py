# tests/test_main.py
def test_index_page(client):
    """메인 페이지가 잘 나오는지 검사합니다."""
    response = client.get('/')  # 메인 주소('/')에 접속해봐!
    assert response.status_code == 200  # 응답 코드가 200(성공)이니?
    assert "환영합니다".encode('utf-8') in response.data # 화면에 '환영합니다'이라는 글자가 있니?

def test_services_page(client):
    """서비스 페이지 접속을 검사합니다."""
    response = client.get('/services')
    # 아직 view 함수에 내용이 없어도, 최소한 서버 에러(500)는 안 나야 해요.
    assert response.status_code != 500
    assert response.status_code == 200  # 응답 코드가 200(성공)이니?
    assert "서비스".encode('utf-8') in response.data # 화면에 '서비스'라는 글자가 있니?
