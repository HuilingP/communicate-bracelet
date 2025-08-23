# dashscope SDK 版本需不低于 1.23.9
import os
import base64
import signal
import sys
import time
import pyaudio
import contextlib
import json
import logging
import threading
import queue
from dotenv import load_dotenv
from dashscope.audio.qwen_omni import *
import dashscope
from dashscope import Generation
from http import HTTPStatus

# Load environment variables from .env file
load_dotenv()

# 如果没有设置环境变量，请用您的 API Key 将下行替换为dashscope.api_key = "sk-xxx"
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
voice = 'Chelsie'
conversation = None

def llm_request(text):
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

    response = Generation.call(
        model='qwen-turbo',
        prompt=prompt
    )

    if response.status_code == HTTPStatus.OK:
        return response.output['text']
    else:
        return f"Error: {response.code} - {response.message}"

class MyCallback(OmniRealtimeCallback):
  def on_open(self) -> None:
    global pya
    global mic_stream
    print('connection opened, init microphone')
    pya = pyaudio.PyAudio()
    mic_stream = pya.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True)
  def on_close(self, close_status_code, close_msg) -> None:
      print('connection closed with code: {}, msg: {}, destroy microphone'.format(close_status_code, close_msg))

  def on_event(self, response: str) -> None:
      try:
          global conversation
          type = response['type']
          if 'session.created' == type:
              print('start session: {}'.format(response['session']['id']))
          if 'conversation.item.input_audio_transcription.completed' == type:
              transcript = response['transcript']
              print('question: {}'.format(transcript))

              # Send transcript to LLM
              llm_response = llm_request(transcript)
              print(f"LLM Response: {llm_response}")

              try:
                  # Parse the JSON response from the LLM
                  response_data = json.loads(llm_response)
                  is_violation = response_data.get("is_violation", False)
                  
                  # Determine the binary signal based on the is_violation flag
                  binary_signal = "1" if is_violation else "0"
                  print(binary_signal)
                  
                  # Log the binary signal to the output file
                  with open("binary_output.log", "a") as f:
                      f.write(binary_signal + "\n")
              except json.JSONDecodeError:
                  print("Error: Failed to decode LLM response as JSON.")

          if 'response.audio_transcript.delta' == type:
              pass
          if 'response.done' == type:
              print('======RESPONSE DONE======')
              print('[Metric] response: {}, first text delay: {}, first audio delay: {}'.format(
                              conversation.get_last_response_id(),
                              conversation.get_last_first_text_delay(),
                              conversation.get_last_first_audio_delay(),
                              ))
      except Exception as e:
          print('[Error] {}'.format(e))
          return

if __name__  == '__main__':
    logging.basicConfig(filename='output.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info('Initializing ...')
    callback = MyCallback()
    conversation = OmniRealtimeConversation(
        model='qwen-omni-turbo-realtime-latest',
        callback=callback, 
        )
    conversation.connect()
    conversation.update_session(
        output_modalities=[MultiModality.TEXT],
        voice=voice,
        input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
        output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
        enable_input_audio_transcription=True,
        input_audio_transcription_model='gummy-realtime-v1',
        enable_turn_detection=True,
        turn_detection_type='server_vad',
    )
    def signal_handler(sig, frame):
        print('Ctrl+C pressed, stop recognition ...')
        conversation.close()
        print('omni realtime stopped.')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    logging.info("Press 'Ctrl+C' to stop conversation...")
    last_photo_time = time.time()*1000
    while True:
        if mic_stream:
            audio_data = mic_stream.read(3200, exception_on_overflow=False)
            audio_b64 = base64.b64encode(audio_data).decode('ascii')
            try:
                conversation.append_audio(audio_b64)
            except Exception as e:
                print(f"Error sending audio: {e}")
                break
        else:
            break
