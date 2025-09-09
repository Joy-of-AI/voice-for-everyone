import asyncio
import numpy as np
from services.onnx_inference_server import onnx_inference_server

async def test_onnx():
    # Test single inference
    input_data = {'input_tensor': np.random.rand(3, 256, 256).astype(np.float32)}
    result = await onnx_inference_server.infer(input_data)
    print(f"Inference time: {result['inference_time_ms']:.2f}ms")
    print(f"Output shape: {result['outputs']['pose_keypoints']['shape']}")
    
    # Test batch inference
    batch_inputs = [
        {'input_tensor': np.random.rand(3, 256, 256).astype(np.float32)},
        {'input_tensor': np.random.rand(3, 256, 256).astype(np.float32)},
        {'input_tensor': np.random.rand(3, 256, 256).astype(np.float32)}
    ]
    batch_results = await onnx_inference_server.batch_infer(batch_inputs)
    print(f"Batch inference time: {batch_results[0]['batch_time_ms']:.2f}ms")
    print(f"Batch size: {batch_results[0]['batch_size']}")
    
    # Get performance stats
    stats = onnx_inference_server.get_performance_stats()
    print(f"Performance stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_onnx())
