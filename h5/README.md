# TimeValue H5移动端

> 微信公众号H5版本 - AI驱动的个人资产管理系统

## 📱 项目简介

这是TimeValue的H5移动端项目，专为微信公众号环境设计，支持微信授权登录、分享、扫码等功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd h5
npm install
```

### 2. 配置环境变量

编辑 `.env` 文件，填写您的微信公众号AppID：

```env
VITE_WECHAT_APPID=您的微信公众号AppID
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:3001

### 4. 构建生产版本

```bash
npm run build
```

## 📂 项目结构

```
h5/
├── src/
│   ├── pages/              # 页面组件
│   │   ├── Dashboard.jsx       # 首页
│   │   ├── WeChatLogin.jsx     # 微信登录页
│   │   ├── WeChatCallback.jsx  # 微信登录回调
│   │   ├── VirtualAssets.jsx   # 虚拟资产
│   │   ├── FixedAssets.jsx     # 固定资产
│   │   ├── Reports.jsx         # AI报告
│   │   └── Profile.jsx         # 个人中心
│   ├── layouts/            # 布局组件
│   │   └── MobileLayout.jsx    # 移动端布局（底部Tab）
│   ├── components/         # 通用组件
│   ├── utils/              # 工具函数
│   │   ├── wechat.js          # 微信SDK封装
│   │   └── request.js         # HTTP请求封装
│   ├── services/           # API服务
│   │   └── auth.js            # 认证相关API
│   ├── assets/             # 静态资源
│   ├── App.jsx             # 根组件
│   ├── main.jsx            # 入口文件
│   └── index.css           # 全局样式
├── public/                 # 公共资源
│   └── logo.jpg           # Logo图片
├── index.html             # HTML模板
├── package.json           # 依赖配置
├── vite.config.js        # Vite配置
├── .env                   # 环境变量
└── README.md             # 项目文档
```

## ✨ 核心功能

### 1. 微信登录

- ✅ 自动检测微信浏览器环境
- ✅ 微信授权登录（snsapi_userinfo）
- ✅ Token自动管理
- ✅ 登录状态持久化

### 2. 微信SDK集成

- ✅ 分享到朋友圈/好友
- ✅ 图片选择/预览
- ✅ 地理位置获取
- ✅ 扫一扫功能

### 3. 移动端UI

- ✅ Ant Design Mobile组件库
- ✅ 底部Tab导航
- ✅ 响应式布局
- ✅ iOS安全区域适配
- ✅ 触摸手势优化

### 4. PWA支持

- ✅ 可添加到主屏幕
- ✅ 离线缓存
- ✅ App体验

## 🔧 后端接口要求

H5端需要后端提供以下接口：

### 1. 微信JSSDK配置接口

```
GET /api/wechat/jssdk-config?url={当前页面URL}

响应:
{
  "code": 200,
  "data": {
    "appId": "微信AppID",
    "timestamp": 1234567890,
    "nonceStr": "随机字符串",
    "signature": "签名"
  }
}
```

### 2. 微信登录接口

```
POST /api/wechat/login
请求体: { "code": "微信授权码", "state": "STATE" }

响应:
{
  "code": 200,
  "data": {
    "token": "JWT Token",
    "user": {
      "id": 1,
      "username": "用户名",
      "email": "邮箱"
    }
  }
}
```

## 📱 微信公众号配置

### 1. 设置JS接口安全域名

在微信公众号后台:
- 进入"设置与开发" → "公众号设置" → "功能设置"
- 设置"JS接口安全域名": `your-domain.com`

### 2. 设置网页授权域名

- 进入"设置与开发" → "公众号设置" → "功能设置"
- 设置"网页授权域名": `your-domain.com`

### 3. 获取AppID和AppSecret

- 进入"设置与开发" → "基本配置"
- 记录AppID和AppSecret

## 🌐 部署指南

### 方式一：使用Nginx部署

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # H5前端
    location / {
        root /path/to/h5/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 方式二：使用Docker部署

参考主项目的 `docker-compose.yml` 配置。

## 🔍 调试技巧

### 1. 微信开发者工具调试

- 下载[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- 使用"公众号网页调试"功能

### 2. 真机调试

- 使用[微信Web开发者工具](https://mp.weixin.qq.com/debug/wxadoc/dev/devtools/download.html)
- 或使用 vConsole 调试:

```javascript
// 在开发环境引入
import VConsole from 'vconsole'
if (import.meta.env.DEV) {
  new VConsole()
}
```

## ⚠️ 注意事项

1. **微信环境要求**: 本H5应用需要在微信浏览器中运行，非微信环境会提示用户
2. **HTTPS要求**: 微信JS-SDK要求生产环境必须使用HTTPS
3. **AppID配置**: 记得在 `.env` 中配置正确的微信AppID
4. **后端接口**: 确保后端已实现微信登录和JSSDK配置接口
5. **域名白名单**: 确保域名已在微信公众号后台配置

## 📞 技术支持

- 🌐 官网: https://fupukeji.com
- 📧 邮箱: contact@fupukeji.com
- 💬 孚普科技（北京）有限公司

## 📄 许可证

MIT License
