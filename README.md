# Chatterbox Deploy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

基于 [Resemble AI 的 Chatterbox](https://github.com/resemble-ai/chatterbox) 项目，增加了离线部署和 API 服务功能的企业级部署解决方案。

## 📋 项目简介

Chatterbox Deploy 是基于 [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) 的增强版本，专门为企业级部署场景设计。本项目在保留原始项目所有功能的基础上，新增了以下特性：

- ✅ **离线部署支持** - 支持完全离线的模型部署，无需网络连接
- ✅ **RESTful API 服务** - 提供标准化的 HTTP API 接口
- ✅ **Docker 容器化** - 开箱即用的 Docker 镜像
- ✅ **模型打包工具** - 自动化模型文件打包和迁移
- ✅ **完整文档** - 详细的部署和使用文档

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/miaoyibo/chatterbox-deploy.git
cd chatterbox-deploy

# 安装依赖
pip install -r requirements-api.txt
pip install -e .
```

### 启动 API 服务

```bash
# 直接运行
python api_server.py

# 或使用 Docker
docker build -t chatterbox-api .
docker run -p 8000:8000 chatterbox-api
```

详细使用说明请参考：
- [API 文档](./API_DOCUMENTATION.md)
- [快速开始指南](./QUICKSTART_API.md)
- [离线部署指南](./DEPLOYMENT.md)

## 🎯 主要功能

### 1. 离线部署

支持在无网络环境下部署和运行，适合内网环境或安全要求高的场景。

```bash
# 打包模型文件
python package_models.py

# 在离线服务器上使用
python Test_offline.py
```

### 2. RESTful API

提供标准的 HTTP API 接口，支持多种编程语言调用。

```bash
curl -X POST "http://localhost:8000/api/v1/tts" \
  -F "text=你好，世界" \
  -F "audio_file=@reference.wav" \
  -F "model_type=multilingual" \
  -F "language=zh" \
  --output output.wav
```

### 3. Docker 部署

一键部署，无需配置环境。

```bash
docker build -t chatterbox-api .
docker run -d -p 8000:8000 \
  -e USE_LOCAL_MODELS=true \
  -v $(pwd)/models:/app/models:ro \
  chatterbox-api
```

## 📚 文档

- [API 文档](./API_DOCUMENTATION.md) - 完整的 API 接口文档
- [快速开始](./QUICKSTART_API.md) - 快速上手指南
- [离线部署指南](./DEPLOYMENT.md) - 离线部署详细说明
- [项目价值说明](./PROJECT_VALUE.md) - 项目核心价值和技术特点

## 🛠️ 技术栈

- **基础框架**: [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) by Resemble AI
- **API 框架**: FastAPI
- **容器化**: Docker
- **深度学习**: PyTorch
- **语音处理**: Librosa, TorchAudio

## 📄 License

本项目采用 [MIT License](./LICENSE)。

本项目基于 [Resemble AI 的 Chatterbox](https://github.com/resemble-ai/chatterbox) 项目（同样采用 MIT License）开发。

## 🙏 致谢

本项目基于以下优秀的开源项目：

- **[Chatterbox TTS](https://github.com/resemble-ai/chatterbox)** by [Resemble AI](https://resemble.ai) - 原始 TTS 模型和核心功能
- [Cosyvoice](https://github.com/FunAudioLLM/CosyVoice) - 语音合成技术参考
- [S3Tokenizer](https://github.com/xingchensong/S3Tokenizer) - 语音标记化技术
- [Llama 3](https://github.com/meta-llama/llama3) - 语言模型基础

特别感谢 Resemble AI 团队提供的优秀开源项目。

## 🔗 相关链接

- **原始项目**: [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox)
- **官方演示**: [Chatterbox Demo](https://resemble-ai.github.io/chatterbox_demopage/)
- **Hugging Face**: [Chatterbox Models](https://huggingface.co/ResembleAI)

## 📝 更新日志

### v1.0.0
- ✨ 新增离线部署支持
- ✨ 新增 RESTful API 服务
- ✨ 新增 Docker 容器化支持
- ✨ 新增模型打包工具
- 📚 完善文档和示例代码

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本项目仅供学习和研究使用。请遵守相关法律法规，不要用于非法用途。

---

**Note**: 本项目是对 [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) 的增强和扩展，保留了原始项目的所有核心功能，并添加了企业级部署所需的工具和文档。
