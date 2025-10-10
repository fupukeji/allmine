# TimeValue 快速开始指南

## 系统要求

- **操作系统**: Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- **Python**: 3.6 或更高版本
- **Node.js**: 14.0 或更高版本
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 1GB 可用空间

## 一键部署（推荐）

### 1. 下载项目
```bash
# 如果是git仓库
git clone <repository-url>
cd TimeValue

# 或者直接解压项目文件到目录
```

### 2. 运行部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

脚本会自动完成以下操作：
- 检查系统要求
- 安装Python和Node.js依赖
- 创建虚拟环境
- 构建前端项目
- 初始化数据库
- 创建启动脚本
- 可选创建系统服务

### 3. 启动服务

**开发模式（推荐用于测试）：**
```bash
# 启动后端（新终端窗口）
./start_backend.sh

# 启动前端（新终端窗口）
./start_frontend_dev.sh
```

**生产模式：**
```bash
# 一键启动所有服务
./start_production.sh

# 停止所有服务
./stop_production.sh
```

### 4. 访问应用
- 前端地址：http://localhost:3000
- 后端API：http://localhost:5000
- 默认管理员账号：admin / admin123

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

## 生产环境配置

### 使用Nginx（推荐）

1. **安装Nginx**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
# 或
sudo dnf install nginx
```

2. **配置Nginx**
```bash
# 复制配置文件
sudo cp nginx.conf /etc/nginx/sites-available/timevalue
sudo ln -s /etc/nginx/sites-available/timevalue /etc/nginx/sites-enabled/

# 修改配置文件中的域名和路径
sudo nano /etc/nginx/sites-available/timevalue

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

3. **配置SSL（可选）**
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 使用系统服务

```bash
# 启用服务
sudo systemctl enable timevalue-backend
sudo systemctl start timevalue-backend

# 检查状态
sudo systemctl status timevalue-backend
```

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