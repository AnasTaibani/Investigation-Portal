#!/usr/bin/env python3
"""
Post-Deployment Verification Script
Tests all critical endpoints and workflows
"""
import requests
import sys
import os
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")


class DeploymentVerifier:
    def __init__(self, backend_url, frontend_url):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        print("\n" + "="*60)
        print("Testing Backend Health")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"Backend is healthy")
                print_info(f"   Database: {data.get('database', 'unknown')}")
                print_info(f"   Status: {data.get('status', 'unknown')}")
                self.test_results['passed'] += 1
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                self.test_results['failed'] += 1
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to connect to backend: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        print("\n" + "="*60)
        print("Testing Frontend Accessibility")
        print("="*60)
        
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                print_success("Frontend is accessible")
                if 'text/html' in response.headers.get('Content-Type', ''):
                    print_info("   Response type: HTML")
                    self.test_results['passed'] += 1
                    return True
                else:
                    print_warning("   Unexpected content type")
                    self.test_results['warnings'] += 1
                    return True
            else:
                print_error(f"Frontend returned status {response.status_code}")
                self.test_results['failed'] += 1
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to connect to frontend: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_login(self):
        """Test login functionality"""
        print("\n" + "="*60)
        print("Testing Login API")
        print("="*60)
        
        credentials = {
            "email": "investigator@test.com",
            "password": "Investigator@123"
        }
        
        try:
            response = self.session.post(
                f"{self.backend_url}/api/auth/login",
                json=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Login successful")
                print_info(f"   User: {data.get('email', 'unknown')}")
                print_info(f"   Role: {data.get('role', 'unknown')}")
                self.test_results['passed'] += 1
                return True
            elif response.status_code == 401:
                print_error("Login failed - Invalid credentials")
                print_warning("   Have you run seed_production_users.py?")
                self.test_results['failed'] += 1
                return False
            else:
                print_error(f"Login failed with status {response.status_code}")
                self.test_results['failed'] += 1
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Login request failed: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_categories_api(self):
        """Test if reference data is seeded"""
        print("\n" + "="*60)
        print("Testing Reference Data")
        print("="*60)
        
        try:
            response = self.session.get(
                f"{self.backend_url}/api/categories",
                timeout=10
            )
            
            if response.status_code == 200:
                categories = response.json()
                if len(categories) > 0:
                    print_success(f"Categories loaded: {len(categories)} found")
                    self.test_results['passed'] += 1
                    return True
                else:
                    print_warning("No categories found - run seed_reference_data.py")
                    self.test_results['warnings'] += 1
                    return False
            else:
                print_error(f"Categories API failed with status {response.status_code}")
                self.test_results['failed'] += 1
                return False
        except requests.exceptions.RequestException as e:
            print_error(f"Categories request failed: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_cors(self):
        """Test CORS configuration"""
        print("\n" + "="*60)
        print("Testing CORS Configuration")
        print("="*60)
        
        headers = {
            'Origin': self.frontend_url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        try:
            response = self.session.options(
                f"{self.backend_url}/api/auth/login",
                headers=headers,
                timeout=10
            )
            
            allow_origin = response.headers.get('Access-Control-Allow-Origin')
            allow_credentials = response.headers.get('Access-Control-Allow-Credentials')
            
            if allow_origin == self.frontend_url or allow_origin == '*':
                print_success("CORS configured correctly")
                print_info(f"   Allow-Origin: {allow_origin}")
                print_info(f"   Allow-Credentials: {allow_credentials}")
                self.test_results['passed'] += 1
                return True
            else:
                print_error("CORS configuration issue")
                print_warning(f"   Expected Origin: {self.frontend_url}")
                print_warning(f"   Got: {allow_origin}")
                self.test_results['failed'] += 1
                return False
        except requests.exceptions.RequestException as e:
            print_warning(f"CORS preflight check failed: {e}")
            self.test_results['warnings'] += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("DEPLOYMENT VERIFICATION SUMMARY")
        print("="*60)
        
        total = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        
        print(f"\nTotal Tests: {total}")
        print(f"{GREEN}Passed: {self.test_results['passed']}{RESET}")
        print(f"{RED}Failed: {self.test_results['failed']}{RESET}")
        print(f"{YELLOW}Warnings: {self.test_results['warnings']}{RESET}")
        
        print("\n" + "-"*60)
        
        if self.test_results['failed'] == 0:
            print(f"{GREEN}🎉 All critical tests passed!{RESET}")
            print("\n✅ Your deployment is ready for use!")
            print("\n📝 Next Steps:")
            print("   1. Change default passwords")
            print("   2. Test complete workflows in the UI")
            print("   3. Set up monitoring and alerts")
            return 0
        else:
            print(f"{RED}❌ Some tests failed{RESET}")
            print("\n🔍 Please review the errors above and:")
            print("   1. Check backend logs (Render Dashboard)")
            print("   2. Verify all environment variables")
            print("   3. Ensure database is initialized")
            print("   4. Review DEPLOYMENT_GUIDE.md for troubleshooting")
            return 1


def main():
    print("="*60)
    print("INVESTIGATION PORTAL - DEPLOYMENT VERIFICATION")
    print("="*60)
    
    # Get URLs from environment or arguments
    backend_url = os.environ.get('BACKEND_URL')
    frontend_url = os.environ.get('FRONTEND_URL')
    
    if len(sys.argv) >= 3:
        backend_url = sys.argv[1]
        frontend_url = sys.argv[2]
    
    if not backend_url or not frontend_url:
        print_error("Missing URLs!")
        print("\nUsage:")
        print("  python verify_deployment.py <backend_url> <frontend_url>")
        print("\nOr set environment variables:")
        print("  export BACKEND_URL=https://your-backend.onrender.com")
        print("  export FRONTEND_URL=https://your-app.vercel.app")
        print("  python verify_deployment.py")
        sys.exit(1)
    
    print(f"\nBackend URL: {backend_url}")
    print(f"Frontend URL: {frontend_url}")
    
    verifier = DeploymentVerifier(backend_url, frontend_url)
    
    # Run all tests
    verifier.test_backend_health()
    verifier.test_frontend_accessibility()
    verifier.test_login()
    verifier.test_categories_api()
    verifier.test_cors()
    
    # Print summary
    exit_code = verifier.print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
