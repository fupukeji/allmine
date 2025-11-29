# TimeValue Node.js + PostgreSQL 快速开始

## 🚀 5分钟快速部署

### 步骤1：安装依赖

```bash
cd backend-node
npm install
```

### 步骤2：初始化数据库

```bash
npm run migrate
```

输出：
```
✅ Database tables created successfully
✅ Default admin user created (admin/admin123)
🎉 Migration completed
```

### 步骤3：启动服务

```bash
# 在项目根目录
chmod +x start_production_node.sh
./start_production_node.sh --install
```

### 步骤4：访问应用

打开浏览器访问：`http://localhost:3000`

登录账号：
- 用户名：`admin`
- 密码：`admin123`

---

## 📂 项目结构

```
backend-node/
├── config/
│   └── database.js          # PostgreSQL连接配置
├── middleware/
│   └── auth.js              # JWT认证中间件
├── migrations/
│   └── init.js              # 数据库初始化脚本
├── routes/
│   ├── auth.js              # 认证路由
│   ├── categories.js        # 分类路由
│   ├── projects.js          # 项目路由
│   ├── assets.js            # 资产路由
│   ├── analytics.js         # 分析路由
│   ├── admin.js             # 管理员路由
│   ├── income.js            # 收入路由
│   ├── maintenance.js       # 维护路由
│   └── reports.js           # 报告路由
├── .env                     # 环境变量配置
├── server.js                # 服务入口
├── package.json             # 依赖配置
└── README.md                # 详细文档
```

---

## 🔧 开发命令

```bash
# 安装依赖
npm install

# 初始化数据库
npm run migrate

# 启动服务（生产模式）
npm start

# 启动服务（开发模式，自动重启）
npm run dev
```

---

## 🗄️ 数据库配置

已配置阿里云PostgreSQL：

- 主机：`pgm-2ze3rv37e804623iqo.pg.rds.aliyuncs.com`
- 端口：`1432`
- 数据库：`wangyongqing_test`
- 用户：`wangyongqing`

配置文件：`backend-node/.env`

---

## 🌐 API文档

基础URL：`http://localhost:5000/api`

### 健康检查
```bash
GET /api/health
```

### 用户认证
```bash
POST /api/auth/register      # 注册
POST /api/auth/login         # 登录
GET  /api/auth/profile       # 获取用户信息
PUT  /api/auth/profile       # 更新用户信息
```

### 项目管理
```bash
GET    /api/projects         # 获取项目列表
POST   /api/projects         # 创建项目
GET    /api/projects/:id     # 获取项目详情
PUT    /api/projects/:id     # 更新项目
DELETE /api/projects/:id     # 删除项目
GET    /api/statistics       # 获取统计数据
```

### 资产管理
```bash
GET    /api/assets           # 获取资产列表
POST   /api/assets           # 创建资产
GET    /api/assets/:id       # 获取资产详情
PUT    /api/assets/:id       # 更新资产
DELETE /api/assets/:id       # 删除资产
GET    /api/assets/statistics # 获取统计信息
```

更多API详见：[backend-node/README.md](README.md)

---

## ✅ 功能清单

- ✅ 用户注册登录（JWT认证）
- ✅ 分类管理
- ✅ 项目管理（虚拟资产）
- ✅ 固定资产管理
- ✅ 折旧计算（直线法、双倍余额递减法）
- ✅ 收入记录管理
- ✅ 维护记录管理
- ✅ 统计分析
- ✅ 管理员功能
- ✅ AI报告（基础框架）

---

## 🔐 默认账号

- 用户名：`admin`
- 密码：`admin123`
- 角色：管理员

**⚠️ 首次登录后请立即修改密码！**

---

## 📊 技术特性

- **后端框架**：Express.js
- **数据库**：PostgreSQL with SSL
- **认证方式**：JWT（30天有效期）
- **密码加密**：bcrypt（10轮加盐）
- **连接池**：最大20个连接
- **API规范**：RESTful
- **日志**：Morgan

---

## 🚀 生产部署建议

1. **使用PM2管理进程**
   ```bash
   npm install -g pm2
   pm2 start server.js --name timevalue
   pm2 startup
   pm2 save
   ```

2. **配置Nginx反向代理**
   ```nginx
   location /api {
       proxy_pass http://localhost:5000;
   }
   ```

3. **修改JWT密钥**
   编辑 `.env` 文件中的 `JWT_SECRET_KEY`

4. **开放端口**
   - 3000（前端）
   - 5000（后端）

---

## 🆘 常见问题

### Q: 数据库连接失败？
A: 检查 `.env` 文件配置，确认网络连接

### Q: 端口被占用？
A: 修改 `.env` 中的 `PORT` 值

### Q: 迁移脚本运行失败？
A: 检查数据库连接，确保数据库为空或手动清理表

---

**Powered by 孚普科技（北京）有限公司**  
🤖 AI驱动的MVP快速迭代解决方案
