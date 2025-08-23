import os
from dashscope import Generation
from http import HTTPStatus

# 从环境变量读取 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")

def llm_request(prompt):
    if not api_key:
        return "DashScope API Key not set. Please check your environment variables."

    response = Generation.call(
        model='qwen-turbo',
        prompt=prompt
    )

    if response.status_code == HTTPStatus.OK:
        return response.output['text']
    else:
        return f"Error: {response.code} - {response.message}"

if __name__ == '__main__':
    prompt = "This is a test. If you receive this message, please respond with '1'."
    llm_response = llm_request(prompt)
    print(f"LLM Response: {llm_response}")
