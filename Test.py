import torchaudio as ta
import torch
from pathlib import Path
from chatterbox import ChatterboxMultilingualTTS
from chatterbox.tts_turbo import ChatterboxTurboTTS
# 模型文件路径（相对于当前脚本）
MODELS_DIR = Path("./models")
TURBO_MODEL_DIR = MODELS_DIR / "chatterbox-turbo"
MULTILINGUAL_MODEL_DIR = MODELS_DIR / "chatterbox"
# Load the Turbo model
#model = ChatterboxTurboTTS.from_pretrained(device="cpu")
model = ChatterboxTurboTTS.from_local(TURBO_MODEL_DIR,device="cpu")
# Generate with Paralinguistic Tags
text = "Hi there, Sarah here from MochaFone calling you back [chuckle], have you got one minute to chat about the billing issue?"

# Generate audio (requires a reference clip for voice cloning)
#wav = model.generate(text, audio_prompt_path="audio.wav")

#ta.save("test-turbo.wav", wav, model.sr)

# Multilingual examples
#multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
multilingual_model = ChatterboxMultilingualTTS.from_local(MULTILINGUAL_MODEL_DIR,device="cpu")
chinese_text = "你好，今天真是个好天气，我真想笑啊，哈哈哈哈 "
wav_chinese = multilingual_model.generate(chinese_text, language_id="zh",audio_prompt_path="2.wav")
ta.save("test-chinese.wav", wav_chinese, model.sr)