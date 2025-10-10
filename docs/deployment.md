# 部署文档

## 部署方式

### 方式一：Docker Compose 部署（推荐）

#### 1. 环境准备
- 安装 Docker 和 Docker Compose
- 确保端口 3000 和 5000 未被占用

#### 2. 克隆项目
```bash
git clone <repository-url>
cd TimeValue
```

#### 3. 配置环境变量
```bash
# 复制环境变量文件
cp backend/.env.example backend/.env

# 编辑环境变量（生产环境务必修改密钥）
# 修改 SECRET_KEY 和 JWT_SECRET_KEY
```

#### 4. 构建并启动
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 5. 访问应用
- 前端：http://localhost:3000
- 后端API：http://localhost:5000

#### 6. 停止服务
```bash
docker-compose down
```

### 方式二：手动部署

#### 后端部署

1. **环境准备**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

2. **配置环境**
```bash
cp .env.example .env
# 编辑 .env 文件，修改相关配置
```

3. **启动后端**
```bash
python app.py
```

#### 前端部署

1. **环境准备**
```bash
cd frontend
npm install
```

2. **开发模式启动**
```bash
npm run dev
```

3. **生产构建**
```bash
npm run build
npm run preview
```

## 生产环境配置

### 1. 安全配置
- 修改默认密钥 `SECRET_KEY` 和 `JWT_SECRET_KEY`
- 设置 `FLASK_ENV=production`
- 配置 HTTPS（建议使用 Nginx 反向代理）

### 2. 数据持久化
- 默认使用 SQLite 数据库
- 数据存储在 `./data/timevalue.db`
- 建议定期备份数据库文件

### 3. Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. 监控和日志
- 使用 `docker-compose logs` 查看日志
- 建议配置日志轮转
- 可集成监控工具如 Prometheus + Grafana

## 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查看端口占用
netstat -an | grep :3000
netstat -an | grep :5000

# 修改 docker-compose.yml 中的端口映射
```

2. **数据库权限问题**
```bash
# 确保数据目录有写权限
chmod 755 ./data
```

3. **前端无法访问后端API**
- 检查 CORS 配置
- 确认后端服务正常运行
- 检查防火墙设置

4. **Docker 构建失败**
```bash
# 清理 Docker 缓存
docker system prune -f

# 重新构建
docker-compose build --no-cache
```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时跟踪日志
docker-compose logs -f
```

## 数据备份与恢复

### 备份
```bash
# 备份数据库
cp ./data/timevalue.db ./backup/timevalue_$(date +%Y%m%d_%H%M%S).db

# 或使用Docker命令
docker-compose exec backend cp /app/data/timevalue.db /app/data/backup/
```

### 恢复
```bash
# 停止服务
docker-compose down

# 恢复数据库
cp ./backup/timevalue_backup.db ./data/timevalue.db

# 重启服务
docker-compose up -d
```

## 性能优化

### 1. 前端优化
- 启用 Gzip 压缩
- 配置 CDN
- 优化图片资源

### 2. 后端优化
- 使用 Gunicorn 或 uWSGI
- 配置数据库连接池
- 添加缓存机制

### 3. 数据库优化
- 对于大量数据，考虑使用 PostgreSQL 或 MySQL
- 添加适当的索引
- 定期清理过期数据

## 扩展部署

### 使用 PostgreSQL
1. 修改 `docker-compose.yml` 添加 PostgreSQL 服务
2. 更新环境变量 `DATABASE_URL`
3. 安装 PostgreSQL 适配器

### 使用 Redis 缓存
1. 添加 Redis 服务
2. 配置 Flask-Caching
3. 缓存用户会话和计算结果

### 负载均衡
1. 使用 Nginx 作为负载均衡器
2. 部署多个后端实例
3. 配置会话持久化