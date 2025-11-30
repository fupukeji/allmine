-- ============================================================
-- TimeValue MySQL数据库配置脚本
-- ============================================================
-- 说明：请在MySQL服务器 60.205.161.210 上执行此脚本
-- 执行方式：登录MySQL后，运行这些SQL命令

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS timevalue DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 授权root用户从任意IP访问（生产环境建议限制具体IP）
GRANT ALL PRIVILEGES ON timevalue.* TO 'root'@'%' IDENTIFIED BY '9b1af5bf20945c3f';
GRANT ALL PRIVILEGES ON timevalue.* TO 'root'@'114.241.248.138' IDENTIFIED BY '9b1af5bf20945c3f';

-- 3. 刷新权限
FLUSH PRIVILEGES;

-- 4. 验证权限
SHOW GRANTS FOR 'root'@'%';
SHOW GRANTS FOR 'root'@'114.241.248.138';

-- 5. 检查数据库
USE timevalue;
SHOW TABLES;

-- ============================================================
-- 注意事项：
-- ============================================================
-- 1. 如果MySQL 8.0+，使用caching_sha2_password插件，需要：
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '9b1af5bf20945c3f';
ALTER USER 'root'@'114.241.248.138' IDENTIFIED WITH mysql_native_password BY '9b1af5bf20945c3f';
FLUSH PRIVILEGES;

-- 2. 检查bind-address配置
-- 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf 或 /etc/my.cnf
-- 确保：bind-address = 0.0.0.0
-- 然后重启MySQL服务：systemctl restart mysql

-- 3. 检查防火墙
-- CentOS/RHEL: firewall-cmd --permanent --add-port=3306/tcp && firewall-cmd --reload
-- Ubuntu: ufw allow 3306/tcp
-- 阿里云/腾讯云：在安全组中开放3306端口

-- ============================================================
-- 备用方案：使用timevalue专用账户
-- ============================================================
CREATE USER IF NOT EXISTS 'timevalue'@'%' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';
CREATE USER IF NOT EXISTS 'timevalue'@'114.241.248.138' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'%';
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'114.241.248.138';
FLUSH PRIVILEGES;
