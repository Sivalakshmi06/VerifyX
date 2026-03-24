"""
Simple test script to verify AI API is working correctly
Run this after starting the Flask server
"""

import requests
import json

API_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_text_analysis():
    """Test text analysis endpoint"""
    print("Testing text analysis...")
    data = {
        "text": "BREAKING: Shocking conspiracy exposed! You won't believe this!",
        "language": "en"
    }
    response = requests.post(f"{API_URL}/api/analyze/text", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_emotion_analysis():
    """Test emotion analysis endpoint"""
    print("Testing emotion analysis...")
    data = {
        "text": "This is a dangerous threat to our religious values! We must act now!"
    }
    response = requests.post(f"{API_URL}/api/analyze/emotion", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("AI API Test Suite")
    print("=" * 50 + "\n")
    
    try:
        test_health()
        test_text_analysis()
        test_emotion_analysis()
        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to AI API")
        print("Make sure the Flask server is running on port 5001")
        print("Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
