#!/usr/bin/env python3
"""
UDP客户端测试脚本
用于测试backend_udp_server.py的功能
支持文本和音频数据测试
"""

import socket
import json
import sys
import struct
import math
import time

def send_udp_request(text, host='localhost', port=5002):
    """发送UDP请求到分析服务器"""
    try:
        # 创建UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(10)  # 10秒超时
        
        # 准备请求数据
        request_data = {"text": text}
        message = json.dumps(request_data, ensure_ascii=False)
        
        print(f"发送到 {host}:{port}")
        print(f"请求: {text}")
        
        # 发送数据
        client_socket.sendto(message.encode('utf-8'), (host, port))
        
        # 接收响应
        response_data, server_addr = client_socket.recvfrom(4096)
        response = json.loads(response_data.decode('utf-8'))
        
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        
        return response
        
    except socket.timeout:
        print("请求超时")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None
    finally:
        client_socket.close()

def send_audio_data(host='localhost', port=5002, num_chunks=3):
    """发送测试音频数据"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(5)
        
        print(f"发送 {num_chunks} 个音频数据块到 {host}:{port}")
        
        for i in range(num_chunks):
            # 生成3200字节的测试音频数据 (440Hz正弦波)
            test_data = b''
            for j in range(1600):  # 1600个16-bit样本 = 3200字节
                sample = int(32767 * 0.1 * math.sin(2 * math.pi * 440 * j / 16000))
                test_data += struct.pack('<h', sample)
            
            # 发送音频数据
            client_socket.sendto(test_data, (host, port))
            print(f"发送音频块 {i+1}/{num_chunks} ({len(test_data)} 字节)")
            
            # 接收响应
            try:
                response_data, server_addr = client_socket.recvfrom(1024)
                response = json.loads(response_data.decode('utf-8'))
                print(f"服务器响应: {response.get('message', 'OK')}")
            except socket.timeout:
                print("服务器无响应")
            
            time.sleep(0.5)  # 500ms间隔
            
    except Exception as e:
        print(f"音频发送错误: {e}")
    finally:
        client_socket.close()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--audio':
            # 音频测试模式
            chunks = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 3
            send_audio_data(num_chunks=chunks)
            return
        else:
            # 从命令行参数获取文本
            text = " ".join(sys.argv[1:])
    else:
        # 交互式模式
        print("UDP客户端测试")
        print("1. 文本分析测试")
        print("2. 音频数据测试")
        choice = input("选择模式 (1/2): ").strip()
        
        if choice == '2':
            chunks = input("音频块数量 (默认3): ").strip()
            chunks = int(chunks) if chunks.isdigit() else 3
            send_audio_data(num_chunks=chunks)
            return
        else:
            text = input("请输入要分析的文本: ")
    
    if not text.strip():
        print("文本不能为空")
        return
    
    # 发送文本请求
    response = send_udp_request(text)
    
    if response and response.get('success'):
        print(f"\n分析结果:")
        print(f"是否越网: {'是' if response.get('is_violation') else '否'}")
        print(f"违规类型: {response.get('violation_type', 'none')}")
        print(f"二进制信号: {response.get('binary_signal')}")
        print(f"解释: {response.get('explanation')}")
        if response.get('suggestion'):
            print(f"建议: {response.get('suggestion')}")

if __name__ == '__main__':
    main()