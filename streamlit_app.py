import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd

# 配置页面
st.set_page_config(
    page_title="UDP数据监控系统",
    page_icon="📡",
    layout="wide"
)

# 后端API配置
API_BASE_URL = "http://localhost:5001"

# UDP相关API调用函数
def check_api_health():
    """检查后端API健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_udp_status():
    """获取UDP服务器状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/status", timeout=5)
        return response.json() if response.status_code == 200 else {"success": False, "udp_running": False}
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

def get_udp_data():
    """获取UDP数据"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/data", timeout=5)
        return response.json() if response.status_code == 200 else {"success": False, "message": "No UDP data available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_udp_stats():
    """获取UDP服务器统计信息"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/stats", timeout=5)
        return response.json() if response.status_code == 200 else {"success": False, "message": "Failed to get stats"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def cleanup_udp_clients():
    """清理不活跃的UDP客户端"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/udp/cleanup", timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_udp_notification_config():
    """获取UDP通知配置"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/udp/notification/config", timeout=5)
        return response.json() if response.status_code == 200 else {"success": False, "message": "Failed to get config"}
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

# 主界面
st.title("📡 UDP数据监控系统")

# 侧边栏控制
with st.sidebar:
    st.header("⚙️ 系统控制")
    
    # API健康检查
    if st.button("🔍 检查API状态"):
        if check_api_health():
            st.success("✅ 后端API正常")
        else:
            st.error("❌ 后端API连接失败")
    
    st.markdown("---")
    
    # UDP服务器控制
    st.subheader("📡 UDP服务器控制")
    udp_status = get_udp_status()
    udp_running = udp_status.get("udp_running", False)
    
    if udp_running:
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
tab1, tab2, tab3, tab4 = st.tabs(["🏠 系统概览", "📊 UDP数据监控", "📈 性能统计", "⚙️ UDP配置"])

