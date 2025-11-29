# TimeValue Node.js + PostgreSQL 部署指南

## 🎯 技术栈迁移完成

- ✅ 后端：Python Flask → **Node.js Express**
- ✅ 数据库：SQLite → **PostgreSQL**
- ✅ 前端：React（保持不变）
- ✅ 认证：JWT（保持不变）

---

## 📦 部署步骤

### 1. 安装依赖

```bash
cd backend-node
npm install
```

### 2. 配置环境变量

编辑 `backend-node/.env` 文件（已配置好阿里云PostgreSQL连接）：

```env
DB_HOST=pgm-2ze3rv37e804623iqo.pg.rds.aliyuncs.com
DB_PORT=1432
DB_NAME=wangyongqing_test
DB_USER=wangyongqing
DB_PASSWORD=!@Wangyongqing
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

### 3. 初始化数据库

```bash
cd backend-node
npm run migrate
```

这将：
- 创建所有数据表
- 创建默认管理员用户（admin/admin123）

### 4. 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
# 在项目根目录
chmod +x start_production_node.sh
./start_production_node.sh

# 首次部署，安装依赖
./start_production_node.sh --install
```

#### 方式二：手动启动

```bash
# 启动后端
cd backend-node
node server.js

# 启动前端（新终端）
cd frontend
npm run dev
```

---

## 🗄️ 数据库表结构

已创建以下表：

- `users` - 用户表
- `categories` - 分类表
- `projects` - 项目表（虚拟资产）
- `fixed_assets` - 固定资产表
- `asset_income` - 资产收入表
- `asset_maintenance` - 维护记录表
- `maintenance_reminders` - 维护提醒表
- `ai_reports` - AI报告表
- `nginx_configs` - Nginx配置表

---

## 🔌 API接口

所有API路径保持不变，前端无需修改：

### 认证相关 `/api/auth`
- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录
- GET `/api/auth/profile` - 获取用户信息
- PUT `/api/auth/profile` - 更新用户信息
- GET `/api/auth/check-token` - 验证Token

### 分类管理 `/api/categories`
- GET `/api/categories` - 获取分类列表
- POST `/api/categories` - 创建分类
- PUT `/api/categories/:id` - 更新分类
- DELETE `/api/categories/:id` - 删除分类

### 项目管理 `/api/projects`
- GET `/api/projects` - 获取项目列表
- POST `/api/projects` - 创建项目
- GET `/api/projects/:id` - 获取项目详情
- PUT `/api/projects/:id` - 更新项目
- DELETE `/api/projects/:id` - 删除项目
- POST `/api/projects/batch-delete` - 批量删除
- GET `/api/projects/:id/calculate` - 计算项目价值
- GET `/api/statistics` - 获取统计数据

### 资产管理 `/api/assets`
- GET `/api/assets` - 获取资产列表
- POST `/api/assets` - 创建资产
- GET `/api/assets/:id` - 获取资产详情
- PUT `/api/assets/:id` - 更新资产
- DELETE `/api/assets/:id` - 删除资产
- POST `/api/assets/batch-delete` - 批量删除
- GET `/api/assets/:id/depreciation` - 获取折旧详情
- GET `/api/assets/statistics` - 获取统计信息

### 收入管理 `/api/income`
- GET `/api/income/:assetId` - 获取收入记录
- POST `/api/income` - 创建收入记录
- DELETE `/api/income/:id` - 删除收入记录

### 维护管理 `/api/maintenance`
- GET `/api/maintenance/:assetId` - 获取维护记录
- POST `/api/maintenance` - 创建维护记录
- DELETE `/api/maintenance/:id` - 删除维护记录

### 分析相关 `/api/analytics`
- GET `/api/analytics/overview` - 概览统计
- GET `/api/analytics/trends` - 趋势分析
- GET `/api/analytics/category-analysis` - 分类分析

### 管理员 `/api/admin`
- GET `/api/admin/users` - 获取所有用户
- PUT `/api/admin/users/:id/status` - 更新用户状态

### AI报告 `/api/reports`
- GET `/api/reports` - 获取报告列表
- POST `/api/reports` - 创建报告
- GET `/api/reports/:id` - 获取报告详情
- DELETE `/api/reports/:id` - 删除报告

---

## 🔐 安全配置

1. **修改JWT密钥**
   编辑 `.env` 文件中的 `JWT_SECRET_KEY`

2. **数据库安全**
   - 已配置SSL连接
   - 使用参数化查询防止SQL注入
   - 密码使用bcrypt加密

3. **阿里云安全组**
   - 开放端口：3000（前端）、5000（后端）
   - PostgreSQL端口1432已在阿里云内网

---

## 📊 性能优化

1. **数据库连接池**
   - 最大连接数：20
   - 空闲超时：30秒
   - 连接超时：2秒

2. **索引优化**
   - 已在用户名、邮箱、分类、项目等关键字段创建索引

3. **生产环境建议**
   - 使用PM2管理Node.js进程
   - 配置Nginx反向代理
   - 启用HTTPS

---

## 🚀 PM2部署（推荐）

```bash
# 安装PM2
npm install -g pm2

# 启动后端
cd backend-node
pm2 start server.js --name timevalue-backend

# 查看状态
pm2 status

# 查看日志
pm2 logs timevalue-backend

# 设置开机自启
pm2 startup
pm2 save
```

---

## 🔄 从Python迁移数据（可选）

如果需要从SQLite迁移数据到PostgreSQL：

```bash
# 1. 导出SQLite数据
sqlite3 data/timevalue.db .dump > backup.sql

# 2. 转换并导入PostgreSQL
# （需要手动处理一些SQLite特有语法）
```

---

## 📝 环境变量说明

```env
PORT=5000                    # 后端端口
NODE_ENV=production          # 运行环境
DB_HOST=                     # PostgreSQL主机
DB_PORT=1432                 # PostgreSQL端口
DB_NAME=                     # 数据库名
DB_USER=                     # 数据库用户
DB_PASSWORD=                 # 数据库密码
JWT_SECRET_KEY=              # JWT密钥
CORS_ORIGIN=*                # CORS设置
```

---

## ✅ 验证部署

1. **检查后端**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **检查数据库连接**
   - 运行迁移脚本成功
   - 可以登录（admin/admin123）

3. **检查前端**
   - 访问 http://localhost:3000
   - 能够正常登录和使用

---

## 🆘 故障排查

### 数据库连接失败
- 检查 `.env` 文件中的数据库配置
- 确认阿里云白名单已添加服务器IP
- 检查网络连接

### 端口被占用
```bash
# 查看端口占用
netstat -tlnp | grep :5000
netstat -tlnp | grep :3000

# 终止进程
kill -9 <PID>
```

### 依赖安装失败
```bash
# 清理并重装
rm -rf node_modules package-lock.json
npm install
```

---

**Powered by 孚普科技（北京）有限公司**  
🤖 AI驱动的MVP快速迭代解决方案
