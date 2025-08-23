#!/usr/bin/env python3
"""
UDP音频客户端测试脚本
模拟发送音频字节流到UDP服务器
"""

import socket
import json
import time
import pyaudio
import threading
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UDPAudioClient:
    def __init__(self, server_host='localhost', server_port=5002):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
        
        # 音频配置 - 与vad_dash.py相同
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk_size = 3200  # 每次发送3200字节
        
        self.pya = None
        self.stream = None
    
    def init_audio(self):
        """初始化音频设备"""
        try:
            self.pya = pyaudio.PyAudio()
            self.stream = self.pya.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size // 2  # 16-bit = 2 bytes per sample
            )
            logger.info("Audio initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            return False
    
    def send_audio_stream(self, duration=30):
        """发送音频流到UDP服务器"""
        if not self.init_audio():
            return
        
        logger.info(f"Starting audio stream for {duration} seconds...")
        self.running = True
        start_time = time.time()
        
        try:
            while self.running and (time.time() - start_time) < duration:
                try:
                    # 读取音频数据
                    audio_data = self.stream.read(
                        self.chunk_size // 2,  # frames
                        exception_on_overflow=False
                    )
                    
                    # 发送到UDP服务器
                    self.socket.sendto(audio_data, (self.server_host, self.server_port))
                    
                    # 接收服务器响应
                    try:
                        self.socket.settimeout(0.1)  # 100ms超时
                        response, addr = self.socket.recvfrom(1024)
                        response_data = json.loads(response.decode('utf-8'))
                        
                        if response_data.get('success'):
                            logger.debug(f"Sent {len(audio_data)} bytes, buffer: {response_data.get('buffer_size', 0)}")
                        else:
                            logger.error(f"Server error: {response_data.get('error')}")
                            
                    except socket.timeout:
                        # 超时是正常的，继续发送
                        pass
                    except Exception as e:
                        logger.warning(f"Response error: {e}")
                    
                    # 小延迟以匹配实时音频
                    time.sleep(0.1)  # 100ms间隔，匹配3200字节@16kHz的时长
                    
                except Exception as e:
                    logger.error(f"Error reading/sending audio: {e}")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.cleanup()
    
    def send_test_audio_data(self, num_chunks=10):
        """发送测试音频数据（模拟数据）"""
        logger.info(f"Sending {num_chunks} chunks of test audio data...")
        
        for i in range(num_chunks):
            # 创建3200字节的测试音频数据
            # 使用简单的正弦波模拟音频
            import struct
            import math
            
            test_data = b''
            for j in range(1600):  # 1600个16-bit样本 = 3200字节
                # 生成440Hz正弦波
                sample = int(32767 * 0.1 * math.sin(2 * math.pi * 440 * j / 16000))
                test_data += struct.pack('<h', sample)  # 小端序16-bit
            
            try:
                # 发送测试数据
                self.socket.sendto(test_data, (self.server_host, self.server_port))
                logger.info(f"Sent chunk {i+1}/{num_chunks} ({len(test_data)} bytes)")
                
                # 接收响应
                try:
                    self.socket.settimeout(1.0)
                    response, addr = self.socket.recvfrom(1024)
                    response_data = json.loads(response.decode('utf-8'))
                    
                    if response_data.get('success'):
                        logger.info(f"Server response: {response_data.get('message')}")
                    else:
                        logger.error(f"Server error: {response_data.get('error')}")
                        
                except socket.timeout:
                    logger.warning("No response from server")
                except Exception as e:
                    logger.error(f"Response error: {e}")
                
                time.sleep(0.5)  # 500ms间隔
                
            except Exception as e:
                logger.error(f"Error sending test data: {e}")
                break
    
    def send_text_message(self, text):
        """发送文本消息进行测试"""
        try:
            message = {
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
            
            message_json = json.dumps(message, ensure_ascii=False)
            self.socket.sendto(message_json.encode('utf-8'), (self.server_host, self.server_port))
            
            logger.info(f"Sent text message: {text}")
            
            # 接收响应
            try:
                self.socket.settimeout(5.0)
                response, addr = self.socket.recvfrom(2048)
                response_data = json.loads(response.decode('utf-8'))
                
                if response_data.get('success'):
                    logger.info(f"Analysis result: {response_data.get('binary_signal')} - {response_data.get('explanation', '')}")
                else:
                    logger.error(f"Analysis failed: {response_data.get('error')}")
                    
            except socket.timeout:
                logger.warning("No response from server")
            except Exception as e:
                logger.error(f"Response error: {e}")
                
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
    
    def cleanup(self):
        """清理资源"""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        if self.pya:
            self.pya.terminate()
            
        if self.socket:
            self.socket.close()
            
        logger.info("Client cleanup completed")

def main():
    """主函数"""
    client = UDPAudioClient()
    
    try:
        print("UDP Audio Client Test")
        print("1. Send real audio stream (requires microphone)")
        print("2. Send test audio data (simulated)")
        print("3. Send text message")
        print("4. Exit")
        
        while True:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                duration = input("Duration in seconds (default 10): ").strip()
                duration = int(duration) if duration.isdigit() else 10
                client.send_audio_stream(duration)
                
            elif choice == '2':
                chunks = input("Number of chunks (default 5): ").strip()
                chunks = int(chunks) if chunks.isdigit() else 5
                client.send_test_audio_data(chunks)
                
            elif choice == '3':
                text = input("Enter text to analyze: ").strip()
                if text:
                    client.send_text_message(text)
                else:
                    print("Text cannot be empty")
                    
            elif choice == '4':
                break
                
            else:
                print("Invalid choice, please select 1-4")
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        client.cleanup()

if __name__ == '__main__':
    main()