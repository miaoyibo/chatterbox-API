# 上传项目到 GitHub 指南

## 步骤 1: 准备文件

确保 `.gitignore` 文件已更新，忽略不需要的文件（如模型文件、临时文件等）。

## 步骤 2: 添加所有文件到 Git

```bash
# 添加所有文件（.gitignore 会自动过滤）
git add .

# 查看将要提交的文件
git status
```

## 步骤 3: 提交更改

```bash
# 提交所有更改
git commit -m "Initial commit: Add Chatterbox TTS API server and deployment files"
```

## 步骤 4: 添加新的远程仓库

如果你要更换远程仓库：

```bash
# 删除旧的远程仓库（如果需要）
git remote remove origin

# 添加新的远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 或者使用 SSH（如果你配置了 SSH key）
# git remote add origin git@github.com:你的用户名/你的仓库名.git
```

## 步骤 5: 推送到 GitHub

```bash
# 推送到主分支
git push -u origin main

# 如果遇到错误，可能需要强制推送（谨慎使用）
# git push -u origin main --force
```

## 完整命令示例

假设你的新仓库地址是 `https://github.com/你的用户名/你的仓库名.git`：

```bash
# 1. 添加所有文件
git add .

# 2. 提交
git commit -m "Initial commit: Add Chatterbox TTS API server and deployment files"

# 3. 更换远程仓库（如果需要）
git remote remove origin
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 4. 推送
git push -u origin main
```

## 注意事项

1. **模型文件**: `models/` 目录已被添加到 `.gitignore`，因为模型文件通常很大（几GB），不应该提交到 Git。如果需要，可以使用 Git LFS 或单独存储。

2. **敏感信息**: 确保不要提交包含 API 密钥、密码等敏感信息的文件。

3. **大文件**: 如果某些文件很大，考虑使用 Git LFS（Large File Storage）。

4. **分支名称**: 如果 GitHub 仓库默认分支是 `master` 而不是 `main`，使用：
   ```bash
   git push -u origin main:master
   ```

