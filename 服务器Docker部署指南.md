# 🚀 TimeValue 服务器Docker部署指南

> **场景**: 在已安装MySQL的服务器上部署TimeValue系统
> **目标**: 使用Docker部署后端，复用现有MySQL数据库
> **服务器**: 60.205.161.210

---

## 📋 部署前提

### 当前服务器状态
- ✅ MySQL 8.0 已安装并运行
- ✅ 数据库: `timevalue`
- ✅ 用户: `timevalue`
- ✅ 密码: `sdA3GThaTaDx3h8S`
- ✅ 端口: `3306`

### 需要安装的软件
- [ ] Docker
- [ ] Docker Compose
- [ ] Git

---

## 🔧 部署步骤

### Step 1: 安装Docker环境

#### 1.1 安装Docker

```bash
# 更新系统包
sudo yum update -y

# 安装必要工具
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

#### 1.2 安装Docker Compose

```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 创建软链接（可选）
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 1.3 配置Docker权限（可选）

```bash
# 将当前用户加入docker组
sudo usermod -aG docker $USER

# 重新登录以生效
exit
# 重新SSH登录
```

---

### Step 2: 获取项目代码

```bash
# 创建项目目录
cd /opt
sudo mkdir -p timevalue
sudo chown $USER:$USER timevalue
cd timevalue

# 克隆代码
git clone https://github.com/fupukeji/timevalue.git .

# 或使用阿里云Codeup
git clone https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git .
```

---

### Step 3: 配置Docker部署文件

#### 3.1 创建专用的docker-compose配置

创建 `docker-compose.server.yml`:

```yaml
version: '3.8'

services:
  # 后端API服务（使用现有MySQL）
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: timevalue-backend
    restart: unless-stopped
    environment:
      # Flask配置
      FLASK_ENV: production
      FLASK_DEBUG: False
      
      # 数据库配置（连接宿主机MySQL）
      DB_TYPE: mysql
      DB_HOST: host.docker.internal  # Docker访问宿主机
      DB_PORT: 3306
      DB_NAME: timevalue
      DB_USER: timevalue
      DB_PASSWORD: sdA3GThaTaDx3h8S
      
      # 安全密钥
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      
      # JWT配置
      JWT_ACCESS_TOKEN_EXPIRES: False
      
      # CORS配置
      CORS_ORIGINS: ${CORS_ORIGINS}
    ports:
      - "5000:5000"
    volumes:
      - ./backend/logs:/app/logs
    extra_hosts:
      - "host.docker.internal:host-gateway"  # 允许容器访问宿主机
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/api/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - timevalue-network

networks:
  timevalue-network:
    driver: bridge
```

#### 3.2 更新环境变量文件

编辑 `.env.docker`:

```bash
nano .env.docker
```

确保内容为:

```env
# ================================
# TimeValue Docker环境配置文件
# ================================

# ================================
# MySQL数据库配置（使用宿主机MySQL）
# ================================
DB_ROOT_PASSWORD=sdA3GThaTaDx3h8S
DB_NAME=timevalue
DB_USER=timevalue
DB_PASSWORD=sdA3GThaTaDx3h8S
DB_PORT=3306

# ================================
# Flask配置
# ================================
FLASK_ENV=production
FLASK_DEBUG=False

# ================================
# 安全密钥
# ================================
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production

# ================================
# JWT配置
# ================================
JWT_ACCESS_TOKEN_EXPIRES=False

# ================================
# CORS配置
# ================================
CORS_ORIGINS=http://60.205.161.210:3000,http://60.205.161.210:5000

# ================================
# 服务端口配置
# ================================
BACKEND_PORT=5000
FRONTEND_PORT=3000
```

---

### Step 4: 配置MySQL远程访问

确保MySQL允许Docker容器访问：

```bash
# 登录MySQL
mysql -u root -p

# 执行以下SQL命令
```

```sql
-- 授权timevalue用户从任何地址访问
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';

-- 更新密码认证插件
ALTER USER 'timevalue'@'%' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证用户权限
SELECT user, host FROM mysql.user WHERE user='timevalue';

-- 退出
EXIT;
```

检查MySQL配置文件:

