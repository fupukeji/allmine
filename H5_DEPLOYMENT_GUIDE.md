# TimeValue H5 + 后端部署完整指南

## 📋 项目概述

TimeValue H5版本已完成重构，包含：
- ✅ **H5前端**：独立的微信公众号H5应用（`/h5`目录）
- ✅ **后端接口**：微信登录、JSSDK配置等接口
- ✅ **数据库**：User模型已扩展微信字段

## 🚀 快速部署流程

### 一、准备工作

#### 1.1 微信公众号准备

登录[微信公众平台](https://mp.weixin.qq.com/)，获取以下信息：

```
AppID: wx1234567890abcdef
AppSecret: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

#### 1.2 配置微信公众号

**设置JS接口安全域名**：
- 路径：设置与开发 → 公众号设置 → 功能设置 → JS接口安全域名
- 填写：`your-domain.com`（不带http://）

**设置网页授权域名**：
- 路径：设置与开发 → 公众号设置 → 功能设置 → 网页授权域名
- 填写：`your-domain.com`

### 二、后端配置

#### 2.1 配置环境变量

编辑 `backend/.env` 文件：

```bash
# 微信公众号配置
WECHAT_APPID=wx1234567890abcdef
WECHAT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
WECHAT_TOKEN=your_random_token_here

# 其他配置保持不变...
```

#### 2.2 数据库迁移

执行迁移脚本，为User表添加微信字段：

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

#### 2.3 启动后端服务

```bash
cd backend
python app.py
```

验证接口：
- 健康检查：http://localhost:5000/api/health
- 微信JSSDK配置：http://localhost:5000/api/wechat/jssdk-config?url=http://test.com

### 三、H5前端配置

#### 3.1 安装依赖

```bash
cd h5
npm install
```

#### 3.2 配置环境变量

编辑 `h5/.env` 文件：

```env
# 微信公众号AppID
VITE_WECHAT_APPID=wx1234567890abcdef

# API基础地址（本地开发）
VITE_API_BASE_URL=/api

# 环境标识
VITE_ENV=development
```

#### 3.3 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:3001

#### 3.4 生产构建

```bash
npm run build
```

构建产物在 `h5/dist` 目录。

### 四、生产环境部署

#### 4.1 Nginx配置示例

创建 `/etc/nginx/sites-available/timevalue`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 强制HTTPS（微信要求）
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # H5前端（根目录）
    location / {
        root /var/www/timevalue/h5/dist;
        try_files $uri $uri/ /index.html;
        
        # 移动端优化
        add_header Cache-Control "no-cache, must-revalidate";
        add_header X-Content-Type-Options nosniff;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS（如果需要）
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
    }
    
    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        root /var/www/timevalue/h5/dist;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 4.2 使用PM2管理后端

```bash
# 安装PM2
npm install -g pm2

# 启动后端
cd backend
pm2 start gunicorn --name timevalue-backend -- -c gunicorn.conf.py app:app

# 设置开机自启
pm2 startup
pm2 save
```

#### 4.3 部署检查清单

- [ ] 域名已备案（中国大陆）
- [ ] SSL证书已配置（微信要求HTTPS）
- [ ] 微信公众号域名已配置
- [ ] 后端环境变量已设置
- [ ] 数据库迁移已执行
- [ ] H5前端已构建并部署
- [ ] Nginx配置已生效
- [ ] 防火墙已开放443端口

### 五、功能测试

#### 5.1 本地测试（使用微信开发者工具）

1. 下载[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 选择"公众号网页调试"
3. 输入URL：http://localhost:3001
4. 测试登录流程

#### 5.2 真机测试

1. 将本地IP加入微信公众号测试白名单
2. 用微信扫码访问：http://your-local-ip:3001
3. 测试完整登录流程

#### 5.3 生产环境测试

1. 微信扫码访问：https://your-domain.com
2. 完成授权登录
3. 测试主要功能

### 六、接口文档

#### 6.1 微信JSSDK配置

**请求**：
```
GET /api/wechat/jssdk-config?url={当前页面完整URL}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "appId": "wx1234567890abcdef",
    "timestamp": 1672531200,
    "nonceStr": "abc123def456",
    "signature": "a1b2c3d4e5f6..."
  }
}
```

#### 6.2 微信登录

**请求**：
```
POST /api/wechat/login
Content-Type: application/json

