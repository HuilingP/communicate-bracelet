import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd

# 配置页面
st.set_page_config(
    page_title="网球场理论分析系统",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 后端API配置
API_BASE_URL = "http://localhost:5001"

# 初始化session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'vad_running' not in st.session_state:
    st.session_state.vad_running = False
if 'custom_prompt' not in st.session_state:
    st.session_state.custom_prompt = """你是一个专门基于人际关系网球场理论进行沟通分析的AI助手。你的核心任务是判断对话中最新一条消息的发送者是否"越网"。

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
{
    "is_violation": true/false,
    "violation_type": "assumption/judgment/mind_reading/generalization/none",
    "explanation": "详细解释为什么越网或未越网",
    "suggestion": "如果越网，提供改进建议"
}"""

def check_api_health():
    """检查后端API健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def analyze_text(text, custom_prompt=None):
    """调用后端API分析文本"""
    try:
        payload = {"text": text}
        if custom_prompt:
            payload["prompt"] = custom_prompt
            
        response = requests.post(
            f"{API_BASE_URL}/api/analyze",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_latest_analysis():
    """获取最新的分析结果"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/analysis/latest", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_analysis_history():
    """获取所有分析历史记录"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/analysis/history", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": "No data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def clear_analysis_history():
    """清空分析历史记录"""
    try:
        response = requests.delete(f"{API_BASE_URL}/api/analysis/history", timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def start_vad():
    """启动VAD服务"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/vad/start", timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def stop_vad():
    """停止VAD服务"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/vad/stop", timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_vad_status():
    """获取VAD状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/vad/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "vad_running": False}
    except Exception as e:
        return {"success": False, "vad_running": False}

def get_udp_data():
    """获取UDP数据"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/data", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": "No UDP data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_udp_status():
    """获取UDP服务器状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "udp_running": False}
    except Exception as e:
        return {"success": False, "udp_running": False}

