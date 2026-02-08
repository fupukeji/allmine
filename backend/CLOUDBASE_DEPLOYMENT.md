# TimeValue 微信云托管部署指南

## 🌟 云托管优势

✅ **Serverless架构** - 按需付费，自动扩缩容  
✅ **与微信深度集成** - 天然支持微信公众号/小程序  
✅ **免运维** - 无需管理服务器，自动容灾  
✅ **快速部署** - 5分钟完成上线  
✅ **自带MySQL** - 免费的云数据库

---

## 📋 您的云托管信息

```
环境ID:      prod-4gqjqr6g0c81bd5a
服务名称:    flask-rvx7
域名地址:    https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
代码源:      GitHub - WeixinCloud/wxcloudrun-flask
```

---

## 🚀 部署方式选择

### 方式一：通过控制台部署（最简单）

#### 步骤1：准备代码

```bash
# 1. 将代码推送到GitHub
cd C:\Users\Administrator\Desktop\timevalue
git init
git add .
git commit -m "TimeValue初始提交"
git remote add origin https://github.com/你的用户名/timevalue.git
git push -u origin main
```

#### 步骤2：配置云托管环境变量

1. 访问 [微信云托管控制台](https://console.cloud.tencent.com/tcb/env/index?envId=prod-4gqjqr6g0c81bd5a)
2. 选择服务 `flask-rvx7`
3. 进入 **服务配置** → **环境变量**
4. 添加以下配置：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `WECHAT_APPID` | `wx7dc28fa1552c069e` | 微信公众号AppID |
| `WECHAT_SECRET` | `您的AppSecret` | ⚠️ 需要从微信公众平台获取 |
| `WECHAT_TOKEN` | `timevalue_wechat_2026` | 微信Token |
| `DB_TYPE` | `mysql` | 数据库类型 |
| `DB_HOST` | `60.205.161.210` | 宝塔服务器IP |
| `DB_PORT` | `3306` | 数据库端口 |
| `DB_NAME` | `timevalue` | 数据库名 |
| `DB_USER` | `timevalue` | 数据库用户 |
| `DB_PASSWORD` | `GX3sAXJzabZpCidp` | 数据库密码 |
| `FLASK_ENV` | `production` | Flask环境 |
| `FLASK_DEBUG` | `False` | 调试模式 |
| `SECRET_KEY` | `生成随机字符串` | Flask密钥 |
| `JWT_SECRET_KEY` | `生成随机字符串` | JWT密钥 |

**生成密钥方法**：
```python
import secrets
print(secrets.token_urlsafe(32))
```

#### 步骤3：配置持续集成

1. 在控制台点击 **服务配置** → **持续集成**
2. 选择 **绑定仓库**
3. 授权GitHub账号
4. 选择仓库：`你的用户名/timevalue`
5. 配置构建：
   - **构建目录**: `backend`
   - **Dockerfile路径**: `Dockerfile`
   - **分支**: `main`
6. 点击 **开启自动构建**

#### 步骤4：触发部署

```bash
# 修改任意文件并推送，触发自动部署
git commit --allow-empty -m "触发部署"
git push
```

---

### 方式二：使用CloudBase CLI部署（推荐开发者）

#### 步骤1：安装CLI

```bash
npm install -g @cloudbase/cli
```

#### 步骤2：登录

```bash
cloudbase login
```

会打开浏览器进行授权登录。

#### 步骤3：部署

```bash
cd backend

# 部署服务
cloudbase run deploy --envId prod-4gqjqr6g0c81bd5a
```

部署过程：
```
1. 构建Docker镜像
2. 推送到云托管镜像仓库
3. 创建/更新服务版本
4. 等待服务就绪
```

#### 步骤4：查看状态

```bash
# 查看服务状态
cloudbase run describe flask-rvx7 --envId prod-4gqjqr6g0c81bd5a

# 查看日志
cloudbase run logs flask-rvx7 --envId prod-4gqjqr6g0c81bd5a
```

---

## 🔍 部署验证

### 1. 健康检查

```bash
curl https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com/api/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2026-02-07T12:00:00Z"
}
```

### 2. 测试微信JSSDK配置接口

```bash
curl "https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com/api/wechat/jssdk-config?url=https://test.com"
```

预期响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "appId": "wx7dc28fa1552c069e",
    "timestamp": 1675756800,
    "nonceStr": "abc123",
    "signature": "..."
  }
}
```

### 3. 查看部署日志

在云托管控制台：
- 进入 **服务监控** → **实时日志**
- 查看应用启动和运行日志

---

## 📱 H5前端配置

### 更新H5环境变量

编辑 `h5/.env.production`：

```env
# 使用云托管域名
VITE_API_BASE_URL=https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
VITE_WECHAT_APPID=wx7dc28fa1552c069e
VITE_ENV=production
```

### 更新微信公众号配置

在微信公众平台（https://mp.weixin.qq.com/）：

1. **JS接口安全域名**：
   - 路径：设置与开发 → 公众号设置 → 功能设置
   - 添加：`flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com`

2. **网页授权域名**：
   - 同样添加：`flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com`

---

## 🗄️ 数据库管理

### 使用云托管内置数据库（推荐）

云托管提供免费的MySQL数据库：

1. 在控制台进入 **数据库** → **CloudBase MySQL**
2. 创建数据库实例（如已创建，跳过）
3. 更新环境变量：
   ```env
   DB_HOST=<云托管数据库地址>
   DB_PORT=3306
   DB_NAME=timevalue
   DB_USER=<自动生成>
   DB_PASSWORD=<自动生成>
   ```

### 或继续使用宝塔服务器数据库

如果继续使用现有宝塔数据库：

⚠️ **注意**：需要在宝塔防火墙开放3306端口，允许云托管IP访问。

---

## 📊 监控与日志

### 查看实时日志

```bash
# CLI方式
cloudbase run logs flask-rvx7 --envId prod-4gqjqr6g0c81bd5a --tail 100

