import pytest
from unittest.mock import MagicMock, patch
from app import app, hash_password

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hash_password():
    hashed = hash_password("test123")
    assert len(hashed) == 64
    assert hashed == "ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae"

def test_risk_level_calculation():
    from app import get_risk_level
    assert get_risk_level(20) == 'high'
    assert get_risk_level(12) == 'medium'
    assert get_risk_level(5) == 'low'

def test_risk_color_mapping():
    from app import get_risk_color
    assert get_risk_color('high') == 'red'
    assert get_risk_color('medium') == 'yellow'
    assert get_risk_color('low') == 'green'

def test_login_success(client):
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = MagicMock(password=hash_password("correct"))

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("pyodbc.connect", return_value=mock_conn):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "correct"
        })
        assert response.status_code == 200
        assert b"Login successful" in response.data

def test_login_failure(client):
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("pyodbc.connect", return_value=mock_conn):
        response = client.post("/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrong"
        })
        assert response.status_code == 401
        assert b"Invalid credentials" in response.data
