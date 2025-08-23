#!/usr/bin/env python3
"""
UDP客户端测试脚本
用于测试backend_udp_server.py的功能
"""

import socket
import json
import sys

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

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 从命令行参数获取文本
        text = " ".join(sys.argv[1:])
    else:
        # 交互式输入
        text = input("请输入要分析的文本: ")
    
    if not text.strip():
        print("文本不能为空")
        return
    
    # 发送请求
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