import streamlit as st
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import time
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
from pydub import AudioSegment
import io
import threading
import queue

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="语音转文本 & LLM 分析系统",
    page_icon="🎤",
    layout="wide"
)

# Backend API 配置
BACKEND_URL = "http://localhost:5000"

# 初始化 session state
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'llm_response' not in st.session_state:
    st.session_state.llm_response = ""
if 'hardware_command' not in st.session_state:
    st.session_state.hardware_command = "0"
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = "请分析以下文本内容，如果内容表示需要开启设备，请回复'1'，否则回复'0'："
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = []
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'real_time_text' not in st.session_state:
    st.session_state.real_time_text = ""
if 'audio_frames_count' not in st.session_state:
    st.session_state.audio_frames_count = 0
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'latest_analysis' not in st.session_state:
    st.session_state.latest_analysis = None

def check_backend_health():
    """检查后端API健康状态"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_latest_analysis():
    """获取最新的分析结果"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/analysis/latest", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_explanation():
    """获取最新的解释"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/analysis/explanation", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_suggestion():
    """获取最新的建议"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/analysis/suggestion", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def start_monitoring():
    """启动后端监控"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/monitoring/start", timeout=5)
        return response.status_code == 200
    except:
        return False

def stop_monitoring():
    """停止后端监控"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/monitoring/stop", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_monitoring_status():
    """获取监控状态"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/monitoring/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def analyze_text_via_api(text, prompt):
    """通过后端API分析文本"""
    try:
        data = {
            "text": text,
            "prompt": prompt
        }
        response = requests.post(f"{BACKEND_URL}/api/analyze", json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def extract_hardware_command(llm_response):
    """从 LLM 响应中提取硬件控制指令"""
    response_lower = llm_response.lower()
    if '1' in response_lower and ('开启' in response_lower or 'on' in response_lower or '启动' in response_lower):
        return "1"
    elif '0' in response_lower and ('关闭' in response_lower or 'off' in response_lower or '停止' in response_lower):
        return "0"
    elif '1' in llm_response:
        return "1"
    else:
        return "0"

# 全局变量用于存储音频数据（避免session_state线程问题）
audio_buffer_global = []
is_recording_global = False

def audio_frame_callback(frame):
    """音频帧回调函数 - 使用全局变量存储音频数据"""
    global audio_buffer_global, is_recording_global
    try:
        if is_recording_global:
            # 将音频帧转换为numpy数组
            audio_array = frame.to_ndarray()
            # 添加到全局缓冲区
            audio_buffer_global.append(audio_array)
        return frame
    except Exception as e:
        print(f"音频帧处理错误: {e}")
        return frame

def process_audio_buffer():
    """处理完整音频缓冲区并转换为最终文本"""
    if not st.session_state.audio_buffer:
        return "没有录制到音频数据"
    
    try:
        # 合并所有音频帧
        audio_data = np.concatenate(st.session_state.audio_buffer, axis=0)
        
        # 计算录音时长
        duration = len(st.session_state.audio_buffer) * 0.02  # 假设每帧20ms
        
        # 使用LLM模拟语音识别
        llm_transcribed_text = simulate_llm_speech_recognition(duration)
        
        return f"{llm_transcribed_text} (录音时长: {duration:.1f}秒)"
        
    except Exception as e:
        return f"音频处理错误: {str(e)}"

def simulate_llm_speech_recognition(audio_duration):
    """使用LLM模拟语音识别结果"""
    try:
        # 根据录音时长生成不同的提示
        if audio_duration < 2:
            return "开启设备"
        elif audio_duration < 5:
            return "请启动系统"
        else:
            return "关闭所有设备并停止运行"
    except Exception as e:
        return f"语音识别模拟失败: {str(e)}"

# WebRTC配置
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# 主界面
st.title("🎤 语音转文本 & LLM 分析系统")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    # 后端API状态检查
    backend_healthy = check_backend_health()
    if backend_healthy:
        st.success("✅ 后端API连接正常")
    else:
        st.error("❌ 后端API连接失败")
        st.info("请确保后端服务运行在 http://localhost:5000")
    
    # 监控状态
    st.subheader("📊 VAD监控状态")
    monitoring_status = get_monitoring_status()
    
    if monitoring_status and monitoring_status.get("success"):
        is_monitoring = monitoring_status.get("monitoring", False)
        has_data = monitoring_status.get("has_data", False)
        
        if is_monitoring:
            st.success("🟢 VAD监控运行中")
            if st.button("⏹️ 停止监控"):
                if stop_monitoring():
                    st.session_state.monitoring_active = False
                    st.success("监控已停止")
                    st.rerun()
                else:
                    st.error("停止监控失败")
        else:
            st.info("⚪ VAD监控未运行")
            if st.button("▶️ 启动监控"):
                if start_monitoring():
                    st.session_state.monitoring_active = True
                    st.success("监控已启动")
                    st.rerun()
                else:
                    st.error("启动监控失败")
        
        if has_data:
            st.info("📊 有可用的分析数据")
        else:
            st.warning("📊 暂无分析数据")
    else:
        st.error("无法获取监控状态")
    
    st.divider()
    
    # API Key 状态
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if api_key:
        st.success("✅ DashScope API Key 已配置")
    else:
        st.error("❌ DashScope API Key 未配置")
        st.info("请在 .env 文件中设置 DASHSCOPE_API_KEY")
    
    st.divider()
    
    # 提示词配置
    st.subheader("📝 提示词设置")
    custom_prompt = st.text_area(
        "自定义提示词",
        value=st.session_state.custom_prompt,
        height=100,
        help="设置发送给 LLM 的提示词"
    )
    
    if st.button("更新提示词"):
        st.session_state.custom_prompt = custom_prompt
        st.success("提示词已更新！")

# 主要内容区域
col1, col2 = st.columns([1, 1])

with col1:
    st.header("🎙️ 语音输入")
    
    # 录音状态显示
    st.info("💡 现在支持真实录音！请允许浏览器访问麦克风权限。")
    
    # WebRTC录音组件
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": False, "audio": True},
        audio_frame_callback=audio_frame_callback,
    )
    
    # 录音控制按钮
    col1_1, col1_2 = st.columns([1, 1])
    
    with col1_1:
        if st.button("🎤 开始录音", type="primary"):
            # 清空缓冲区
            global audio_buffer_global, is_recording_global
            audio_buffer_global = []
            st.session_state.audio_buffer = []
            st.session_state.audio_frames_count = 0
            st.session_state.real_time_text = ""
            st.session_state.is_recording = True
            is_recording_global = True
            st.rerun()  # 刷新页面状态
    
    with col1_2:
        if st.button("⏹️ 停止录音", type="secondary"):
            global audio_buffer_global, is_recording_global
            st.session_state.is_recording = False
            is_recording_global = False
            
            # 将全局缓冲区数据复制到session_state
            if audio_buffer_global:
                st.session_state.audio_buffer = audio_buffer_global.copy()
                with st.spinner("正在处理录音..."):
                    transcribed_text = process_audio_buffer()
                    st.session_state.transcribed_text = transcribed_text
                    st.success("录音处理完成！")
                    st.rerun()  # 刷新页面显示最终结果
            else:
                st.warning("没有录制到音频数据，请检查麦克风权限")
    
    # 录音状态指示和实时转录
    if webrtc_ctx.state.playing and st.session_state.is_recording:
        st.success("🔴 正在录音...")
        
        # 实时显示录音状态和模拟转录
        global audio_buffer_global
        if audio_buffer_global:
            duration = len(audio_buffer_global) * 0.02  # 假设每帧20ms
            frame_count = len(audio_buffer_global)
            
            # 模拟实时转录文本
            sample_texts = [
                "正在录音中...",
                "请开启设备",
                "关闭设备", 
                "启动系统",
                "停止运行",
                "开始工作",
                "结束任务"
            ]
            
            # 根据录音时长选择不同的文本
            text_index = (frame_count // 25) % len(sample_texts)
            current_text = sample_texts[text_index]
            
            st.info(f"🎯 实时转录 [{duration:.1f}s]: {current_text}")
            st.caption(f"📊 已收集音频帧: {frame_count} 帧")
            
            # 自动刷新页面以更新实时转录
            time.sleep(0.1)
            st.rerun()
        else:
            st.info("🎯 等待音频数据...")
    else:
        st.info("⚪ 录音已停止")
    
    # 显示转录文本
    st.subheader("📄 转录文本")
    transcribed_display = st.text_area(
        "实时转录结果",
        value=st.session_state.transcribed_text,
        height=150,
        disabled=True
    )
    
    # 发送录音文本分析按钮
    if st.session_state.transcribed_text and st.button("🚀 分析录音文本", type="primary"):
        with st.spinner("正在分析录音文本..."):
            result = analyze_text_via_api(st.session_state.transcribed_text, st.session_state.custom_prompt)
            
            if result and result.get("success"):
                st.session_state.llm_response = result.get("llm_response", "")
                st.session_state.hardware_command = result.get("hardware_command", "0")
                
                # 添加到对话历史
                st.session_state.conversation_history.append({
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'input': st.session_state.transcribed_text,
                    'response': st.session_state.llm_response,
                    'command': st.session_state.hardware_command
                })
                
                st.success("录音文本分析完成！")
            else:
                st.error("分析失败，请检查后端API连接")
    
    # 手动文本输入
    st.subheader("✏️ 手动文本输入")
    manual_input = st.text_area(
        "输入文本进行 LLM 分析",
        height=100,
        placeholder="在这里输入文本..."
    )
    
    if st.button("📤 发送文本分析", type="secondary"):
        if manual_input.strip():
            with st.spinner("正在分析..."):
                result = analyze_text_via_api(manual_input, st.session_state.custom_prompt)
                
                if result and result.get("success"):
                    st.session_state.llm_response = result.get("llm_response", "")
                    st.session_state.hardware_command = result.get("hardware_command", "0")
                    
                    # 添加到对话历史
                    st.session_state.conversation_history.append({
                        'timestamp': datetime.now().strftime("%H:%M:%S"),
                        'input': manual_input,
                        'response': st.session_state.llm_response,
                        'command': st.session_state.hardware_command
                    })
                    
                    st.success("分析完成！")
                else:
                    st.error("分析失败，请检查后端API连接")
        else:
            st.warning("请输入文本内容")

with col2:
    st.header("🤖 分析结果")
    
    # VAD实时分析结果
    st.subheader("🎯 VAD实时分析")
    
    # 获取最新分析数据按钮
    if st.button("🔄 刷新VAD分析", type="primary"):
        latest_analysis = get_latest_analysis()
        if latest_analysis and latest_analysis.get("success"):
            st.session_state.latest_analysis = latest_analysis.get("data")
            st.success("VAD分析数据已更新！")
        else:
            st.warning("暂无VAD分析数据")
    
    # 显示VAD分析结果
    if st.session_state.latest_analysis:
        analysis_data = st.session_state.latest_analysis
        
        # 显示问题和时间戳
        st.info(f"**最新问题:** {analysis_data.get('question', 'N/A')}")
        st.caption(f"**时间:** {analysis_data.get('timestamp', 'N/A')}")
        
        # 违规状态
        is_violation = analysis_data.get('is_violation', False)
        violation_type = analysis_data.get('violation_type', 'none')
        binary_signal = analysis_data.get('binary_signal', '0')
        
        col2_vad1, col2_vad2 = st.columns([1, 1])
        
        with col2_vad1:
            if is_violation:
                st.error(f"❌ 越网行为: {violation_type}")
            else:
                st.success("✅ 未越网")
        
        with col2_vad2:
            st.metric(
                label="二进制信号",
                value=binary_signal,
                delta="违规" if binary_signal == "1" else "正常"
            )
        
        # 解释部分
        st.subheader("📝 详细解释")
        explanation = analysis_data.get('explanation', '暂无解释')
        st.text_area(
            "分析解释",
            value=explanation,
            height=120,
            disabled=True
        )
        
        # 建议部分
        st.subheader("💡 改进建议")
        suggestion = analysis_data.get('suggestion', '暂无建议')
        st.text_area(
            "改进建议",
            value=suggestion,
            height=100,
            disabled=True
        )
    else:
        st.info("暂无VAD分析数据，请启动监控并等待语音输入")
    
    st.divider()
    
    # 手动分析结果
    st.subheader("💬 手动分析响应")
    st.text_area(
        "LLM 分析结果",
        value=st.session_state.llm_response,
        height=150,
        disabled=True
    )
    
    # 硬件控制指令
    st.subheader("⚡ 硬件控制指令")
    
    col2_1, col2_2 = st.columns([1, 1])
    
    with col2_1:
        if st.session_state.hardware_command == "1":
            st.success("🟢 设备状态: 开启 (1)")
        else:
            st.info("🔴 设备状态: 关闭 (0)")
    
    with col2_2:
        st.metric(
            label="当前指令",
            value=st.session_state.hardware_command,
            delta="开启" if st.session_state.hardware_command == "1" else "关闭"
        )

# 对话历史
st.header("📚 对话历史")

if st.session_state.conversation_history:
    for i, conversation in enumerate(reversed(st.session_state.conversation_history[-10:])):  # 显示最近10条
        with st.expander(f"对话 {len(st.session_state.conversation_history)-i} - {conversation['timestamp']}"):
            st.write("**用户输入:**")
            st.write(conversation['input'])
            st.write("**LLM 响应:**")
            st.write(conversation['response'])
            st.write("**硬件指令:**", f"**{conversation['command']}**")
else:
    st.info("暂无对话历史")

# 清除历史按钮
if st.button("🗑️ 清除对话历史"):
    st.session_state.conversation_history = []
    st.success("对话历史已清除！")

# 底部信息
st.divider()
st.caption("💡 提示：这是一个演示版本。在生产环境中，语音识别功能需要配置适当的音频处理和 WebSocket 连接。")