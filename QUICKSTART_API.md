# API 快速开始指南

## 🚀 快速部署

### 方式 1: 使用 Docker（推荐）

```bash
# 1. 准备模型文件（如果有本地模型，用于离线部署）
python package_models.py
tar -czf models.tar.gz models/

# 2. 在服务器上解压模型（如果使用离线模式）
tar -xzf models.tar.gz

# 3. 构建镜像
docker build -t chatterbox-api .

# 4. 运行容器（在线模式，自动下载模型）
docker run -d -p 8000:8000 \
  --name chatterbox-api \
  -e USE_LOCAL_MODELS=false \
  chatterbox-api

# 或运行容器（离线模式，使用本地模型）
docker run -d -p 8000:8000 \
  --name chatterbox-api \
  -e USE_LOCAL_MODELS=true \
  -v $(pwd)/models:/app/models:ro \
  chatterbox-api

# 5. 查看日志
docker logs -f chatterbox-api

# 6. 测试 API
curl http://localhost:8000/health
```

### 方式 2: 直接运行

```bash
# 1. 安装依赖
pip install -r requirements-api.txt
pip install -e .

# 2. 启动服务器
python api_server.py
```

## 📝 使用示例

### Python 示例

```python
import requests

# 准备请求
with open("zh01.wav", "rb") as f:
    files = {"audio_file": ("zh01.wav", f, "audio/wav")}
    data = {
        "text": "你好，今天真是个好天气。",
        "model_type": "multilingual",
        "language": "zh",
        "temperature": 0.8,
    }
    
    # 发送请求
    response = requests.post(
        "http://localhost:8000/api/v1/tts",
        files=files,
        data=data
    )
    
    # 保存结果
    if response.status_code == 200:
        with open("output.wav", "wb") as out:
            out.write(response.content)
        print("✅ 成功生成音频！")
    else:
        print(f"❌ 错误: {response.text}")
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/tts" \
  -F "text=你好，今天真是个好天气。" \
  -F "audio_file=@zh01.wav" \
  -F "model_type=multilingual" \
  -F "language=zh" \
  --output output.wav
```

### 使用测试脚本

```bash
python test_api.py zh01.wav "你好，世界" multilingual zh
```

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEVICE` | 计算设备：`cpu` 或 `cuda` | `cpu` |
| `USE_LOCAL_MODELS` | 是否使用本地模型 | `false` |
| `MODELS_DIR` | 本地模型目录 | `./models` |
| `PORT` | 服务端口 | `8000` |
| `HOST` | 服务主机 | `0.0.0.0` |

### Docker 运行参数

使用环境变量配置 Docker 容器：

```bash
docker run -d -p 8000:8000 \
  --name chatterbox-api \
  -e DEVICE=cuda \              # 如果有 GPU
  -e USE_LOCAL_MODELS=true \
  -e MODELS_DIR=/app/models \
  -v $(pwd)/models:/app/models:ro \
  chatterbox-api
```

## 📚 更多文档

详细 API 文档请参考 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

