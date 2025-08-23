#!/usr/bin/env python3
"""
系统测试脚本
"""

import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_backend_health():
    """测试后端健康状态"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端服务正常")
            print(f"   API Key 配置状态: {'✅' if data.get('api_key_configured') else '❌'}")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def test_llm_analysis():
    """测试 LLM 分析功能"""
    test_cases = [
        {
            "text": "请开启设备",
            "expected_command": "1",
            "description": "开启指令测试"
        },
        {
            "text": "关闭所有设备",
            "expected_command": "0", 
            "description": "关闭指令测试"
        },
        {
            "text": "今天天气很好",
            "expected_command": "0",
            "description": "无关内容测试"
        }
    ]
    
    print("\n🧪 测试 LLM 分析功能:")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"输入: {test_case['text']}")
        
        try:
            response = requests.post(
                "http://localhost:5000/api/analyze",
                json={
                    "text": test_case["text"],
                    "prompt": "请分析以下文本内容，如果内容表示需要开启设备，请回复'1'，否则回复'0'："
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    llm_response = data.get("llm_response", "")
                    hardware_command = data.get("hardware_command", "")
                    
                    print(f"LLM 响应: {llm_response}")
                    print(f"硬件指令: {hardware_command}")
                    
                    if hardware_command == test_case["expected_command"]:
                        print("✅ 测试通过")
                    else:
                        print(f"⚠️  指令不符合预期 (期望: {test_case['expected_command']}, 实际: {hardware_command})")
                else:
                    print(f"❌ 分析失败: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")

def test_hardware_command():
    """测试硬件控制指令"""
    print("\n⚡ 测试硬件控制指令:")
    
    for command in ["0", "1"]:
        try:
            response = requests.post(
                "http://localhost:5000/api/hardware/command",
                json={"command": command},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ 硬件指令 '{command}' 发送成功")
                else:
                    print(f"❌ 硬件指令发送失败: {data.get('error')}")
            else:
                print(f"❌ 硬件指令请求失败: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 硬件指令请求异常: {e}")

def main():
    """主测试函数"""
    print("🧪 系统功能测试")
    print("=" * 40)
    
    # 检查环境配置
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: DASHSCOPE_API_KEY 未配置")
    else:
        print("✅ DASHSCOPE_API_KEY 已配置")
    
    # 测试后端健康状态
    print("\n🏥 测试后端服务:")
    if not test_backend_health():
        print("❌ 后端服务未启动，请先运行: python backend_api.py")
        return
    
    # 测试 LLM 分析
    if api_key:
        test_llm_analysis()
    else:
        print("\n⚠️  跳过 LLM 测试 (API Key 未配置)")
    
    # 测试硬件控制
    test_hardware_command()
    
    print("\n✅ 测试完成!")
    print("\n📋 下一步:")
    print("1. 启动完整系统: python start_app.py")
    print("2. 访问前端界面: http://localhost:8501")

if __name__ == "__main__":
    main()