{
  "code": "071AbCdEf123456",
  "state": "STATE"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJh...",
    "user": {
      "id": 1,
      "username": "wx_12345678",
      "email": "o1234567890@wechat.user",
      "role": "user",
      "wechat_nickname": "张三",
      "wechat_avatar": "https://..."
    }
  }
}
```

### 七、常见问题

#### Q1: 微信授权后提示"redirect_uri参数错误"

**原因**：网页授权域名未配置或配置错误

**解决**：
1. 检查微信公众号后台的"网页授权域名"是否正确
2. 确保域名不包含http://和端口号
3. 确保回调地址的域名与配置的一致

#### Q2: JSSDK初始化失败

**原因**：JS接口安全域名未配置或签名错误

**解决**：
1. 检查"JS接口安全域名"是否配置
2. 确保后端获取的access_token和jsapi_ticket有效
3. 检查签名算法是否正确（参数字典序、URL完整性）

#### Q3: 生产环境无法登录

**原因**：未使用HTTPS

**解决**：微信公众号网页授权要求生产环境必须使用HTTPS

#### Q4: 登录后token失效

**原因**：JWT配置问题

**解决**：检查backend/.env中的JWT_SECRET_KEY是否设置且不变

### 八、监控与日志

#### 8.1 后端日志

查看后端日志：
```bash
# PM2日志
pm2 logs timevalue-backend

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### 8.2 前端错误监控

在H5中集成Sentry（可选）：

```javascript
// src/main.jsx
import * as Sentry from '@sentry/react'

if (import.meta.env.PROD) {
  Sentry.init({
    dsn: 'your-sentry-dsn',
    environment: 'production'
  })
}
```

### 九、性能优化

#### 9.1 前端优化

- ✅ 已配置路由懒加载
- ✅ 已配置代码分割（react-vendor, antd-mobile, utils）
- ✅ 已禁用sourcemap
- ⏳ 可添加CDN加速
- ⏳ 可添加图片懒加载

#### 9.2 后端优化

- ✅ 使用Gunicorn多进程
- ⏳ 添加Redis缓存（access_token、jsapi_ticket）
- ⏳ 添加数据库连接池优化

#### 9.3 缓存策略

**access_token和jsapi_ticket缓存**（推荐）：

```python
# backend/utils/wechat_cache.py
import redis
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_access_token():
    """从Redis获取缓存的access_token"""
    token = redis_client.get('wechat_access_token')
    if token:
        return token.decode('utf-8')
    
    # 如果没有缓存，重新获取并缓存2小时
    token = get_access_token()  # 原函数
    if token:
        redis_client.setex('wechat_access_token', 7000, token)
    return token
```

### 十、安全建议

1. ✅ **HTTPS**：生产环境必须使用HTTPS
2. ✅ **环境变量**：敏感信息通过环境变量配置
3. ⏳ **请求限流**：添加接口访问频率限制
4. ⏳ **日志脱敏**：避免记录敏感信息
5. ⏳ **XSS防护**：前端输出转义
6. ⏳ **CSRF防护**：添加CSRF token

### 十一、联系支持

- 🌐 官网：https://fupukeji.com
- 📧 邮箱：contact@fupukeji.com
- 💬 技术支持：孚普科技（北京）有限公司

---

**部署成功标志**：

✅ 后端服务正常运行（http://localhost:5000/api/health 返回200）
✅ H5前端可以访问（http://localhost:3001 显示登录页）
✅ 微信环境中可以完成授权登录
✅ 登录后可以正常访问首页和其他功能

**下一步**：继续开发虚拟资产、固定资产、AI报告等业务页面。
