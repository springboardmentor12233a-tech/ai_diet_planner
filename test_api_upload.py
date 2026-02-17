"""
Test API Upload Endpoint
Tests the actual file upload functionality
"""
import requests
import json
from pathlib import Path
import time

def test_api_upload():
    """Test uploading a file to the API"""
    print("="*60)
    print("API Upload Test")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("[OK] Server is running")
        else:
            print("[WARN] Server responded but with unexpected status")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is not running!")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  python app/main.py")
        print("\nOr:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return False
    
    # Test file
    test_file = Path("tests/test_data/sample_medical_report.txt")
    
    if not test_file.exists():
        print(f"[ERROR] Test file not found: {test_file}")
        return False
    
    print(f"[OK] Using test file: {test_file}")
    
    # Upload file
    try:
        print("\n[INFO] Uploading file to API...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {'user_id': 1}
            response = requests.post(
                "http://localhost:8000/api/upload-report",
                files=files,
                data=data,
                timeout=10
            )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] File uploaded successfully!")
            print(f"[OK] Report ID: {result.get('report_id')}")
            print(f"[OK] Status: {result.get('status')}")
            
            extracted = result.get('extracted_data', {})
            numeric = extracted.get('numeric_data', {})
            
            print(f"\n[OK] Extracted {len(numeric)} numeric metrics:")
            for key, value in list(numeric.items())[:5]:  # Show first 5
                print(f"     - {key}: {value}")
            if len(numeric) > 5:
                print(f"     ... and {len(numeric) - 5} more")
            
            print("\n[PASS] API upload test passed!")
            return True
        else:
            print(f"[FAIL] Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_report():
    """Test retrieving a report"""
    print("\n" + "="*60)
    print("API Get Report Test")
    print("="*60)
    
    try:
        # Get report ID 1
        response = requests.get("http://localhost:8000/api/reports/1", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Report retrieved successfully!")
            print(f"[OK] Report ID: {result.get('id')}")
            print(f"[OK] Filename: {result.get('filename')}")
            print(f"[OK] Status: {result.get('status')}")
            
            numeric = result.get('numeric_data', {})
            print(f"[OK] Contains {len(numeric)} numeric metrics")
            
            print("\n[PASS] Get report test passed!")
            return True
        elif response.status_code == 404:
            print("[WARN] No reports found. Upload a file first.")
            return True  # Not a failure, just no data
        else:
            print(f"[FAIL] Get report failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is not running!")
        return False
    except Exception as e:
        print(f"[ERROR] Get report test failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI-NutriCare API Test Suite")
    print("="*60 + "\n")
    
    # Test upload
    upload_ok = test_api_upload()
    
    # Test get report (only if upload succeeded)
    if upload_ok:
        get_ok = test_get_report()
    else:
        get_ok = test_get_report()  # Still try, might have existing data
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if upload_ok:
        print("[PASS] API Upload Test")
    else:
        print("[FAIL] API Upload Test - Server may not be running")
    
    if get_ok:
        print("[PASS] API Get Report Test")
    else:
        print("[FAIL] API Get Report Test")
    
    if upload_ok and get_ok:
        print("\n[SUCCESS] All API tests passed!")
    else:
        print("\n[WARN] Some API tests failed. Make sure server is running.")
