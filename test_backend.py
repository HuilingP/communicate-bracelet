#!/usr/bin/env python3
"""
测试后端API是否正常工作
"""

import requests
import json

def test_backend():
    """测试后端API"""
    base_url = "http://localhost:5001"
    
    print("🔍 测试后端API...")
    
    # 1. 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查连接失败: {e}")
        return False
    
    # 2. 测试文本分析
    try:
        test_text = "你总是这样不负责任"
        payload = {"text": test_text}
        
        response = requests.post(
            f"{base_url}/api/analyze",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 文本分析测试通过")
            print(f"   输入: {test_text}")
            print(f"   是否违规: {result.get('is_violation')}")
            print(f"   违规类型: {result.get('violation_type')}")
            print(f"   硬件信号: {result.get('binary_signal')}")
            print(f"   解释: {result.get('explanation', '')[:100]}...")
        else:
            print(f"❌ 文本分析失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 文本分析连接失败: {e}")
        return False
    
    # 3. 测试VAD状态
    try:
        response = requests.get(f"{base_url}/api/vad/status", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ VAD状态检查通过")
            print(f"   VAD运行状态: {result.get('vad_running')}")
        else:
            print(f"❌ VAD状态检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ VAD状态检查连接失败: {e}")
    
    print("\n🎉 后端API测试完成！")
    return True

if __name__ == "__main__":
    test_backend()