#!/usr/bin/env python3
"""
Test video file upload rejection (should fail gracefully with helpful message)
"""
import requests
import json
import io

API_URL = "http://localhost:8000/api/generate-quiz"

def test_video_file_upload():
    """Test that video file uploads are rejected with helpful error"""
    print("=" * 60)
    print("Testing Video File Upload (should be rejected)")
    print("=" * 60)

    # Create a fake video file
    fake_video = io.BytesIO(b"fake video content")

    files = {
        'file': ('test_video.mp4', fake_video, 'video/mp4')
    }
    data = {
        'age_mode': '18+'
    }

    print("Attempting to upload MP4 file...")
    try:
        response = requests.post(API_URL, files=files, data=data, timeout=30)

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 400:
            print("✅ EXPECTED BEHAVIOR: Video upload rejected")
            result = response.json()
            print(f"\nError Message: {result.get('detail')}")

            # Check if error message is helpful
            error_msg = str(result.get('detail', '')).lower()
            if 'youtube' in error_msg and 'url' in error_msg:
                print("\n✅ Error message guides user to use YouTube URL instead")
                return True
            else:
                print("\n⚠️ Error message could be more helpful")
                return False
        else:
            print("❌ UNEXPECTED: Video upload was not rejected properly")
            print(json.dumps(response.json(), indent=2))
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_video_file_upload()
    if success:
        print("\n🎉 Video upload rejection working as expected!")
    else:
        print("\n❌ Video upload handling needs improvement")
