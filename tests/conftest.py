# tests/conftest.py
import sys
import os

# 현재 폴더의 한 단계 위(프로젝트 루트)를 파이썬 경로에 추가합니다.
# ModuleNotFoundError: No module named 'apps' 에러 예방
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from apps import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,  # 테스트 모드 활성화
    })
    yield app

@pytest.fixture
def client(app):
    # 이 'client'가 웹 브라우저 대신 우리 사이트에 접속해줄 로봇입니다.
    return app.test_client()
