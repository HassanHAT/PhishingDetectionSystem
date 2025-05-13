# test_security.py
def test_sql_injection_protection(client):
    # Attempt SQL injection in login
    response = client.post('/api/auth/login', json={
        'email': "admin'--",
        'password': 'anything'
    })
    assert response.status_code != 500  
    assert b"SQL" not in response.data 