```bash
# 编辑MySQL配置
sudo nano /etc/my.cnf

# 确保包含以下配置
[mysqld]
bind-address = 0.0.0.0
```

重启MySQL:

```bash
sudo systemctl restart mysqld
```

---

### Step 5: 配置防火墙

```bash
# 检查防火墙状态
sudo firewall-cmd --state

# 如果防火墙开启，添加端口规则
sudo firewall-cmd --permanent --add-port=5000/tcp  # 后端API
sudo firewall-cmd --permanent --add-port=3000/tcp  # 前端（可选）
sudo firewall-cmd --reload

# 查看已开放端口
sudo firewall-cmd --list-ports
```

---

### Step 6: 构建并启动服务

#### 6.1 构建Docker镜像

```bash
# 进入项目目录
cd /opt/timevalue

# 构建后端镜像
docker-compose -f docker-compose.server.yml build backend
```

#### 6.2 启动服务

```bash
# 启动后端服务
docker-compose -f docker-compose.server.yml --env-file .env.docker up -d

# 查看日志
docker-compose -f docker-compose.server.yml logs -f backend
```

#### 6.3 验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.server.yml ps

# 检查后端健康状态
curl http://localhost:5000/api/health

# 检查数据库连接
docker-compose -f docker-compose.server.yml exec backend python -c "
from database import db
from app import create_app
app = create_app()
with app.app_context():
    db.session.execute(db.text('SELECT 1'))
    print('✅ Database connection successful')
"
```

---

### Step 7: 设置开机自启

#### 7.1 创建Systemd服务

创建 `/etc/systemd/system/timevalue.service`:

```bash
sudo nano /etc/systemd/system/timevalue.service
```

内容:

```ini
[Unit]
Description=TimeValue Backend Service
Requires=docker.service
After=docker.service mysqld.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/timevalue
ExecStart=/usr/local/bin/docker-compose -f docker-compose.server.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.server.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

启用服务:

```bash
# 重载systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable timevalue

# 启动服务
sudo systemctl start timevalue

# 查看状态
sudo systemctl status timevalue
```

---

## 🛠️ 日常管理命令

### 查看服务

```bash
# 查看容器状态
docker-compose -f docker-compose.server.yml ps

# 查看实时日志
docker-compose -f docker-compose.server.yml logs -f

# 查看后端日志
docker-compose -f docker-compose.server.yml logs -f backend
```

### 重启服务

```bash
# 重启后端
docker-compose -f docker-compose.server.yml restart backend

# 或使用systemd
sudo systemctl restart timevalue
```

### 停止服务

```bash
# 停止服务
docker-compose -f docker-compose.server.yml down

# 或使用systemd
sudo systemctl stop timevalue
```

### 更新代码

```bash
# 拉取最新代码
cd /opt/timevalue
git pull

# 重新构建
docker-compose -f docker-compose.server.yml build backend

# 重启服务
docker-compose -f docker-compose.server.yml up -d
```

### 备份数据库

```bash
# 备份MySQL数据
mysqldump -u timevalue -psdA3GThaTaDx3h8S timevalue > /opt/backups/timevalue_$(date +%Y%m%d_%H%M%S).sql

# 创建备份脚本
sudo nano /opt/backup_timevalue.sh
```

备份脚本内容:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR
mysqldump -u timevalue -psdA3GThaTaDx3h8S timevalue | gzip > $BACKUP_DIR/timevalue_$(date +%Y%m%d_%H%M%S).sql.gz
# 保留最近7天的备份
find $BACKUP_DIR -name "timevalue_*.sql.gz" -mtime +7 -delete
```

设置定时备份:

```bash
# 添加执行权限
sudo chmod +x /opt/backup_timevalue.sh

# 添加到crontab（每天凌晨2点备份）
sudo crontab -e
# 添加: 0 2 * * * /opt/backup_timevalue.sh
```

---

## 🔍 故障排查

### 问题1: 容器无法连接MySQL

**症状**: 
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**解决方案**:

```bash
# 1. 检查MySQL是否运行
sudo systemctl status mysqld

# 2. 测试MySQL连接
mysql -h 127.0.0.1 -u timevalue -psdA3GThaTaDx3h8S -e "SELECT 1"

