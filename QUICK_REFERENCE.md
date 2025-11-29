# TimeValue 快速操作指南

## 🚀 快速命令

### Git操作

```bash
# Windows - 推送代码到Git
git_push.bat

# Windows - 首次配置Git
git_init.bat

# Linux/服务器 - 推送代码
./git_push.sh
```

### 生产环境部署

```bash
# 一键部署（首次）
./deploy.sh

# 启动服务
./start_production.sh

# 停止服务
./stop_production.sh

# 查看状态
./check_status.sh
```

---

## 📦 项目文件说明

### 部署相关

| 文件 | 用途 | 平台 |
|------|------|------|
| `deploy.sh` | 一键部署脚本 | Linux |
| `start_production.sh` | 启动生产服务 | Linux |
| `stop_production.sh` | 停止生产服务 | Linux |
| `check_status.sh` | 检查服务状态 | Linux |
| `systemd-service-example.txt` | Systemd服务配置 | Linux |

### Git维护相关

| 文件 | 用途 | 平台 |
|------|------|------|
| `git_push.bat` | 推送代码脚本 | Windows |
| `git_push.sh` | 推送代码脚本 | Linux |
| `git_init.bat` | 初始化Git | Windows |
| `.gitignore` | Git忽略文件配置 | 通用 |

### 文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目说明 |
| `QUICKSTART.md` | 快速开始 |
| `DEPLOY_GUIDE.md` | 部署指南 |
| `WINDOWS_DEPLOY_GUIDE.md` | Windows部署指南 |
| `GIT_GUIDE.md` | Git使用指南 |
| `NGINX_CONFIG_GUIDE.md` | Nginx配置指南 |

---

## 🌐 重要链接

- **Git仓库**: https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue
- **访问令牌管理**: https://codeup.aliyun.com/settings/personal_access_tokens
- **SSH密钥管理**: https://codeup.aliyun.com/settings/ssh_keys

---

## 💡 常用场景

### 场景1: 本地开发完成，推送到Git

```bash
# Windows
git_push.bat

# 或手动操作
git add .
git commit -m "feat: 你的更新内容"
git push origin main
```

### 场景2: 首次部署到阿里云服务器

```bash
# 1. 上传项目
scp -r timevalue root@your-server-ip:/root/

# 2. 连接服务器
ssh root@your-server-ip

# 3. 部署
cd /root/timevalue
chmod +x *.sh
./deploy.sh
./start_production.sh
```

### 场景3: 更新服务器代码

```bash
# 在服务器上执行
cd /root/timevalue
./stop_production.sh
git pull origin main
./start_production.sh --install
```

### 场景4: 查看服务运行状态

```bash
./check_status.sh
```

---

## 🔧 默认配置

- **后端端口**: 5000
- **前端端口**: 3000
- **默认管理员**: admin / admin123
- **数据库**: SQLite (data/timevalue.db)
- **日志目录**: logs/
- **主分支**: main

---

## 📞 获取帮助

遇到问题时查看：
1. 服务日志: `tail -f logs/backend.log`
2. 服务状态: `./check_status.sh`
3. 详细文档: `DEPLOY_GUIDE.md`、`GIT_GUIDE.md`

---

**Powered by 孚普科技（北京）有限公司**  
🤖 AI驱动的MVP快速迭代解决方案
