"""
测试 API 服务器的脚本
"""

import requests
import os

# API 服务器地址
API_URL = os.getenv("API_URL", "http://localhost:8000")


def test_health():
    """测试健康检查接口"""
    print("测试健康检查接口...")
    response = requests.get(f"{API_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()


def test_tts(audio_file_path: str, text: str, model_type: str = "turbo", language: str = "en"):
    """测试文本转语音接口"""
    print(f"测试 TTS 接口...")
    print(f"文本: {text}")
    print(f"模型类型: {model_type}")
    print(f"语言: {language}")
    
    # 准备文件和数据
    with open(audio_file_path, "rb") as f:
        files = {"audio_file": (os.path.basename(audio_file_path), f, "audio/wav")}
        data = {
            "text": text,
            "model_type": model_type,
            "language": language,
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 1000,
            "repetition_penalty": 1.2,
        }
        
        # 发送请求
        response = requests.post(f"{API_URL}/api/v1/tts", files=files, data=data)
        
        if response.status_code == 200:
            # 保存生成的音频
            output_file = f"output_{model_type}.wav"
            with open(output_file, "wb") as out:
                out.write(response.content)
            print(f"✅ 成功！音频已保存到: {output_file}")
            print(f"文件大小: {len(response.content)} 字节")
        else:
            print(f"❌ 失败！状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    print()


if __name__ == "__main__":
    import sys
    
    # 检查参数
    if len(sys.argv) < 3:
        print("使用方法: python test_api.py <音频文件路径> <文本> [模型类型] [语言]")
        print("示例: python test_api.py zh01.wav '你好，世界' multilingual zh")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    text = sys.argv[2]
    model_type = sys.argv[3] if len(sys.argv) > 3 else "turbo"
    language = sys.argv[4] if len(sys.argv) > 4 else "en"
    
    # 检查音频文件是否存在
    if not os.path.exists(audio_file):
        print(f"错误: 音频文件不存在: {audio_file}")
        sys.exit(1)
    
    # 测试健康检查
    try:
        test_health()
    except Exception as e:
        print(f"健康检查失败: {e}")
        print("请确保 API 服务器正在运行")
        sys.exit(1)
    
    # 测试 TTS
    test_tts(audio_file, text, model_type, language)

