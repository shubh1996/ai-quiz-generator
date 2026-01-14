#!/usr/bin/env python3
"""
Test web URL processing
"""
import requests
import json

API_URL = "http://localhost:8000/api/generate-quiz"

def test_web_url():
    """Test web URL processing"""
    print("=" * 60)
    print("Testing Web URL Processing")
    print("=" * 60)

    url = "https://en.wikipedia.org/wiki/Machine_learning"
    print(f"URL: {url}")
    print()

    data = {
        'url': url,
        'age_mode': '18+'
    }

    print("Sending request to API...")
    try:
        response = requests.post(API_URL, data=data, timeout=120)

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Quiz generated from web URL")
            print()
            print(f"Number of Questions: {result.get('quiz', {}).get('num_quiz_questions')}")
            print(f"Points Awarded: {result.get('points_awarded')}")

            content = result.get('content', {})
            print(f"\nContent Title: {content.get('title')}")
            print(f"Topics: {', '.join(content.get('topics', []))}")

            verification = result.get('verification')
            if verification:
                print(f"\nVerification: {verification.get('status')}")

            return True
        else:
            print("❌ FAILED!")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_web_url()
