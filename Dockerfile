# syntax=docker.m.daocloud.io/docker/dockerfile:1
# 构建阶段：安装编译工具和依赖
FROM --platform=linux/amd64 docker.m.daocloud.io/python:3.11-slim AS build

# 安装构建时需要的依赖（编译工具）
# 注意：build-essential 包含 gcc, g++, make 等，会安装很多依赖
# 但这些只在构建时需要，不会进入最终镜像
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层）
COPY pyproject.toml requirements-api.txt /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-api.txt

# 复制项目文件
COPY . /app/

# 安装项目本身
RUN pip install --no-cache-dir -e .

# 运行阶段：只保留运行时需要的依赖
FROM --platform=linux/amd64 docker.m.daocloud.io/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEVICE=cpu \
    USE_LOCAL_MODELS=false \
    MODELS_DIR=/app/models \
    PKUSEG_HOME=/app/models/pkuseg \
    PORT=8000 \
    HOST=0.0.0.0

# 只安装运行时需要的系统依赖
# - curl: 用于健康检查
# - libsndfile1: librosa 需要，用于读取音频文件
# 移除了：
# - build-essential: 只在构建时需要，运行时不需要
# - git: 不需要，因为不从 git 安装包
# - ffmpeg: 不需要，librosa 可以处理常见音频格式
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的 Python 包
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# 复制项目文件
COPY . /app/

# 创建模型目录（用于离线部署）
RUN mkdir -p /app/models

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "api_server.py"]
