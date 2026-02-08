# 微信公众号配置信息

## 基本信息

- **公众号ID**: `gh_800f188b43b5`
- **AppID**: `wx7dc28fa1552c069e`
- **登录邮箱**: `wangyongqing@fupukeji.com`

## 配置步骤

### 1. 获取AppSecret

1. 登录[微信公众平台](https://mp.weixin.qq.com/)
2. 进入：设置与开发 → 基本配置 → 开发者密码(AppSecret)
3. 点击"重置"或"生成"按钮获取AppSecret
4. **立即复制保存**（只显示一次）

### 2. 配置服务器域名

#### 2.1 JS接口安全域名

路径：设置与开发 → 公众号设置 → 功能设置 → JS接口安全域名

需要配置：
```
your-domain.com
```

注意：
- 不要加 `http://` 或 `https://`
- 不要加端口号
- 需要下载验证文件并上传到网站根目录

#### 2.2 网页授权域名

路径：设置与开发 → 公众号设置 → 功能设置 → 网页授权域名

需要配置：
```
your-domain.com
```

注意：
- 同样需要下载验证文件
- 此域名用于微信登录回调

### 3. 配置服务器地址（可选）

路径：设置与开发 → 基本配置 → 服务器配置

- **URL**: `https://your-domain.com/api/wechat/verify`
- **Token**: `timevalue_wechat_2026`（或自定义）
- **EncodingAESKey**: 点击"随机生成"
- **消息加解密方式**: 明文模式

### 4. 更新backend/.env文件

复制 `.env.example` 为 `.env`：

```bash
cd backend
cp .env.example .env
```

然后编辑 `.env`，填入AppSecret：

```env
# 微信公众号配置
# 公众号ID: gh_800f188b43b5
# 登录邮箱: wangyongqing@fupukeji.com
WECHAT_APPID=wx7dc28fa1552c069e
WECHAT_SECRET=在这里填入您的AppSecret
WECHAT_TOKEN=timevalue_wechat_2026
```

## 快速检查清单

部署前请确认以下项目：

- [ ] 已获取AppSecret并配置到 `backend/.env`
- [ ] 已配置JS接口安全域名
- [ ] 已配置网页授权域名
- [ ] 域名验证文件已上传
- [ ] 使用HTTPS（生产环境必须）
- [ ] 防火墙已开放443端口
- [ ] 已执行数据库迁移脚本

## 测试方法

### 本地测试

使用微信开发者工具：

1. 下载[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 选择"公众号网页调试"
3. 输入URL：`http://localhost:3001`
4. 测试登录流程

### 真机测试

1. 确保手机和电脑在同一局域网
2. 访问：`http://你的电脑IP:3001`
3. 用微信扫码测试

### 生产环境测试

1. 部署到服务器
2. 配置好域名和SSL
3. 微信扫码访问：`https://your-domain.com`

## 常见问题

### Q1: 如何获取AppSecret？

A: 登录微信公众平台 → 基本配置 → AppSecret → 重置/生成

### Q2: 域名验证文件放哪里？

A: 
- 如果使用Nginx，放在 `/var/www/timevalue/h5/dist/` 目录
- 验证URL应该能访问：`http://your-domain.com/MP_verify_xxx.txt`

### Q3: 测试环境如何配置？

A: 可以在微信公众平台的"开发者工具"中配置测试白名单，添加开发者的微信号

## 安全建议

1. ✅ **不要将AppSecret提交到Git**（`.env`文件已加入`.gitignore`）
2. ✅ **定期更换AppSecret**
3. ✅ **使用环境变量管理敏感信息**
4. ✅ **生产环境必须使用HTTPS**
5. ✅ **限制服务器访问IP（如有必要）**

## 联系支持

如有问题，请联系：
- **邮箱**: wangyongqing@fupukeji.com
- **公司**: 孚普科技（北京）有限公司