with tab1:
    st.header("🏠 系统概览")
    
    # 系统状态卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if check_api_health():
            st.success("🟢 后端API")
            st.write("状态：正常运行")
        else:
            st.error("🔴 后端API")
            st.write("状态：连接失败")
    
    with col2:
        if udp_running:
            st.success("🟢 UDP服务器")
            st.write("状态：正在监听")
        else:
            st.error("🔴 UDP服务器")
            st.write("状态：未启动")
    
    with col3:
        # 获取统计信息
        stats_data = get_udp_stats()
        if stats_data.get("success"):
            active_clients = stats_data.get("stats", {}).get("active_clients", 0)
            if active_clients > 0:
                st.success(f"🟢 ESP设备")
                st.write(f"连接数：{active_clients}")
            else:
                st.warning("🟡 ESP设备")
                st.write("连接数：0")
        else:
            st.info("🔵 ESP设备")
            st.write("状态：未知")
    
    st.markdown("---")
    
    # 流程图展示
    st.subheader("🔄 优化后的处理流程")
    
    # 使用列来展示流程步骤
    flow_cols = st.columns(5)
    
    with flow_cols[0]:
        st.markdown("""
        **1. 接收音频**
        - ESP发送音频数据
        - UDP服务器接收
        - 立即返回确认
        """)
    
    with flow_cols[1]:
        st.markdown("""
        **2. 异步处理**
        - 音频缓冲管理
        - 并发任务控制
        - 线程安全处理
        """)
    
    with flow_cols[2]:
        st.markdown("""
        **3. 语音识别**
        - 实时转录
        - 智能分段
        - 错误重试
        """)
    
    with flow_cols[3]:
        st.markdown("""
        **4. LLM分析**
        - 网球场理论
        - 异步分析
        - 结果缓存
        """)
    
    with flow_cols[4]:
        st.markdown("""
        **5. 智能响应**
        - 🔴 违规警告
        - 🟢 正常信号
        - 🟡 错误提示
        """)
    
    st.markdown("---")
    
    # 实时统计概览
    st.subheader("📊 实时统计概览")
    
    if stats_data.get("success"):
        stats = stats_data.get("stats", {}).get("stats", {})
        
        # 主要指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总请求数", stats.get("total_requests", 0))
        with col2:
            st.metric("分析次数", stats.get("analysis_count", 0))
        with col3:
            st.metric("违规检测", stats.get("violation_count", 0))
        with col4:
            violation_rate = 0
            if stats.get("analysis_count", 0) > 0:
                violation_rate = (stats.get("violation_count", 0) / stats.get("analysis_count", 0)) * 100
            st.metric("违规率", f"{violation_rate:.1f}%")
        
        # 系统运行时间
        if stats.get("start_time"):
            uptime = time.time() - stats.get("start_time", time.time())
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            st.info(f"⏱️ 系统运行时间: {hours}小时 {minutes}分钟")
    else:
        st.warning("无法获取统计信息")
    
    st.markdown("---")
    
    # 快速操作
    st.subheader("⚡ 快速操作")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not udp_running:
            if st.button("🚀 启动系统", type="primary"):
                with st.spinner("正在启动UDP服务器..."):
                    result = start_udp_server()
                    if result.get("success"):
                        st.success("系统启动成功！")
                        st.rerun()
                    else:
                        st.error(f"启动失败: {result.get('error')}")
        else:
            if st.button("⏹️ 停止系统", type="secondary"):
                result = stop_udp_server()
                if result.get("success"):
                    st.success("系统已停止")
                    st.rerun()
                else:
                    st.error(f"停止失败: {result.get('error')}")
    
    with col2:
        if st.button("🔄 刷新状态"):
            st.rerun()
    
    with col3:
        if st.button("🧹 清理客户端"):
            result = cleanup_udp_clients()
            if result.get("success"):
                st.success(result.get("message", "清理完成"))
                st.rerun()
            else:
                st.error(f"清理失败: {result.get('error')}")
    
    with col4:
        if st.button("🧪 测试通知"):
            result = test_udp_notification("-blue")
            if result.get("success"):
                st.success("测试通知发送成功")
            else:
                st.error(f"测试失败: {result.get('error')}")
    
    # 系统健康检查
    st.markdown("---")
    st.subheader("🏥 系统健康检查")
    
    health_checks = []
    
    # API健康检查
    if check_api_health():
        health_checks.append("✅ 后端API连接正常")
    else:
        health_checks.append("❌ 后端API连接失败")
    
    # UDP服务器检查
    if udp_running:
        health_checks.append("✅ UDP服务器运行正常")
    else:
        health_checks.append("⚠️ UDP服务器未启动")
    
    # 统计信息检查
    if stats_data.get("success"):
        health_checks.append("✅ 统计信息获取正常")
    else:
        health_checks.append("⚠️ 统计信息获取失败")
    
    for check in health_checks:
        st.write(check)

with tab2:
    st.header("📡 UDP数据监控")
    
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
                    "数据类型": item.get("type", "unknown"),
                    "数据长度": len(str(item.get("data", ""))),
                    "分析状态": analysis_status,
                    "数据预览": str(item.get("data", ""))[:50] + "..." if len(str(item.get("data", ""))) > 50 else str(item.get("data", ""))
                })
            
            # 显示表格
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, height=400)
            
            st.markdown("---")
            
            # 详细数据查看
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
                    st.write(f"数据类型: {selected_item.get('type', 'unknown')}")
                    st.write(f"数据长度: {len(str(selected_item.get('data', '')))} 字节")
                
                with col2:
                    st.write("**完整数据内容:**")
                    data_content = selected_item.get("data", "")
                    
                    # 尝试解析JSON
                    try:
                        if isinstance(data_content, str) and data_content.startswith('{'):
                            json_data = json.loads(data_content)
                            st.json(json_data)
                        else:
                            st.code(str(data_content), language="text")
                    except:
                        st.code(str(data_content), language="text")
                
                # 显示分析结果（如果有的话）
                if "analysis_result" in selected_item:
                    st.markdown("---")
                    st.subheader("🤖 分析结果")
                    
                    analysis_result = selected_item.get("analysis_result", {})
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        binary_signal = analysis_result.get("binary_signal", "0")
                        is_violation = analysis_result.get("is_violation", False)
                        
                        if is_violation:
                            st.error(f"🚨 硬件控制指令: {binary_signal}")
                            st.error("⚠️ 检测到越网行为")
                        else:
                            st.success(f"✅ 硬件控制指令: {binary_signal}")
                            st.success("✅ 未检测到越网行为")
                    
                    with col2:
                        st.write(f"**违规类型:** {analysis_result.get('violation_type', 'none')}")
                        st.write(f"**解释:** {analysis_result.get('explanation', '')}")
                        if analysis_result.get('suggestion'):
                            st.write(f"**建议:** {analysis_result.get('suggestion')}")
    else:
        st.info("暂无UDP数据或UDP服务器未运行")
        st.write("请确保:")
        st.write("- UDP服务器已启动")
        st.write("- 有客户端正在发送数据")
        st.write("- 后端API正常运行")

