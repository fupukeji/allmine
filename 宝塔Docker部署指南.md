# 🚀 TimeValue 宝塔面板Docker部署指南

> **场景**: 使用宝塔面板部署TimeValue后端
> **优势**: 可视化操作，无需命令行
> **服务器**: 60.205.161.210

---

## 📋 部署前提

### 已有环境
- ✅ 宝塔面板已安装
- ✅ MySQL 8.0 已通过宝塔安装
- ✅ 数据库: `timevalue`
- ✅ 用户: `timevalue`
- ✅ 密码: `sdA3GThaTaDx3h8S`

### 需要安装
- [ ] Docker管理器（宝塔应用商店）
- [ ] Docker Compose管理器（可选）

---

## 🎯 宝塔部署步骤（图文教程）

### Step 1: 安装Docker管理器

#### 1.1 进入宝塔面板

```
浏览器打开: http://60.205.161.210:8888
登录宝塔面板
```

#### 1.2 安装Docker

```
1. 点击左侧菜单【软件商店】
2. 搜索【Docker管理器】
3. 点击【安装】
4. 等待安装完成（约1-2分钟）
```

#### 1.3 验证Docker安装

```
1. 点击左侧菜单【Docker】
2. 应该能看到Docker容器列表页面
3. 或在【终端】中执行: docker --version
```

---

### Step 2: 上传项目文件

#### 2.1 使用宝塔文件管理器

```
1. 点击左侧菜单【文件】
2. 进入 /opt 目录
3. 点击【新建目录】，创建 timevalue 文件夹
4. 进入 /opt/timevalue 目录
5. 点击【上传】，选择项目文件
```

**推荐上传方式**:
- 方式1: 压缩本地项目为 `timevalue.zip`，上传后解压
- 方式2: 使用Git克隆（见Step 2.2）

#### 2.2 使用Git克隆（推荐）

```
1. 点击左侧菜单【终端】
2. 执行以下命令:

cd /opt
git clone https://github.com/fupukeji/timevalue.git
cd timevalue
```

---

### Step 3: 配置MySQL数据库

#### 3.1 检查MySQL配置

```
1. 点击左侧菜单【数据库】
2. 找到 timevalue 数据库
3. 点击【权限】
4. 确保允许以下访问:
   - 本地服务器: 127.0.0.1
   - Docker网段: 172.17.0.0/16
   - 本机访问: localhost
```

#### 3.2 添加Docker访问权限

```
1. 点击左侧菜单【数据库】→【root密码】
2. 进入【phpMyAdmin】
3. 点击【SQL】标签
4. 执行以下SQL语句:
```

```sql
-- 授权Docker容器访问
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'172.%.%.%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';

-- 更新认证插件
ALTER USER 'timevalue'@'%' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';
ALTER USER 'timevalue'@'172.%.%.%' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证权限
SELECT user, host FROM mysql.user WHERE user='timevalue';
```

#### 3.3 修改MySQL绑定地址（如果需要）

```
1. 点击左侧菜单【软件商店】
2. 找到【MySQL】，点击【设置】
3. 点击【配置修改】
4. 找到 bind-address，确保是:
   bind-address = 0.0.0.0
5. 如有修改，点击【保存】→【重启】
```

---

### Step 4: 构建Docker镜像

#### 4.1 使用宝塔终端

```
1. 点击左侧菜单【终端】
2. 执行以下命令:

cd /opt/timevalue
docker-compose -f docker-compose.server.yml build
```

**预计时间**: 3-5分钟

#### 4.2 使用Docker管理器（可视化）

```
1. 点击左侧菜单【Docker】
2. 点击【镜像】标签
3. 点击【构建镜像】
4. 填写:
   - 名称: timevalue-backend
   - Dockerfile路径: /opt/timevalue/backend/Dockerfile
   - 构建参数: 留空
5. 点击【提交】
```

---

### Step 5: 创建并启动容器

#### 5.1 方式一：使用终端（推荐）

