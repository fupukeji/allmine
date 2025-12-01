# 🐳 TimeValue Docker 部署指南

> 完整的Docker容器化部署方案
> 支持开发环境和生产环境

---

## 📋 目录

- [快速开始](#快速开始)
- [系统要求](#系统要求)
- [部署架构](#部署架构)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排查](#故障排查)
- [性能优化](#性能优化)
- [安全加固](#安全加固)

---

## 🚀 快速开始

### 一键部署（推荐）

```bash
# 1. 克隆代码
git clone https://github.com/fupukeji/timevalue.git
cd timevalue

# 2. 配置环境变量
cp .env.docker .env.docker
# 编辑 .env.docker 修改密码

# 3. 初始化并启动
make init
make up

# 4. 查看服务状态
make ps
```

**访问地址**:
- 后端API: http://localhost:5000
- 健康检查: http://localhost:5000/api/health
- 前端Web: http://localhost:3000

### 手动部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose --env-file .env.docker up -d

# 3. 查看日志
docker-compose logs -f
```

---

## 💻 系统要求

### 硬件要求

| 环境 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| **最小配置** | 1核 | 2GB | 10GB |
| **推荐配置** | 2核 | 4GB | 20GB |
| **生产环境** | 4核+ | 8GB+ | 50GB+ |

### 软件要求

- **Docker**: >= 20.10.0
- **Docker Compose**: >= 2.0.0
- **操作系统**: Linux/macOS/Windows

验证安装：
```bash
docker --version
docker-compose --version
```

---

## 🏗️ 部署架构

### 服务组件

```
┌─────────────────────────────────────────┐
│          Nginx (可选)                   │
│      反向代理 + 负载均衡                │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│  Frontend      │  │   Backend      │
│  React + Vite  │  │  Flask + API   │
│  Port: 3000    │  │  Port: 5000    │
└────────────────┘  └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │     MySQL      │
                    │  Database      │
                    │  Port: 3306    │
                    └────────────────┘
```

### 网络配置

- **网络名称**: `timevalue-network`
- **网络类型**: Bridge
- **容器互联**: 通过服务名访问（如 `mysql`、`backend`）

### 数据持久化

| 数据类型 | 存储位置 | 挂载方式 |
|---------|---------|---------|
| MySQL数据 | `mysql_data` volume | Docker Volume |
| 后端日志 | `./backend/logs` | Bind Mount |
| 备份文件 | `./backups` | Bind Mount |

---

## 📖 详细步骤

### Step 1: 准备环境

#### 1.1 安装Docker

**Ubuntu/Debian**:
```bash
curl -fsSL https://get.docker.com | bash -s docker
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL**:
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

**macOS/Windows**:
- 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)

#### 1.2 安装Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: 配置环境变量

#### 2.1 复制配置模板

```bash
cp .env.docker .env.docker
```

#### 2.2 生成安全密钥

```bash
# 生成SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# 生成JWT_SECRET_KEY
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

#### 2.3 编辑配置文件

```bash
nano .env.docker
```

**必须修改的配置**:
```env
# 数据库密码（必改！）
DB_ROOT_PASSWORD=your_strong_root_password_here
DB_PASSWORD=your_strong_password_here

# 安全密钥（必改！）
SECRET_KEY=刚才生成的SECRET_KEY
JWT_SECRET_KEY=刚才生成的JWT_SECRET_KEY

# CORS域名（根据实际情况）
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Step 3: 构建镜像

#### 3.1 构建后端镜像

```bash
docker-compose build backend
```

**构建过程**:
1. 基础镜像: `python:3.11-slim`
2. 安装系统依赖: `gcc`, `mysql-client`
3. 安装Python依赖: `requirements.txt`
4. 复制应用代码
5. 创建非root用户 `timevalue`

#### 3.2 验证镜像

```bash
docker images | grep timevalue
```

预期输出:
```
timevalue-backend    latest    xxx    xxx    xxxMB
```

### Step 4: 启动服务

#### 4.1 启动所有服务

```bash
docker-compose --env-file .env.docker up -d
```

**启动顺序**:
1. MySQL (等待健康检查通过)
2. Backend (依赖MySQL)
3. Frontend (可选)

#### 4.2 查看启动日志

```bash
docker-compose logs -f
```

#### 4.3 验证服务状态

```bash
# 查看容器状态
docker-compose ps

# 健康检查
curl http://localhost:5000/api/health
```

### Step 5: 初始化数据

#### 5.1 自动初始化

首次启动时，后端会自动:
- 创建数据库表结构
- 创建默认管理员账户: `admin/admin123`
- 初始化默认分类

#### 5.2 手动初始化（如需要）

```bash
docker-compose exec backend python init_db.py
```

### Step 6: 访问应用

- **后端API**: http://localhost:5000
- **API健康检查**: http://localhost:5000/api/health
- **前端Web**: http://localhost:3000
- **管理员登录**: admin / admin123

---

## ⚙️ 配置说明

### 环境变量详解

#### MySQL配置

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `DB_ROOT_PASSWORD` | MySQL root密码 | - | ✅ |
| `DB_NAME` | 数据库名称 | timevalue | ❌ |
| `DB_USER` | 数据库用户名 | timevalue | ❌ |
| `DB_PASSWORD` | 数据库密码 | - | ✅ |
| `DB_PORT` | MySQL端口 | 3306 | ❌ |

#### Flask配置

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `FLASK_ENV` | 运行环境 | production | ✅ |
| `FLASK_DEBUG` | 调试模式 | False | ❌ |
| `SECRET_KEY` | Flask密钥 | - | ✅ |
| `JWT_SECRET_KEY` | JWT密钥 | - | ✅ |

#### CORS配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `CORS_ORIGINS` | 允许的跨域源 | `http://localhost:3000,https://app.com` |

### Gunicorn配置

编辑 `backend/gunicorn.conf.py`:

```python
# Worker进程数
workers = 4

# 每个worker的线程数
threads = 2

# 超时时间（秒）
timeout = 120
```

**性能调优建议**:
- **workers**: CPU核心数 × 2 + 1
- **threads**: 2-4（适合I/O密集型）
- **timeout**: 根据最长请求时间调整

---

## 🛠️ 常用命令

### Makefile命令（推荐）

| 命令 | 说明 |
|------|------|
| `make help` | 显示帮助信息 |
| `make build` | 构建镜像 |
| `make up` | 启动服务 |
| `make down` | 停止服务 |
| `make restart` | 重启服务 |
| `make logs` | 查看所有日志 |
| `make logs-backend` | 查看后端日志 |
| `make logs-mysql` | 查看MySQL日志 |
| `make ps` | 查看服务状态 |
| `make exec-backend` | 进入后端容器 |
| `make exec-mysql` | 进入MySQL容器 |
| `make backup` | 备份数据库 |
| `make restore` | 恢复数据库 |
| `make clean` | 清理容器（保留数据） |
| `make prune` | 完全清理（删除数据） |
| `make health` | 健康检查 |
| `make update` | 更新并重启 |

### Docker Compose命令

```bash
# 启动服务（前台）
docker-compose up

# 启动服务（后台）
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash

# 查看服务状态
docker-compose ps

# 查看资源占用
docker-compose top
```

### 数据库管理

```bash
# 进入MySQL
docker-compose exec mysql mysql -u timevalue -p

# 备份数据库
docker-compose exec mysql mysqldump -u root -p[密码] timevalue > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p[密码] timevalue < backup.sql

# 查看数据库大小
docker-compose exec mysql mysql -u root -p -e "SELECT table_schema AS 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)' FROM information_schema.tables GROUP BY table_schema;"
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f --tail=100

# 导出日志
docker-compose logs > logs_$(date +%Y%m%d).txt

# 清理日志
docker-compose down && docker-compose up -d
```

---

## 🔍 故障排查

### 常见问题

#### 1. MySQL连接失败

**症状**:
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**解决方案**:
```bash
# 检查MySQL容器状态
docker-compose ps mysql

# 查看MySQL日志
docker-compose logs mysql

# 重启MySQL
docker-compose restart mysql

# 等待MySQL就绪
docker-compose exec backend bash -c "while ! mysqladmin ping -h mysql --silent; do sleep 1; done; echo 'MySQL is ready'"
```

#### 2. 端口被占用

**症状**:
```
Error: Bind for 0.0.0.0:5000 failed: port is already allocated
```

**解决方案**:
```bash
# 查看端口占用
netstat -tulpn | grep :5000

# 修改端口（.env.docker）
BACKEND_PORT=5001

# 或停止占用进程
kill -9 <PID>
```

#### 3. 容器启动失败

**排查步骤**:
```bash
# 1. 查看容器日志
docker-compose logs backend

# 2. 查看容器状态
docker-compose ps

# 3. 进入容器调试
docker-compose run --rm backend bash

# 4. 检查环境变量
docker-compose exec backend env | grep DB_
```

#### 4. 数据库初始化失败

**症状**:
```
sqlalchemy.exc.OperationalError: (1049, "Unknown database 'timevalue'")
```

**解决方案**:
```bash
# 1. 手动创建数据库
docker-compose exec mysql mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS timevalue CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. 重启后端
docker-compose restart backend
```

#### 5. 权限问题

**症状**:
```
PermissionError: [Errno 13] Permission denied: '/app/logs'
```

**解决方案**:
```bash
# 创建日志目录并设置权限
mkdir -p backend/logs
chmod 777 backend/logs

# 重新构建
docker-compose build --no-cache backend
```

### 调试技巧

#### 查看容器内部

```bash
# 进入后端容器
docker-compose exec backend bash

# 检查Python环境
python --version
pip list

# 测试数据库连接
python -c "import pymysql; conn = pymysql.connect(host='mysql', user='timevalue', password='xxx', database='timevalue'); print('OK')"
```

#### 查看健康状态

```bash
# 后端健康检查
curl -v http://localhost:5000/api/health

# 数据库健康检查
docker-compose exec mysql mysqladmin ping -h localhost -u root -p
```

#### 查看资源占用

```bash
# 查看容器资源
docker stats

# 查看磁盘占用
docker system df

# 清理无用数据
docker system prune -a
```

---

## ⚡ 性能优化

### 1. Gunicorn优化

**调整Worker数量**:
```python
# gunicorn.conf.py
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
```

**启用预加载**:
```python
preload_app = True  # 减少内存占用
```

### 2. MySQL优化

**调整缓冲池大小**:
```yaml
# docker-compose.yml
command:
  - --innodb_buffer_pool_size=512M  # 根据内存调整
  - --max_connections=500
```

**启用查询缓存**:
```sql
SET GLOBAL query_cache_size = 67108864;
SET GLOBAL query_cache_type = 1;
```

### 3. Docker优化

**限制资源使用**:
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

**使用多阶段构建**:
- ✅ 已在Dockerfile中实现
- 减小镜像体积：~500MB → ~200MB

### 4. 网络优化

**启用HTTP/2**:
```nginx
listen 443 ssl http2;
```

**启用Gzip压缩**:
```nginx
gzip on;
gzip_types text/plain application/json;
```

---

## 🔒 安全加固

### 1. 密码安全

✅ **强密码策略**:
```bash
# 生成32字符随机密码
openssl rand -base64 32
```

❌ **禁止使用**:
- `admin123`
- `password`
- `123456`

### 2. 网络隔离

**仅暴露必要端口**:
```yaml
# docker-compose.yml
services:
  mysql:
    # 不暴露端口到宿主机（仅容器互联）
    # ports:
    #   - "3306:3306"
```

**使用私有网络**:
```yaml
networks:
  timevalue-network:
    driver: bridge
    internal: true  # 禁止外网访问
```

### 3. 用户权限

**非root运行**:
```dockerfile
# Dockerfile
USER timevalue  # 使用非特权用户
```

**只读文件系统**:
```yaml
services:
  backend:
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
```

### 4. 数据加密

**敏感数据加密存储**:
```python
# 密码哈希
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash(password, method='pbkdf2:sha256')
```

**SSL/TLS连接**:
```yaml
environment:
  DB_SSL_CA: /path/to/ca-cert.pem
```

### 5. 日志审计

**记录敏感操作**:
```python
import logging
logger.info(f"User {username} performed {action}")
```

**日志轮转**:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 6. 定期更新

```bash
# 更新基础镜像
docker pull python:3.11-slim
docker pull mysql:8.0

# 重新构建
make build
make restart
```

---

## 📊 监控告警

### Prometheus监控（可选）

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

### Grafana可视化（可选）

```yaml
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 🎯 生产环境清单

- [ ] 修改所有默认密码
- [ ] 生成强随机SECRET_KEY
- [ ] 配置HTTPS证书
- [ ] 限制暴露端口
- [ ] 配置防火墙规则
- [ ] 启用日志审计
- [ ] 配置备份策略
- [ ] 设置监控告警
- [ ] 压力测试
- [ ] 灾难恢复演练

---

## 📞 技术支持

- **GitHub**: https://github.com/fupukeji/timevalue
- **官网**: https://fupukeji.com
- **邮箱**: support@fupukeji.com

---

## 📝 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2025-11-30 | 初始Docker部署方案 |

---

> 🎉 **恭喜！您已成功部署TimeValue系统**
> 
> 💡 **提示**: 建议阅读完整文档，了解所有功能和最佳实践
