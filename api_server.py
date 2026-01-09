"""
Chatterbox TTS API 服务器
提供文本转语音的 RESTful API 接口
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import torch
import torchaudio as ta
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from chatterbox.tts_turbo import ChatterboxTurboTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

# 初始化 FastAPI 应用
app = FastAPI(
    title="Chatterbox TTS API",
    description="零样本语音克隆和文本转语音 API",
    version="1.0.0"
)

# 全局模型变量
turbo_model: Optional[ChatterboxTurboTTS] = None
multilingual_model: Optional[ChatterboxMultilingualTTS] = None

# 设备配置
DEVICE = os.getenv("DEVICE", "cpu")
if DEVICE == "cuda" and not torch.cuda.is_available():
    DEVICE = "cpu"
    print("CUDA 不可用，使用 CPU")

# 模型路径配置（支持离线部署）
MODELS_DIR = Path(os.getenv("MODELS_DIR", "./models"))
USE_LOCAL_MODELS =  "true"

# 设置 pkuseg 模型路径（用于离线部署）
# pkuseg 需要预先下载模型，在离线环境下需要设置 PKUSEG_HOME 环境变量
# 必须在导入 chatterbox 模块之前设置，因为模块导入时会初始化 pkuseg
PKUSEG_HOME = os.getenv("PKUSEG_HOME")
print(f" PKUSEG_HOME={PKUSEG_HOME}")
if not PKUSEG_HOME and USE_LOCAL_MODELS:
    pkuseg_dir = MODELS_DIR / "pkuseg"
    if pkuseg_dir.exists():
        PKUSEG_HOME = str(pkuseg_dir.absolute())
        os.environ["PKUSEG_HOME"] = PKUSEG_HOME
        print(f"设置 PKUSEG_HOME={PKUSEG_HOME}")
    else:
        print(f"警告: pkuseg 模型目录不存在: {pkuseg_dir}")
        print("提示: 在有网络的机器上运行 package_models.py 会自动下载并打包 pkuseg 模型")


class TTSRequest(BaseModel):
    """文本转语音请求模型"""
    text: str
    language: Optional[str] = "en"  # 语言代码，默认英文
    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 1000
    repetition_penalty: Optional[float] = 1.2
    model_type: Optional[str] = "turbo"  # "turbo" 或 "multilingual"


@app.on_event("startup")
async def load_models():
    """启动时加载模型"""
    global turbo_model, multilingual_model
    
    print(f"正在加载模型，设备: {DEVICE}")
    print(f"使用本地模型: {USE_LOCAL_MODELS}")
    print(f"模型目录: {MODELS_DIR}")
    
    try:
        if USE_LOCAL_MODELS:
            # 使用本地模型
            turbo_model_path = MODELS_DIR / "chatterbox-turbo"
            multilingual_model_path = MODELS_DIR / "chatterbox"
            
            if turbo_model_path.exists():
                print("加载 Turbo 模型（本地）...")
                turbo_model = ChatterboxTurboTTS.from_local(turbo_model_path, device=DEVICE)
                print("Turbo 模型加载完成")
            else:
                print(f"警告: Turbo 模型目录不存在: {turbo_model_path}")
            
            if multilingual_model_path.exists():
                print("加载多语言模型（本地）...")
                multilingual_model = ChatterboxMultilingualTTS.from_local(
                    multilingual_model_path, device=DEVICE
                )
                print("多语言模型加载完成")
            else:
                print(f"警告: 多语言模型目录不存在: {multilingual_model_path}")
        else:
            # 从网络下载模型
            print("加载 Turbo 模型（在线）...")
            turbo_model = ChatterboxTurboTTS.from_pretrained(device=DEVICE)
            print("Turbo 模型加载完成")
            
            print("加载多语言模型（在线）...")
            multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=DEVICE)
            print("多语言模型加载完成")
        
        print("所有模型加载完成！")
    except Exception as e:
        print(f"模型加载失败: {e}")
        raise


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "name": "Chatterbox TTS API",
        "version": "1.0.0",
        "status": "running",
        "device": DEVICE,
        "models_loaded": {
            "turbo": turbo_model is not None,
            "multilingual": multilingual_model is not None
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "device": DEVICE,
        "models_loaded": {
            "turbo": turbo_model is not None,
            "multilingual": multilingual_model is not None
        }
    }


@app.post("/api/v1/tts")
async def text_to_speech(
    background_tasks: BackgroundTasks,
    text: str = Form(..., description="要转换的文本"),
    audio_file: UploadFile = File(..., description="语音样本文件（用于声音克隆）"),
    language: str = Form("en", description="语言代码（仅多语言模型）"),
    model_type: str = Form("turbo", description="模型类型: turbo 或 multilingual"),
    temperature: float = Form(0.8, description="温度参数，控制随机性"),
    top_p: float = Form(0.95, description="Top-p 采样参数"),
    top_k: int = Form(1000, description="Top-k 采样参数"),
    repetition_penalty: float = Form(1.2, description="重复惩罚参数"),
):
    """
    文本转语音接口
    
    参数:
    - text: 要转换的文本
    - audio_file: 语音样本文件（用于声音克隆）
    - language: 语言代码（仅多语言模型需要，如 "zh", "en", "fr" 等）
    - model_type: 模型类型，"turbo" 或 "multilingual"
    - temperature: 温度参数（0.05-2.0）
    - top_p: Top-p 采样（0.0-1.0）
    - top_k: Top-k 采样（0-1000）
    - repetition_penalty: 重复惩罚（1.0-2.0）
    
    返回:
    - 生成的音频文件（WAV 格式）
    """
    
    # 验证文本
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="文本长度不能超过 1000 个字符")
    
    # 验证模型类型
    if model_type not in ["turbo", "multilingual"]:
        raise HTTPException(status_code=400, detail="model_type 必须是 'turbo' 或 'multilingual'")
    
    # 选择模型
    if model_type == "turbo":
        model = turbo_model
        if model is None:
            raise HTTPException(status_code=503, detail="Turbo 模型未加载")
    else:
        model = multilingual_model
        if model is None:
            raise HTTPException(status_code=503, detail="多语言模型未加载")
    
    # 保存上传的音频文件到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        try:
            # 读取上传的文件
            content = await audio_file.read()
            tmp_audio.write(content)
            tmp_audio_path = tmp_audio.name
            
            # 验证音频文件
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="音频文件不能为空")
            
            # 生成语音
            try:
                if model_type == "multilingual":
                    # 多语言模型需要 language_id 参数
                    wav = model.generate(
                        text,
                        language_id=language,
                        audio_prompt_path=tmp_audio_path,
                        temperature=temperature,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty,
                    )
                else:
                    # Turbo 模型
                    wav = model.generate(
                        text,
                        audio_prompt_path=tmp_audio_path,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        repetition_penalty=repetition_penalty,
                    )
                
                # 保存生成的音频到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_output:
                    ta.save(tmp_output.name, wav, model.sr)
                    output_path = tmp_output.name
                
                # 定义清理函数，在响应后删除临时文件
                def cleanup_file(file_path: str):
                    try:
                        if os.path.exists(file_path):
                            os.unlink(file_path)
                    except Exception:
                        pass
                
                # 添加后台任务，在响应发送后清理文件
                background_tasks.add_task(cleanup_file, output_path)
                
                # 返回音频文件
                return FileResponse(
                    output_path,
                    media_type="audio/wav",
                    filename="output.wav"
                )
            
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"语音生成失败: {str(e)}")
        
        finally:
            # 清理临时音频文件
            if os.path.exists(tmp_audio_path):
                os.unlink(tmp_audio_path)


@app.post("/api/v1/tts/json")
async def text_to_speech_json(
    background_tasks: BackgroundTasks,
    request: TTSRequest, 
    audio_file: UploadFile = File(...)
):
    """
    文本转语音接口（JSON 格式请求）
    
    使用 JSON 格式传递参数，音频文件通过 multipart/form-data 上传
    """
    return await text_to_speech(
        background_tasks=background_tasks,
        text=request.text,
        audio_file=audio_file,
        language=request.language or "en",
        model_type=request.model_type or "turbo",
        temperature=request.temperature or 0.8,
        top_p=request.top_p or 0.95,
        top_k=request.top_k or 1000,
        repetition_penalty=request.repetition_penalty or 1.2,
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=False,  # 生产环境关闭自动重载
    )