```
1. 点击左侧菜单【终端】
2. 执行以下命令:

cd /opt/timevalue
docker-compose -f docker-compose.server.yml --env-file .env.docker up -d
```

#### 5.2 方式二：使用Docker管理器

```
1. 点击左侧菜单【Docker】
2. 点击【容器】标签
3. 点击【创建容器】
4. 填写以下信息:

容器名称: timevalue-backend
镜像: timevalue-backend:latest

端口映射:
  容器端口: 5000
  服务器端口: 5000

环境变量:
  DB_HOST=host.docker.internal
  DB_PORT=3306
  DB_NAME=timevalue
  DB_USER=timevalue
  DB_PASSWORD=sdA3GThaTaDx3h8S
  FLASK_ENV=production
  FLASK_DEBUG=False
  SECRET_KEY=dev-secret-key-change-in-production
  JWT_SECRET_KEY=jwt-secret-key-change-in-production
  JWT_ACCESS_TOKEN_EXPIRES=False
  CORS_ORIGINS=http://60.205.161.210:3000

网络模式: bridge

额外参数:
  --add-host=host.docker.internal:host-gateway

挂载目录:
  /opt/timevalue/backend/logs -> /app/logs

自动重启: 是

5. 点击【提交】
```

---

### Step 6: 配置安全组和防火墙

#### 6.1 宝塔安全配置

```
1. 点击左侧菜单【安全】
2. 点击【添加规则】
3. 填写:
   - 端口: 5000
   - 协议: TCP
   - 策略: 放行
   - 备注: TimeValue后端API
4. 点击【确定】
```

#### 6.2 阿里云/腾讯云安全组

```
1. 登录云服务器控制台
2. 找到安全组规则
3. 添加入站规则:
   - 协议: TCP
   - 端口: 5000
   - 源: 0.0.0.0/0（或指定IP）
   - 描述: TimeValue后端
4. 保存规则
```

---

### Step 7: 验证部署

#### 7.1 检查容器状态

```
方式1: 使用Docker管理器
1. 点击左侧菜单【Docker】→【容器】
2. 查看 timevalue-backend 状态
3. 应该显示【运行中】，绿色状态

方式2: 使用终端
docker ps | grep timevalue-backend
```

#### 7.2 测试健康检查

```
方式1: 浏览器访问
http://60.205.161.210:5000/api/health

方式2: 终端测试
curl http://localhost:5000/api/health

预期返回:
{
  "status": "healthy",
  "timestamp": "2025-11-30...",
  "service": "timevalue-backend",
  "checks": {
    "database": {"status": "up"},
    "environment": {"status": "up"}
  }
}
```

#### 7.3 查看容器日志

```
方式1: Docker管理器
1. 点击左侧菜单【Docker】→【容器】
2. 找到 timevalue-backend
3. 点击【日志】按钮
4. 查看实时日志

方式2: 终端
docker logs -f timevalue-backend
```

---

### Step 8: 设置自动启动和监控

#### 8.1 容器自动重启

```
在创建容器时，自动重启已设置为【是】
容器会在以下情况自动启动:
- 服务器重启
- Docker服务重启
- 容器异常退出
```

#### 8.2 配置宝塔监控

```
1. 点击左侧菜单【监控】
2. 点击【进程守护】
3. 添加守护进程:
   - 名称: TimeValue Backend
   - 启动命令: docker start timevalue-backend
   - 检测方式: 端口检测
   - 检测端口: 5000
4. 点击【添加】
```

#### 8.3 设置告警通知

```
1. 点击左侧菜单【面板设置】
2. 点击【通知设置】
3. 配置邮件/钉钉/微信通知
4. 启用【Docker容器异常】告警
```

---

## 🛠️ 宝塔日常管理

### 容器管理

#### 启动/停止容器

```
1. 点击左侧菜单【Docker】→【容器】
2. 找到 timevalue-backend
3. 点击对应的按钮:
   - 【启动】: 启动容器
   - 【停止】: 停止容器
   - 【重启】: 重启容器
```

#### 查看容器资源占用

