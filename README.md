# 语音转文本 & LLM 分析系统

一个基于 Streamlit 和 Flask 的实时语音转文本和 LLM 分析系统，支持硬件控制指令生成。

## 功能特性

- 🎤 **实时语音录音**：支持麦克风录音（需要 HTTPS 环境）
- 📝 **语音转文本**：实时音频转文本显示
- 🤖 **LLM 分析**：使用阿里云 DashScope API 进行文本分析
- ⚙️ **自定义提示词**：可调整发送给 LLM 的提示词
- ⚡ **硬件控制**：基于 LLM 分析结果生成硬件控制指令（0/1）
- ✏️ **手动输入**：支持手动输入文本进行 LLM 分析
- 📚 **对话历史**：显示完整的对话记录

## 系统架构

```
前端 (Streamlit) ←→ 后端 (Flask API) ←→ DashScope LLM API
     ↓
   用户界面
   - 语音录音
   - 文本输入
   - 结果显示
   - 历史记录
```

## 安装和配置

### 1. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件并配置 API Key：

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 DashScope API Key
DASHSCOPE_API_KEY=your_api_key_here
```

## 运行应用

### 方式一：使用启动脚本（推荐）

```bash
python start_app.py
```

这将同时启动：
- Flask 后端服务：http://localhost:5000
- Streamlit 前端：http://localhost:8501

### 方式二：分别启动

**启动后端服务：**
```bash
python backend_api.py
```

**启动前端应用：**
```bash
streamlit run streamlit_app.py
```

## API 接口

### 后端 API 端点

- `GET /api/health` - 健康检查
- `POST /api/analyze` - 文本分析
- `POST /api/hardware/command` - 硬件控制指令
- `POST /api/audio/transcribe` - 音频转文本（待实现）

### 请求示例

**文本分析：**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "请开启设备",
    "prompt": "请分析以下文本，如果需要开启设备回复1，否则回复0："
  }'
```

## 使用说明

### 前端界面功能

1. **语音输入区域**
   - 点击"开始录音"按钮进行录音
   - 实时显示转录文本
   - 支持手动文本输入

2. **LLM 分析区域**
   - 显示 LLM 完整响应
   - 显示硬件控制指令（0/1）
   - 实时状态指示

3. **配置侧边栏**
   - API Key 状态检查
   - 自定义提示词设置
   - 系统配置选项

4. **对话历史**
   - 显示最近的对话记录
   - 包含输入、响应和控制指令
   - 支持清除历史记录

### 硬件控制指令逻辑

系统会分析 LLM 的响应，提取硬件控制指令：
- **返回 "1"**：当检测到开启、启动、打开等关键词
- **返回 "0"**：当检测到关闭、停止、关掉等关键词
- **默认 "0"**：无明确指令时

## 文件结构

```
.
├── .env                 # 环境变量配置
├── .env.example         # 环境变量示例
├── requirements.txt     # Python 依赖
├── streamlit_app.py     # Streamlit 前端应用
├── backend_api.py       # Flask 后端 API
├── start_app.py         # 启动脚本
├── README.md           # 说明文档
└── .venv/              # 虚拟环境目录
```

## 开发说明

### 扩展语音识别功能

当前版本的语音识别是模拟实现。要添加真实的语音识别功能，可以：

1. 集成 OpenAI Whisper
2. 使用百度语音识别 API
3. 集成阿里云语音识别服务
4. 使用 Google Speech-to-Text API

### 硬件控制集成

要实现真实的硬件控制，可以在 `backend_api.py` 中添加：

1. MQTT 消息发布
2. 串口通信
3. HTTP 请求到硬件控制器
4. GPIO 控制（树莓派等）

### 部署注意事项

1. **HTTPS 要求**：浏览器的麦克风访问需要 HTTPS 环境
2. **跨域配置**：确保 Flask 后端正确配置 CORS
3. **API Key 安全**：生产环境中妥善保护 API Key
4. **性能优化**：考虑使用 Redis 缓存和负载均衡

## 故障排除

### 常见问题

1. **API Key 未配置**
   - 检查 `.env` 文件是否存在
   - 确认 API Key 格式正确

2. **端口占用**
   - 修改 `start_app.py` 中的端口配置
   - 或手动指定端口启动

3. **依赖安装失败**
   - 确保使用正确的 Python 版本
   - 尝试升级 pip：`pip install --upgrade pip`

4. **语音录音不工作**
   - 确保使用 HTTPS 环境
   - 检查浏览器麦克风权限

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！