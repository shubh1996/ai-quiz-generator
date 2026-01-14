#!/usr/bin/env python3
"""
Quick test script to verify the API is working after OpenAI removal
"""
import requests
import json
import sys

API_URL = "http://localhost:8000/api/generate-quiz"

def test_youtube_video():
    """Test YouTube video processing"""
    print("=" * 60)
    print("Testing YouTube Video Processing")
    print("=" * 60)

    video_url = "https://www.youtube.com/watch?v=fNk_zzaMoSs"
    print(f"Video URL: {video_url}")
    print("Age Mode: 18+")
    print()

    data = {
        'video_url': video_url,
        'age_mode': '18+'
    }

    print("Sending request to API...")
    try:
        response = requests.post(API_URL, data=data, timeout=120)

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Quiz generated successfully")
            print()
            print(f"Job ID: {result.get('job_id')}")
            print(f"Number of Questions: {result.get('quiz', {}).get('num_quiz_questions')}")
            print(f"Points Awarded: {result.get('points_awarded')}")
            print()

            # Show content metadata
            content = result.get('content', {})
            print("Content Metadata:")
            print(f"  Title: {content.get('title')}")
            print(f"  Topics: {', '.join(content.get('topics', []))}")
            print(f"  Difficulty: {content.get('difficulty_level')}")
            print()

            # Show verification status
            verification = result.get('verification')
            if verification:
                print("Verification Status:")
                print(f"  Status: {verification.get('status')}")
                print(f"  Method: {verification.get('verification_method')}")
                if verification.get('confidence_score'):
                    print(f"  Confidence: {verification.get('confidence_score')}%")
            print()

            # Show first question as example
            questions = result.get('quiz', {}).get('questions', [])
            if questions:
                print("Sample Question:")
                q = questions[0]
                print(f"  Q: {q.get('question')}")
                print(f"  Difficulty: {q.get('difficulty')}")
                print(f"  Options:")
                for opt in q.get('options', []):
                    print(f"    - {opt}")
                print(f"  Correct Answer: {q.get('correct_answer')}")

            return True
        else:
            print("❌ FAILED!")
            print()
            print("Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out after 120 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🧪 Quiz Generator API Test Suite\n")

    # Test 1: Health check
    health_ok = test_health_endpoint()

    if not health_ok:
        print("⚠️ Health check failed. Stopping tests.")
        sys.exit(1)

    # Test 2: YouTube video processing
    youtube_ok = test_youtube_video()

    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"YouTube Processing: {'✅ PASS' if youtube_ok else '❌ FAIL'}")
    print()

    if health_ok and youtube_ok:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
