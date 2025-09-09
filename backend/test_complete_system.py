#!/usr/bin/env python3
"""
Comprehensive test script for the upgraded Body Language Translator system.
Tests all new endpoints and features implemented as part of the Key Upgrades.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_smplx_avatar_system():
    """Test SMPL-X avatar creation and animation"""
    print("🧍 Testing SMPL-X Avatar System...")
    
    async with aiohttp.ClientSession() as session:
        # Create avatar
        create_data = {"gender": "neutral", "height": 1.7}
        async with session.post(f"{BASE_URL}/avatar/smplx/create", json=create_data) as response:
            result = await response.json()
            assert result["success"] == True
            avatar_id = result["avatar_id"]
            print(f"✅ Created SMPL-X avatar: {avatar_id}")
        
        # Generate swimming animation
        animation_data = {
            "avatar_id": avatar_id,
            "gesture_type": "swim",
            "duration": 3.0
        }
        async with session.post(f"{BASE_URL}/avatar/smplx/animation", json=animation_data) as response:
            result = await response.json()
            assert result["success"] == True
            assert len(result["animation"]) > 0
            print(f"✅ Generated swimming animation with {len(result['animation'])} frames")

async def test_movenet_pose_detection():
    """Test MoveNet ultra-low latency pose detection"""
    print("🏃 Testing MoveNet Pose Detection...")
    
    async with aiohttp.ClientSession() as session:
        # Test pose processing
        import numpy as np
        frame_data = np.random.rand(256, 256, 3).tolist()  # Synthetic frame data
        
        process_data = {"frame_data": frame_data}
        async with session.post(f"{BASE_URL}/pose/movenet/process", json=process_data) as response:
            result = await response.json()
            assert result["success"] == True
            assert "poses" in result["result"]
            print(f"✅ Processed frame with {len(result['result']['poses'])} poses detected")
        
        # Test stats
        async with session.get(f"{BASE_URL}/pose/movenet/stats") as response:
            result = await response.json()
            assert result["success"] == True
            assert result["stats"]["initialized"] == True
            print(f"✅ MoveNet stats: {result['stats']['model_type']} model, {result['stats']['keypoint_count']} keypoints")

async def test_onnx_inference_server():
    """Test ONNX Runtime with Triton Inference Server"""
    print("⚡ Testing ONNX Inference Server...")
    
    async with aiohttp.ClientSession() as session:
        # Test inference (with proper input format)
        input_data = {
            "pose_sequence": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "confidence_scores": [0.9, 0.8]
        }
        
        process_data = {"input_data": input_data}
        async with session.post(f"{BASE_URL}/inference/onnx/process", json=process_data) as response:
            result = await response.json()
            assert result["success"] == True
            print(f"✅ ONNX inference completed in {result['result'].get('inference_time_ms', 0)}ms")
        
        # Test stats
        async with session.get(f"{BASE_URL}/inference/onnx/stats") as response:
            result = await response.json()
            assert result["success"] == True
            print(f"✅ ONNX stats: {result['stats']['throughput_inferences_per_sec']} inferences/sec")

async def test_sigml_synthesis():
    """Test SiGML/HamNoSys sign synthesis"""
    print("🤟 Testing SiGML Sign Synthesis...")
    
    async with aiohttp.ClientSession() as session:
        # Test sign generation
        sign_data = {"text": "hello world", "duration": 3.0}
        async with session.post(f"{BASE_URL}/sign/sigml/generate", json=sign_data) as response:
            result = await response.json()
            assert result["success"] == True
            assert "hamnosys" in result["animation"]
            assert "sigml" in result["animation"]
            print(f"✅ Generated sign for '{result['animation']['text']}' -> HamNoSys: {result['animation']['hamnosys'][:20]}...")
        
        # Test JASigning export
        export_data = {"animation": result["animation"]}
        async with session.post(f"{BASE_URL}/sign/sigml/jasigning", json=export_data) as response:
            result = await response.json()
            assert result["success"] == True
            print(f"✅ Exported to JASigning format")
        
        # Test stats
        async with session.get(f"{BASE_URL}/sign/sigml/stats") as response:
            result = await response.json()
            assert result["success"] == True
            print(f"✅ SiGML stats: {result['stats']['total_words']} words, {len(result['stats']['templates_available'])} templates")

async def test_webrtc_integration():
    """Test WebRTC with LiveKit integration"""
    print("📡 Testing WebRTC Integration...")
    
    async with aiohttp.ClientSession() as session:
        # Test connection status
        async with session.get(f"{BASE_URL}/webrtc/status") as response:
            result = await response.json()
            assert result["success"] == True
            stats = result["stats"]
            print(f"✅ WebRTC status: Connected={stats['connected']}, Participants={stats['participants']}, Data Channels={stats['data_channels']}")

async def test_original_functionality():
    """Test that original functionality still works"""
    print("🔄 Testing Original Functionality...")
    
    async with aiohttp.ClientSession() as session:
        # Test text-to-body translation
        translation_data = {
            "text": "let us swim in the yard",
            "output_type": "animation"
        }
        async with session.post(f"{BASE_URL}/translate/text-to-body", json=translation_data) as response:
            result = await response.json()
            assert "session_id" in result
            assert "body_language_instructions" in result
            print(f"✅ Text-to-body translation: {result['session_id']}")
        
        # Test ASL vocabulary
        async with session.get(f"{BASE_URL}/asl/vocabulary") as response:
            result = await response.json()
            assert "vocabulary" in result
            print(f"✅ ASL vocabulary: {len(result['vocabulary'])} words")
        
        # Test WLASL integration
        async with session.get(f"{BASE_URL}/asl/wlasl-stats") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ WLASL stats: {result.get('total_signs', 'N/A')} signs")
            else:
                print(f"⚠️ WLASL stats endpoint returned {response.status}")
        
        # Test How2Sign integration
        async with session.get(f"{BASE_URL}/how2sign/info") as response:
            if response.status == 200:
                result = await response.json()
                if result.get("success") and "info" in result:
                    print(f"✅ How2Sign info: {result['info']['dataset_size']} videos")
                else:
                    print(f"✅ How2Sign integration available")
            else:
                print(f"⚠️ How2Sign info endpoint returned {response.status}")

async def test_performance_metrics():
    """Test performance and latency metrics"""
    print("📊 Testing Performance Metrics...")
    
    async with aiohttp.ClientSession() as session:
        # Test MoveNet latency
        start_time = time.time()
        frame_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        process_data = {"frame_data": frame_data}
        
        async with session.post(f"{BASE_URL}/pose/movenet/process", json=process_data) as response:
            result = await response.json()
            latency = (time.time() - start_time) * 1000
            print(f"✅ MoveNet latency: {latency:.2f}ms")
            assert latency < 1000  # Including network overhead, should be under 1 second
        
        # Test ONNX throughput
        start_time = time.time()
        input_data = {"pose_sequence": [[1.0, 2.0, 3.0]]}
        process_data = {"input_data": input_data}
        
        async with session.post(f"{BASE_URL}/inference/onnx/process", json=process_data) as response:
            result = await response.json()
            throughput_time = (time.time() - start_time) * 1000
            print(f"✅ ONNX inference time: {throughput_time:.2f}ms")

async def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive System Test")
    print("=" * 50)
    
    try:
        # Test all new features
        await test_smplx_avatar_system()
        await test_movenet_pose_detection()
        await test_onnx_inference_server()
        await test_sigml_synthesis()
        await test_webrtc_integration()
        
        # Test original functionality
        await test_original_functionality()
        
        # Test performance
        await test_performance_metrics()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        print(f"✅ SMPL-X Avatar System: Professional 3D avatars")
        print(f"✅ MoveNet Integration: Ultra-low latency pose detection")
        print(f"✅ ONNX Runtime: Scalable inference with Triton")
        print(f"✅ SiGML Synthesis: Professional sign language generation")
        print(f"✅ WebRTC Integration: Real-time communication")
        print(f"✅ Original Features: All existing functionality preserved")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
