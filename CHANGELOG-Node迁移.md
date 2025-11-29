# 更新日志 - Node.js迁移版本

## [1.1.0] - 2025-11-29

### 🎉 重大变更

#### 后端技术栈迁移
- ✅ **Python Flask → Node.js Express**
  - 统一使用JavaScript技术栈
  - 部署更简单，无需Python环境
  - 性能优秀，异步I/O处理

#### 数据库升级
- ✅ **SQLite → PostgreSQL**
  - 数据库：阿里云RDS PostgreSQL
  - 支持高并发访问
  - 生产级可靠性
  - 主机：pgm-2ze3rv37e804623iqo.pg.rds.aliyuncs.com
  - 端口：1432

### ✨ 新增功能

1. **完整的Node.js后端实现**
   - 19个核心文件
   - 40+个API接口
   - 完整的JWT认证系统
   - 管理员权限控制

2. **数据库迁移脚本**
   - 自动创建9张表
   - 自动创建索引
   - 自动创建默认管理员（admin/admin123）

3. **部署工具**
   - `start_production_node.sh` - 一键启动脚本
   - `verify_deployment.sh` - 部署验证脚本
   - `.env.example` - 环境变量模板

4. **完整文档**
   - Node.js后端技术文档
   - 快速开始指南
   - 部署指南（中文）
   - 前端配置说明

### 🔧 修复

1. **路由冲突修复**
   - 问题：`/api/assets/statistics` 被 `/api/assets/:id` 匹配
   - 解决：调整路由顺序，具体路由在前，通配路由在后

2. **数据库连接修复**
   - 问题：阿里云RDS不支持SSL连接
   - 解决：禁用SSL配置（`ssl: false`）

### 📝 API兼容性

#### 完全兼容原Python后端API
- ✅ 相同的路由路径（`/api/*`）
- ✅ 相同的请求参数
- ✅ 相同的响应格式
- ✅ 相同的错误处理
- ✅ **前端代码零改动**

#### 核心业务逻辑保持一致
- ✅ 项目价值计算（基于时间流逝）
- ✅ 资产折旧计算（直线法、双倍余额递减法）
- ✅ 统计分析
- ✅ AI报告生成接口（预留）

### 🔐 安全性增强

1. **密码加密**
   - 使用bcrypt（10轮加盐）
   - 符合现代安全标准

2. **JWT认证**
   - 30天有效期
   - 自动刷新机制
   - 支持Token验证

3. **权限控制**
   - 普通用户权限
   - 管理员权限
   - 数据隔离（user_id）

### 📊 性能优化

1. **数据库连接池**
   - 最大连接数：20
   - 空闲超时：30秒
   - 连接超时：2秒

2. **异步处理**
   - 全部使用async/await
   - 非阻塞I/O
   - 并发性能优秀

### 🗃️ 数据库结构

创建了9张核心表：
1. `users` - 用户表
2. `categories` - 分类表
3. `projects` - 项目表
4. `fixed_assets` - 固定资产表
5. `asset_income` - 资产收入表
6. `asset_maintenance` - 资产维护记录表
7. `maintenance_reminders` - 维护提醒表
8. `ai_reports` - AI报告表
9. `nginx_configs` - NGINX配置表

### 📦 依赖管理

#### 后端核心依赖
```json
{
  "express": "^4.18.2",
  "pg": "^8.11.3",
  "bcrypt": "^5.1.1",
  "jsonwebtoken": "^9.0.2",
  "cors": "^2.8.5",
  "dotenv": "^16.3.1",
  "morgan": "^1.10.0",
  "dayjs": "^1.11.10"
}
```

#### 前端保持不变
- React 18.2.0
- Ant Design 5.12.8
- Axios 1.6.0
- ECharts 6.0.0

### 🚀 部署方式

#### 开发环境
```bash
# 后端
cd backend-node
npm install
npm run migrate
node server.js

# 前端
cd frontend
npm install
npm run dev
```

#### 生产环境
```bash
./start_production_node.sh
```

### 📝 文件变更统计

#### 新增文件（20+）
- `backend-node/` - 完整的Node.js后端目录
- `start_production_node.sh` - 生产环境启动脚本
- `verify_deployment.sh` - 部署验证脚本
- `部署指南-Node版本.md` - 中文部署指南
- `前端配置说明-Node版本.md` - 前端配置说明
- `NODEJS_MIGRATION_COMPLETE.md` - 迁移完成报告
- `CHANGELOG-Node迁移.md` - 更新日志

#### 修改文件
- `backend-node/config/database.js` - SSL配置修复
- `backend-node/routes/assets.js` - 路由顺序调整

#### 保留文件
- `backend/` - 原Python后端（保留作为参考）
- `frontend/` - 前端代码（无需修改）

### ⚠️ 注意事项

1. **默认管理员密码**
   - 用户名：admin
   - 密码：admin123
   - ⚠️ 生产环境请立即修改

2. **环境变量配置**
   - 复制 `.env.example` 到 `.env`
   - 修改数据库连接信息
   - 修改JWT密钥

3. **数据库连接**
   - 确保PostgreSQL可访问
   - 检查防火墙设置
   - 验证连接参数

### 🎯 下一步计划

- [ ] 添加单元测试
- [ ] 添加集成测试
- [ ] 性能基准测试
- [ ] API文档生成（Swagger）
- [ ] Docker容器化部署
- [ ] CI/CD流水线配置
- [ ] 监控和日志系统

### 🙏 致谢

- **孚普科技（北京）有限公司** - 项目支持
- **阿里云** - RDS PostgreSQL服务
- **Node.js社区** - 优秀的生态系统

---

💰 **恒产生金 - 让每一份资产都创造价值**
🏢 Powered by 孚普科技（北京）有限公司
🤖 AI驱动的MVP快速迭代解决方案