```
1. 点击左侧菜单【Docker】→【容器】
2. 查看【CPU】和【内存】列
3. 或点击【监控】按钮，查看详细图表
```

#### 进入容器终端

```
1. 点击左侧菜单【Docker】→【容器】
2. 找到 timevalue-backend
3. 点击【终端】按钮
4. 进入容器bash环境
```

---

### 数据库管理

#### 使用phpMyAdmin

```
1. 点击左侧菜单【数据库】
2. 点击 timevalue 数据库的【管理】
3. 进入phpMyAdmin界面
4. 可以:
   - 查看表结构
   - 执行SQL查询
   - 导入/导出数据
```

#### 备份数据库

```
1. 点击左侧菜单【数据库】
2. 找到 timevalue 数据库
3. 点击【备份】按钮
4. 选择备份方式:
   - 立即备份
   - 定时备份（推荐每天凌晨2点）
```

---

### 日志管理

#### 查看应用日志

```
1. 点击左侧菜单【文件】
2. 进入 /opt/timevalue/backend/logs
3. 查看日志文件:
   - app.log: 应用日志
   - error.log: 错误日志
```

#### 查看Docker日志

```
方式1: Docker管理器
1. 【Docker】→【容器】→【日志】

方式2: 文件查看
1. 【文件】→ /var/lib/docker/containers/
2. 找到对应容器ID目录
3. 查看 xxx-json.log
```

---

### 更新部署

#### 更新代码

```
1. 点击左侧菜单【终端】
2. 执行:

cd /opt/timevalue
git pull

3. 重新构建镜像:

docker-compose -f docker-compose.server.yml build

4. 重启容器:

docker-compose -f docker-compose.server.yml up -d
```

#### 或使用宝塔界面

```
1. 【Docker】→【容器】→停止 timevalue-backend
2. 【Docker】→【镜像】→删除旧镜像
3. 【终端】→重新构建镜像
4. 【Docker】→【容器】→启动 timevalue-backend
```

---

## 🔍 故障排查（宝塔版）

### 问题1: 容器无法启动

**排查步骤**:

```
1. 【Docker】→【容器】→查看状态
2. 点击【日志】查看错误信息
3. 常见错误:
   - 端口被占用: 修改端口映射
   - 镜像不存在: 重新构建镜像
   - 环境变量错误: 检查环境变量配置
```

**解决方案**:

```
1. 检查端口占用:
   【终端】→ netstat -tulpn | grep :5000

2. 检查镜像:
   【Docker】→【镜像】→确认 timevalue-backend 存在

3. 检查环境变量:
   【Docker】→【容器】→【编辑】→查看环境变量
```

---

### 问题2: 数据库连接失败

**排查步骤**:

```
1. 检查MySQL是否运行:
   【软件商店】→【MySQL】→查看状态

2. 检查用户权限:
   【数据库】→【phpMyAdmin】→执行:
   SELECT user, host FROM mysql.user WHERE user='timevalue';

3. 测试容器内连接:
   【Docker】→【容器】→【终端】→执行:
   mysql -h host.docker.internal -u timevalue -psdA3GThaTaDx3h8S timevalue
```

**解决方案**:

```
1. 重新执行Step 3的SQL授权语句
2. 重启MySQL: 【软件商店】→【MySQL】→【重启】
3. 重启容器: 【Docker】→【容器】→【重启】
```

---

### 问题3: 无法外网访问

**排查步骤**:

```
1. 检查宝塔防火墙:
   【安全】→查看5000端口是否放行

2. 检查云服务器安全组:
   登录云控制台→安全组→查看规则

3. 测试本地访问:
   【终端】→ curl http://localhost:5000/api/health
```

**解决方案**:

```
1. 宝塔放行端口: 【安全】→添加5000端口
2. 云服务器放行: 控制台→安全组→添加规则
3. 重启容器: 【Docker】→【容器】→【重启】
```

---

## 📊 性能监控

### 宝塔监控面板

