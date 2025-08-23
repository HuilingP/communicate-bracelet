#!/usr/bin/env python3
"""
启动脚本 - 同时运行 Flask 后端和 Streamlit 前端
"""

import subprocess
import threading
import time
import os
import sys
from pathlib import Path

def start_flask_backend():
    """启动 Flask 后端服务"""
    print("🚀 启动 Flask 后端服务...")
    try:
        subprocess.run([sys.executable, "backend_api.py"], check=True)
    except KeyboardInterrupt:
        print("Flask 后端服务已停止")
    except Exception as e:
        print(f"Flask 后端启动失败: {e}")

def start_udp_server():
    """启动 UDP 服务器"""
    print("📡 启动 UDP 分析服务器...")
    try:
        subprocess.run([sys.executable, "backend_udp_server.py"], check=True)
    except KeyboardInterrupt:
        print("UDP 服务器已停止")
    except Exception as e:
        print(f"UDP 服务器启动失败: {e}")

def start_streamlit_frontend():
    """启动 Streamlit 前端"""
    print("🌐 启动 Streamlit 前端...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501"], check=True)
    except KeyboardInterrupt:
        print("Streamlit 前端已停止")
    except Exception as e:
        print(f"Streamlit 前端启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🎤 语音转文本 & LLM 分析系统")
    print("=" * 50)
    
    # 检查虚拟环境
    if not os.path.exists('.venv'):
        print("❌ 未找到虚拟环境 .venv")
        print("请先创建虚拟环境：")
        print("  python -m venv .venv")
        print("  source .venv/bin/activate  # Linux/Mac")
        print("  .venv\\Scripts\\activate     # Windows")
        print("  pip install -r requirements.txt")
        return
    
    # 检查环境变量
    if not os.path.exists('.env'):
        print("⚠️  未找到 .env 文件，请创建并配置 DASHSCOPE_API_KEY")
    
    print("📋 服务信息:")
    print("  - Flask 后端: http://localhost:5001")
    print("  - UDP 分析服务器: udp://localhost:5002")
    print("  - Streamlit 前端: http://localhost:8501")
    print("  - 按 Ctrl+C 停止所有服务")
    print()
    
    try:
        # 创建线程启动后端服务
        backend_thread = threading.Thread(target=start_flask_backend, daemon=True)
        backend_thread.start()
        
        # 创建线程启动UDP服务器
        udp_thread = threading.Thread(target=start_udp_server, daemon=True)
        udp_thread.start()
        
        # 等待后端启动
        time.sleep(3)
        
        # 启动前端（主线程）
        start_streamlit_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 正在停止所有服务...")
        print("✅ 所有服务已停止")

if __name__ == "__main__":
    main()