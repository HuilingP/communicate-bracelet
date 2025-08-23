# 网球场理论分析系统 - 集成版本

基于人际关系网球场理论的智能沟通分析系统，支持实时语音识别、UDP音频数据处理和文本分析。

## 🎯 功能特性

- � ***网球场理论分析**: 基于人际沟通理论，判断对话是否"越网"
- 🎤 **实时语音识别**: 支持实时语音转文本并进行分析
- 📝 **文本分析**: 直接输入文本进行网球场理论分析
- 📊 **可视化界面**: 基于Streamlit的直观Web界面
- 📡 **UDP音频处理**: 支持UDP协议接收和处理音频数据
- 🔄 **实时监控**: 实时显示分析结果和历史记录
- 🎛️ **集成控制**: 通过Web界面统一控制所有服务

## 🏗️ 系统架构（集成版本）

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web界面                        │
│                    (端口8501)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API调用
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                Flask API服务器 (端口5001)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   文本分析   │  │   VAD语音   │  │   集成UDP服务器      │  │
│  │   服务      │  │   识别服务   │  │   (端口5002)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │ LLM API调用
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                DashScope LLM服务                            │
│              (阿里云通义千问)                                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件并配置：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key_here
UDP_HOST=0.0.0.0
UDP_PORT=5002
```

### 3. 一键启动

```bash
# 启动集成系统
python start_app.py
```

系统将自动启动：
- ✅ Flask API服务器 (http://localhost:5001)
- ✅ 集成UDP服务器 (udp://localhost:5002)
- ✅ Streamlit Web界面 (http://localhost:8501)

### 4. 访问系统

打开浏览器访问: **http://localhost:8501**

## 📱 使用指南

### Web界面功能

#### 1. 📝 文本分析
- 在"文本分析"标签页输入文本
- 点击"分析文本"按钮
- 查看网球场理论分析结果

#### 2. 🎤 实时语音分析
- 在侧边栏点击"启动语音识别"
- 开始说话，系统自动识别并分析
- 在"实时语音"标签页查看结果

#### 3. 📡 UDP音频数据
- 在侧边栏点击"启动UDP服务器"
- 发送UDP音频数据到端口5002
- 在"UDP数据"标签页查看处理结果

#### 4. ⚙️ 系统设置
- 自定义分析提示词
- 查看系统信息
- 配置API设置

### 侧边栏控制

- 🔍 **API状态检查**: 检查后端服务健康状态
- 🎤 **语音识别控制**: 启动/停止VAD服务
- 📡 **UDP服务器控制**: 启动/停止UDP服务器
- 🔄 **自动刷新**: 配置界面自动刷新

## 🔧 API接口文档

### 基础接口

```http
GET  /api/health              # 健康检查
POST /api/analyze             # 文本分析
GET  /api/analysis/latest     # 最新分析结果
GET  /api/analysis/history    # 分析历史记录
DELETE /api/analysis/history  # 清空历史记录
```

### 语音识别接口

```http
POST /api/vad/start    # 启动语音识别
POST /api/vad/stop     # 停止语音识别
GET  /api/vad/status   # 获取VAD状态
```

### UDP服务器接口

```http
POST /api/udp/start    # 启动UDP服务器
POST /api/udp/stop     # 停止UDP服务器
GET  /api/udp/status   # 获取UDP状态
GET  /api/udp/data     # 获取UDP数据历史
DELETE /api/udp/data   # 清空UDP数据
```

### 文本分析示例

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "我觉得这个方案不太合适"}'
```

响应：
```json
{
  "success": true,
  "is_violation": false,
  "violation_type": "none",
  "explanation": "这是一个合规的表达...",
  "suggestion": "",
  "binary_signal": "0",
  "llm_response": "..."
}
```

## 🎾 网球场理论详解

### 核心概念
在人际沟通中，每个人应该待在自己的"半场"，只谈论自己的感受和观察到的行为，不要跨过"网"去猜测对方的动机或内心想法。

