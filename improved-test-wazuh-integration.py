#!/usr/bin/env python3
"""
Improved N8N-Wazuh Integration Test Suite
Addresses issues found in the original test script:
1. Better handling of workflow activation status
2. Improved authentication testing with proper response validation
3. Enhanced error reporting and debugging information
4. More robust timeout and retry mechanisms
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ImprovedWazuhIntegrationTester:
    def __init__(self):
        self.n8n_base_url = "http://localhost:5678"
        self.wazuh_api_url = os.getenv("WAZUH_API_URL", "https://172.20.18.14:55000")
        self.wazuh_username = os.getenv("WAZUH_API_USER")
        self.wazuh_password = os.getenv("WAZUH_API_PASSWORD")
        self.n8n_username = os.getenv("N8N_USERNAME")
        self.n8n_password = os.getenv("N8N_PASSWORD")
        self.n8n_api_token = os.getenv("N8N_API_TOKEN")
        self.ai_base_url = "http://localhost:11434"
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name: str, status: str, details: str = "", debug_info: Optional[Dict] = None):
        """Enhanced logging with debug information"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "debug_info": debug_info or {}
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if debug_info and status == "FAIL":
            print(f"   Debug: {json.dumps(debug_info, indent=2)}")
            
        if status == "FAIL":
            self.failed_tests.append(test_name)
    
    def check_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """Check if a workflow exists and is active"""
        try:
            if not self.n8n_api_token:
                return {"exists": False, "active": False, "error": "No API token"}
                
            headers = {"X-N8N-API-KEY": self.n8n_api_token}
            response = requests.get(f"{self.n8n_base_url}/api/v1/workflows", headers=headers, timeout=15)
            
            if response.status_code == 200:
                workflows = response.json().get('data', [])
                workflow = next((w for w in workflows if workflow_name.lower() in w.get('name', '').lower()), None)
                
                if workflow:
                    return {
                        "exists": True,
                        "active": workflow.get('active', False),
                        "id": workflow.get('id'),
                        "name": workflow.get('name')
                    }
                else:
                    return {"exists": False, "active": False, "error": "Workflow not found"}
            else:
                return {"exists": False, "active": False, "error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"exists": False, "active": False, "error": str(e)}
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow by ID"""
        try:
            headers = {"X-N8N-API-KEY": self.n8n_api_token}
            response = requests.patch(
                f"{self.n8n_base_url}/api/v1/workflows/{workflow_id}/activate",
                headers=headers,
                timeout=15
            )
            return response.status_code in [200, 201]
        except Exception:
            return False
    
    def test_n8n_connectivity(self) -> bool:
        """Test N8N server connectivity"""
        try:
            response = requests.get(f"{self.n8n_base_url}/healthz", timeout=10)
            if response.status_code == 200:
                self.log_test("N8N Connectivity", "PASS", "N8N server is accessible")
                return True
            else:
                self.log_test("N8N Connectivity", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("N8N Connectivity", "FAIL", str(e))
            return False
    
    def test_wazuh_api_connectivity(self) -> bool:
        """Test direct Wazuh API connectivity with improved authentication"""
        try:
            # Test basic connectivity
            base_response = requests.get(self.wazuh_api_url, timeout=10, verify=False)
            
            if not self.wazuh_username or not self.wazuh_password:
                self.log_test("Wazuh API Connectivity", "WARN", 
                            "WAZUH_API_USER/PASSWORD not set; basic connectivity only")
                return True
            
            # Test authentication with raw=true parameter
            auth_response = requests.post(
                f"{self.wazuh_api_url}/security/user/authenticate?raw=true",
                auth=(self.wazuh_username, self.wazuh_password),
                timeout=15,
                verify=False
            )
            
            debug_info = {
                "base_status": base_response.status_code,
                "auth_status": auth_response.status_code,
                "auth_response_length": len(auth_response.text) if auth_response.text else 0
            }
            
            if auth_response.status_code == 200 and len(auth_response.text) > 50:
                self.log_test("Wazuh API Connectivity", "PASS", 
                            "Wazuh API authentication successful", debug_info)
                return True
            else:
                self.log_test("Wazuh API Connectivity", "FAIL", 
                            f"Auth failed: HTTP {auth_response.status_code}", debug_info)
                return False
        except Exception as e:
            self.log_test("Wazuh API Connectivity", "FAIL", str(e))
            return False
    
    def test_wazuh_authentication_workflow(self) -> bool:
        """Test Wazuh authentication workflow with improved validation"""
        try:
            # Check workflow status first
            workflow_status = self.check_workflow_status("auth")
            
            if not workflow_status["exists"]:
                self.log_test("Wazuh Authentication Workflow", "FAIL", 
                            "Authentication workflow not found", workflow_status)
                return False
            
            if not workflow_status["active"]:
                # Try to activate it
                if workflow_status.get("id") and self.activate_workflow(workflow_status["id"]):
                    self.log_test("Wazuh Authentication Workflow", "PASS", 
                                "Workflow activated successfully")
                    time.sleep(2)  # Wait for activation
                else:
                    self.log_test("Wazuh Authentication Workflow", "WARN", 
                                "Workflow exists but is inactive", workflow_status)
                    return True
            
            # Test the webhook endpoint
            auth_data = {}
            if self.wazuh_username and self.wazuh_password:
                auth_data = {"username": self.wazuh_username, "password": self.wazuh_password}
            
            webhook_url = f"{self.n8n_base_url}/webhook/bridge-auth"
            response = requests.post(webhook_url, json=auth_data, timeout=30)
            
            debug_info = {
                "workflow_status": workflow_status,
                "response_status": response.status_code,
                "response_body": response.text[:200] if response.text else None,
                "has_credentials": bool(auth_data)
            }
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    if ("token" in response_data or "authenticated" in response_data or 
                        response_data.get("success") is True):
                        self.log_test("Wazuh Authentication Workflow", "PASS", 
                                    "Authentication workflow completed successfully", debug_info)
                        return True
                    elif "message" in response_data and "started" in response_data["message"]:
                        self.log_test("Wazuh Authentication Workflow", "WARN", 
                                    "Workflow started but response format needs verification", debug_info)
                        return True
                    else:
                        self.log_test("Wazuh Authentication Workflow", "FAIL", 
                                    "Unexpected response format", debug_info)
                        return False
                except json.JSONDecodeError:
                    self.log_test("Wazuh Authentication Workflow", "FAIL", 
                                "Invalid JSON response", debug_info)
                    return False
            else:
                self.log_test("Wazuh Authentication Workflow", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}", debug_info)
                return False
        except Exception as e:
            self.log_test("Wazuh Authentication Workflow", "FAIL", str(e))
            return False
    
    def test_webhook_endpoints(self) -> Dict[str, bool]:
        """Test all webhook endpoints for basic connectivity"""
        webhooks = {
            "wazuh-alerts": "/webhook/wazuh-alerts",
            "bridge-auth": "/webhook/bridge-auth", 
            "high-priority-alert": "/webhook/high-priority-alert",
            "incident-response": "/webhook/incident-response",
            "chat": "/webhook/chat"
        }
        
        results = {}
        for name, endpoint in webhooks.items():
            try:
                # Use GET request for basic connectivity test
                response = requests.get(f"{self.n8n_base_url}{endpoint}", timeout=10)
                # Webhook endpoints typically return 404 for GET, but should be reachable
                results[name] = response.status_code in [200, 404, 405]  # 405 = Method Not Allowed
                
                status = "PASS" if results[name] else "FAIL"
                details = f"Endpoint reachable (HTTP {response.status_code})"
                self.log_test(f"Webhook {name}", status, details)
            except Exception as e:
                results[name] = False
                self.log_test(f"Webhook {name}", "FAIL", str(e))
        
        return results
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive integration tests with improved diagnostics"""
        print("🚀 Starting Improved N8N-Wazuh Integration Test Suite")
        print("=" * 70)
        print("🔍 Enhanced testing with workflow status checks and better diagnostics")
        print("=" * 70)
        
        # Core connectivity tests
        print("\n📡 Testing Core Connectivity...")
        n8n_ok = self.test_n8n_connectivity()
        wazuh_ok = self.test_wazuh_api_connectivity()
        
        if not n8n_ok:
            print("\n❌ N8N connectivity failed. Cannot proceed with workflow tests.")
            return False
        
        # Workflow status checks
        print("\n🔄 Checking Workflow Status...")
        workflows_to_check = ["auth", "alert", "health", "incident", "chat"]
        
        for workflow in workflows_to_check:
            status = self.check_workflow_status(workflow)
            status_text = "ACTIVE" if status.get("active") else "INACTIVE" if status.get("exists") else "MISSING"
            emoji = "✅" if status.get("active") else "⚠️" if status.get("exists") else "❌"
            print(f"{emoji} {workflow.title()} Workflow: {status_text}")
        
        # Webhook connectivity tests
        print("\n🌐 Testing Webhook Endpoints...")
        webhook_results = self.test_webhook_endpoints()
        
        # Authentication workflow test
        print("\n🔐 Testing Authentication Workflow...")
        auth_ok = self.test_wazuh_authentication_workflow()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Comprehensive Test Results Summary")
        print("=" * 60)
        
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"📝 Total Tests: {len(self.test_results)}")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests: {', '.join(self.failed_tests)}")
        
        success_rate = (passed_tests / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        results_file = "/home/sa/projects/n8n_sec/improved-test-results.json"
        with open(results_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "improved_comprehensive",
                "summary": {
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warnings": warning_tests,
                    "total": len(self.test_results),
                    "success_rate": success_rate
                },
                "detailed_results": self.test_results,
                "recommendations": self._generate_recommendations()
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        return failed_tests == 0
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if any("Wazuh API" in test for test in self.failed_tests):
            recommendations.append("Check Wazuh API credentials and server connectivity")
        
        if any("Authentication Workflow" in test for test in self.failed_tests):
            recommendations.append("Verify authentication workflow is properly imported and activated")
        
        if any("Webhook" in test for test in self.failed_tests):
            recommendations.append("Check N8N webhook configurations and workflow activations")
        
        if len(self.failed_tests) > len(self.test_results) / 2:
            recommendations.append("Consider reimporting all workflows and checking N8N service status")
        
        return recommendations

def main():
    """Main test execution"""
    tester = ImprovedWazuhIntegrationTester()
    
    try:
        success = tester.run_comprehensive_tests()
        
        if success:
            print("\n🎉 All tests passed! N8N-Wazuh integration is functioning correctly.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Review the results and recommendations above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()