"""
离线版本的 Test.py，使用本地模型文件而不是从网络下载。

使用方法:
1. 确保 models/ 目录下有模型文件（通过 package_models.py 生成）
2. 运行: python Test_offline.py
"""

import torchaudio as ta
import torch

from chatterbox import ChatterboxMultilingualTTS
from chatterbox.tts_turbo import ChatterboxTurboTTS
from pathlib import Path

# 模型文件路径（相对于当前脚本）
MODELS_DIR = Path("./models")
TURBO_MODEL_DIR = MODELS_DIR / "chatterbox-turbo"
MULTILINGUAL_MODEL_DIR = MODELS_DIR / "chatterbox"

# 检查模型目录是否存在
if not TURBO_MODEL_DIR.exists():
    raise FileNotFoundError(
        f"Turbo 模型目录不存在: {TURBO_MODEL_DIR}\n"
        "请先运行 package_models.py 打包模型文件"
    )

if not MULTILINGUAL_MODEL_DIR.exists():
    raise FileNotFoundError(
        f"多语言模型目录不存在: {MULTILINGUAL_MODEL_DIR}\n"
        "请先运行 package_models.py 打包模型文件"
    )

# 加载 Turbo 模型（从本地）
print("正在加载 Turbo 模型...")
model = ChatterboxTurboTTS.from_local(TURBO_MODEL_DIR, device="cpu")
print("Turbo 模型加载完成")

# 生成示例（需要参考音频）
# text = "Hi there, Sarah here from MochaFone calling you back [chuckle], have you got one minute to chat about the billing issue?"
# wav = model.generate(text, audio_prompt_path="audio.wav")
# ta.save("test-turbo.wav", wav, model.sr)

# 加载多语言模型（从本地）
print("正在加载多语言模型...")
multilingual_model = ChatterboxMultilingualTTS.from_local(MULTILINGUAL_MODEL_DIR, device="cpu")
print("多语言模型加载完成")

# 生成中文语音
chinese_text = "你好，今天真是个好天气。"
print(f"正在生成语音: {chinese_text}")
wav_chinese = multilingual_model.generate(
    chinese_text, 
    language_id="zh",
    audio_prompt_path="zh01.wav"
)
ta.save("test-chinese.wav", wav_chinese, multilingual_model.sr)
print("语音生成完成，已保存到 test-chinese.wav")