# 或在控制台查看
# 服务监控 → 实时日志
```

### 查看性能监控

在控制台：
- **服务监控** → **性能监控**
- 查看CPU、内存、请求量等指标

### 设置告警

1. 进入 **服务监控** → **告警配置**
2. 添加告警规则：
   - CPU使用率 > 80%
   - 内存使用率 > 80%
   - 请求失败率 > 10%
3. 配置通知渠道（邮件/微信）

---

## 💰 成本预估

### 免费额度

- **计算资源**：每月0.5GB-s免费
- **流量**：每月1GB免费
- **数据库**：基础版免费

### 预估费用（中等流量）

| 资源 | 配置 | 月费用 |
|------|------|--------|
| 计算 | 0.25核0.5GB | ~10元 |
| 数据库 | 外部宝塔 | 0元 |
| 流量 | 10GB | ~2元 |
| **总计** | | **~12元/月** |

---

## 🔧 常见问题

### Q1: 部署失败，提示"镜像构建失败"

**原因**：依赖安装超时或网络问题

**解决**：
1. 检查Dockerfile中的镜像源配置
2. 确保requirements.txt中的依赖可安装
3. 查看构建日志定位具体错误

### Q2: 服务启动后无法访问

**原因**：端口配置错误或健康检查失败

**解决**：
1. 确认`containerPort: 5000`与应用监听端口一致
2. 检查健康检查路径 `/api/health` 是否可访问
3. 查看应用日志排查启动错误

### Q3: 数据库连接失败

**原因**：环境变量未配置或防火墙限制

**解决**：
1. 检查环境变量是否正确配置
2. 宝塔服务器需开放3306端口
3. 测试数据库连接：
   ```bash
   cloudbase run exec flask-rvx7 --envId prod-4gqjqr6g0c81bd5a -- python test_db_connection.py
   ```

### Q4: 如何回滚版本？

在控制台：
1. 进入 **版本管理**
2. 选择历史版本
3. 点击 **回滚**

---

## 🎯 下一步

- [ ] 推送代码到GitHub
- [ ] 配置云托管环境变量
- [ ] 设置持续集成
- [ ] 触发部署
- [ ] 验证接口可用性
- [ ] 配置微信公众号域名
- [ ] 部署H5前端
- [ ] 配置监控告警

---

## 📞 技术支持

- **微信云托管文档**: https://developers.weixin.qq.com/miniprogram/dev/wxcloud/guide/container/
- **CloudBase CLI**: https://docs.cloudbase.net/cli/intro.html
- **项目邮箱**: wangyongqing@fupukeji.com

---

**部署TimeValue到微信云托管，开启Serverless之旅！** 🚀
