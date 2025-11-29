# TimeValue 阿里云生产环境部署指南

## 📋 快速开始

### 方式一：一键部署（推荐）

适合首次部署，会自动安装所有依赖。

```bash
# 1. 上传项目到服务器
scp -r timevalue root@your-server-ip:/root/

# 2. 连接到服务器
ssh root@your-server-ip

# 3. 进入项目目录
cd /root/timevalue

# 4. 设置脚本权限
chmod +x *.sh

# 5. 执行一键部署
./deploy.sh

# 6. 启动生产服务
./start_production.sh
```

### 方式二：快速启动

适合已完成部署，只需启动服务。

```bash
# 启动服务
./start_production.sh

# 或者重新安装依赖后启动
./start_production.sh --install
```

---

## 🎯 核心脚本说明

### 1. deploy.sh - 一键部署脚本

**功能：**
- ✅ 自动检测操作系统（Ubuntu/CentOS/Alibaba Cloud Linux）
- ✅ 自动安装Python3和Node.js（如未安装）
- ✅ 创建数据目录和日志目录
- ✅ 生成安全密钥
- ✅ 安装后端和前端依赖
- ✅ 设置脚本执行权限

**使用：**
```bash
./deploy.sh
```

### 2. start_production.sh - 生产环境启动脚本

**功能：**
- ✅ 检查Python和Node.js环境
- ✅ 停止已运行的服务
- ✅ 后台启动后端服务（端口5000）
- ✅ 后台启动前端服务（端口3000）
- ✅ 记录进程PID
- ✅ 输出访问地址和管理信息

**使用：**
```bash
# 直接启动
./start_production.sh

# 重新安装依赖后启动
./start_production.sh --install
```

**启动后显示：**
- 服务PID
- 本地访问地址
- 局域网访问地址
- 公网访问地址
- 默认管理员账号
- 日志文件路径

### 3. stop_production.sh - 停止服务脚本

**功能：**
- ✅ 优雅停止后端和前端服务
- ✅ 清理PID文件
- ✅ 清理残留进程

**使用：**
```bash
./stop_production.sh
```

### 4. check_status.sh - 服务状态检查脚本

**功能：**
- ✅ 检查后端和前端服务运行状态
- ✅ 显示进程PID和资源占用
- ✅ 显示端口监听状态
- ✅ 显示最近的日志
- ✅ 显示系统资源使用情况
- ✅ 显示访问地址

**使用：**
```bash
./check_status.sh
```

---

## 🚀 完整部署流程

### 步骤1：准备阿里云ECS

1. **购买ECS实例**
   - 推荐配置：2核4GB或以上
   - 操作系统：Ubuntu 20.04 或 Alibaba Cloud Linux 3
   - 带宽：5Mbps及以上

2. **配置安全组**
   - 登录阿里云控制台
   - 进入ECS实例 → 安全组 → 配置规则
   - 添加入方向规则：
     - 端口：3000，协议：TCP，授权对象：0.0.0.0/0
     - 端口：5000，协议：TCP，授权对象：0.0.0.0/0
     - （可选）端口：80，协议：TCP，授权对象：0.0.0.0/0
     - （可选）端口：443，协议：TCP，授权对象：0.0.0.0/0

### 步骤2：上传项目

**方式A：使用Git（推荐）**
```bash
ssh root@your-server-ip
git clone https://github.com/your-repo/timevalue.git
cd timevalue
```

**方式B：使用SCP**
```bash
# 在本地执行
scp -r d:\timevalue root@your-server-ip:/root/
```

**方式C：使用SFTP工具**
- 使用FileZilla、WinSCP等工具上传

### 步骤3：执行部署

```bash
# 连接到服务器
ssh root@your-server-ip

# 进入项目目录
cd /root/timevalue

# 设置权限
chmod +x *.sh

# 执行一键部署
./deploy.sh
```

### 步骤4：启动服务

```bash
./start_production.sh
```

### 步骤5：验证部署

```bash
# 检查服务状态
./check_status.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

### 步骤6：访问应用

打开浏览器访问：`http://your-server-ip:3000`

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

---

## 🔧 常用操作

### 查看服务状态
```bash
./check_status.sh
```

### 重启服务
```bash
./stop_production.sh
./start_production.sh
```

### 查看实时日志
```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log
```

### 更新代码
```bash
# 停止服务
./stop_production.sh

# 拉取最新代码
git pull

# 重新安装依赖并启动
./start_production.sh --install
```

### 备份数据
```bash
# 备份数据库
cp data/timevalue.db data/backup/timevalue_$(date +%Y%m%d_%H%M%S).db

# 查看备份
ls -lh data/backup/
```

---

## 🔐 安全建议

### 1. 修改默认密码
首次登录后立即修改admin密码

### 2. 配置防火墙
```bash
# Ubuntu
sudo ufw allow 3000
sudo ufw allow 5000
sudo ufw enable

# CentOS/Alibaba Cloud Linux
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 3. 使用Nginx反向代理（推荐）
```bash
# 安装Nginx
sudo apt install nginx  # Ubuntu
sudo yum install nginx  # CentOS

# 复制配置
sudo cp nginx.conf /etc/nginx/conf.d/timevalue.conf

# 修改配置中的域名
sudo nano /etc/nginx/conf.d/timevalue.conf

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 4. 配置SSL证书
```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu
sudo yum install certbot python3-certbot-nginx  # CentOS

# 自动配置SSL
sudo certbot --nginx -d your-domain.com
```

---

## 🛠️ 故障排查

### 服务无法启动

**问题：** 端口被占用
```bash
# 查看端口占用
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :3000

# 终止占用进程
sudo kill -9 <PID>
```

**问题：** Python依赖缺失
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**问题：** Node.js依赖缺失
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 服务运行异常

**查看详细日志：**
```bash
# 后端日志
cat logs/backend.log

# 前端日志
cat logs/frontend.log

# 系统日志
sudo journalctl -xe
```

**检查数据库：**
```bash
ls -lh data/timevalue.db

# 重新初始化数据库（会清空数据）
cd backend
source venv/bin/activate
python -c "from app import create_app; from database import db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
```

---

## 📊 性能优化

### 使用Gunicorn（生产环境推荐）

1. 安装Gunicorn
```bash
cd backend
source venv/bin/activate
pip install gunicorn
```

2. 修改start_production.sh中的启动命令
```bash
# 替换原来的 python3 app.py
# 改为
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 启用Nginx缓存

编辑nginx配置添加缓存：
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 🔄 使用systemd管理（可选）

如果需要开机自启动和systemd管理，参考`systemd-service-example.txt`文件。

**优点：**
- ✅ 开机自动启动
- ✅ 服务崩溃自动重启
- ✅ 统一的服务管理接口
- ✅ 完善的日志管理

---

## 📞 获取帮助

如果遇到问题：
1. 查看日志文件：`logs/backend.log` 和 `logs/frontend.log`
2. 检查服务状态：`./check_status.sh`
3. 查看系统资源：`top` 或 `htop`

---

## 📄 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [NGINX_CONFIG_GUIDE.md](NGINX_CONFIG_GUIDE.md) - Nginx配置指南
- [README.md](README.md) - 项目说明文档

---

**Powered by 孚普科技（北京）有限公司**  
🤖 AI驱动的MVP快速迭代解决方案
