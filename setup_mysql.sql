CREATE USER IF NOT EXISTS 'timevalue'@'%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';
CREATE USER IF NOT EXISTS 'timevalue'@'localhost' IDENTIFIED BY 'sdA3GThaTaDx3h8S';
CREATE USER IF NOT EXISTS 'timevalue'@'172.%' IDENTIFIED BY 'sdA3GThaTaDx3h8S';
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'%';
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'localhost';
GRANT ALL PRIVILEGES ON timevalue.* TO 'timevalue'@'172.%';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user='timevalue';
