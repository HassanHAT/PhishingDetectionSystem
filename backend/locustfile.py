from locust import HttpUser, task, between, SequentialTaskSet
import random
import string

class PhishingDetectionBehavior(SequentialTaskSet):
    user_id = None
    message_ids = []
    
    def on_start(self):

        email = f"user_{random.randint(1000, 9999)}@example.com"
        password = "Password123!"
        response = self.client.post("/api/users", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 201:
            self.user_data = {"email": email, "password": password}
            self.user_id = response.json().get("user_id")
            print(f"Created user: {email} with ID: {self.user_id}")
        else:
            self.login_existing_user()

    def login_existing_user(self):
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
        if response.status_code == 200:
            self.user_id = 1  
            print("Logged in with existing user")
        else:
            print("Login failed")

    @task
    def login(self):
        if hasattr(self, 'user_data'):
            response = self.client.post("/api/auth/login", json=self.user_data)
            print(f"Login status: {response.status_code}")

    @task
    def check_phishing_messages(self):
        phishing_samples = [
            "URGENT: Your account has been compromised. Click here to reset your password immediately.",
            "مرحبًا، هناك مشكلة في حسابك المصرفي. يرجى النقر هنا للتحقق" 
        ]
        
        safe_samples = [
            "Hey, just wanted to confirm our meeting for tomorrow at 2pm.",
            "Thanks for sending those files over. I've reviewed them and everything looks good.",
            "Don't forget to bring your laptop to the workshop on Friday.",
            "The quarterly report is ready for your review when you have time."

        ]
        
        message_list = random.choices([phishing_samples, safe_samples], weights=[0.7, 0.3])[0]
        message = random.choice(message_list)
        
        response = self.client.post("/api/phishing/check", json={
            "messages": [message]
        })
        
        if response.status_code == 200:
            result = response.json()
            probability = result.get("probability", 0)
            print(f"Phishing check: {message[:30]}... - Probability: {probability}")
            
            if self.user_id:
                self.save_message(message, probability)

    def save_message(self, message, probability):
        if self.user_id:
            response = self.client.post(f"/api/users/{self.user_id}/messages", json={
                "message": message,
                "probability": probability
            })
            
            if response.status_code == 201:
                message_id = response.json().get("message_id")
                if message_id:
                    self.message_ids.append(message_id)
                    print(f"Saved message ID: {message_id}")

    @task
    def get_message_history(self):
        if self.user_id:
            response = self.client.get(f"/api/users/{self.user_id}/messages")
            if response.status_code == 200:
                messages = response.json().get("results", [])
                print(f"Retrieved {len(messages)} messages for user {self.user_id}")

    @task
    def delete_random_message(self):
        if self.user_id and self.message_ids:
            if random.random() < 0.3 and self.message_ids:
                message_id = random.choice(self.message_ids)
                response = self.client.delete(f"/api/users/{self.user_id}/messages/{message_id}")
                
                if response.status_code == 200:
                    self.message_ids.remove(message_id)
                    print(f"Deleted message ID: {message_id}")

class PhishingDetectionUser(HttpUser):
    tasks = [PhishingDetectionBehavior]
    wait_time = between(1, 5) 
    host = "http://localhost:5000"  
    
    def on_start(self):
        pass

class PhishingCheckOnlyUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:5000"  
    
    @task
    def check_phishing(self):
        phishing_messages = [
            "URGENT: Your account has been compromised. Click here to reset your password immediately.",
            "Congratulations! You've won a $1000 gift card. Claim your prize now!",
            "Your payment failed. Update your billing information within 24 hours.",
            "مرحبًا، هناك مشكلة في حسابك المصرفي. يرجى النقر هنا للتحقق"  # Arabic example
        ]
        
        message = random.choice(phishing_messages)
        self.client.post("/api/phishing/check", json={
            "messages": [message]
        })

class AuthenticationUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://localhost:5000"  
    @task(3)
    def login(self):
        self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
    
    @task(1)
    def register(self):
        random_email = f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}@example.com"
        self.client.post("/api/users", json={
            "email": random_email,
            "password": "Password123!"
        })