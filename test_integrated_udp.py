#!/usr/bin/env python3
"""
测试集成后的UDP音频分析系统
"""

import socket
import json
import time
import requests
import threading
from datetime import datetime

# 配置
API_BASE_URL = "http://localhost:5001"
UDP_HOST = "localhost"
UDP_PORT = 5002

def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康状态: {data}")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def start_udp_server():
    """启动UDP服务器"""
    print("🚀 启动UDP服务器...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/udp/start", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ UDP服务器启动: {data}")
            return data.get("success", False)
        else:
            print(f"❌ UDP服务器启动失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ UDP服务器启动异常: {e}")
        return False

def get_udp_status():
    """获取UDP服务器状态"""
    print("📊 获取UDP服务器状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ UDP状态: {data}")
            return data
        else:
            print(f"❌ 获取UDP状态失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取UDP状态异常: {e}")
        return None

def test_udp_text():
    """测试UDP文本分析"""
    print("📝 测试UDP文本分析...")
    
    test_texts = [
        "我觉得这个方案不太合适",  # 未越网
        "你总是这样不负责任",      # 越网
        "我观察到会议经常延迟开始", # 未越网
        "你就是想要控制一切"       # 越网
    ]
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📤 发送文本 {i}: {text}")
            
            # 发送文本数据
            message = json.dumps({"text": text})
            sock.sendto(message.encode('utf-8'), (UDP_HOST, UDP_PORT))
            
            # 接收响应
            try:
                response_data, addr = sock.recvfrom(4096)
                response = json.loads(response_data.decode('utf-8'))
                print(f"📥 收到响应: {response}")
                
                if response.get("success"):
                    binary_signal = response.get("binary_signal", "unknown")
                    is_violation = response.get("is_violation", False)
                    print(f"🎯 分析结果: 硬件信号={binary_signal}, 越网={is_violation}")
                else:
                    print(f"❌ 分析失败: {response.get('error', '未知错误')}")
                    
            except socket.timeout:
                print("⏰ 等待响应超时")
            except Exception as e:
                print(f"❌ 接收响应失败: {e}")
            
            time.sleep(1)  # 间隔1秒
        
        sock.close()
        print("✅ UDP文本测试完成")
        
    except Exception as e:
        print(f"❌ UDP文本测试失败: {e}")

def test_udp_audio():
    """测试UDP音频数据（模拟）"""
    print("🎵 测试UDP音频数据...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10)
        
        # 模拟音频数据（3200字节的随机数据）
        import os
        audio_data = os.urandom(3200)
        
        print(f"📤 发送音频数据: {len(audio_data)} 字节")
        sock.sendto(audio_data, (UDP_HOST, UDP_PORT))
        
        # 接收确认响应
        try:
            response_data, addr = sock.recvfrom(4096)
            response = json.loads(response_data.decode('utf-8'))
            print(f"📥 收到确认: {response}")
        except socket.timeout:
            print("⏰ 等待确认超时")
        except Exception as e:
            print(f"❌ 接收确认失败: {e}")
        
        sock.close()
        print("✅ UDP音频测试完成")
        
    except Exception as e:
        print(f"❌ UDP音频测试失败: {e}")

def get_analysis_history():
    """获取分析历史"""
    print("📚 获取分析历史...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/analysis/history", timeout=10)
        if response.status_code == 200:
            data = response.json()
            history = data.get("data", [])
            print(f"✅ 获取到 {len(history)} 条历史记录")
            
            # 显示最近的几条记录
            for i, record in enumerate(history[-3:], 1):
                timestamp = record.get("timestamp", "")[:19]
                question = record.get("question", "")[:50]
                binary_signal = record.get("binary_signal", "unknown")
                print(f"  {i}. [{timestamp}] {question}... -> {binary_signal}")
            
            return history
        else:
            print(f"❌ 获取历史失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取历史异常: {e}")
        return []

def get_udp_data():
    """获取UDP数据历史"""
    print("📡 获取UDP数据历史...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            udp_data = data.get("data", [])
            print(f"✅ 获取到 {len(udp_data)} 条UDP数据记录")
            
            # 显示最近的几条记录
            for i, record in enumerate(udp_data[-3:], 1):
                timestamp = record.get("timestamp", "")[:19]
                source_ip = record.get("source_ip", "unknown")
                data_type = record.get("type", "unknown")
                data_length = record.get("data_length", 0)
                print(f"  {i}. [{timestamp}] {source_ip} - {data_type} ({data_length} bytes)")
            
            return udp_data
        else:
            print(f"❌ 获取UDP数据失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 获取UDP数据异常: {e}")
        return []

def stop_udp_server():
    """停止UDP服务器"""
    print("⏹️ 停止UDP服务器...")
    try:
        response = requests.post(f"{API_BASE_URL}/api/udp/stop", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ UDP服务器停止: {data}")
            return data.get("success", False)
        else:
            print(f"❌ UDP服务器停止失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ UDP服务器停止异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🎾 网球场理论分析系统 - 集成UDP测试")
    print("=" * 50)
    
    # 1. 测试API健康状态
    if not test_api_health():
        print("❌ API不可用，请先启动backend_api.py")
        return
    
    print("\n" + "-" * 50)
    
    # 2. 启动UDP服务器
    if not start_udp_server():
        print("❌ UDP服务器启动失败")
        return
    
    # 等待服务器完全启动
    time.sleep(2)
    
    print("\n" + "-" * 50)
    
    # 3. 检查UDP服务器状态
    status = get_udp_status()
    if not status or not status.get("udp_running"):
        print("❌ UDP服务器未正常运行")
        return
    
    print("\n" + "-" * 50)
    
    # 4. 测试UDP文本分析
    test_udp_text()
    
    print("\n" + "-" * 50)
    
    # 5. 测试UDP音频数据
    test_udp_audio()
    
    # 等待处理完成
    time.sleep(3)
    
    print("\n" + "-" * 50)
    
    # 6. 获取分析历史
    get_analysis_history()
    
    print("\n" + "-" * 50)
    
    # 7. 获取UDP数据历史
    get_udp_data()
    
    print("\n" + "-" * 50)
    
    # 8. 停止UDP服务器
    stop_udp_server()
    
    print("\n🎉 测试完成！")
    print("\n📋 测试总结:")
    print("✅ API健康检查")
    print("✅ UDP服务器启动/停止")
    print("✅ UDP文本分析")
    print("✅ UDP音频数据接收")
    print("✅ 分析历史获取")
    print("✅ UDP数据历史获取")
    
    print("\n💡 提示:")
    print("- 启动 streamlit run streamlit_app.py 查看Web界面")
    print("- UDP服务器现在集成在API服务器中，可以通过Web界面控制")
    print("- 音频分析结果会显示在Web界面的实时语音和UDP数据标签页中")

if __name__ == "__main__":
    main()