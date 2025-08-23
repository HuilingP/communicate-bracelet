from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
from dashscope import Generation
import dashscope
from http import HTTPStatus
import logging
import threading
import time
from datetime import datetime
import base64
import pyaudio
from dashscope.audio.qwen_omni import *

# 加载环境变量
load_dotenv()

# 设置 dashscope API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量存储最新的分析结果
latest_analysis = {
    "timestamp": None,
    "question": None,
    "is_violation": None,
    "violation_type": None,
    "explanation": None,
    "suggestion": None,
    "binary_signal": None
}

# 全局变量存储所有分析历史
analysis_history = []

# VAD 全局变量
vad_conversation = None
vad_running = False
pya = None
mic_stream = None

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            logger.error("DashScope API Key not found in environment variables")
    
    def analyze_text(self, text):
        """使用网球场理论分析文本"""
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
                    
                    # 更新全局分析结果
                    global latest_analysis, analysis_history
                    latest_analysis.update(analysis_result)
                    
                    # 添加到历史记录
                    analysis_history.append(analysis_result.copy())
                    
                    # 记录到文件
                    with open("output.log", "a", encoding='utf-8') as f:
                        f.write(f"question: {text}\n")
                        f.write(f"LLM Response: {llm_response}\n")
                        f.write(f"{binary_signal}======RESPONSE DONE======\n")
                    
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

class LogMonitorService:
    def __init__(self):
        self.log_file = "output.log"
        self.binary_log_file = "binary_output.log"
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """启动日志监控"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
            self.monitor_thread.start()
            logger.info("Log monitoring started")
    
    def stop_monitoring(self):
        """停止日志监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("Log monitoring stopped")
    
    def _monitor_logs(self):
        """监控日志文件变化"""
        last_position = 0
        
        while self.monitoring:
            try:
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        f.seek(last_position)
                        new_content = f.read()
                        if new_content:
                            self._parse_log_content(new_content)
                            last_position = f.tell()
                
                time.sleep(0.5)  # 检查间隔
            except Exception as e:
                logger.error(f"Log monitoring error: {e}")
                time.sleep(1)
    
    def _parse_log_content(self, content):
        """解析日志内容，提取问题和LLM响应"""
        global latest_analysis
        
        lines = content.strip().split('\n')
        current_question = None
        
        for line in lines:
            # 提取问题
            if 'question:' in line:
                current_question = line.split('question:', 1)[1].strip()
            
            # 提取LLM响应
            elif 'LLM Response:' in line:
                try:
                    llm_response_text = line.split('LLM Response:', 1)[1].strip()
                    llm_data = json.loads(llm_response_text)
                    
                    # 读取对应的二进制信号
                    binary_signal = self._get_latest_binary_signal()
                    
                    # 更新全局分析结果
                    latest_analysis.update({
                        "timestamp": datetime.now().isoformat(),
                        "question": current_question,
                        "explanation": llm_data.get("explanation"),
                        "suggestion": llm_data.get("suggestion"),
                        "is_violation": llm_data.get("is_violation"),
                        "violation_type": llm_data.get("violation_type"),
                        "binary_signal": binary_signal
                    })
                    
                    logger.info(f"Updated analysis: {current_question} -> {llm_data.get('is_violation')}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse LLM response JSON: {e}")
                except Exception as e:
                    logger.error(f"Error processing LLM response: {e}")
    
    def _get_latest_binary_signal(self):
        """获取最新的二进制信号"""
        try:
            if os.path.exists(self.binary_log_file):
                with open(self.binary_log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        return lines[-1].strip()
        except Exception as e:
            logger.error(f"Error reading binary log: {e}")
        return None

def vad_llm_request(text):
    """VAD专用的LLM请求 - 网球场理论分析"""
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

    if not dashscope.api_key:
        return "DashScope API Key not set. Please check your environment variables."

    try:
        response = Generation.call(
            model='qwen-turbo',
            prompt=prompt
        )

        if response.status_code == HTTPStatus.OK:
            return response.output['text']
        else:
            return f"Error: {response.code} - {response.message}"
    except Exception as e:
        return f"Request failed: {str(e)}"

class VADCallback(OmniRealtimeCallback):
    def on_open(self) -> None:
        global pya, mic_stream
        print('VAD connection opened, init microphone')
        try:
            pya = pyaudio.PyAudio()
            mic_stream = pya.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=16000,
                                input=True)
            logger.info("VAD microphone initialized")
        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")

    def on_close(self, close_status_code, close_msg) -> None:
        global pya, mic_stream
        print(f'VAD connection closed with code: {close_status_code}, msg: {close_msg}')
        if mic_stream:
            mic_stream.close()
        if pya:
            pya.terminate()
        logger.info("VAD microphone destroyed")

    def on_event(self, response: str) -> None:
        try:
            global latest_analysis, vad_conversation
            event_type = response['type']
            
            if 'session.created' == event_type:
                logger.info(f'VAD session started: {response["session"]["id"]}')
            
            if 'conversation.item.input_audio_transcription.completed' == event_type:
                transcript = response['transcript']
                logger.info(f'VAD question: {transcript}')

                # 发送到LLM进行网球场理论分析
                llm_response = vad_llm_request(transcript)
                logger.info(f"VAD LLM Response: {llm_response}")

                try:
                    # 解析LLM的JSON响应
                    response_data = json.loads(llm_response)
                    is_violation = response_data.get("is_violation", False)
                    
                    # 根据is_violation标志确定二进制信号
                    binary_signal = "1" if is_violation else "0"
                    logger.info(f"VAD Binary signal: {binary_signal}")
                    
                    # 创建分析结果
                    analysis_result = {
                        "timestamp": datetime.now().isoformat(),
                        "question": transcript,
                        "explanation": response_data.get("explanation"),
                        "suggestion": response_data.get("suggestion"),
                        "is_violation": is_violation,
                        "violation_type": response_data.get("violation_type"),
                        "binary_signal": binary_signal
                    }
                    
                    # 更新全局分析结果
                    global analysis_history
                    latest_analysis.update(analysis_result)
                    
                    # 添加到历史记录
                    analysis_history.append(analysis_result.copy())
                    
                    # 记录到文件（保持兼容性）
                    with open("binary_output.log", "a") as f:
                        f.write(binary_signal + "\n")
                        
                except json.JSONDecodeError:
                    logger.error("Error: Failed to decode VAD LLM response as JSON.")

            if 'response.done' == event_type:
                logger.info('VAD Response done')
                if vad_conversation:
                    logger.info(f'[VAD Metric] response: {vad_conversation.get_last_response_id()}, '
                              f'first text delay: {vad_conversation.get_last_first_text_delay()}, '
                              f'first audio delay: {vad_conversation.get_last_first_audio_delay()}')
                              
        except Exception as e:
            logger.error(f'[VAD Error] {e}')

