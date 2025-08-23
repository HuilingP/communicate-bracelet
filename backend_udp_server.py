import socket
import json
import threading
import logging
import os
from dotenv import load_dotenv
from dashscope import Generation
import dashscope
from http import HTTPStatus
from datetime import datetime

# 加载环境变量
load_dotenv()

# 设置 dashscope API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UDPAnalysisServer:
    def __init__(self, host='localhost', port=5002):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not self.api_key:
            logger.error("DashScope API Key not found in environment variables")
    
    def analyze_text(self, text):
        """使用网球场理论分析文本 - 与backend_api.py相同的逻辑"""
        if not self.api_key:
            return {
                "success": False,
                "error": "API Key not configured"
            }
        
        # 验证输入文本
        if text is None:
            return {
                "success": False,
                "error": "Text input cannot be None"
            }
        
        # 确保text是字符串
        text = str(text).strip()
        if not text:
            return {
                "success": False,
                "error": "Text input cannot be empty"
            }
        
        prompt = f"""你是一个专门基于人际关系网球场理论进行沟通分析的AI助手。你的核心任务是判断对话中最新一条消息的发送者是否"越网"。

核心理论框架：
**网球场理论**：在人际沟通中，每个人应该待在自己的"半场"，只谈论自己的感受和观察到的行为，不要跨过"网"去猜测对方的动机或内心想法。

判断标准：
✅ 未越网（合规表达）
* 使用"我"的表达：描述自己的感受、想法、观察
* 陈述可观察的事实行为
* 表达自己的需求和边界
* 分享自己的体验和感受
* 询问而非假设对方的想法

❌ 越网（违规表达）
* 使用"你"的判断：对他人动机进行推测
* 解释他人行为背后的原因
* 对他人内心状态做假设性判断
* 代替他人表达感受或想法
* 将自己的推测当作事实陈述

请分析以下文本："{text}"

请返回JSON格式结果：
{{
    "is_violation": true/false,
    "violation_type": "assumption/judgment/mind_reading/generalization/none",
    "explanation": "详细解释为什么越网或未越网",
    "suggestion": "如果越网，提供改进建议"
}}"""
        
        try:
            response = Generation.call(
                model='qwen-turbo',
                prompt=prompt
            )
            
            if response.status_code == HTTPStatus.OK:
                llm_response = response.output['text']
                
                try:
                    # 解析JSON响应
                    response_data = json.loads(llm_response)
                    is_violation = response_data.get("is_violation", False)
                    binary_signal = "1" if is_violation else "0"
                    
                    # 创建分析结果
                    analysis_result = {
                        "timestamp": datetime.now().isoformat(),
                        "question": text,
                        "is_violation": is_violation,
                        "violation_type": response_data.get("violation_type", "none"),
                        "explanation": response_data.get("explanation", ""),
                        "suggestion": response_data.get("suggestion", ""),
                        "binary_signal": binary_signal
                    }
                    
                    # 记录到文件
                    with open("output.log", "a", encoding='utf-8') as f:
                        f.write(f"UDP question: {text}\n")
                        f.write(f"UDP LLM Response: {llm_response}\n")
                        f.write(f"{binary_signal}======UDP RESPONSE DONE======\n")
                    
                    with open("binary_output.log", "a") as f:
                        f.write(binary_signal + "\n")
                    
                    return {
                        "success": True,
                        "is_violation": is_violation,
                        "violation_type": response_data.get("violation_type", "none"),
                        "explanation": response_data.get("explanation", ""),
                        "suggestion": response_data.get("suggestion", ""),
                        "binary_signal": binary_signal,
                        "llm_response": llm_response
                    }
                    
                except json.JSONDecodeError:
                    logger.error("Failed to parse LLM response as JSON")
                    return {
                        "success": False,
                        "error": "Failed to parse LLM response"
                    }
                    
            else:
                return {
                    "success": False,
                    "error": f"LLM API Error: {response.code} - {response.message}"
                }
        except Exception as e:
            logger.error(f"LLM request failed: {str(e)}")
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def start_server(self):
        """启动UDP服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.running = True
            
            logger.info(f"UDP Analysis Server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    # 接收数据
                    data, addr = self.socket.recvfrom(4096)
                    
                    # 在新线程中处理请求
                    thread = threading.Thread(
                        target=self.handle_request,
                        args=(data, addr),
                        daemon=True
                    )
                    thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logger.error(f"Socket error: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to start UDP server: {e}")
        finally:
            self.stop_server()
    
    def handle_request(self, data, addr):
        """处理UDP请求"""
        try:
            # 解码接收到的数据
            message = data.decode('utf-8')
            logger.info(f"Received from {addr}: {message}")
            
            # 解析JSON请求
            try:
                request_data = json.loads(message)
            except json.JSONDecodeError:
                # 如果不是JSON，直接当作文本处理
                request_data = {"text": message}
            
            # 获取要分析的文本
            text = request_data.get('text', '').strip()
            
            if not text:
                response = {
                    "success": False,
                    "error": "Text input is required"
                }
            else:
                # 调用分析函数
                response = self.analyze_text(text)
            
            # 发送响应
            response_json = json.dumps(response, ensure_ascii=False)
            self.socket.sendto(response_json.encode('utf-8'), addr)
            
            logger.info(f"Response sent to {addr}: {response.get('binary_signal', 'error')}")
            
        except Exception as e:
            logger.error(f"Error handling request from {addr}: {e}")
            error_response = {
                "success": False,
                "error": str(e)
            }
            try:
                error_json = json.dumps(error_response)
                self.socket.sendto(error_json.encode('utf-8'), addr)
            except:
                pass
    
    def stop_server(self):
        """停止UDP服务器"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        logger.info("UDP Analysis Server stopped")

def main():
    """主函数"""
    # 从环境变量获取配置
    host = os.getenv('UDP_HOST', 'localhost')
    port = int(os.getenv('UDP_PORT', 5002))
    
    server = UDPAnalysisServer(host, port)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        server.stop_server()

if __name__ == '__main__':
    main()