def start_udp_server():
    """启动UDP服务器"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/udp/start", timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def stop_udp_server():
    """停止UDP服务器"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/udp/stop", timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_udp_notification_config():
    """获取UDP通知配置"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/notification/config", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": "Failed to get config"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_udp_notification_config(host, port):
    """设置UDP通知配置"""
    try:
        payload = {"host": host, "port": port}
        response = requests.post(f"{API_BASE_URL}/api/udp/notification/config", json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_udp_notification(message="-blue"):
    """测试UDP通知发送"""
    try:
        payload = {"message": message}
        response = requests.post(f"{API_BASE_URL}/api/udp/notification/test", json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def display_analysis_result(result):
    """显示分析结果"""
    if not result or not result.get("success"):
        st.error("分析失败或无数据")
        return
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # 硬件控制指令
        binary_signal = result.get("binary_signal", "0")
        is_violation = result.get("is_violation", False)
        
        if is_violation:
            st.error(f"🚨 硬件控制指令: {binary_signal}")
            st.error("⚠️ 检测到越网行为")
        else:
            st.success(f"✅ 硬件控制指令: {binary_signal}")
            st.success("✅ 未检测到越网行为")
    
    with col2:
        # LLM完整输出
        st.subheader("📋 LLM 完整分析结果")
        
        if "llm_response" in result:
            try:
                llm_data = json.loads(result["llm_response"])
                st.json(llm_data)
            except:
                st.text(result["llm_response"])
        
        # 详细信息
        st.subheader("📝 详细分析")
        
        violation_type = result.get("violation_type", "none")
        explanation = result.get("explanation", "")
        suggestion = result.get("suggestion", "")
        
        st.write(f"**违规类型:** {violation_type}")
        st.write(f"**解释:** {explanation}")
        if suggestion:
            st.write(f"**建议:** {suggestion}")
    
    with col3:
        # 时间戳和其他信息
        st.subheader("ℹ️ 分析信息")
        timestamp = result.get("timestamp", datetime.now().isoformat())
        st.write(f"**分析时间:** {timestamp}")
        st.write(f"**是否违规:** {'是' if is_violation else '否'}")

# 主界面
st.title("🎾 网球场理论分析系统")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统控制")
    
    # API健康检查
    if st.button("🔍 检查API状态"):
        if check_api_health():
            st.success("✅ 后端API正常")
        else:
            st.error("❌ 后端API连接失败")
    
    st.markdown("---")
    
    # VAD控制
    st.subheader("🎤 语音识别控制")
    
    # 获取VAD状态
    vad_status_data = get_vad_status()
    current_vad_running = vad_status_data.get("vad_running", False)
    st.session_state.vad_running = current_vad_running
    
    if st.session_state.vad_running:
        st.success("🟢 VAD服务运行中")
        if st.button("⏹️ 停止语音识别"):
            result = stop_vad()
            if result.get("success"):
                st.success("VAD服务已停止")
                st.session_state.vad_running = False
                st.rerun()
            else:
                st.error(f"停止失败: {result.get('error', '未知错误')}")
    else:
        st.info("🔴 VAD服务未运行")
        if st.button("▶️ 启动语音识别"):
            with st.spinner("正在启动VAD服务..."):
                result = start_vad()
                if result.get("success"):
                    st.success("VAD服务已启动")
                    st.session_state.vad_running = True
                    st.rerun()
                else:
                    st.error(f"启动失败: {result.get('error', '未知错误')}")
    
    st.markdown("---")
    
    # UDP服务器控制
    st.subheader("📡 UDP服务器控制")
    
    # 获取UDP状态
    udp_status_data = get_udp_status()
    current_udp_running = udp_status_data.get("udp_running", False)
    
    if current_udp_running:
        st.success("🟢 UDP服务器运行中")
        if st.button("⏹️ 停止UDP服务器"):
            result = stop_udp_server()
            if result.get("success"):
                st.success("UDP服务器已停止")
                st.rerun()
            else:
                st.error(f"停止失败: {result.get('error', '未知错误')}")
    else:
        st.info("🔴 UDP服务器未运行")
        if st.button("▶️ 启动UDP服务器"):
            with st.spinner("正在启动UDP服务器..."):
                result = start_udp_server()
                if result.get("success"):
                    st.success("UDP服务器已启动")
                    st.rerun()
                else:
                    st.error(f"启动失败: {result.get('error', '未知错误')}")
    
    st.markdown("---")
    
    # 自动刷新控制
    st.subheader("🔄 自动刷新")
    auto_refresh = st.checkbox("启用自动刷新", value=True)
    if auto_refresh:
        refresh_interval = st.slider("刷新间隔(秒)", 1, 10, 3)

# 主内容区域
tab1, tab2, tab3, tab4 = st.tabs(["📝 文本分析", "� 实时语音",  "📡 UDP数据", "⚙️ 设置"])

with tab1:
    st.header("📝 文本分析")
    
    # 文本输入
    user_input = st.text_area(
        "请输入要分析的文本:",
        height=100,
        placeholder="例如：你总是这样不负责任..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔍 分析文本", type="primary"):
            if user_input.strip():
                with st.spinner("正在分析..."):
                    result = analyze_text(user_input.strip())
                    if result.get("success"):
                        st.session_state.analysis_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "input": user_input.strip(),
                            "result": result
                        })
                        display_analysis_result(result)
                    else:
                        st.error(f"分析失败: {result.get('error', '未知错误')}")
            else:
                st.warning("请输入要分析的文本")

with tab2:
    st.header("🎤 实时语音分析")
    
    if st.session_state.vad_running:
        st.success("🎤 语音识别服务正在运行，请开始说话...")
        
        # 获取所有分析历史记录
        history_data = get_analysis_history()
        
        if history_data.get("success") and history_data.get("data"):
            analysis_list = history_data["data"]
            
            # 显示统计信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总识别次数", len(analysis_list))
            with col2:
                violations = sum(1 for item in analysis_list if item.get("is_violation", False))
                st.metric("越网次数", violations)
            with col3:
                violation_rate = (violations / len(analysis_list) * 100) if analysis_list else 0
                st.metric("越网率", f"{violation_rate:.1f}%")
            
            st.markdown("---")
            
            # 显示所有分析结果（最新的在前）
            st.subheader("📝 所有语音识别与分析结果")
            
            for i, analysis in enumerate(reversed(analysis_list)):
                with st.expander(f"语音 #{len(analysis_list) - i} - {analysis.get('timestamp', '')[:19]} - {analysis.get('question', 'N/A')[:50]}..."):
                    # 显示识别的文本
                    st.write(f"**识别文本:** {analysis.get('question', 'N/A')}")
                    
                    # 显示分析结果
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # 硬件控制指令
                        binary_signal = analysis.get("binary_signal", "0")
                        is_violation = analysis.get("is_violation", False)
                        
                        if is_violation:
                            st.error(f"🚨 硬件控制指令: {binary_signal}")
                            st.error("⚠️ 检测到越网行为")
                        else:
                            st.success(f"✅ 硬件控制指令: {binary_signal}")
                            st.success("✅ 未检测到越网行为")
                    
                    with col2:
                        # 详细分析
                        violation_type = analysis.get("violation_type", "none")
                        explanation = analysis.get("explanation", "")
                        suggestion = analysis.get("suggestion", "")
                        
                        st.write(f"**违规类型:** {violation_type}")
                        st.write(f"**解释:** {explanation}")
                        if suggestion:
                            st.write(f"**建议:** {suggestion}")
            
            # 清空历史记录按钮
            if st.button("🗑️ 清空语音分析历史"):
                result = clear_analysis_history()
                if result.get("success"):
                    st.success("历史记录已清空")
                    st.rerun()
                else:
                    st.error(f"清空失败: {result.get('error', '未知错误')}")
        else:
            st.info("等待语音输入...")
        
        # 手动刷新按钮
        if st.button("🔄 刷新结果"):
            st.rerun()
            
    else:
        st.warning("⚠️ 请先在侧边栏启动语音识别服务")
        st.info("启动后，系统将自动识别您的语音并进行网球场理论分析")
 

with tab3:
    st.header("📡 UDP数据监控")
    
    # UDP服务器状态
    udp_status_data = get_udp_status()
    udp_running = udp_status_data.get("udp_running", False)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if udp_running:
            st.success("🟢 UDP服务器运行中")
        else:
            st.error("🔴 UDP服务器未运行")
    
    with col2:
        if st.button("🔄 刷新UDP数据"):
            st.rerun()
    
    st.markdown("---")
    
    # 获取UDP数据
    udp_data = get_udp_data()
    
    if udp_data.get("success") and udp_data.get("data"):
        data_list = udp_data["data"]
        
        # 显示统计信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总接收数据包", len(data_list))
        with col2:
            # 计算最近1分钟的数据包数量
            recent_count = 0
            current_time = datetime.now()
            for item in data_list:
                try:
                    item_time = datetime.fromisoformat(item.get("timestamp", ""))
                    if (current_time - item_time).total_seconds() <= 60:
                        recent_count += 1
                except:
                    pass
            st.metric("最近1分钟", recent_count)
        with col3:
            # 显示最新数据包时间
            if data_list:
                latest_time = data_list[-1].get("timestamp", "N/A")[:19]
                st.metric("最新数据", latest_time)
            else:
                st.metric("最新数据", "无")
        with col4:
            # 显示数据包大小统计
            if data_list:
                avg_size = sum(len(str(item.get("data", ""))) for item in data_list) / len(data_list)
                st.metric("平均包大小", f"{avg_size:.0f}字节")
            else:
                st.metric("平均包大小", "0字节")
        
        st.markdown("---")
        
        # 实时数据显示
        st.subheader("📊 实时UDP数据流")
        
        # 创建数据表格
        if data_list:
            # 只显示最近50条数据
            recent_data = data_list[-50:] if len(data_list) > 50 else data_list
            
            # 准备表格数据
            table_data = []
            for i, item in enumerate(reversed(recent_data)):
                # 检查是否有分析结果
                analysis_status = "未分析"
                if "analysis_result" in item:
                    analysis_result = item.get("analysis_result", {})
                    if analysis_result.get("is_violation"):
                        analysis_status = "🚨 越网"
                    else:
                        analysis_status = "✅ 正常"
                
                table_data.append({
                    "序号": len(recent_data) - i,
                    "时间": item.get("timestamp", "N/A")[:19],
                    "源地址": item.get("source_ip", "N/A"),
                    "源端口": item.get("source_port", "N/A"),
                    "数据长度": len(str(item.get("data", ""))),
                    "分析状态": analysis_status,
                    "数据预览": str(item.get("data", ""))[:50] + "..." if len(str(item.get("data", ""))) > 50 else str(item.get("data", ""))
                })
            
            # 显示表格
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, height=400)
            
            st.markdown("---")
            
            # 详细数据展开
            st.subheader("🔍 详细数据查看")
            
            # 选择要查看的数据包
            selected_index = st.selectbox(
                "选择要查看的数据包:",
                options=range(len(recent_data)),
                format_func=lambda x: f"数据包 #{len(recent_data) - x} - {recent_data[len(recent_data) - 1 - x].get('timestamp', 'N/A')[:19]}"
            )
            
            if selected_index is not None:
                selected_item = recent_data[len(recent_data) - 1 - selected_index]
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**基本信息:**")
                    st.write(f"时间戳: {selected_item.get('timestamp', 'N/A')}")
                    st.write(f"源IP: {selected_item.get('source_ip', 'N/A')}")
                    st.write(f"源端口: {selected_item.get('source_port', 'N/A')}")
                    st.write(f"数据长度: {len(str(selected_item.get('data', '')))} 字节")
                
                with col2:
                    st.write("**完整数据内容:**")
                    data_content = selected_item.get("data", "")
                    
                    # 尝试解析JSON
                    try:
                        if isinstance(data_content, str):
                            json_data = json.loads(data_content)
                            st.json(json_data)
                        else:
                            st.json(data_content)
                    except:
                        # 如果不是JSON，显示为文本
                        st.code(str(data_content), language="text")
                
                # 显示模型分析结果（如果有的话）
                if "analysis_result" in selected_item:
                    st.markdown("---")
                    st.subheader("🤖 模型分析结果")
                    
                    analysis_result = selected_item.get("analysis_result", {})
                    
                    # 创建两列布局显示分析结果
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # 硬件控制指令和状态
                        binary_signal = analysis_result.get("binary_signal", "0")
                        is_violation = analysis_result.get("is_violation", False)
                        
                        if is_violation:
                            st.error(f"🚨 硬件控制指令: {binary_signal}")
                            st.error("⚠️ 检测到越网行为")
                        else:
                            st.success(f"✅ 硬件控制指令: {binary_signal}")
                            st.success("✅ 未检测到越网行为")
                        
                        # 基本分析信息
                        st.write(f"**分析时间:** {analysis_result.get('timestamp', 'N/A')[:19]}")
                        st.write(f"**是否违规:** {'是' if is_violation else '否'}")
                    
                    with col2:
                        # 详细分析结果
                        violation_type = analysis_result.get("violation_type", "none")
                        explanation = analysis_result.get("explanation", "")
                        suggestion = analysis_result.get("suggestion", "")
                        
                        st.write(f"**违规类型:** {violation_type}")
                        st.write(f"**解释:** {explanation}")
                        if suggestion:
                            st.write(f"**建议:** {suggestion}")
                        
                        # 显示LLM原始响应（如果有的话）
                        if "llm_response" in analysis_result:
                            with st.expander("查看LLM原始响应"):
                                try:
                                    llm_data = json.loads(analysis_result["llm_response"])
                                    st.json(llm_data)
                                except:
                                    st.text(analysis_result["llm_response"])
                else:
                    st.info("💡 此数据包未进行模型分析")
                    
                    # 如果是文本数据且未分析，提供分析按钮
                    if selected_item.get("type") == "text" or (isinstance(selected_item.get("data"), str) and not selected_item.get("data", "").startswith("<binary")):
                        text_data = selected_item.get("data", "")
                        if text_data and len(text_data.strip()) > 0:
                            if st.button(f"🔍 分析此数据包", key=f"analyze_{selected_index}"):
                                with st.spinner("正在分析UDP数据..."):
                                    # 尝试解析JSON或直接使用文本
                                    try:
                                        if text_data.startswith('{'):
                                            json_data = json.loads(text_data)
                                            analyze_text_content = json_data.get('text', text_data)
                                        else:
                                            analyze_text_content = text_data
                                    except:
                                        analyze_text_content = text_data
                                    
                                    # 调用分析API
                                    result = analyze_text(analyze_text_content.strip())
                                    if result.get("success"):
                                        # 将分析结果存储到session state中，以便立即显示
                                        analysis_key = f"udp_analysis_{selected_index}"
                                        st.session_state[analysis_key] = result
                                        st.success("✅ 分析完成！")
                                        st.rerun()  # 刷新页面以显示结果
                                    else:
                                        st.error(f"❌ 分析失败: {result.get('error', '未知错误')}")
                
                # 检查是否有临时分析结果需要显示
                analysis_key = f"udp_analysis_{selected_index}"
                if analysis_key in st.session_state:
                    st.markdown("---")
                    st.subheader("🤖 刚完成的分析结果")
                    
                    temp_result = st.session_state[analysis_key]
                    
                    # 显示分析结果
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # 硬件控制指令和状态
                        binary_signal = temp_result.get("binary_signal", "0")
                        is_violation = temp_result.get("is_violation", False)
                        
                        if is_violation:
                            st.error(f"🚨 硬件控制指令: {binary_signal}")
                            st.error("⚠️ 检测到越网行为")
                        else:
                            st.success(f"✅ 硬件控制指令: {binary_signal}")
                            st.success("✅ 未检测到越网行为")
                        
                        # 基本分析信息
                        st.write(f"**分析时间:** {temp_result.get('timestamp', datetime.now().isoformat())[:19]}")
                        st.write(f"**是否违规:** {'是' if is_violation else '否'}")
                    
                    with col2:
                        # 详细分析结果
                        violation_type = temp_result.get("violation_type", "none")
                        explanation = temp_result.get("explanation", "")
                        suggestion = temp_result.get("suggestion", "")
                        
                        st.write(f"**违规类型:** {violation_type}")
                        st.write(f"**解释:** {explanation}")
                        if suggestion:
                            st.write(f"**建议:** {suggestion}")
                        
                        # 显示LLM原始响应（如果有的话）
                        if "llm_response" in temp_result:
                            with st.expander("查看LLM原始响应"):
                                try:
                                    llm_data = json.loads(temp_result["llm_response"])
                                    st.json(llm_data)
                                except:
                                    st.text(temp_result["llm_response"])
                    
                    # 提供清除临时结果的按钮
                    if st.button("✅ 确认查看完毕", key=f"clear_temp_{selected_index}"):
                        del st.session_state[analysis_key]
                        st.rerun()
        
        # 清空UDP数据按钮
        if st.button("🗑️ 清空UDP数据历史"):
            # 这里需要后端API支持清空UDP数据
            st.warning("清空功能需要后端API支持")
            
    else:
        st.info("暂无UDP数据或UDP服务器未运行")
        st.write("请确保:")
        st.write("- UDP服务器已启动")
        st.write("- 有客户端正在发送数据")
        st.write("- 后端API正常运行")

with tab4:
    st.header("⚙️ 系统设置")
    
    # 提示词设置
    st.subheader("📝 自定义提示词")
    st.info("注意：修改提示词可能影响分析准确性，建议保持默认设置")
    
    custom_prompt = st.text_area(
        "提示词内容:",
        value=st.session_state.custom_prompt,
        height=300,
        help="用于指导LLM进行网球场理论分析的提示词"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存提示词"):
            st.session_state.custom_prompt = custom_prompt
            st.success("提示词已保存")
    
    with col2:
        if st.button("🔄 重置为默认"):
            st.session_state.custom_prompt = """你是一个专门基于人际关系网球场理论进行沟通分析的AI助手。你的核心任务是判断对话中最新一条消息的发送者是否"越网"。

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
{
    "is_violation": true/false,
    "violation_type": "assumption/judgment/mind_reading/generalization/none",
    "explanation": "详细解释为什么越网或未越网",
    "suggestion": "如果越网，提供改进建议"
}"""
            st.success("提示词已重置为默认")
            st.rerun()
    
    st.markdown("---")
    
    # UDP通知设置
    st.subheader("📡 UDP通知设置")
    
    # 初始化通知消息的session state
    if 'notification_message' not in st.session_state:
        st.session_state.notification_message = "-blue"
    
    st.info(f"当检测到越网行为时，系统会自动发送UDP通知消息 '{st.session_state.notification_message}'")
    
    # 获取当前UDP通知配置
    udp_config = get_udp_notification_config()
    
    if udp_config.get("success"):
        current_config = udp_config.get("config", {})
        current_host = current_config.get("host", "127.0.0.1")
        current_port = current_config.get("port", 5003)
    else:
        current_host = "127.0.0.1"
        current_port = 5003
        st.warning("无法获取当前UDP通知配置，使用默认值")
    
    # UDP通知配置表单
    with st.form("udp_notification_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            notification_host = st.text_input(
                "目标主机地址:",
                value=current_host,
                help="接收UDP通知的目标主机IP地址"
            )
        
        with col2:
            notification_port = st.number_input(
                "目标端口:",
                min_value=1,
                max_value=65535,
                value=current_port,
                help="接收UDP通知的目标端口号"
            )
        
        # 通知消息配置
        notification_message = st.text_input(
            "通知消息:",
            value=st.session_state.notification_message,
            help="检测到越网行为时发送的UDP通知消息"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 保存配置", type="primary"):
                # 保存UDP配置
                result = set_udp_notification_config(notification_host, notification_port)
                if result.get("success"):
                    # 保存通知消息到session state
                    st.session_state.notification_message = notification_message
                    st.success("UDP通知配置已保存")
                    st.rerun()
                else:
                    st.error(f"保存失败: {result.get('error', '未知错误')}")
        
        with col2:
            if st.form_submit_button("🧪 测试通知"):
                with st.spinner("正在发送测试通知..."):
                    result = test_udp_notification(notification_message)
                    if result.get("success"):
                        st.success(f"测试通知发送成功！\n消息: {result.get('sent_message')}")
                    else:
                        st.error(f"测试失败: {result.get('error', '未知错误')}")
        
        with col3:
            if st.form_submit_button("🔄 刷新配置"):
                st.rerun()
    
    # 显示当前配置状态
    st.write("**当前UDP通知配置:**")
    st.write(f"- 目标地址: `{current_host}:{current_port}`")
    st.write(f"- 通知消息: `{st.session_state.notification_message}`")
    st.write(f"- 触发条件: 检测到越网行为 (binary_signal = '1')")
    
    st.markdown("---")
    
    # API设置
    st.subheader("🔗 API设置")
    st.write(f"**后端API地址:** {API_BASE_URL}")
    
    # 系统信息
    st.subheader("ℹ️ 系统信息")
    st.write("**版本:** 1.0.0")
    st.write("**功能:** 网球场理论沟通分析")
    st.write("**支持:** 文本分析、实时语音识别、历史记录、UDP通知")

# 自动刷新逻辑
if auto_refresh and st.session_state.vad_running:
    time.sleep(refresh_interval)
    st.rerun()

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🎾 网球场理论分析系统 | 基于人际沟通理论的智能分析工具
    </div>
    """,
    unsafe_allow_html=True
)