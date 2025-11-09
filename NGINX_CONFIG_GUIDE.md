# Nginx动态配置管理功能说明

## 📋 功能概述

TimeValue系统现已支持**通过Web界面动态管理Nginx配置**，无需手动编辑配置文件。管理员可以在系统运行后，通过Web界面完成以下操作：

✅ 配置域名和端口
✅ 配置SSL证书（HTTPS）
✅ 配置反向代理规则
✅ 配置Gzip压缩、日志等高级选项
✅ 预览配置文件
✅ 一键应用配置并重载Nginx

---

## 🚀 快速开始

### 1. 首次部署准备

在ECS服务器上部署系统后，需要执行**一次性权限设置**：

```bash
# 切换到项目目录
cd /path/to/timevalue

# 以root权限运行权限设置脚本
sudo bash setup_nginx_permissions.sh
```

此脚本会自动完成：
- 创建Nginx配置目录
- 配置应用用户权限
- 设置sudo权限（允许应用重载Nginx）
- 安装Nginx（如未安装）
- 启动Nginx服务

### 2. 启动应用

权限设置完成后，**重新登录**以使组权限生效：

```bash
# 退出当前会话
exit

# 重新登录（替换为实际用户名）
su - your_username

# 启动应用
cd /path/to/timevalue
bash start_production.sh
```

### 3. 访问Nginx配置管理界面

1. 使用管理员账号登录系统（默认：admin/admin123）
2. 在左侧菜单中点击 **"Nginx配置"**
3. 即可进入配置管理界面

---

## 📝 使用指南

### 创建新配置

1. 点击 **"新建配置"** 按钮
2. 填写配置信息：
   - **基础配置**：服务器名称（域名）、监听端口
   - **SSL配置**：SSL证书路径、私钥路径、强制HTTPS
   - **代理配置**：前端端口、后端API端口
   - **高级配置**：上传大小限制、Gzip压缩、访问日志
3. （可选）添加自定义Nginx配置
4. 点击 **"创建配置"** 保存

### 预览配置

在配置列表中，点击 **"预览"** 按钮可以查看生成的Nginx配置文件内容。

### 应用配置

1. 点击 **"应用"** 按钮
2. 确认提示信息
3. 系统会自动：
   - 生成Nginx配置文件
   - 写入 `/etc/nginx/sites-available/timevalue.conf`
   - 创建软链接到 `/etc/nginx/sites-enabled/`
   - 测试配置是否有效
   - 重载Nginx服务

⚠️ **注意**：应用配置会短暂中断服务（通常小于1秒），请在低峰期操作。

---

## 🔧 配置示例

### 示例1：基础HTTP配置

```yaml
服务器名称: example.com
监听端口: 80
SSL启用: 否
前端端口: 3000
后端API端口: 5000
```

### 示例2：HTTPS配置（带强制跳转）

```yaml
服务器名称: example.com
监听端口: 80
SSL启用: 是
SSL端口: 443
SSL证书路径: /etc/ssl/certs/example.com.pem
SSL私钥路径: /etc/ssl/private/example.com.key
强制HTTPS: 是
```

### 示例3：自定义配置

在 **"自定义配置"** 文本框中添加：

```nginx
location /static/ {
    alias /var/www/static/;
    expires 30d;
}

location /downloads/ {
    alias /var/www/downloads/;
    autoindex on;
}
```

---

## 🔐 SSL证书配置

### 获取SSL证书

**方案1：Let's Encrypt免费证书**

```bash
# 安装certbot
sudo apt-get install certbot  # Ubuntu/Debian
sudo yum install certbot       # CentOS/RHEL

# 申请证书
sudo certbot certonly --standalone -d example.com

# 证书路径（自动生成）：
# 证书: /etc/letsencrypt/live/example.com/fullchain.pem
# 私钥: /etc/letsencrypt/live/example.com/privkey.pem
```

**方案2：阿里云SSL证书**

1. 在阿里云控制台申请SSL证书
2. 下载证书文件（Nginx格式）
3. 上传到ECS服务器，建议路径：
   - 证书：`/etc/ssl/certs/your-domain.pem`
   - 私钥：`/etc/ssl/private/your-domain.key`

### 在Web界面配置SSL

1. 创建新配置或编辑现有配置
2. 开启 **"启用SSL"** 开关
3. 填写证书路径和私钥路径
4. （推荐）开启 **"强制HTTPS"**
5. 预览并应用配置

---

## 🛠️ 技术架构

### 后端实现

- **模型**：`models/nginx_config.py` - Nginx配置数据模型
- **路由**：`routes/nginx.py` - Nginx配置管理API
- **权限**：仅管理员可应用配置
- **安全**：使用sudo执行nginx命令（配置在sudoers.d）

### 前端实现

