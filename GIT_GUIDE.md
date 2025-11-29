# TimeValue Git 仓库维护指南

## 📋 仓库信息

- **仓库地址**: https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git
- **平台**: 阿里云 Codeup
- **主分支**: main

---

## 🚀 快速开始

### Windows用户

双击运行 `git_push.bat` 即可完成以下操作：
1. 初始化Git仓库（如果未初始化）
2. 配置远程仓库地址
3. 添加所有更改到暂存区
4. 提交代码
5. 推送到阿里云Codeup

### Linux/Mac用户

```bash
chmod +x git_push.sh
./git_push.sh
```

---

## 🔧 首次配置

### 1. 安装Git

**Windows:**
- 下载地址: https://git-scm.com/download/win
- 安装后重启命令行

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install git
```

### 2. 配置Git用户信息

```bash
# 配置用户名
git config --global user.name "你的名字"

# 配置邮箱
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

### 3. 配置阿里云Codeup凭据

#### 方式A: HTTPS访问令牌（推荐）

1. 访问阿里云Codeup个人设置
   https://codeup.aliyun.com/settings/personal_access_tokens

2. 创建个人访问令牌
   - 名称: TimeValue Access Token
   - 权限: 选择 `api`
   - 点击创建

3. 复制生成的令牌

4. 推送时使用令牌作为密码
   ```
   用户名: 你的阿里云账号
   密码: 刚才复制的访问令牌
   ```

#### 方式B: SSH密钥

1. 生成SSH密钥
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
   ```

2. 查看公钥
   ```bash
   # Windows Git Bash / Linux / Mac
   cat ~/.ssh/id_rsa.pub
   ```

3. 添加到Codeup
   - 访问: https://codeup.aliyun.com/settings/ssh_keys
   - 点击"新增SSH公钥"
   - 粘贴公钥内容

4. 修改远程仓库为SSH地址
   ```bash
   git remote set-url origin git@codeup.aliyun.com:670f88349d3c82efe37b1105/timevalue.git
   ```

---

## 📝 日常使用

### 推送代码到远程仓库

**使用脚本（推荐）:**
```bash
# Windows
git_push.bat

# Linux/Mac
./git_push.sh
```

**手动操作:**
```bash
# 1. 查看状态
git status

# 2. 添加文件
git add .

# 3. 提交
git commit -m "你的提交信息"

# 4. 推送
git push origin main
```

### 拉取最新代码

```bash
# 拉取并合并
git pull origin main

# 拉取并变基（推荐）
git pull origin main --rebase
```

### 查看提交历史

```bash
# 查看提交日志
git log

# 查看简洁日志
git log --oneline

# 查看图形化日志
git log --graph --oneline --all
```

### 查看差异

```bash
# 查看工作区变更
git diff

# 查看暂存区变更
git diff --staged

# 查看与远程的差异
git diff origin/main
```

---

## 🌳 分支管理

### 创建分支

```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 或使用新命令
git switch -c feature/new-feature
```

### 切换分支

```bash
# 切换到已存在的分支
git checkout main

# 或使用新命令
git switch main
```

### 合并分支

```bash
# 切换到主分支
git checkout main

# 合并功能分支
git merge feature/new-feature
```

### 删除分支

```bash
# 删除本地分支
git branch -d feature/new-feature

# 强制删除
git branch -D feature/new-feature

# 删除远程分支
git push origin --delete feature/new-feature
```

---

## 🔄 常见工作流

### 功能开发流程

```bash
# 1. 从main分支创建功能分支
git checkout main
git pull origin main
git checkout -b feature/dashboard-update

# 2. 开发功能，多次提交
git add .
git commit -m "feat: 更新仪表盘UI"

# 3. 推送功能分支
git push origin feature/dashboard-update

# 4. 合并到主分支
git checkout main
git merge feature/dashboard-update
git push origin main

# 5. 删除功能分支
git branch -d feature/dashboard-update
```

### 修复线上Bug流程

```bash
# 1. 从main创建修复分支
git checkout main
git checkout -b hotfix/fix-login-issue

# 2. 修复并提交
git add .
git commit -m "fix: 修复登录问题"

# 3. 推送并合并
git push origin hotfix/fix-login-issue
git checkout main
git merge hotfix/fix-login-issue
git push origin main
```

---

## 📦 提交规范

建议使用语义化提交信息：

```bash
# 新功能
git commit -m "feat: 添加资产收益图表"

# Bug修复
git commit -m "fix: 修复仪表盘数据显示问题"

# 文档更新
git commit -m "docs: 更新部署文档"

# 样式修改
git commit -m "style: 优化仪表盘样式"

# 代码重构
git commit -m "refactor: 重构资产管理模块"

# 性能优化
git commit -m "perf: 优化数据库查询性能"

# 测试相关
git commit -m "test: 添加用户认证测试"

# 构建相关
git commit -m "build: 更新依赖版本"

# 配置相关
git commit -m "chore: 更新生产环境配置"
```

---

## 🛠️ 常见问题

### Q1: 推送被拒绝（remote rejected）

**原因**: 远程分支有更新

**解决**:
```bash
# 先拉取远程更新
git pull origin main --rebase

# 解决冲突后继续
git rebase --continue

# 重新推送
git push origin main
```

### Q2: 忘记提交信息

**解决**:
```bash
# 修改最近一次提交信息
git commit --amend -m "新的提交信息"

# 强制推送（如果已推送到远程）
git push origin main --force
```

### Q3: 撤销本地更改

```bash
# 撤销单个文件
git checkout -- filename

# 撤销所有更改
git checkout .

# 或使用新命令
git restore filename
git restore .
```

### Q4: 撤销已提交的更改

```bash
# 撤销最近一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最近一次提交（不保留更改）
git reset --hard HEAD~1

# 创建反向提交
git revert HEAD
```

### Q5: 查看大文件

```bash
# 查找大于1MB的文件
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort --numeric-sort --key=2 | \
  tail -n 10
```

### Q6: .gitignore不生效

**解决**:
```bash
# 清除缓存
git rm -r --cached .
git add .
git commit -m "chore: 更新gitignore"
```

---

## 🔒 .gitignore 说明

项目已配置 `.gitignore`，以下文件/目录不会被提交：

- `venv/` - Python虚拟环境
- `node_modules/` - Node.js依赖
- `*.db` - 数据库文件
- `.env` - 环境变量文件
- `logs/` - 日志文件
- `data/` - 数据目录
- `__pycache__/` - Python缓存
- `dist/` - 构建输出

---

## 📊 仓库统计

```bash
# 查看代码统计
git log --shortstat --author="你的名字" | grep "files changed" | \
  awk '{files+=$1; inserted+=$4; deleted+=$6} END \
  {print "文件数:", files, "新增:", inserted, "删除:", deleted}'

# 查看贡献者排名
git shortlog -sn

# 查看文件修改频率
git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -10
```

---

## 🌐 Web界面访问

访问阿里云Codeup仓库：
https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue

可以进行：
- 查看代码
- 创建分支
- 提交记录
- 合并请求
- 代码审查
- Issue管理

---

## 📞 获取帮助

- Git官方文档: https://git-scm.com/doc
- 阿里云Codeup帮助: https://help.aliyun.com/product/153741.html
- Pro Git电子书: https://git-scm.com/book/zh/v2

---

**Powered by 孚普科技（北京）有限公司**  
🤖 AI驱动的MVP快速迭代解决方案

