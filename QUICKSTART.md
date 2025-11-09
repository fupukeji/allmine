# TimeValue 快速开始指南

🚀 **Powered by 孚普科技（北京）有限公司**  
🤖 **AI驱动的MVP快速迭代解决方案**

---

## 系统要求

- **操作系统**: 
  - Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+, Alibaba Cloud Linux)
  - Windows 10/11 (开发环境)
- **Python**: 3.8 或更高版本（推荐 3.11+）
- **Node.js**: 16.0 或更高版本（推荐 18.x LTS）
- **内存**: 至少 2GB RAM（推荐 4GB+）
- **磁盘空间**: 至少 2GB 可用空间

---

## 阿里云ECS一键部署（推荐）

### 准备工作

1. **购买阿里云ECS实例**
   - 推荐配置：2核4GB及以上
   - 操作系统：Alibaba Cloud Linux 3 或 Ubuntu 20.04+
   - 带宽：5Mbps及以上

2. **配置安全组**
   - 开放端口：80 (HTTP)、443 (HTTPS)、3000 (前端)、5000 (后端)
   - 如果只使用Nginx代理，只需开放80和443

### 快速部署步骤

#### 1. 连接到ECS服务器
```bash
ssh root@<你的ECS公网IP>
```

#### 2. 下载项目
```bash
# 如果是git仓库
git clone <repository-url>
cd timevalue

# 或者使用wget/scp上传项目文件
```

#### 3. 一键部署
```bash
chmod +x deploy.sh
./deploy.sh
```

**脚本会自动完成：**
- ✅ 检测操作系统类型（Ubuntu/CentOS/Alibaba Cloud Linux）
- ✅ 自动安装Python3和Node.js（如果未安装）
- ✅ 创建数据持久化目录
- ✅ 生成安全密钥
- ✅ 安装后端和前端依赖

#### 4. 配置Nginx权限（首次部署必需）
```bash
sudo bash setup_nginx_permissions.sh
```

**此脚本会自动：**
- ✅ 创建Nginx配置目录
- ✅ 配置应用用户权限
- ✅ 设置sudo权限（允许Web界面管理Nginx）
- ✅ 安装Nginx（如果未安装）
- ✅ 启动Nginx服务

⚠️ **重要**：配置完成后需要重新登录才能使权限生效：
```bash
exit
su - your_username
cd /path/to/timevalue
```

#### 5. 启动生产服务
```bash
chmod +x start_production.sh
./start_production.sh
```

#### 6. 访问应用
- **本地访问**: http://localhost:3000
- **公网访问**: http://<你的ECS公网IP>:3000
- **默认管理员**: admin / admin123

#### 7. 配置Nginx（通过Web界面）
1. 使用管理员账号登录（admin/admin123）
2. 点击左侧菜单 **"Nginx配置"**
3. 创建新的Nginx配置：
   - 设置域名（或使用 `_` 接受所有请求）
   - 配置SSL证书路径（如果有）
   - 调整端口和代理规则
4. 预览配置确认无误
5. 点击 **"应用"** 激活配置

📖 详细说明请参考：[NGINX_CONFIG_GUIDE.md](NGINX_CONFIG_GUIDE.md)

### 服务管理命令

```bash
# 查看服务状态
./check-status.sh

# 停止所有服务
./stop_production.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

---

## Windows本地开发

### 1. 安装依赖
- 安装 [Python 3.8+](https://www.python.org/downloads/)
- 安装 [Node.js 16+](https://nodejs.org/)

### 2. 启动后端
双击运行 `start_backend.bat` 或在命令行执行：
```cmd
start_backend.bat
```

### 3. 启动前端
打开新的命令行窗口：
```cmd
cd frontend
npm install
npm run dev
```

### 4. 访问应用
- 前端：http://localhost:3000
- 后端API：http://localhost:5000

---

## 手动部署

如果自动部署脚本遇到问题，可以按照以下步骤手动部署：

### 后端部署

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件，修改密钥和配置

# 初始化数据库
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from database import db
    db.create_all()
"

# 启动后端
python app.py
```

### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 或者构建生产版本
npm run build
# 然后使用 http-server 或 nginx 提供静态文件服务
```

---

## 生产环境Nginx配置（推荐）

### 1. 安装Nginx
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y nginx

# CentOS/RHEL/Alibaba Cloud Linux
sudo yum install -y nginx
```

### 2. 配置Nginx反向代理
```bash
# 复制配置文件
sudo cp nginx.conf /etc/nginx/conf.d/timevalue.conf

# 编辑配置（修改域名）
sudo nano /etc/nginx/conf.d/timevalue.conf

# 测试配置
sudo nginx -t

# 启动Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 3. 配置SSL证书（推荐）
```bash
# 使用Let's Encrypt免费证书
sudo yum install -y certbot python3-certbot-nginx  # CentOS/Alibaba
# 或
sudo apt install -y certbot python3-certbot-nginx  # Ubuntu

# 自动配置SSL
sudo certbot --nginx -d your-domain.com
```

配置后访问：
- HTTP: http://your-domain.com
- HTTPS: https://your-domain.com

---

## 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :3000

# 修改端口
# 后端：编辑 backend/app.py 中的端口号
# 前端：编辑 frontend/vite.config.js 中的端口配置
```

### 2. 权限问题
```bash
# 确保项目目录有正确的权限
chmod -R 755 /path/to/TimeValue
chown -R $USER:$USER /path/to/TimeValue

# 确保数据目录可写
chmod 755 data/
```

### 3. Python虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf backend/venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Node.js依赖问题
```bash
# 清理并重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 5. 数据库连接问题
```bash
# 检查数据库文件权限
ls -la data/timevalue.db

# 重新初始化数据库
cd backend
source venv/bin/activate
python -c "
from app import create_app
from database import db
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
"
```

---

## 更新和维护

### 更新代码
```bash
# 如果是git仓库
git pull origin main

# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 更新前端依赖并重新构建
cd frontend
npm install
npm run build

# 重启服务
./stop_production.sh
./start_production.sh
```

### 数据备份
```bash
# 备份数据库
cp data/timevalue.db data/backup/timevalue_$(date +%Y%m%d_%H%M%S).db

# 设置定时备份
echo "0 2 * * * cp /path/to/TimeValue/data/timevalue.db /path/to/backup/timevalue_\$(date +\%Y\%m\%d_\%H\%M\%S).db" | crontab -
```

### 日志查看
```bash
# 查看应用日志
tail -f logs/backend.log
tail -f logs/frontend.log

# 查看系统服务日志
sudo journalctl -u timevalue-backend -f
```

---

## 性能优化

### 后端优化
- 使用Gunicorn或uWSGI作为WSGI服务器
- 配置数据库连接池
- 启用Redis缓存

### 前端优化  
- 启用Nginx gzip压缩
- 配置静态资源缓存
- 使用CDN加速

### 数据库优化
- 定期清理过期数据
- 创建必要的索引
- 考虑迁移到PostgreSQL或MySQL

---

## 获取帮助

如果遇到问题，请检查：
1. 系统日志：`/var/log/`
2. 应用日志：`logs/`目录
3. 服务状态：`systemctl status timevalue-backend`

联系方式：
- 邮箱：[support@example.com]
- 文档：[项目文档地址]
- Issues：[GitHub Issues地址]