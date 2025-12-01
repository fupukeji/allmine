-- TimeValue MySQL用户权限配置脚本
-- 用于确保Docker容器能够访问宿主机MySQL

-- 1. 授权timevalue用户从任何地址访问
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';

-- 2. 更新密码认证插件（兼容Docker容器）
ALTER USER 'timevalue'@'%' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';

-- 3. 授权从localhost访问
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'localhost' IDENTIFIED BY 'sdA3GThaTaDx3h8S';
ALTER USER 'timevalue'@'localhost' IDENTIFIED WITH mysql_native_password BY 'sdA3GThaTaDx3h8S';

-- 4. 授权从Docker网关访问
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'172.%.%.%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';

-- 5. 刷新权限
FLUSH PRIVILEGES;

-- 6. 验证用户权限
SELECT user, host, plugin FROM mysql.user WHERE user='timevalue';

-- 7. 验证数据库访问
SHOW GRANTS FOR 'timevalue'@'%';