class VADService:
    def __init__(self):
        self.callback = VADCallback()
        self.conversation = None
        self.running = False
        self.vad_thread = None
        
    def start_vad(self):
        """启动VAD服务"""
        if self.running:
            return {"success": False, "message": "VAD already running"}
            
        try:
            global vad_conversation, vad_running
            
            self.conversation = OmniRealtimeConversation(
                model='qwen-omni-turbo-realtime-latest',
                callback=self.callback,
            )
            
            vad_conversation = self.conversation
            self.conversation.connect()
            self.conversation.update_session(
                output_modalities=[MultiModality.TEXT],
                voice='Chelsie',
                input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
                output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                enable_input_audio_transcription=True,
                input_audio_transcription_model='gummy-realtime-v1',
                enable_turn_detection=True,
                turn_detection_type='server_vad',
            )
            
            self.running = True
            vad_running = True
            
            # 启动音频处理线程
            self.vad_thread = threading.Thread(target=self._audio_loop, daemon=True)
            self.vad_thread.start()
            
            logger.info("VAD service started successfully")
            return {"success": True, "message": "VAD service started"}
            
        except Exception as e:
            logger.error(f"Failed to start VAD service: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_vad(self):
        """停止VAD服务"""
        try:
            global vad_running
            self.running = False
            vad_running = False
            
            if self.conversation:
                self.conversation.close()
                self.conversation = None
                
            if self.vad_thread:
                self.vad_thread.join(timeout=2)
                
            logger.info("VAD service stopped")
            return {"success": True, "message": "VAD service stopped"}
            
        except Exception as e:
            logger.error(f"Failed to stop VAD service: {e}")
            return {"success": False, "error": str(e)}
    
    def _audio_loop(self):
        """音频处理循环"""
        global mic_stream
        
        while self.running:
            try:
                if mic_stream and self.conversation:
                    audio_data = mic_stream.read(3200, exception_on_overflow=False)
                    audio_b64 = base64.b64encode(audio_data).decode('ascii')
                    self.conversation.append_audio(audio_b64)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Audio loop error: {e}")
                break

# 初始化服务
llm_service = LLMService()
log_monitor = LogMonitorService()
vad_service = VADService()

@app.route('/', methods=['GET'])
def root():
    """根路由"""
    return jsonify({
        "message": "网球场理论分析系统 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/analyze",
            "latest_analysis": "/api/analysis/latest",
            "start_vad": "/api/vad/start",
            "stop_vad": "/api/vad/stop",
            "vad_status": "/api/vad/status"
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "api_key_configured": bool(llm_service.api_key)
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """文本分析接口 - 网球场理论分析"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        user_input = data.get('text', '').strip()
        
        if not user_input:
            return jsonify({"success": False, "error": "Text input is required"}), 400
        
        result = llm_service.analyze_text(user_input)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Analyze endpoint error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/api/analysis/latest', methods=['GET'])
def get_latest_analysis():
    """获取最新的分析结果"""
    global latest_analysis
    
    if latest_analysis["timestamp"] is None:
        return jsonify({
            "success": False,
            "message": "No analysis data available yet"
        }), 404
    
    return jsonify({
        "success": True,
        "data": latest_analysis
    })

@app.route('/api/analysis/history', methods=['GET'])
def get_analysis_history():
    """获取所有分析历史记录"""
    global analysis_history
    
    return jsonify({
        "success": True,
        "data": analysis_history,
        "count": len(analysis_history)
    })

@app.route('/api/analysis/history', methods=['DELETE'])
def clear_analysis_history():
    """清空分析历史记录"""
    global analysis_history
    analysis_history.clear()
    
    return jsonify({
        "success": True,
        "message": "Analysis history cleared"
    })



@app.route('/api/vad/start', methods=['POST'])
def start_vad():
    """启动VAD服务"""
    try:
        result = vad_service.start_vad()
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Failed to start VAD: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/vad/stop', methods=['POST'])
def stop_vad():
    """停止VAD服务"""
    try:
        result = vad_service.stop_vad()
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 500
    except Exception as e:
        logger.error(f"Failed to stop VAD: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/vad/status', methods=['GET'])
def vad_status():
    """获取VAD状态"""
    return jsonify({
        "success": True,
        "vad_running": vad_service.running,
        "has_data": latest_analysis["timestamp"] is not None,
        "latest_analysis": latest_analysis if latest_analysis["timestamp"] else None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)