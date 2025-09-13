import requests
import sys
import json
from datetime import datetime
import time

class AIWebAutomationTester:
    def __init__(self, base_url="https://auto-user-manager.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.access_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:200]}")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                try:
                    return False, response.json()
                except:
                    return False, response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_mock_saas_login(self):
        """Test Mock SaaS login"""
        success, response = self.run_test(
            "Mock SaaS Login",
            "POST",
            "mock-saas/login",
            200,
            data={"username": "admin", "password": "password"}
        )
        if success and isinstance(response, dict) and response.get('requires_mfa'):
            self.session_token = response.get('session_token')
            print(f"✅ MFA required, session token received")
            return True
        return success

    def test_mock_saas_mfa(self):
        """Test Mock SaaS MFA verification"""
        if not self.session_token:
            print("❌ No session token available for MFA test")
            self.failed_tests.append("MFA Test: No session token")
            return False
            
        success, response = self.run_test(
            "Mock SaaS MFA Verification",
            "POST",
            "mock-saas/verify-mfa",
            200,
            data={"otp_code": "123456", "session_token": self.session_token}
        )
        if success and isinstance(response, dict) and response.get('access_token'):
            self.access_token = response.get('access_token')
            print(f"✅ Access token received")
            return True
        return success

    def test_get_mock_users(self):
        """Test getting mock users"""
        if not self.access_token:
            print("❌ No access token available for users test")
            self.failed_tests.append("Get Users Test: No access token")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        success, response = self.run_test(
            "Get Mock Users",
            "GET",
            "mock-saas/users",
            200,
            headers=headers
        )
        
        if success and isinstance(response, dict):
            users = response.get('users', [])
            print(f"✅ Retrieved {len(users)} users")
            return True
        return success

    def test_create_mock_user(self):
        """Test creating a mock user"""
        if not self.access_token:
            print("❌ No access token available for create user test")
            self.failed_tests.append("Create User Test: No access token")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        test_user = {
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"test.user.{datetime.now().strftime('%H%M%S')}@example.com",
            "role": "user"
        }
        
        success, response = self.run_test(
            "Create Mock User",
            "POST",
            "mock-saas/users",
            200,
            data=test_user,
            headers=headers
        )
        
        if success and isinstance(response, dict):
            self.test_user_id = response.get('id')
            print(f"✅ User created with ID: {self.test_user_id}")
            return True
        return success

    def test_delete_mock_user(self):
        """Test deleting a mock user"""
        if not self.access_token or not hasattr(self, 'test_user_id'):
            print("❌ No access token or user ID available for delete test")
            self.failed_tests.append("Delete User Test: No access token or user ID")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        
        success, response = self.run_test(
            "Delete Mock User",
            "DELETE",
            f"mock-saas/users/{self.test_user_id}",
            200,
            headers=headers
        )
        return success

    def test_create_automation_job(self, job_type="scrape_users"):
        """Test creating automation job"""
        success, response = self.run_test(
            f"Create Automation Job ({job_type})",
            "POST",
            f"automation/jobs?job_type={job_type}",
            200
        )
        
        if success and isinstance(response, dict):
            job_id = response.get('id')
            print(f"✅ Job created with ID: {job_id}")
            return job_id
        return None

    def test_get_automation_jobs(self):
        """Test getting automation jobs"""
        success, response = self.run_test(
            "Get Automation Jobs",
            "GET",
            "automation/jobs",
            200
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} automation jobs")
            return True
        return success

    def test_automation_job_execution(self):
        """Test automation job execution by creating and monitoring a job"""
        print("\n🤖 Testing Automation Job Execution...")
        
        # Create a scrape_users job
        job_id = self.test_create_automation_job("scrape_users")
        if not job_id:
            return False
        
        # Monitor job status for up to 60 seconds
        max_wait = 60
        wait_time = 0
        
        while wait_time < max_wait:
            success, response = self.run_test(
                f"Check Job Status ({job_id})",
                "GET",
                f"automation/jobs/{job_id}",
                200
            )
            
            if success and isinstance(response, dict):
                status = response.get('status')
                print(f"Job status: {status}")
                
                if status in ['completed', 'failed']:
                    if status == 'completed':
                        results = response.get('results', {})
                        logs = response.get('logs', [])
                        print(f"✅ Job completed successfully")
                        print(f"Results: {json.dumps(results, indent=2)}")
                        print(f"Logs: {len(logs)} log entries")
                        return True
                    else:
                        print(f"❌ Job failed")
                        print(f"Results: {response.get('results', {})}")
                        self.failed_tests.append(f"Automation Job Execution: Job failed with status {status}")
                        return False
                        
            time.sleep(5)
            wait_time += 5
        
        print(f"❌ Job did not complete within {max_wait} seconds")
        self.failed_tests.append("Automation Job Execution: Timeout waiting for job completion")
        return False

def main():
    print("🚀 Starting AI Web Automation Backend Testing...")
    print("=" * 60)
    
    tester = AIWebAutomationTester()
    
    # Test sequence
    tests = [
        ("Root API", tester.test_root_endpoint),
        ("Mock SaaS Login", tester.test_mock_saas_login),
        ("Mock SaaS MFA", tester.test_mock_saas_mfa),
        ("Get Mock Users", tester.test_get_mock_users),
        ("Create Mock User", tester.test_create_mock_user),
        ("Delete Mock User", tester.test_delete_mock_user),
        ("Get Automation Jobs", tester.test_get_automation_jobs),
        ("Automation Job Execution", tester.test_automation_job_execution),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                print(f"⚠️  {test_name} failed, but continuing with other tests...")
        except Exception as e:
            print(f"❌ {test_name} threw exception: {str(e)}")
            tester.failed_tests.append(f"{test_name}: Exception - {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 BACKEND TEST RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(tester.failed_tests)}")
    
    if tester.failed_tests:
        print("\n❌ FAILED TESTS:")
        for i, failure in enumerate(tester.failed_tests, 1):
            print(f"{i}. {failure}")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Backend testing completed with good results!")
        return 0
    else:
        print("❌ Backend testing completed with issues that need attention!")
        return 1

if __name__ == "__main__":
    sys.exit(main())