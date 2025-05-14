import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_full_workflow(client):
    create_resp = client.post('/api/users', json={
        'email': 'test@example.com',
        'password': 'test123'
    })
    assert create_resp.status_code == 201
    user_id = json.loads(create_resp.data)['user_id']
    
    login_resp = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'test123'
    })
    assert login_resp.status_code == 200
    
    save_resp = client.post(f'/api/users/{user_id}/messages', json={
        'message': 'Test phishing message',
        'probability': 12.5
    })
    assert save_resp.status_code == 201
    
    get_resp = client.get(f'/api/users/{user_id}/messages')
    assert get_resp.status_code == 200
    messages = json.loads(get_resp.data)['results']
    assert len(messages) > 0
    
    delete_resp = client.delete(f'/api/users/{user_id}')
    assert delete_resp.status_code == 200