### ✅ 未越网（合规表达）
- **"我"的表达**: "我觉得..."、"我观察到..."
- **事实陈述**: 描述可观察的具体行为
- **感受分享**: "我感到困惑"、"我需要..."
- **询问确认**: "你是这个意思吗？"

### ❌ 越网（违规表达）
- **动机推测**: "你就是想..."、"你故意..."
- **内心判断**: "你不在乎..."、"你总是..."
- **代替表达**: "你应该感到..."
- **绝对化**: "你从来不..."、"你每次都..."

### 分析结果说明

| 字段 | 说明 |
|------|------|
| `is_violation` | 是否越网（true/false） |
| `violation_type` | 违规类型（assumption/judgment/mind_reading/generalization/none） |
| `explanation` | 详细解释 |
| `suggestion` | 改进建议 |
| `binary_signal` | 硬件控制信号（1=越网，0=未越网） |

## 🧪 测试功能

### 运行集成测试

```bash
# 测试完整系统功能
python test_integrated_udp.py
```

### 测试用例

```python
# 未越网示例
test_cases_valid = [
    "我觉得这个方案不太合适",
    "我观察到会议经常延迟开始", 
    "我需要更多的时间来完成这个任务",
    "我感到有些困惑，能解释一下吗？"
]

# 越网示例  
test_cases_violation = [
    "你总是这样不负责任",
    "你就是想要控制一切",
    "你从来不关心别人的感受",
    "你故意不回复我的消息"
]
```

## 🔍 故障排除

### 常见问题

#### 1. API Key配置问题
```bash
# 检查环境变量
cat .env
# 应该包含: DASHSCOPE_API_KEY=sk-xxx...
```

#### 2. 端口占用问题
```bash
# 检查端口占用
netstat -an | grep :5001  # API服务器
netstat -an | grep :5002  # UDP服务器  
netstat -an | grep :8501  # Streamlit
```

#### 3. 语音识别问题
- 检查麦克风权限
- 确认音频设备正常
- 查看浏览器控制台错误

#### 4. UDP连接问题
- 检查防火墙设置
- 确认UDP端口未被阻止
- 验证客户端发送格式

### 日志文件

| 文件 | 说明 |
|------|------|
| `output.log` | 分析结果详细日志 |
| `binary_output.log` | 二进制信号日志 |
| `streamlit.log` | Web界面运行日志 |

## 📁 项目结构

```
├── backend_api.py              # 集成API服务器（包含UDP）
├── backend_udp_server.py       # 独立UDP服务器（已弃用）
├── streamlit_app.py            # Streamlit Web界面
├── start_app.py               # 系统启动脚本
├── test_integrated_udp.py     # 集成测试脚本
├── requirements.txt           # Python依赖包
├── .env.example              # 环境变量示例
├── README.md                 # 项目文档
└── 其他测试和工具文件...
```

## 🆕 集成版本更新

### v2.0 主要改进

1. **🔗 服务集成**: UDP服务器集成到API服务器中
2. **🎛️ 统一控制**: 通过Web界面控制所有服务
3. **📊 数据共享**: UDP音频分析结果直接显示在UI中
4. **🚀 简化部署**: 一键启动所有服务
5. **📈 性能优化**: 减少进程间通信开销

### 迁移指南

如果你使用的是旧版本：
1. 停止所有旧服务
2. 更新代码到最新版本
3. 使用新的启动脚本 `python start_app.py`
4. 通过Web界面控制UDP服务器

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持与反馈

- 🐛 **Bug报告**: 请提交 GitHub Issue
- 💡 **功能建议**: 欢迎提交 Feature Request  
- 📧 **技术支持**: 联系开发团队
- 📚 **文档问题**: 提交文档改进建议

---

**🎾 让沟通回归本质，用网球场理论构建更好的人际关系！**