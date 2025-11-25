#!/usr/bin/env python
"""
Improved test script for voice processing endpoint
Uses local test audio file instead of external URLs
"""
import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
VOICE_ENDPOINT = f"{BASE_URL}/api/voice/process"

def create_test_audio():
    """
    Create a simple test audio file using gTTS
    This ensures we have a local test file
    """
    try:
        from gtts import gTTS
        import tempfile
        
        # Create test audio
        text = "Check my balance"
        tts = gTTS(text=text, lang='en')
        
        # Save to temp file
        test_audio_path = os.path.join(os.path.dirname(__file__), "test_audio.mp3")
        tts.save(test_audio_path)
        
        print(f"[OK] Created test audio file: {test_audio_path}")
        return test_audio_path
    except Exception as e:
        print(f"[ERROR] Failed to create test audio: {e}")
        return None

def test_voice_endpoint_with_file_upload():
    """
    Test voice endpoint with direct file upload
    This is more reliable than URL-based testing
    """
    print("=" * 60)
    print("TEST: Voice Processing (File Upload)")
    print("=" * 60)
    
    # Create test audio
    test_audio_path = create_test_audio()
    if not test_audio_path:
        print("❌ Cannot proceed without test audio file")
        return
    
    try:
        # Test with file upload
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio': ('test_audio.mp3', audio_file, 'audio/mpeg')}
            data = {
                'phone': '+237600000001',
                'output_format': 'both'
            }
            
            print(f"\nUploading: {test_audio_path}")
            print(f"Phone: {data['phone']}")
            print(f"Output Format: {data['output_format']}")
            
            response = requests.post(VOICE_ENDPOINT, files=files, data=data, timeout=60)
            
            print(f"\nStatus Code: {response.status_code}")
            
            try:
                print(f"\nResponse:")
                print(json.dumps(response.json(), indent=2))
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"\n[OK] SUCCESS!")
                        print(f"   Transcription: {result.get('transcription')}")
                        print(f"   Response: {result.get('response_text')}")
                        if result.get('audio_url'):
                            print(f"   Audio URL: {result.get('audio_url')}")
                    else:
                        print(f"\n[FAIL] FAILED: {result.get('error')}")
                else:
                    print(f"\n[FAIL] HTTP Error: {response.status_code}")
            except json.JSONDecodeError:
                print(f"\n[ERROR] Failed to decode JSON response")
                print(f"Raw Response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out (>60s)")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
    finally:
        # Cleanup test file
        try:
            if test_audio_path and os.path.exists(test_audio_path):
                os.remove(test_audio_path)
                print(f"\n🧹 Cleaned up test file")
        except:
            pass

def test_voice_endpoint_text_only():
    """
    Test voice endpoint with text-only output (faster)
    """
    print("\n" + "=" * 60)
    print("TEST: Voice Processing (Text-Only, Faster)")
    print("=" * 60)
    
    # Create test audio
    test_audio_path = create_test_audio()
    if not test_audio_path:
        print("❌ Cannot proceed without test audio file")
        return
    
    try:
        # Test with file upload, text-only output
        with open(test_audio_path, 'rb') as audio_file:
            files = {'audio': ('test_audio.mp3', audio_file, 'audio/mpeg')}
            data = {
                'phone': '+237600000001',
                'output_format': 'text'  # Text only - faster
            }
            
            print(f"\nUploading: {test_audio_path}")
            print(f"Output Format: text (no TTS generation)")
            
            response = requests.post(VOICE_ENDPOINT, files=files, data=data, timeout=30)
            
            print(f"\nStatus Code: {response.status_code}")
            
            try:
                print(f"\nResponse:")
                print(json.dumps(response.json(), indent=2))
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"\n[OK] SUCCESS!")
                        print(f"   Transcription: {result.get('transcription')}")
                        print(f"   Response: {result.get('response_text')}")
                        print(f"   Audio URL: {result.get('audio_url', 'N/A (text-only mode)')}")
                    else:
                        print(f"\n[FAIL] FAILED: {result.get('error')}")
                else:
                    print(f"\n[FAIL] HTTP Error: {response.status_code}")
            except json.JSONDecodeError:
                print(f"\n[ERROR] Failed to decode JSON response")
                print(f"Raw Response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out (>30s)")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
    finally:
        # Cleanup test file
        try:
            if test_audio_path and os.path.exists(test_audio_path):
                os.remove(test_audio_path)
        except:
            pass

def test_endpoint_availability():
    """Check if Flask server is running"""
    print("=" * 60)
    print("PRE-TEST: Checking Flask Server")
    print("=" * 60)
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"[OK] Flask server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Flask server is NOT running at {BASE_URL}")
        print("   Please start the server with: python bot/app.py")
        return False
    except Exception as e:
        print(f"[ERROR] Error checking server: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("VOICE ENDPOINT TEST SUITE (Improved)")
    print("=" * 60)
    
    # Check server availability
    if not test_endpoint_availability():
        return
    
    print("\n[NOTE] These tests require:")
    print("   1. Flask server running (python bot/app.py)")
    print("   2. ffmpeg installed and in PATH")
    print("   3. Whisper model downloaded (auto-downloads on first use)")
    print("   4. gTTS installed (pip install gTTS)")
    
    input("\nPress Enter to continue with tests...")
    
    # Run tests
    test_voice_endpoint_with_file_upload()
    test_voice_endpoint_text_only()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\n[INFO] NOTES:")
    print("   - These tests use locally generated audio files")
    print("   - For production, Botpress will send real WhatsApp voice URLs")
    print("   - The endpoint supports both file upload and URL download")
    print("\n[INFO] See voice_endpoint_botpress_guide.md for Botpress integration\n")

if __name__ == "__main__":
    main()
