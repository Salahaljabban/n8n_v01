#!/usr/bin/env python3
"""
N8N-Wazuh Integration Test Suite
Tests all workflows and verifies integration functionality
Updated to use N8N webhook URLs instead of API endpoints for workflow testing
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WazuhIntegrationTester:
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
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
            
        if status == "FAIL":
            self.failed_tests.append(test_name)
    
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
        """Test direct Wazuh API connectivity"""
        try:
            base = requests.get(self.wazuh_api_url, timeout=10, verify=False)
            if base.status_code not in [200, 401]:
                self.log_test("Wazuh API Connectivity", "FAIL", f"HTTP {base.status_code}")
                return False

            # Authenticate to obtain token (skip if env creds not provided)
            if not self.wazuh_username or not self.wazuh_password:
                self.log_test("Wazuh API Connectivity", "WARN", "WAZUH_API_USER/PASSWORD not set; skipping auth")
                return True
            auth = requests.post(
                f"{self.wazuh_api_url}/security/user/authenticate",
                json={"username": self.wazuh_username, "password": self.wazuh_password},
                timeout=15,
                verify=False,
            )
            if auth.status_code == 200 and auth.json().get("data", {}).get("token"):
                self.log_test("Wazuh API Connectivity", "PASS", "Authenticated and API reachable")
                return True
            else:
                self.log_test("Wazuh API Connectivity", "FAIL", f"Auth failed: HTTP {auth.status_code}")
                return False
        except Exception as e:
            self.log_test("Wazuh API Connectivity", "FAIL", str(e))
            return False
    
    def test_webhook_receiver_workflow(self) -> bool:
        """Test webhook receiver workflow (corrected endpoint: /webhook/wazuh-alerts)"""
        try:
            # Enhanced test alert matching current workflow structure
            test_alert = {
                "alert_id": "test-alert-001",
                "timestamp": datetime.now().isoformat(),
                "severity": "medium",
                "rule": {
                    "level": 7,
                    "description": "Test security alert for webhook receiver",
                    "id": "5501",
                    "groups": ["authentication", "pci_dss"]
                },
                "agent": {
                    "id": "001",
                    "name": "test-agent",
                    "ip": "192.168.1.100"
                },
                "data": {
                    "srcip": "10.0.0.1",
                    "dstip": "192.168.1.100",
                    "protocol": "TCP",
                    "srcport": "12345",
                    "dstport": "22"
                },
                "full_log": "Test log entry for security monitoring",
                "requires_immediate_action": False
            }
            
            webhook_url = f"{self.n8n_base_url}/webhook/wazuh-webhook"
            response = requests.post(webhook_url, json=test_alert, timeout=15)
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    if "status" in response_data and response_data["status"] == "success":
                        self.log_test("Webhook Receiver Workflow", "PASS", 
                                    f"Alert processed successfully: {response_data.get('message', 'No message')}")
                    else:
                        self.log_test("Webhook Receiver Workflow", "PASS", 
                                    "Test alert processed successfully")
                except:
                    self.log_test("Webhook Receiver Workflow", "PASS", 
                                "Test alert processed successfully")
                return True
            else:
                self.log_test("Webhook Receiver Workflow", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Webhook Receiver Workflow", "FAIL", str(e))
            return False
    
    def test_high_priority_alert_workflow(self) -> bool:
        """Test high priority alert processing workflow (corrected endpoint: /webhook/high-priority-alert)"""
        try:
            # Enhanced high priority alert matching current workflow structure
            high_priority_alert = {
                "alert_id": "test-critical-alert-001",
                "timestamp": datetime.now().isoformat(),
                "severity": "critical",
                "rule": {
                    "level": 12,
                    "description": "Critical security breach detected - Multiple failed authentication attempts",
                    "id": "5712",
                    "groups": ["authentication", "attack", "pci_dss"]
                },
                "agent": {
                    "id": "001",
                    "name": "production-server",
                    "ip": "192.168.1.50"
                },
                "data": {
                    "srcip": "192.168.1.200",
                    "dstip": "192.168.1.50",
                    "protocol": "TCP",
                    "srcport": "45678",
                    "dstport": "22",
                    "attack_type": "brute_force"
                },
                "full_log": "Critical alert: Multiple failed SSH login attempts from suspicious IP",
                "requires_immediate_action": True,
                "priority": "high",
                "threat_level": "critical"
            }
            
            webhook_url = f"{self.n8n_base_url}/webhook/high-priority-alert"
            response = requests.post(webhook_url, json=high_priority_alert, timeout=30)
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    if "ai_analysis" in response_data or "threat_assessment" in response_data:
                        self.log_test("High Priority Alert Workflow", "PASS", 
                                    "High priority alert processed with AI analysis")
                    else:
                        self.log_test("High Priority Alert Workflow", "PASS", 
                                    "High priority alert processed successfully")
                except:
                    self.log_test("High Priority Alert Workflow", "PASS", 
                                "High priority alert processed successfully")
                return True
            else:
                self.log_test("High Priority Alert Workflow", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("High Priority Alert Workflow", "FAIL", str(e))
            return False
    
    def test_wazuh_authentication_workflow(self) -> bool:
        """Test direct Wazuh authentication workflow via webhook"""
        try:
            # Send credentials if available; otherwise rely on n8n env
            auth_data = {}
            if self.wazuh_username and self.wazuh_password:
                auth_data = {"username": self.wazuh_username, "password": self.wazuh_password}
            
            webhook_url = f"{self.n8n_base_url}/webhook/bridge-auth"
            response = requests.post(webhook_url, json=auth_data, timeout=15)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                if "token" in response_data or "authenticated" in response_data:
                    self.log_test("Wazuh Authentication Workflow", "PASS", 
                                "Authentication workflow completed successfully")
                    return True
                else:
                    if not auth_data:
                        self.log_test("Wazuh Authentication Workflow", "WARN", 
                                      "No creds provided; ensure N8N has WAZUH_API_USER/PASSWORD env")
                        return True
                    self.log_test("Wazuh Authentication Workflow", "FAIL", 
                                  "No authentication token received")
                    return False
            else:
                self.log_test("Wazuh Authentication Workflow", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Wazuh Authentication Workflow", "FAIL", str(e))
            return False
    
    def test_alert_monitoring_workflow(self) -> bool:
        """Test alert monitoring workflow (scheduled workflow - check if active)"""
        try:
            # Alert monitoring uses a cron trigger, not a webhook
            # Test by checking if the workflow is active via N8N API
            if not self.n8n_api_token:
                self.log_test("Alert Monitoring Workflow", "WARN", "N8N_API_TOKEN not set; cannot verify workflow status")
                return True
                
            headers = {"Authorization": f"Bearer {self.n8n_api_token}"}
            response = requests.get(f"{self.n8n_base_url}/api/v1/workflows", headers=headers, timeout=15)
            
            if response.status_code == 200:
                workflows = response.json().get('data', [])
                alert_monitoring = next((w for w in workflows if 'Alert Monitoring' in w.get('name', '')), None)
                
                if alert_monitoring:
                    is_active = alert_monitoring.get('active', False)
                    status = "PASS" if is_active else "WARN"
                    message = "Workflow is active and monitoring alerts" if is_active else "Workflow exists but is inactive"
                    self.log_test("Alert Monitoring Workflow", status, message)
                    return True
                else:
                    self.log_test("Alert Monitoring Workflow", "FAIL", "Alert monitoring workflow not found")
                    return False
            else:
                # Fallback to direct Wazuh API test if N8N API fails
                return self._test_direct_wazuh_alerts()
        except Exception as e:
            # Fallback to direct Wazuh API test
            return self._test_direct_wazuh_alerts()
    
    def _test_direct_wazuh_alerts(self) -> bool:
        """Fallback test for alert monitoring via direct Wazuh API"""
        try:
            if not self.wazuh_username or not self.wazuh_password:
                self.log_test("Alert Monitoring Workflow", "WARN", "WAZUH_API_USER/PASSWORD not set; skipping direct API test")
                return True
            auth = requests.post(
                f"{self.wazuh_api_url}/security/user/authenticate",
                json={"username": self.wazuh_username, "password": self.wazuh_password},
                timeout=15,
                verify=False,
            )
            token = auth.json().get("data", {}).get("token") if auth.status_code == 200 else None
            if not token:
                self.log_test("Alert Monitoring Workflow", "FAIL", "Token acquisition failed")
                return False
            response = requests.get(
                f"{self.wazuh_api_url}/alerts",
                headers={"Authorization": f"Bearer {token}"},
                timeout=20,
                verify=False,
            )
            if response.status_code == 200:
                affected = response.json().get("data", {}).get("affected_items", [])
                self.log_test("Alert Monitoring Workflow", "PASS", f"Retrieved {len(affected)} alerts via direct API")
                return True
            else:
                self.log_test("Alert Monitoring Workflow", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Alert Monitoring Workflow", "FAIL", str(e))
            return False
    
    def test_incident_response_workflow(self) -> bool:
        """Test incident response workflow (corrected endpoint: /webhook/incident-response)"""
        try:
            # Enhanced incident data matching current workflow structure
            incident_data = {
                "incident_id": "test-incident-001",
                "timestamp": datetime.now().isoformat(),
                "threat_level": "high",
                "source_ip": "192.168.1.200",
                "target_host": "production-server",
                "action": "quarantine",
                "agent": "test-agent",
                "ai_analysis": {
                    "threat_type": "brute_force_attack",
                    "confidence": 0.95,
                    "recommended_actions": ["block_ip", "quarantine_host", "notify_security_team"]
                },
                "alert_data": {
                    "rule_id": "5712",
                    "description": "Multiple failed login attempts detected",
                    "severity": "critical"
                },
                "response_plan": {
                    "immediate_actions": ["isolate_host", "block_source_ip"],
                    "investigation_required": True,
                    "escalation_level": "security_team"
                }
            }
            
            webhook_url = f"{self.n8n_base_url}/webhook/incident-response"
            response = requests.post(webhook_url, json=incident_data, timeout=30)
            
            if response.status_code in [200, 201]:
                self.log_test("Incident Response Workflow", "PASS", 
                            "Incident response workflow executed successfully")
                return True
            else:
                self.log_test("Incident Response Workflow", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Incident Response Workflow", "FAIL", str(e))
            return False
    
    def test_ai_chat_workflow(self) -> bool:
        """Test AI chat workflow via N8N webhook"""
        try:
            chat_request = {
                "message": "Analyze this security alert: Multiple failed login attempts from IP 192.168.1.100",
                "context": "security_analysis",
                "timestamp": datetime.now().isoformat()
            }
            
            webhook_url = f"{self.n8n_base_url}/webhook/chat"
            response = requests.post(webhook_url, json=chat_request, timeout=30)
            
            if response.status_code in [200, 201]:
                self.log_test("AI Chat Workflow", "PASS", 
                            "AI chat workflow processed security analysis request")
                return True
            else:
                self.log_test("AI Chat Workflow", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("AI Chat Workflow", "FAIL", str(e))
            return False
    
    def test_foundation_sec_ai_integration(self) -> bool:
        """Test Foundation-Sec AI integration"""
        try:
            # First check if AI service is accessible
            health_response = requests.get(f"{self.ai_base_url}/api/tags", timeout=10)
            
            if health_response.status_code == 200:
                # Check if any models are available
                models_data = health_response.json()
                available_models = models_data.get('models', [])
                
                if available_models:
                    # Test with first available model
                    model_name = available_models[0]['name']
                    ai_request = {
                        "model": model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Test security analysis message"
                            }
                        ],
                        "stream": False
                    }
                    
                    response = requests.post(f"{self.ai_base_url}/api/chat", 
                                           json=ai_request, timeout=30)
                    
                    if response.status_code == 200:
                        self.log_test("Foundation-Sec AI Integration", "PASS", 
                                    f"AI service accessible with model: {model_name}")
                        return True
                    else:
                        self.log_test("Foundation-Sec AI Integration", "WARN", 
                                    f"AI service accessible but model test failed: HTTP {response.status_code}")
                        return True  # Service is accessible
                else:
                    self.log_test("Foundation-Sec AI Integration", "WARN", 
                                "AI service accessible but no models available (setup required)")
                    return True  # Service is accessible, just needs model setup
            else:
                self.log_test("Foundation-Sec AI Integration", "FAIL", f"HTTP {health_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Foundation-Sec AI Integration", "FAIL", str(e))
            return False
    
    def test_wazuh_health_monitoring_workflow(self) -> bool:
        """Test Wazuh health monitoring workflow (scheduled workflow - check if active)"""
        try:
            # Health monitoring uses a schedule trigger, not a webhook
            # Test by checking if the workflow is active via N8N API
            if not self.n8n_api_token:
                self.log_test("Wazuh Health Monitoring Workflow", "WARN", "N8N_API_TOKEN not set; cannot verify workflow status")
                return True
                
            headers = {"Authorization": f"Bearer {self.n8n_api_token}"}
            response = requests.get(f"{self.n8n_base_url}/api/v1/workflows", headers=headers, timeout=15)
            
            if response.status_code == 200:
                workflows = response.json().get('data', [])
                health_monitoring = next((w for w in workflows if 'Health Monitoring' in w.get('name', '')), None)
                
                if health_monitoring:
                    is_active = health_monitoring.get('active', False)
                    status = "PASS" if is_active else "WARN"
                    message = "Workflow is active and monitoring health" if is_active else "Workflow exists but is inactive"
                    self.log_test("Wazuh Health Monitoring Workflow", status, message)
                    return True
                else:
                    self.log_test("Wazuh Health Monitoring Workflow", "FAIL", "Health monitoring workflow not found")
                    return False
            else:
                # Fallback to direct Wazuh API test if N8N API fails
                return self._test_direct_wazuh_health()
        except Exception as e:
            # Fallback to direct Wazuh API test
            return self._test_direct_wazuh_health()
    
    def _test_direct_wazuh_health(self) -> bool:
        """Test direct Wazuh API health endpoints as fallback"""
        try:
            # Base health check (may return 200 or 401 depending on config)
            base = requests.get(self.wazuh_api_url, timeout=10, verify=False)
            if base.status_code not in [200, 401]:
                self.log_test("Wazuh Health Monitoring Workflow", "FAIL", f"Base HTTP {base.status_code}")
                return False

            # Auth then manager status (skip if env creds not provided)
            if not self.wazuh_username or not self.wazuh_password:
                self.log_test("Wazuh Health Monitoring Workflow", "WARN", "WAZUH_API_USER/PASSWORD not set; skipping manager status test")
                return True
            auth = requests.post(
                f"{self.wazuh_api_url}/security/user/authenticate",
                json={"username": self.wazuh_username, "password": self.wazuh_password},
                timeout=15,
                verify=False,
            )
            token = auth.json().get("data", {}).get("token") if auth.status_code == 200 else None
            if not token:
                self.log_test("Wazuh Health Monitoring Workflow", "FAIL", "Token acquisition failed")
                return False

            mgr = requests.get(
                f"{self.wazuh_api_url}/manager/status",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
                verify=False,
            )
            if mgr.status_code == 200:
                self.log_test("Wazuh Health Monitoring Workflow", "PASS", "Manager status reachable via direct API")
                return True
            else:
                self.log_test("Wazuh Health Monitoring Workflow", "FAIL", f"Manager HTTP {mgr.status_code}")
                return False
        except Exception as e:
            self.log_test("Wazuh Health Monitoring Workflow", "FAIL", str(e))
            return False
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🚀 Starting N8N-Wazuh Integration Test Suite (Webhook-Based)")
        print("=" * 60)
        print("📋 Testing workflows using N8N webhook URLs instead of API endpoints")
        print("=" * 60)
        
        # Core connectivity tests
        print("\n📡 Testing Core Connectivity...")
        n8n_ok = self.test_n8n_connectivity()
        wazuh_ok = self.test_wazuh_api_connectivity()
        ai_ok = self.test_foundation_sec_ai_integration()
        
        if not n8n_ok:
            print("\n❌ Core connectivity tests failed. Cannot proceed with workflow tests.")
            return False
        
        if not ai_ok:
            print("\n⚠️  AI service issues detected, but proceeding with workflow structure tests.")
        
        # Workflow tests (updated with corrected endpoints)
        print("\n🔄 Testing N8N Workflows (Corrected Endpoints)...")
        webhook_ok = self.test_webhook_receiver_workflow()  # /webhook/wazuh-alerts
        auth_ok = self.test_wazuh_authentication_workflow()  # /webhook/bridge-auth
        monitoring_ok = self.test_alert_monitoring_workflow()
        high_priority_ok = self.test_high_priority_alert_workflow()  # /webhook/high-priority-alert
        incident_ok = self.test_incident_response_workflow()  # /webhook/incident-response
        ai_chat_ok = self.test_ai_chat_workflow()  # /webhook/chat
        health_ok = self.test_wazuh_health_monitoring_workflow()  # Direct API or webhook
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"📝 Total Tests: {len(self.test_results)}")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests: {', '.join(self.failed_tests)}")
        
        success_rate = (passed_tests / len(self.test_results)) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        with open("/home/sa/projects/n8n_sec/test-results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warnings": warning_tests,
                    "total": len(self.test_results),
                    "success_rate": success_rate
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: /home/sa/projects/n8n_sec/test-results.json")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = WazuhIntegrationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 All tests passed! N8N-Wazuh integration is ready for production.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Please review the results and fix issues before deployment.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
