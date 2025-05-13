import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_system_workflow():
    # Test user creation
    response = requests.post(f"{BASE_URL}/api/users", json={
        "email": f"test@example.com",
        "password": "test123"
    })
    print(f"User creation response: {response.status_code}")
    assert response.status_code == 201
    user_id = response.json()["user_id"]
    print(f"User created with user_id: {user_id}")
    
    # Test login
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": f"test@example.com",
        "password": "test123"
    })
    print(f"Login response: {login_resp.status_code}")
    assert login_resp.status_code == 200
    
    # Test phishing check
    check_resp = requests.post(f"{BASE_URL}/api/phishing/check", json={
        "messages": ["Your account has been compromised. Click here to secure it."]
    })
    print(f"Phishing check response: {check_resp.status_code}")
    assert check_resp.status_code == 200
    assert "results" in check_resp.json()
    
    # Clean up
    delete_resp = requests.delete(f"{BASE_URL}/api/users/{user_id}")
    print(f"Delete user response: {delete_resp.status_code}")
    assert delete_resp.status_code == 200

# Run the tests
if __name__ == "__main__":
    test_system_workflow()
