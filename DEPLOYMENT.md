# 离线部署指南

本指南说明如何将 Chatterbox 项目部署到没有网络的服务器上。

## 步骤 1: 在本地打包模型文件

在有网络的机器上运行打包脚本：

```bash
python package_models.py
```

这个脚本会：
1. 查找 Hugging Face 缓存目录中的模型文件
2. 将模型文件复制到 `./models/` 目录下
3. 如果缓存中没有，会尝试下载

打包完成后，你会看到以下目录结构：

```
models/
├── chatterbox-turbo/      # Turbo 模型文件
└── chatterbox/            # 多语言模型文件
```

## 步骤 2: 打包模型文件

将模型目录打包：

```bash
tar -czf models.tar.gz models/
```

或者使用 zip：

```bash
zip -r models.zip models/
```

## 步骤 3: 传输到目标服务器

使用 scp、rsync 或其他方式将打包文件传输到目标服务器：

```bash
# 使用 scp
scp models.tar.gz user@target-server:/path/to/chatterbox/

# 或使用 rsync
rsync -avz models.tar.gz user@target-server:/path/to/chatterbox/
```

## 步骤 4: 在目标服务器上解压

在目标服务器上解压模型文件：

```bash
cd /path/to/chatterbox
tar -xzf models.tar.gz
```

确保解压后的目录结构是：

```
chatterbox/
├── models/
│   ├── chatterbox-turbo/
│   └── chatterbox/
├── src/
├── Test.py
└── ...
```

## 步骤 5: 修改代码使用本地模型

有两种方式：

### 方式 1: 使用离线版本脚本

直接使用 `Test_offline.py`：

```bash
python Test_offline.py
```

### 方式 2: 修改现有代码

修改 `Test.py`，将 `from_pretrained()` 改为 `from_local()`：

```python
from pathlib import Path

# 原来的代码
# model = ChatterboxTurboTTS.from_pretrained(device="cpu")
# multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")

# 改为使用本地模型
MODELS_DIR = Path("./models")
model = ChatterboxTurboTTS.from_local(MODELS_DIR / "chatterbox-turbo", device="cpu")
multilingual_model = ChatterboxMultilingualTTS.from_local(MODELS_DIR / "chatterbox", device="cpu")
```

## 模型文件说明

### Turbo 模型 (chatterbox-turbo)
需要的文件：
- `*.safetensors` - 模型权重文件
- `*.json` - 配置文件
- `*.txt` - 文本文件
- `*.pt` - PyTorch 模型文件
- `*.model` - 其他模型文件

### 多语言模型 (chatterbox)
需要的文件：
- `ve.pt` - 语音编码器
- `t3_mtl23ls_v2.safetensors` - T3 模型
- `s3gen.pt` - S3Gen 模型
- `grapheme_mtl_merged_expanded_v1.json` - 分词器配置
- `conds.pt` - 条件文件（可选）
- `Cangjie5_TC.json` - 中文分词器配置

## 验证部署

运行测试脚本确认一切正常：

```bash
python Test_offline.py
```

如果一切正常，应该会生成 `test-chinese.wav` 文件。

## 常见问题

### Q: 模型文件很大，传输很慢怎么办？

A: 模型文件确实比较大（可能几GB），可以考虑：
- 使用压缩率更高的压缩方式（如 7z）
- 分批传输
- 使用更快的传输方式（如内网传输）

### Q: 找不到模型文件？

A: 检查以下几点：
1. 确认 `models/` 目录存在且包含模型文件
2. 确认路径正确（使用绝对路径或相对路径）
3. 确认文件权限正确

### Q: 内存不足？

A: 模型加载需要一定内存，如果内存不足：
- 使用 CPU 模式（device="cpu"）
- 确保有足够的可用内存（建议至少 8GB）

## 注意事项

1. **Python 环境**: 确保目标服务器上的 Python 环境和依赖包版本与本地一致
2. **文件权限**: 确保模型文件有读取权限
3. **路径问题**: 使用绝对路径可以避免路径问题
4. **依赖包**: 确保所有 Python 依赖包都已安装（不需要网络连接，但需要预先安装）

