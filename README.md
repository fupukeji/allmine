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

### 方式一：一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/fupukeji/timevalue.git
cd timevalue

# 一键启动（自动配置安全密钥、安装依赖、启动服务）
python start_timevalue.py
```

### 方式二：手动启动

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
- **框架**: Python Flask
- **数据库**: SQLAlchemy + SQLite
- **认证**: Flask-JWT-Extended
- **API文档**: RESTful API设计

### 前端技术
- **框架**: React 18
- **构建工具**: Vite
- **UI组件**: Ant Design
- **状态管理**: React Hooks
- **路由**: React Router
- **图表**: Recharts

## 🔐 安全特性

- ✅ **自动密钥生成** - 生产环境自动生成安全密钥
- ✅ **JWT认证** - 无状态身份验证
- ✅ **权限控制** - 基于角色的访问控制
- ✅ **数据加密** - 敏感数据加密存储

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