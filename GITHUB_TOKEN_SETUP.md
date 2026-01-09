# GitHub 推送设置指南

## 重要提示

GitHub 从 2021 年 8 月开始**不再支持密码认证**，必须使用 **Personal Access Token (PAT)**。

## 创建 Personal Access Token 步骤

### 1. 访问 GitHub Token 设置页面

打开浏览器，访问：
```
https://github.com/settings/tokens
```

或者：
1. 登录 GitHub
2. 点击右上角头像 → **Settings**
3. 左侧菜单找到 **Developer settings**
4. 点击 **Personal access tokens** → **Tokens (classic)**

### 2. 生成新 Token

1. 点击 **Generate new token** → **Generate new token (classic)**
2. 输入 Token 名称（例如：`chatterbox-deploy`）
3. 选择过期时间（建议选择 90 天或自定义）
4. **勾选权限**（至少需要）：
   - ✅ `repo` (完整仓库访问权限)
     - ✅ `repo:status`
     - ✅ `repo_deployment`
     - ✅ `public_repo`
     - ✅ `repo:invite`
     - ✅ `security_events`
5. 点击 **Generate token** 按钮

### 3. 复制 Token

**重要**：Token 只会显示一次，请立即复制并保存！

Token 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 使用 Token 推送代码

### 方法 1: 在 URL 中包含 Token（推荐）

```bash
# 替换 YOUR_TOKEN 为你的实际 token
git remote set-url origin https://YOUR_TOKEN@github.com/miaoyibo/chatterbox-deploy.git

# 推送代码
git push -u origin main
```

### 方法 2: 使用 Git Credential Helper

```bash
# 配置 credential helper（macOS）
git config --global credential.helper osxkeychain

# 推送代码（会提示输入用户名和密码）
git push -u origin main
# 用户名：miaoyibo@yeah.net
# 密码：粘贴你的 token（不是账户密码）
```

### 方法 3: 使用 GitHub CLI

```bash
# 安装 GitHub CLI（如果还没有）
brew install gh

# 登录
gh auth login

# 推送代码
git push -u origin main
```

## 快速命令（使用 Token）

创建好 Token 后，运行：

```bash
# 替换 ghp_xxxxxxxxxxxx 为你的实际 token
git remote set-url origin https://ghp_xxxxxxxxxxxx@github.com/miaoyibo/chatterbox-deploy.git
git push -u origin main
```

## 安全提示

1. **不要将 Token 提交到 Git 仓库**
2. **不要在公共场合分享 Token**
3. **Token 过期后需要重新生成**
4. **如果 Token 泄露，立即在 GitHub 设置中撤销它**

## 当前状态

✅ 代码已提交到本地仓库
⏳ 等待推送到 GitHub（需要 Token）

创建好 Token 后，告诉我，我可以帮你完成推送！