```
1. 点击左侧菜单【监控】
2. 查看:
   - CPU使用率
   - 内存使用率
   - 磁盘I/O
   - 网络流量
```

### Docker资源监控

```
1. 【Docker】→【容器】
2. 查看每个容器的:
   - CPU占用
   - 内存占用
   - 网络流量
3. 点击【监控】查看历史图表
```

---

## 🔒 安全加固

### 1. 修改默认密码

```
1. 浏览器访问: http://60.205.161.210:5000
2. 登录管理员账户: admin / admin123
3. 进入【用户设置】→修改密码
```

### 2. 生成新的安全密钥

```
1. 【终端】→执行:

python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

2. 复制生成的密钥

3. 【文件】→编辑 /opt/timevalue/.env.docker
   更新 SECRET_KEY 和 JWT_SECRET_KEY

4. 【Docker】→【容器】→【重启】
```

### 3. 限制IP访问

```
1. 【安全】→【5000端口】
2. 修改【源】为指定IP
3. 例如: 只允许公司IP访问
```

### 4. 启用HTTPS

```
1. 【网站】→【添加站点】
2. 配置域名
3. 【SSL】→【Let's Encrypt】→申请证书
4. 配置反向代理:
   目标URL: http://127.0.0.1:5000
```

---

## 📋 宝塔部署检查清单

- [ ] 宝塔面板正常运行
- [ ] Docker管理器已安装
- [ ] 项目文件已上传到 /opt/timevalue
- [ ] MySQL用户权限已配置
- [ ] Docker镜像已构建成功
- [ ] 容器已创建并运行
- [ ] 5000端口已在宝塔放行
- [ ] 云服务器安全组已配置
- [ ] 健康检查通过: http://IP:5000/api/health
- [ ] 数据库连接正常（查看容器日志）
- [ ] 自动重启已启用
- [ ] 数据库备份已配置

---

## 🎯 宝塔部署优势

### vs 纯命令行部署

| 功能 | 宝塔部署 | 命令行部署 |
|------|---------|-----------|
| **难度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **可视化** | ✅ 全程图形界面 | ❌ 纯命令行 |
| **监控** | ✅ 实时监控面板 | ⚠️ 需手动配置 |
| **日志** | ✅ 一键查看 | ⚠️ 需记住命令 |
| **备份** | ✅ 定时自动备份 | ⚠️ 需写脚本 |
| **告警** | ✅ 多渠道通知 | ⚠️ 需配置 |
| **管理** | ✅ 点击操作 | ⚠️ 记住命令 |

---

## 📞 常见问题FAQ

### Q1: 如何查看容器是否运行？

**A**: 【Docker】→【容器】，查看状态是否为【运行中】（绿色）

### Q2: 如何重启容器？

**A**: 【Docker】→【容器】→找到容器→点击【重启】按钮

### Q3: 如何查看日志？

**A**: 【Docker】→【容器】→找到容器→点击【日志】按钮

### Q4: 如何备份数据？

**A**: 【数据库】→找到timevalue→点击【备份】

### Q5: 容器启动失败怎么办？

**A**: 查看日志（【Docker】→【容器】→【日志】），根据错误信息排查

### Q6: 如何更新代码？

**A**: 【终端】→ `cd /opt/timevalue && git pull` → 重新构建镜像 → 重启容器

---

## 🎉 部署完成

部署成功后，您将拥有：

- ✅ **可视化管理**: 宝塔面板图形化管理所有服务
- ✅ **实时监控**: CPU、内存、网络监控
- ✅ **自动备份**: 数据库定时备份
- ✅ **自动重启**: 容器异常自动恢复
- ✅ **日志查看**: 一键查看应用日志
- ✅ **告警通知**: 异常及时通知

**访问地址**:
- 后端API: http://60.205.161.210:5000
- 健康检查: http://60.205.161.210:5000/api/health
- 宝塔面板: http://60.205.161.210:8888

---

> 💡 **提示**: 使用宝塔面板，运维变得简单！
>
> 📚 **参考**: 结合《服务器Docker部署指南.md》深入了解技术细节
