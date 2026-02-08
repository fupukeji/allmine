# TimeValue H5 快速启动指南

## 📌 您的微信公众号信息

```
公众号ID:   gh_800f188b43b5
AppID:      wx7dc28fa1552c069e
登录邮箱:   wangyongqing@fupukeji.com
```

## 🌟 **微信云托管部署（推荐）**

您已经申请了腾讯云CloudBase，可以直接部署后端。

### 微信云托管信息

```
环境ID:    prod-4gqjqr6g0c81bd5a
服务名称:  flask-rvx7
域名地址:  https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
```

### 部署步骤

#### 1. 配置云托管环境变量

在微信云托管控制台：

1. 进入服务配置 → 环境变量
2. 添加以下配置：

```env
# 微信公众号配置
WECHAT_APPID=wx7dc28fa1552c069e
WECHAT_SECRET=您的AppSecret
WECHAT_TOKEN=timevalue_wechat_2026

# 数据库配置
DB_TYPE=mysql
DB_HOST=60.205.161.210
DB_PORT=3306
DB_NAME=timevalue
DB_USER=timevalue
DB_PASSWORD=GX3sAXJzabZpCidp

# Flask配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
JWT_SECRET_KEY=your-production-jwt-secret-key-change-this

# CORS配置
CORS_ORIGINS=https://your-h5-domain.com
```

#### 2. 使用GitHub部署

**方式一：命令行部署**

```bash
# 1. 安装微信云托管CLI
npm install -g @cloudbase/cli

# 2. 登录
cloudbase login

# 3. 初始化配置
cd backend
cloudbase init --without-template

# 4. 部署
cloudbase run deploy --envId prod-4gqjqr6g0c81bd5a
```

**方式二：GitHub自动部署**

1. 将项目推送到GitHub
2. 在微信云托管控制台：
   - 点击“服务配置” → “持续集成”
   - 绑定GitHub仓库
   - 选择分支（main或master）
   - 设置构建目录：`backend`
3. 每次Push代码后自动部署

#### 3. 更新H5前端配置

编辑 `h5/.env.production`：

```env
# 使用云托管域名
VITE_API_BASE_URL=https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
VITE_WECHAT_APPID=wx7dc28fa1552c069e
VITE_ENV=production
```

#### 4. 测试接口

```bash
# 健康检查
curl https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com/api/health

# 预期返回：{"status": "healthy"}
```

---

## 🚀 **快速启动（3步）**

### 步骤1：获取微信AppSecret

1. 访问 https://mp.weixin.qq.com/
2. 使用邮箱 `wangyongqing@fupukeji.com` 登录
3. 进入：**设置与开发** → **基本配置** → **开发者密码(AppSecret)**
4. 点击"重置"或"生成"，**立即复制保存**（只显示一次）

### 步骤2：配置后端环境变量

```bash
# 进入后端目录
cd backend

# 复制环境变量模板（Windows PowerShell）
Copy-Item .env.example .env

# 编辑 .env 文件，填入AppSecret
# WECHAT_SECRET=粘贴您刚才复制的AppSecret
```

**backend/.env 配置示例**：
```env
# 微信公众号配置
WECHAT_APPID=wx7dc28fa1552c069e
WECHAT_SECRET=你的AppSecret在这里
WECHAT_TOKEN=timevalue_wechat_2026
```

### 步骤3：启动项目

**方式一：使用启动脚本（推荐）**
```bash
# 双击运行
start_h5.bat
```

**方式二：手动启动**
```bash
# 终端1 - 启动后端
cd backend
python app.py

# 终端2 - 启动H5前端
cd h5
npm install
npm run dev
```

## ✅ 验证启动成功

访问以下地址验证：

- **后端健康检查**: http://localhost:5000/api/health
  - 预期响应：`{"status": "healthy"}`

- **H5前端**: http://localhost:3001
  - 预期显示：微信登录页面

## 📱 本地微信测试

### 使用微信开发者工具

1. 下载 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 启动后选择 **公众号网页调试**
3. 输入URL: `http://localhost:3001`
4. 测试登录流程

### 真机测试（局域网）

1. 查看电脑IP地址：
   ```bash
   # Windows
   ipconfig | findstr IPv4
   ```

2. 手机连接同一WiFi

3. 微信扫码访问：`http://你的电脑IP:3001`

## 🔧 数据库迁移

**首次启动前需要执行**：

```bash
cd backend
python migrate_add_wechat_fields.py
```

预期输出：
```
开始数据库迁移：添加微信字段...
添加字段：wechat_openid, wechat_unionid, wechat_nickname, wechat_avatar
✅ 迁移成功！微信字段已添加
```

## 🌐 生产环境部署

### 前置条件

1. **获取域名并备案**（中国大陆服务器）
2. **配置SSL证书**（微信要求HTTPS）
3. **配置微信公众号域名**（详见下方）

### 微信公众号域名配置

#### 1. JS接口安全域名

路径：**设置与开发** → **公众号设置** → **功能设置** → **JS接口安全域名**

```
your-domain.com  (不要加http://和端口号)
```

#### 2. 网页授权域名

路径：**设置与开发** → **公众号设置** → **功能设置** → **网页授权域名**

```
your-domain.com  (不要加http://和端口号)
```

**注意**：两个域名配置都需要：
- 下载验证文件（如：`MP_verify_xxx.txt`）
- 上传到网站根目录（`/var/www/timevalue/h5/dist/`）
- 确保可访问：`https://your-domain.com/MP_verify_xxx.txt`

### 构建和部署

```bash
# 1. 构建H5前端
cd h5
npm run build

# 2. 上传 h5/dist 目录到服务器
# 3. 配置Nginx（详见 H5_DEPLOYMENT_GUIDE.md）
# 4. 启动后端服务
cd backend
pm2 start gunicorn --name timevalue-backend -- -c gunicorn.conf.py app:app
```

## 📚 详细文档

- **H5项目说明**: [h5/README.md](h5/README.md)
- **完整部署指南**: [H5_DEPLOYMENT_GUIDE.md](H5_DEPLOYMENT_GUIDE.md)
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **微信配置指南**: [backend/WECHAT_CONFIG.md](backend/WECHAT_CONFIG.md)

## ❓ 常见问题

### Q1: 启动后端报错 "No module named 'xxx'"

**解决**：安装Python依赖
```bash
cd backend
pip install -r requirements.txt
```

### Q2: H5启动报错 "Cannot find module"

**解决**：安装Node依赖
```bash
cd h5
npm install
```

### Q3: 微信登录提示 "redirect_uri参数错误"

**原因**：网页授权域名未配置或配置错误

**解决**：
1. 检查微信公众号后台的"网页授权域名"
2. 确保域名与实际访问域名一致（不含http://和端口）
3. 确保验证文件已上传且可访问

### Q4: 本地测试微信登录失败

**原因**：微信公众号只能在配置的域名下工作

**解决**：
1. 使用微信开发者工具测试
2. 或配置内网穿透工具（如ngrok）
3. 或在测试白名单添加开发者微信号

### Q5: 数据库连接失败

**检查**：
1. MySQL服务是否运行
2. backend/.env 中的数据库配置是否正确
3. 数据库用户是否有权限

## 🎯 下一步

- [ ] 获取微信AppSecret
- [ ] 配置backend/.env文件
- [ ] 执行数据库迁移
- [ ] 启动项目测试
- [ ] 开发业务页面（虚拟资产、固定资产等）
- [ ] 生产环境部署

## 📞 技术支持

- **邮箱**: wangyongqing@fupukeji.com
- **公司**: 孚普科技（北京）有限公司

---

**祝您使用愉快！** 🎉
