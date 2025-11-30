# MySQL数据库配置完整指南

## 问题描述

当前TimeValue系统尝试连接到MySQL服务器时遇到以下错误：
```
Host '114.241.248.138' is not allowed to connect to this MySQL server
```

## 当前状态

- ✅ **临时解决方案**：系统已切换到SQLite数据库，可以正常运行
- ⏳ **待处理**：MySQL服务器需要配置远程访问权限
- 📌 **目标**：迁移到MySQL 8.4.5生产环境数据库

## MySQL服务器信息

- **主机**: 60.205.161.210
- **端口**: 3306
- **数据库**: timevalue
- **用户**: root
- **密码**: 9b1af5bf20945c3f

## 配置步骤

### 1. 登录MySQL服务器

```bash
# SSH登录到服务器
ssh root@60.205.161.210

# 登录MySQL
mysql -u root -p
# 输入密码: 9b1af5bf20945c3f
```

### 2. 执行授权命令

在MySQL命令行中执行以下SQL（完整脚本见 `mysql_setup.sql`）：

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS timevalue DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- MySQL 8.0+ 使用mysql_native_password插件
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '9b1af5bf20945c3f';
GRANT ALL PRIVILEGES ON timevalue.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- 或者授权特定IP
GRANT ALL PRIVILEGES ON timevalue.* TO 'root'@'114.241.248.138' IDENTIFIED WITH mysql_native_password BY '9b1af5bf20945c3f';
FLUSH PRIVILEGES;
```

### 3. 配置MySQL远程访问

#### 3.1 修改MySQL配置文件

编辑配置文件（路径可能是 `/etc/mysql/mysql.conf.d/mysqld.cnf` 或 `/etc/my.cnf`）：

```ini
[mysqld]
bind-address = 0.0.0.0
```

#### 3.2 重启MySQL服务

```bash
# CentOS/RHEL
systemctl restart mysqld

# Ubuntu/Debian
systemctl restart mysql
```

### 4. 配置防火墙

#### Linux防火墙

```bash
# CentOS/RHEL (firewalld)
firewall-cmd --permanent --add-port=3306/tcp
firewall-cmd --reload

# Ubuntu/Debian (ufw)
ufw allow 3306/tcp
ufw reload

# 或者直接使用iptables
iptables -A INPUT -p tcp --dport 3306 -j ACCEPT
```

#### 云服务器安全组

如果使用阿里云/腾讯云/AWS等云服务器，需要在控制台配置安全组规则：

1. 登录云服务器控制台
2. 找到实例的安全组配置
3. 添加入站规则：
   - 协议：TCP
   - 端口：3306
   - 源IP：114.241.248.138/32 或 0.0.0.0/0（所有IP）

### 5. 测试连接

使用诊断工具测试：

```bash
cd c:\Users\Administrator\timevalue\backend
python mysql_diagnostic.py
```

## 切换到MySQL

完成上述配置后，修改 `.env` 文件：

```env
DB_TYPE=mysql
```

然后重启服务：

```bash
python init_db.py  # 初始化数据库表结构
python app.py      # 启动服务
```

## 数据迁移

如果需要从SQLite迁移数据到MySQL，使用迁移脚本：

```bash
python migrate_to_mysql.py
```

## 常见问题排查

### 问题1: Host 'xxx' is not allowed to connect

**原因**: MySQL用户权限未授权远程IP访问

**解决方案**:
```sql
GRANT ALL PRIVILEGES ON timevalue.* TO 'root'@'%' IDENTIFIED BY '9b1af5bf20945c3f';
FLUSH PRIVILEGES;
```

### 问题2: Can't connect to MySQL server

**原因**: 
- MySQL服务未启动
- 网络问题
- 防火墙阻止
- bind-address配置错误

**解决方案**:
1. 检查MySQL服务: `systemctl status mysql`
2. 测试网络连接: `telnet 60.205.161.210 3306`
3. 检查防火墙规则
4. 检查bind-address配置

### 问题3: Access denied for user

**原因**: 用户名或密码错误

**解决方案**: 检查`.env`文件中的DB_USER和DB_PASSWORD是否正确

### 问题4: Unknown database 'timevalue'

**原因**: 数据库不存在

**解决方案**:
```sql
CREATE DATABASE timevalue DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 安全建议

1. **生产环境不要使用root账户**，创建专用数据库用户：
   ```sql
   CREATE USER 'timevalue'@'114.241.248.138' IDENTIFIED WITH mysql_native_password BY 'strong_password_here';
   GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'114.241.248.138';
   FLUSH PRIVILEGES;
   ```

2. **限制访问IP**：不要使用'%'允许所有IP，仅授权需要的IP地址

3. **使用强密码**：更改默认密码为更复杂的密码

4. **开启SSL连接**：在生产环境中使用SSL加密数据传输

5. **定期备份**：配置MySQL自动备份策略

## 工具文件说明

- `mysql_setup.sql` - MySQL数据库完整配置SQL脚本
- `mysql_diagnostic.py` - MySQL连接诊断工具
- `migrate_to_mysql.py` - SQLite到MySQL数据迁移脚本（待创建）

## 技术支持

如遇到问题，请检查：
1. 后端日志：查看Flask应用输出
2. MySQL日志：通常在 `/var/log/mysql/error.log`
3. 系统日志：`journalctl -u mysql`

## 联系信息

- **技术支持**: 孚普科技（北京）有限公司
- **网站**: https://fupukeji.com
- **GitHub**: https://github.com/fupukeji
