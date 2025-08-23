import os
import dashscope

# 从环境变量读取 API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 验证是否读取成功
if dashscope.api_key:
    print("DashScope API Key 已设置成功！")
else:
    print("DashScope API Key 未设置，请检查环境变量。")
