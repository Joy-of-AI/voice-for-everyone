#!/usr/bin/env python3
"""
Interactive test for WLASL and How2Sign - Type text and see outputs!
Run from backend directory: python interactive_test.py
"""
import requests
import json

BASE = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def test_wlasl(text):
    """Test WLASL text-to-animation"""
    print_section("WLASL TEST")
    print(f"Input text: '{text}'")
    
    try:
        # Get WLASL vocabulary first
        vocab_response = requests.get(f"{BASE}/asl/wlasl-vocabulary")
        if vocab_response.status_code == 200:
            vocab_data = vocab_response.json()
            print(f"✓ WLASL Vocabulary loaded: {len(vocab_data.get('vocabulary', []))} words")
        else:
            print(f"✗ WLASL Vocabulary failed: {vocab_response.status_code}")
        
        # Test text-to-WLASL animation
        print(f"\nTesting WLASL animation for: '{text}'")
        response = requests.post(f"{BASE}/asl/text-to-wlasl-animation", 
                               json={"text": text})
        
        if response.status_code == 200:
            data = response.json()
            print("✓ WLASL Animation Response:")
            print(f"  Success: {data.get('success', 'N/A')}")
            print(f"  Gloss: {data.get('gloss', 'N/A')}")
            print(f"  Has animation data: {bool(data.get('animation_data') or data.get('animation'))}")
            
            # Show some animation details if available
            if data.get('animation_data'):
                anim_data = data['animation_data']
                if isinstance(anim_data, list):
                    print(f"  Animation frames: {len(anim_data)}")
                elif isinstance(anim_data, dict):
                    print(f"  Animation keys: {list(anim_data.keys())}")
            
        else:
            print(f"✗ WLASL Animation failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"✗ WLASL test error: {str(e)}")

def test_how2sign(text):
    """Test How2Sign text-to-animation"""
    print_section("HOW2SIGN TEST")
    print(f"Input text: '{text}'")
    
    try:
        # Get How2Sign info first
        info_response = requests.get(f"{BASE}/how2sign/info")
        if info_response.status_code == 200:
            info_data = info_response.json()
            print(f"✓ How2Sign Info:")
            print(f"  Success: {info_data.get('success', 'N/A')}")
            if info_data.get('info'):
                info = info_data['info']
                print(f"  Dataset size: {info.get('dataset_size', 'N/A')}")
                print(f"  Classes: {info.get('classes', 'N/A')}")
        else:
            print(f"✗ How2Sign Info failed: {info_response.status_code}")
        
        # Test How2Sign animation
        print(f"\nTesting How2Sign animation for: '{text}'")
        response = requests.post(f"{BASE}/how2sign/animation", 
                               json={"sign_gloss": text.upper()})
        
        if response.status_code == 200:
            data = response.json()
            print("✓ How2Sign Animation Response:")
            print(f"  Success: {data.get('success', 'N/A')}")
            
            if data.get('animation'):
                anim = data['animation']
                if isinstance(anim, list):
                    print(f"  Animation frames: {len(anim)}")
                    if len(anim) > 0:
                        print(f"  First frame keys: {list(anim[0].keys()) if isinstance(anim[0], dict) else 'Not a dict'}")
                elif isinstance(anim, dict):
                    print(f"  Animation keys: {list(anim.keys())}")
            else:
                print("  No animation data found")
                
        else:
            print(f"✗ How2Sign Animation failed: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"✗ How2Sign test error: {str(e)}")

def main():
    print("🎯 Interactive WLASL & How2Sign Test")
    print("Type text and see both WLASL and How2Sign outputs!")
    print("Type 'quit' to exit")
    
    while True:
        try:
            # Get user input
            text = input("\n📝 Enter text to test (or 'quit'): ").strip()
            
            if text.lower() == 'quit':
                print("👋 Goodbye!")
                break
                
            if not text:
                print("❌ Please enter some text!")
                continue
            
            # Test both systems
            test_wlasl(text)
            test_how2sign(text)
            
            print(f"\n✅ Completed tests for: '{text}'")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