- **页面**：`pages/NginxConfig.jsx` - 配置管理界面
- **路由**：`/nginx`（仅管理员可访问）
- **功能**：表单配置、预览、应用、状态监控

### 文件路径

```
/etc/nginx/sites-available/timevalue.conf  # Nginx配置文件
/etc/nginx/sites-enabled/timevalue.conf    # 软链接
/etc/sudoers.d/timevalue-nginx            # sudo权限配置
```

---

## ⚠️ 注意事项

### 权限要求

- 应用用户必须在 `timevalue` 用户组中
- 必须配置sudo权限（通过setup_nginx_permissions.sh）
- 用户需重新登录才能使组权限生效

### 安全建议

1. **限制管理员账号**：只给可信用户分配管理员角色
2. **定期备份配置**：重要配置应手动备份
3. **测试后再应用**：应用前先预览配置，确保正确性
4. **SSL证书安全**：私钥文件权限应设为600

```bash
# 设置私钥文件权限
sudo chmod 600 /etc/ssl/private/your-domain.key
```

### 故障排查

**问题1：无法应用配置**

```bash
# 检查Nginx是否运行
sudo systemctl status nginx

# 手动测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

**问题2：权限不足**

```bash
# 检查用户组
groups

# 应该包含 timevalue 组，如果没有则重新登录
exit
su - your_username
```

**问题3：配置文件路径不存在**

```bash
# 手动创建目录
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# 重新运行权限设置
sudo bash setup_nginx_permissions.sh
```

---

## 📚 API文档

### 配置管理API

```
GET    /api/nginx/configs           # 获取所有配置
POST   /api/nginx/configs           # 创建新配置
GET    /api/nginx/configs/:id       # 获取单个配置
PUT    /api/nginx/configs/:id       # 更新配置
DELETE /api/nginx/configs/:id       # 删除配置
GET    /api/nginx/configs/:id/preview  # 预览配置
POST   /api/nginx/configs/:id/apply    # 应用配置
GET    /api/nginx/status            # 获取Nginx状态
```

### 请求示例

**创建配置：**

```bash
curl -X POST http://localhost:5000/api/nginx/configs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_name": "example.com",
    "listen_port": 80,
    "ssl_enabled": true,
    "ssl_certificate": "/etc/ssl/certs/cert.pem",
    "ssl_certificate_key": "/etc/ssl/private/key.pem"
  }'
```

---

## 🎯 最佳实践

### 1. 开发环境配置

```yaml
服务器名称: _
监听端口: 80
SSL启用: 否
前端端口: 3000  # Vite开发服务器
后端端口: 5000
```

### 2. 生产环境配置（有域名）

```yaml
服务器名称: your-domain.com
监听端口: 80
SSL启用: 是
SSL端口: 443
强制HTTPS: 是
前端端口: 3000  # 或使用构建后的静态文件
后端端口: 5000
Gzip压缩: 是
访问日志: 是
```

### 3. 配置管理流程

1. **创建测试配置** → 预览 → 在测试环境验证
2. **创建生产配置** → 预览 → 确认无误
3. **低峰期应用** → 监控日志 → 验证功能
4. **保留备份配置** → 出问题可快速切换

---

## 🔄 升级说明

### 从原有部署方式迁移

如果您已经部署了旧版本（使用静态nginx.conf），可以按以下步骤迁移：

1. **备份现有配置**

```bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
sudo cp /path/to/timevalue/nginx.conf /path/to/timevalue/nginx.conf.backup
```

2. **运行权限设置脚本**

```bash
sudo bash setup_nginx_permissions.sh
```

3. **通过Web界面重建配置**
   - 参考原有nginx.conf的设置
   - 在Web界面创建相应配置
   - 预览确认后应用

4. **验证服务正常**

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 测试应用访问
curl http://localhost
```

---

## 💡 常见问题

**Q: 配置文件存储在哪里？**

A: 数据库中存储配置参数，应用时动态生成到 `/etc/nginx/sites-available/timevalue.conf`

**Q: 可以同时激活多个配置吗？**

A: 不可以，系统只允许一个配置处于激活状态。

**Q: 删除配置会影响Nginx吗？**

A: 不会，激活的配置不允许删除。必须先应用其他配置才能删除。

**Q: 是否支持多域名配置？**

A: 支持。可以在"服务器名称"中填写多个域名，用空格分隔，如：`example.com www.example.com`

**Q: 如何回滚到之前的配置？**

A: 在配置列表中找到之前的配置，点击"应用"即可。

---

## 📧 技术支持

如遇到问题，请联系：

- 📧 Email: support@fupukeji.com
- 🌐 Website: https://fupukeji.com
- 📱 GitHub: https://github.com/fupukeji

---

**© 2024 孚普科技（北京）有限公司 | TimeValue 时间价值系统**