# 3. 检查MySQL用户权限
mysql -u root -p -e "SELECT user, host FROM mysql.user WHERE user='timevalue'"

# 4. 检查容器网络
docker-compose -f docker-compose.server.yml exec backend ping host.docker.internal

# 5. 查看容器日志
docker-compose -f docker-compose.server.yml logs backend
```

### 问题2: 端口被占用

**症状**:
```
Error: Bind for 0.0.0.0:5000 failed: port is already allocated
```

**解决方案**:

```bash
# 查看端口占用
netstat -tulpn | grep :5000

# 停止占用进程
sudo kill -9 <PID>

# 或修改端口
# 编辑 docker-compose.server.yml 将 5000:5000 改为 5001:5000
```

### 问题3: 健康检查失败

**排查步骤**:

```bash
# 1. 进入容器检查
docker-compose -f docker-compose.server.yml exec backend bash

# 2. 测试健康检查端点
curl http://localhost:5000/api/health

# 3. 检查Python环境
python --version
pip list | grep Flask

# 4. 手动测试数据库连接
python -c "import pymysql; conn = pymysql.connect(host='host.docker.internal', user='timevalue', password='sdA3GThaTaDx3h8S', database='timevalue'); print('OK')"
```

---

## 📊 监控与日志

### 查看资源占用

```bash
# 查看容器资源
docker stats timevalue-backend

# 查看磁盘占用
df -h
du -sh /opt/timevalue/backend/logs
```

### 日志管理

```bash
# 查看后端日志
tail -f /opt/timevalue/backend/logs/app.log

# 清理旧日志
find /opt/timevalue/backend/logs -name "*.log" -mtime +30 -delete
```

---

## 🔒 安全建议

### 1. 生成强密钥

```bash
# 生成SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# 生成JWT_SECRET_KEY
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# 更新到 .env.docker
```

### 2. 配置HTTPS

如果需要HTTPS访问，可以配置Nginx反向代理:

```bash
# 安装Nginx
sudo yum install -y nginx

# 配置Nginx（见后续章节）
```

### 3. 限制访问

```bash
# 仅允许特定IP访问后端
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="your-ip/32" port protocol="tcp" port="5000" accept'
sudo firewall-cmd --reload
```

---

## 📈 性能优化

### Gunicorn配置

编辑 `backend/gunicorn.conf.py`:

```python
import multiprocessing

# 根据CPU核心数调整
workers = multiprocessing.cpu_count() * 2 + 1

# 每个worker的线程数
threads = 2

# 超时时间
timeout = 120
```

### MySQL优化

```sql
-- 调整MySQL缓冲池大小（根据服务器内存）
SET GLOBAL innodb_buffer_pool_size = 512M;

-- 启用查询缓存
SET GLOBAL query_cache_size = 67108864;
SET GLOBAL query_cache_type = 1;
```

---

## ✅ 部署检查清单

部署完成后，请确认:

- [ ] Docker和Docker Compose已安装
- [ ] 项目代码已克隆到 `/opt/timevalue`
- [ ] MySQL用户权限已配置
- [ ] 防火墙端口已开放
- [ ] Docker镜像已构建
- [ ] 容器成功启动
- [ ] 健康检查通过: `curl http://localhost:5000/api/health`
- [ ] 数据库连接正常
- [ ] Systemd服务已启用
- [ ] 备份脚本已配置
- [ ] 安全密钥已更新（生产环境）

---

## 🎯 访问地址

部署成功后，服务访问地址:

- **后端API**: http://60.205.161.210:5000
- **健康检查**: http://60.205.161.210:5000/api/health
- **管理员登录**: admin / admin123（首次登录后请修改）

---

## 📞 技术支持

如遇问题，请查看:

1. **容器日志**: `docker-compose -f docker-compose.server.yml logs -f`
2. **应用日志**: `/opt/timevalue/backend/logs/app.log`
3. **MySQL日志**: `sudo tail -f /var/log/mysqld.log`
4. **系统日志**: `sudo journalctl -u timevalue -f`

---

> 🎉 **部署完成后，系统将自动运行在服务器上**
> 
> 💡 **建议**: 首次部署后，修改管理员密码并生成新的安全密钥