with tab3:
    st.header("📈 性能统计")
    
    # 获取UDP服务器统计信息
    stats_data = get_udp_stats()
    
    if stats_data.get("success") and stats_data.get("stats"):
        server_stats = stats_data["stats"]
        
        # 服务器状态概览
        st.subheader("🖥️ 服务器状态")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("服务器状态", "🟢 运行中" if server_stats.get("running", False) else "🔴 已停止")
        with col2:
            st.metric("活跃客户端", server_stats.get("active_clients", 0))
        with col3:
            st.metric("活跃线程", server_stats.get("active_threads", 0))
        with col4:
            st.metric("音频缓冲区", f"{server_stats.get('buffer_size', 0)} 字节")
        
        st.markdown("---")
        
        # 请求统计
        st.subheader("📊 请求统计")
        stats = server_stats.get("stats", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总请求数", stats.get("total_requests", 0))
        with col2:
            st.metric("音频请求", stats.get("audio_requests", 0))
        with col3:
            st.metric("文本请求", stats.get("text_requests", 0))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("分析次数", stats.get("analysis_count", 0))
        with col2:
            st.metric("违规检测", stats.get("violation_count", 0))
        with col3:
            violation_rate = 0
            if stats.get("analysis_count", 0) > 0:
                violation_rate = (stats.get("violation_count", 0) / stats.get("analysis_count", 0)) * 100
            st.metric("违规率", f"{violation_rate:.1f}%")
        
        st.markdown("---")
        
        # 性能图表
        st.subheader("📈 性能趋势")
        
        # 创建简单的性能数据可视化
        if stats.get("total_requests", 0) > 0:
            chart_data = pd.DataFrame({
                '请求类型': ['音频请求', '文本请求'],
                '数量': [stats.get("audio_requests", 0), stats.get("text_requests", 0)]
            })
            st.bar_chart(chart_data.set_index('请求类型'))
        else:
            st.info("暂无请求数据用于图表显示")
        
        st.markdown("---")
        
        # 系统管理
        st.subheader("🔧 系统管理")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 清理不活跃客户端"):
                with st.spinner("正在清理不活跃客户端..."):
                    result = cleanup_udp_clients()
                    if result.get("success"):
                        st.success(result.get("message", "清理完成"))
                        st.rerun()
                    else:
                        st.error(f"清理失败: {result.get('error', '未知错误')}")
        
        with col2:
            if st.button("📊 刷新统计信息"):
                st.rerun()
        
        # 详细统计信息
        with st.expander("🔍 详细统计信息"):
            st.json(server_stats)
    
    else:
        st.warning("无法获取服务器统计信息")
        if not udp_running:
            st.info("请先启动UDP服务器")
        else:
            st.error("服务器统计API可能不可用")

with tab4:
    st.header("⚙️ UDP通知配置")
    
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
    
    st.info("当检测到越网行为时，系统会自动发送UDP通知消息")
    
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
                help="接收UDP通知的目标端口"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 保存配置", type="primary"):
                result = set_udp_notification_config(notification_host, notification_port)
                if result.get("success"):
                    st.success("UDP通知配置已保存")
                    st.rerun()
                else:
                    st.error(f"保存失败: {result.get('error', '未知错误')}")
        
        with col2:
            if st.form_submit_button("🧪 测试通知"):
                with st.spinner("正在发送测试通知..."):
                    result = test_udp_notification("-blue")
                    if result.get("success"):
                        st.success("测试通知发送成功")
                    else:
                        st.error(f"测试失败: {result.get('error', '未知错误')}")
    
    st.markdown("---")
    
    # 显示当前配置
    st.subheader("📋 当前配置")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("通知目标地址", current_host)
    with col2:
        st.metric("通知目标端口", current_port)

# 自动刷新逻辑
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()