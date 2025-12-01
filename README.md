# TimeValue 个人资产管理系统

<div align="center">

![TimeValue Logo](https://img.shields.io/badge/TimeValue-个人资产管理系统-blue?style=for-the-badge)

**🚀 Powered by 孚普科技（北京）有限公司**  
**🤖 AI驱动的MVP快速迭代解决方案**

[![GitHub](https://img.shields.io/badge/GitHub-fupukeji-black?style=flat-square&logo=github)](https://github.com/fupukeji)
[![Website](https://img.shields.io/badge/Website-fupukeji.com-blue?style=flat-square)](https://fupukeji.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)

</div>

## 🌟 项目简介

TimeValue是一个功能强大的个人资产管理系统，专为个人用户设计，帮助您全面掌控资产状况，实现"恒产生金"的财富管理目标。

### ✨ 核心功能

- 💰 **资产收入管理** - 多元化收入记录与分析
- 📊 **投资回报分析** - ROI、年化收益率、回本周期计算
- 🔧 **维护管理** - 资产保养计划与成本跟踪
- 📈 **BI数据分析** - 可视化图表与趋势分析
- 👥 **用户权限管理** - 完整的用户管理体系
- 🔐 **安全保障** - 自动生成安全密钥，JWT认证

## 🏢 关于孚普科技

**孚普科技（北京）有限公司**是一家专注于AI驱动的MVP快速迭代解决方案的创新公司。我们致力于：

- 🤖 **AI代码生成** - 智能化代码生成工具
- ⚡ **快速原型开发** - MVP最小可行产品快速迭代
- 🎯 **企业数字化转型** - 定制化企业级解决方案
- 📱 **移动应用开发** - 跨平台应用开发服务

🌐 **官网**: [https://fupukeji.com](https://fupukeji.com)  
📧 **商务合作**: contact@fupukeji.com  
📚 **GitHub**: [https://github.com/fupukeji](https://github.com/fupukeji)

## 🚀 快速开始

### 📦 获取代码

```bash
# 从阿里云Codeup克隆（推荐）
git clone https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git
cd timevalue

# 或从GitHub克隆
git clone https://github.com/fupukeji/timevalue.git
cd timevalue
```

### 方式一：Docker部署（推荐👍）

**一键部署，生产就绪**

#### 本地开发环境

```bash
# Linux/Mac
chmod +x deploy-docker.sh
./deploy-docker.sh

# Windows
deploy-docker.bat

# 或使用Makefile（推荐）
make init   # 初始化
make up     # 启动服务
make ps     # 查看状态
```

#### 服务器部署（已有MySQL）

**使用命令行**:

```bash
# SSH登录服务器
ssh root@your-server-ip

# 上传项目到 /opt/timevalue
cd /opt/timevalue

# 一键部署
chmod +x 快速部署.sh
./快速部署.sh
```

**使用宝塔面板** 👍 推荐：

```bash
# 1. 宝塔面板安装Docker管理器
# 2. 上传项目到 /opt/timevalue
# 3. 终端执行：
cd /opt/timevalue
docker-compose -f docker-compose.server.yml build
docker-compose -f docker-compose.server.yml up -d

# 4. 宝塔【安全】开放5000端口
```

📖 **Docker部署详细文档**:
- **[宝塔快速部署.md](宝塔快速部署.md)** - 宝塔逄5分钟部署 👍
- **[宝塔Docker部署指南.md](宝塔Docker部署指南.md)** - 宝塔完整教程689行
- **[部署操作清单.md](部署操作清单.md)** - 5分钟快速部署 ⭐️
- **[服务器Docker部署指南.md](服务器Docker部署指南.md)** - 完整文档655行
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - 通用Docker部署

**Docker部署特性**:
- ✅ 生产级配置（Gunicorn + MySQL 8.0）
- ✅ 多阶段构建（镜像体积优化）
- ✅ 非root用户运行（安全加固）
- ✅ 健康检查（/health, /ready, /live）
- ✅ 自动备份（make backup）
- ✅ 一键管理（20+个Makefile命令）

### 方式二：一键启动（Windows开发环境）

```bash
# 一键启动（自动配置安全密钥、安装依赖、启动服务）
python start_timevalue.py
```

### 方式三：生产环境部署（阿里云服务器）

```bash
# 1. 一键部署
chmod +x *.sh
./deploy.sh

# 2. 启动服务
./start_production.sh

# 3. 查看状态
./check_status.sh
```

📖 **详细部署文档**:
- [Docker部署指南](DOCKER_DEPLOYMENT.md) ⭐️ 推荐
- [生产环境部署指南](DEPLOY_GUIDE.md)
- [Windows部署指南](WINDOWS_DEPLOY_GUIDE.md)
- [Git使用指南](GIT_GUIDE.md)
- [快速参考](QUICK_REFERENCE.md)

### 方式四：手动启动

#### 1. 生成安全密钥

```bash
cd backend
python generate_keys.py
```

#### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 📖 技术栈

### 后端技术
- **框架**: Python Flask 3.0
- **数据库**: SQLAlchemy + MySQL 8.0
- **认证**: Flask-JWT-Extended
- **WSGI**: Gunicorn (生产环境)
- **API文档**: RESTful API设计

### 前端技术
- **框架**: React 18
- **构建工具**: Vite
- **UI组件**: Ant Design 5.x
- **状态管理**: React Hooks
- **路由**: React Router
- **图表**: Recharts

### 部署技术
- **容器**: Docker + Docker Compose
- **反向代理**: Nginx (可选)
- **进程管理**: Systemd / PM2
- **监控**: Prometheus + Grafana (可选)

## 🔐 安全特性

- ✅ **自动密钥生成** - 生产环境自动生成安全密钥
- ✅ **JWT认证** - 无状态身份验证
- ✅ **权限控制** - 基于角色的访问控制
- ✅ **数据加密** - 敏感数据加密存储

## 🌐 Git仓库

本项目托管在阿里云Codeup，支持快速克隆和部署：

- **主仓库**: https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git
- **镜像仓库**: https://github.com/fupukeji/timevalue

### 推送代码

```bash
# Windows用户
git_push.bat

# Linux/Mac用户  
./git_push.sh
```

## 📱 功能预览

### 资产管理
- 固定资产的增删改查
- 折旧计算与追踪
- 资产分类管理

### 收入分析
- 多种收入类型支持
- ROI投资回报率计算
- 收入趋势可视化

### BI数据分析
- 资产价值分布
- 收入统计图表
- 财务健康度评估

## 🤝 参与贡献

我们欢迎各种形式的贡献！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系我们

如果您在使用过程中遇到问题，或者对我们的AI解决方案感兴趣，欢迎联系我们：

- 🌐 **官网**: [https://fupukeji.com](https://fupukeji.com)
- 📧 **邮箱**: contact@fupukeji.com
- 📱 **微信**: 添加微信群了解更多
- 💬 **QQ群**: [待补充]

## 📄 开源协议

本项目采用 MIT 开源协议 - 查看 [LICENSE](./LICENSE) 文件了解详情

---

<div align="center">

**🚀 让MVP开发更简单、更快速、更安全**

**感谢选择孚普科技的AI解决方案！**

[![Star](https://img.shields.io/github/stars/fupukeji/timevalue?style=social)](https://github.com/fupukeji/timevalue)
[![Fork](https://img.shields.io/github/forks/fupukeji/timevalue?style=social)](https://github.com/fupukeji/timevalue)

</div>