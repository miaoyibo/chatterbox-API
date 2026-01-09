# Chatterbox TTS API 文档

## 概述

Chatterbox TTS API 提供了零样本语音克隆和文本转语音的 RESTful API 接口。

## 快速开始

### 1. 启动 API 服务器

#### 方式 1: 直接运行
```bash
python api_server.py
```

#### 方式 2: 使用 Docker（推荐）
```bash
# 构建镜像
docker build -t chatterbox-api .

# 运行容器（在线模式，自动下载模型）
docker run -d -p 8000:8000 \
  --name chatterbox-api \
  -e DEVICE=cpu \
  -e USE_LOCAL_MODELS=false \
  chatterbox-api

# 或运行容器（离线模式，使用本地模型）
docker run -d -p 8055:8000 \
  --name chatterbox-api \
  -e DEVICE=cpu \
  -e USE_LOCAL_MODELS=true \
  -v $(pwd)/models:/app/models:ro \
  chatterbox-api
```

### 2. 测试 API

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试 TTS（需要音频文件）
python test_api.py zh01.wav "你好，世界" multilingual zh
```

## API 接口

### 1. 健康检查

**GET** `/health`

检查 API 服务器和模型状态。

**响应示例:**
```json
{
  "status": "healthy",
  "device": "cpu",
  "models_loaded": {
    "turbo": true,
    "multilingual": true
  }
}
```

### 2. 文本转语音

**POST** `/api/v1/tts`

将文本转换为语音，使用提供的音频样本进行声音克隆。

**请求格式:** `multipart/form-data`

**参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | 是 | 要转换的文本（最大 1000 字符） |
| `audio_file` | file | 是 | 语音样本文件（用于声音克隆，WAV 格式） |
| `model_type` | string | 否 | 模型类型：`turbo` 或 `multilingual`（默认：`turbo`） |
| `language` | string | 否 | 语言代码（仅多语言模型需要，如 `zh`, `en`, `fr` 等，默认：`en`） |
| `temperature` | float | 否 | 温度参数，控制随机性（0.05-2.0，默认：0.8） |
| `top_p` | float | 否 | Top-p 采样参数（0.0-1.0，默认：0.95） |
| `top_k` | int | 否 | Top-k 采样参数（0-1000，默认：1000） |
| `repetition_penalty` | float | 否 | 重复惩罚参数（1.0-2.0，默认：1.2） |

**响应:**

成功时返回 WAV 格式的音频文件。

**示例请求 (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/tts" \
  -F "text=你好，今天真是个好天气。" \
  -F "audio_file=@zh01.wav" \
  -F "model_type=multilingual" \
  -F "language=zh" \
  -F "temperature=0.8" \
  --output output.wav
```

**示例请求 (Python):**
```python
import requests

with open("zh01.wav", "rb") as f:
    files = {"audio_file": ("zh01.wav", f, "audio/wav")}
    data = {
        "text": "你好，今天真是个好天气。",
        "model_type": "multilingual",
        "language": "zh",
        "temperature": 0.8,
    }
    response = requests.post("http://localhost:8000/api/v1/tts", files=files, data=data)
    
    if response.status_code == 200:
        with open("output.wav", "wb") as out:
            out.write(response.content)
        print("音频已保存到 output.wav")
```

**示例请求 (JavaScript):**
```javascript
const formData = new FormData();
formData.append('text', '你好，今天真是个好天气。');
formData.append('audio_file', audioFileInput.files[0]);
formData.append('model_type', 'multilingual');
formData.append('language', 'zh');
formData.append('temperature', '0.8');

fetch('http://localhost:8000/api/v1/tts', {
    method: 'POST',
    body: formData
})
.then(response => response.blob())
.then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.wav';
    a.click();
});
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEVICE` | 计算设备：`cpu` 或 `cuda` | `cpu` |
| `USE_LOCAL_MODELS` | 是否使用本地模型：`true` 或 `false` | `false` |
| `MODELS_DIR` | 本地模型目录路径 | `./models` |
| `PORT` | API 服务器端口 | `8000` |
| `HOST` | API 服务器主机 | `0.0.0.0` |
| `HF_TOKEN` | Hugging Face 访问令牌（可选） | - |

## 部署说明

### 离线部署（使用本地模型）

1. **准备模型文件**
   ```bash
   # 在有网络的机器上运行
   python package_models.py
   tar -czf models.tar.gz models/
   ```

2. **传输到服务器**
   ```bash
   scp models.tar.gz user@server:/path/to/chatterbox/
   ```

3. **在服务器上解压**
   ```bash
   cd /path/to/chatterbox
   tar -xzf models.tar.gz
   ```

4. **使用 Docker 部署**
   ```bash
   # 构建镜像
   docker build -t chatterbox-api .
   
   # 运行容器
   docker run -d \
     --name chatterbox-api \
     -p 8000:8000 \
     -e USE_LOCAL_MODELS=true \
     -e MODELS_DIR=/app/models \
     -v $(pwd)/models:/app/models:ro \
     chatterbox-api
   ```

### 在线部署（自动下载模型）

```bash
# 构建镜像
docker build -t chatterbox-api .

# 运行容器
docker run -d \
  --name chatterbox-api \
  -p 8000:8000 \
  -e USE_LOCAL_MODELS=false \
  -e HF_TOKEN=your_token_here \
  chatterbox-api
```

## 错误处理

API 可能返回以下错误：

- **400 Bad Request**: 请求参数错误（如文本为空、文件格式错误等）
- **503 Service Unavailable**: 模型未加载
- **500 Internal Server Error**: 服务器内部错误（如语音生成失败）

**错误响应格式:**
```json
{
  "detail": "错误描述信息"
}
```

## 性能优化

1. **使用 GPU**: 设置 `DEVICE=cuda` 可以显著提升生成速度
2. **模型预热**: 首次请求会较慢，因为需要加载模型
3. **并发控制**: 建议使用负载均衡器控制并发请求数
4. **缓存**: 对于相同文本和音频样本，可以考虑添加缓存层

## 安全建议

1. **API 认证**: 在生产环境中添加 API 密钥或 OAuth 认证
2. **速率限制**: 使用 Nginx 或 API 网关限制请求频率
3. **文件大小限制**: 限制上传音频文件的大小
4. **HTTPS**: 使用 HTTPS 加密传输

## 示例代码

完整示例请参考 `test_api.py` 文件。

## 支持的语言

多语言模型支持以下语言：

- `zh` - 中文
- `en` - 英语
- `fr` - 法语
- `de` - 德语
- `es` - 西班牙语
- `it` - 意大利语
- `ja` - 日语
- `ko` - 韩语
- 等等...（共 23+ 种语言）

完整列表请参考项目 README。

