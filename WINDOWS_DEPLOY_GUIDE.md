# Windows环境下上传部署到阿里云服务器指南

## 📋 准备工作

### 1. 安装必要工具

#### Git Bash（推荐）
- 下载地址：https://git-scm.com/download/win
- 安装后可以在Windows上使用Linux命令

#### 或使用其他工具：
- **WinSCP** - 图形化SFTP客户端
- **FileZilla** - FTP/SFTP客户端
- **PuTTY** - SSH客户端

### 2. 获取阿里云ECS信息

登录阿里云控制台获取：
- 公网IP地址
- SSH登录用户名（通常是root）
- SSH登录密码或密钥

---

## 🚀 方式一：使用Git Bash（推荐）

### 步骤1：打开Git Bash

在项目目录 `d:\timevalue` 右键选择 "Git Bash Here"

### 步骤2：上传项目到服务器

```bash
# 使用SCP上传整个项目
scp -r . root@your-server-ip:/root/timevalue

# 输入服务器密码
```

### 步骤3：连接到服务器

```bash
# SSH连接到服务器
ssh root@your-server-ip

# 输入服务器密码
```

### 步骤4：在服务器上部署

```bash
# 进入项目目录
cd /root/timevalue

# 设置脚本权限
chmod +x *.sh

# 执行一键部署
./deploy.sh

# 启动服务
./start_production.sh
```

---

## 🚀 方式二：使用WinSCP

### 步骤1：安装并打开WinSCP

1. 下载WinSCP：https://winscp.net/
2. 安装后打开WinSCP

### 步骤2：连接到服务器

```
文件协议：SFTP
主机名：your-server-ip
端口：22
用户名：root
密码：your-password
```

### 步骤3：上传文件

1. 左侧窗口导航到 `d:\timevalue`
2. 右侧窗口导航到 `/root/`
3. 将左侧的 `timevalue` 文件夹拖拽到右侧
4. 等待上传完成

### 步骤4：使用PuTTY连接服务器

1. 打开PuTTY
2. 输入服务器IP
3. 点击Open连接
4. 输入用户名root和密码

### 步骤5：在服务器上部署

```bash
cd /root/timevalue
chmod +x *.sh
./deploy.sh
./start_production.sh
```

---

## 🚀 方式三：使用PowerShell（Windows 10+）

### 步骤1：打开PowerShell

在项目目录 `d:\timevalue` 按住Shift右键，选择"在此处打开PowerShell窗口"

### 步骤2：上传项目

```powershell
# 使用scp上传（Windows 10+ 内置）
scp -r * root@your-server-ip:/root/timevalue/
```

### 步骤3：SSH连接

```powershell
# 使用ssh连接（Windows 10+ 内置）
ssh root@your-server-ip
```

### 步骤4：部署服务

```bash
cd /root/timevalue
chmod +x *.sh
./deploy.sh
./start_production.sh
```

---

## 📝 完整操作示例

### 使用Git Bash的完整流程：

```bash
# 1. 在Windows的项目目录打开Git Bash
cd /d/timevalue

# 2. 上传项目到服务器
scp -r . root@123.456.789.123:/root/timevalue
# 输入密码

# 3. 连接到服务器
ssh root@123.456.789.123
# 输入密码

# 4. 在服务器上执行部署
cd /root/timevalue
chmod +x *.sh
./deploy.sh

# 5. 等待部署完成后启动服务
./start_production.sh

# 6. 检查服务状态
./check_status.sh

# 7. 查看日志（可选）
tail -f logs/backend.log
# 按Ctrl+C退出日志查看

# 8. 访问应用
# 在浏览器打开：http://123.456.789.123:3000
```

---

## 🔐 配置SSH密钥（可选，更安全）

### 在Windows上生成SSH密钥

```bash
# 打开Git Bash或PowerShell
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 按Enter使用默认路径
# 输入密码（可选）
```

### 上传公钥到服务器

```bash
# 方式1：使用ssh-copy-id（Git Bash）
ssh-copy-id root@your-server-ip

# 方式2：手动复制
# 1. 查看公钥
cat ~/.ssh/id_rsa.pub

# 2. 复制输出内容

# 3. 连接到服务器
ssh root@your-server-ip

# 4. 添加公钥
mkdir -p ~/.ssh
echo "粘贴刚才复制的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 之后就可以免密登录

```bash
ssh root@your-server-ip
# 无需输入密码
```

---

## 🔍 常见问题

### Q1: SCP上传时提示权限被拒绝

**解决方案：**
```bash
# 检查目标目录是否存在
ssh root@your-server-ip "mkdir -p /root/timevalue"

# 重新上传
scp -r . root@your-server-ip:/root/timevalue
```

### Q2: Windows上没有scp命令

**解决方案：**
- 安装Git Bash
- 或使用WinSCP图形化工具
- 或升级到Windows 10 1809或更高版本

### Q3: 上传速度很慢

**解决方案：**
```bash
# 压缩后上传
tar -czf timevalue.tar.gz .
scp timevalue.tar.gz root@your-server-ip:/root/

# 在服务器上解压
ssh root@your-server-ip
cd /root
tar -xzf timevalue.tar.gz
```

### Q4: 连接超时

**解决方案：**
- 检查阿里云安全组是否开放22端口
- 检查服务器防火墙设置
- 确认IP地址是否正确

---

## 📊 快速命令参考

### Windows → 服务器传输

```bash
# 上传单个文件
scp file.txt root@server-ip:/root/

# 上传整个目录
scp -r directory root@server-ip:/root/

# 从服务器下载文件
scp root@server-ip:/root/file.txt .

# 从服务器下载目录
scp -r root@server-ip:/root/directory .
```

### 服务器管理命令

```bash
# 连接服务器
ssh root@server-ip

# 查看进程
ps aux | grep python
ps aux | grep node

# 查看端口
netstat -tlnp | grep :3000
netstat -tlnp | grep :5000

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 重启服务器（慎用）
sudo reboot
```

---

## 🎯 部署检查清单

部署前检查：
- [ ] 已购买并配置好阿里云ECS
- [ ] 安全组已开放3000和5000端口
- [ ] 已安装Git Bash或其他SSH工具
- [ ] 已获取服务器IP和登录凭证

部署后检查：
- [ ] `./check_status.sh` 显示服务运行正常
- [ ] 可以通过浏览器访问 `http://server-ip:3000`
- [ ] 可以使用admin/admin123登录
- [ ] 日志文件正常写入

---

## 📞 获取帮助

如果遇到问题：
1. 检查服务器防火墙和安全组配置
2. 查看服务器日志：`tail -f logs/backend.log`
3. 检查服务状态：`./check_status.sh`
4. 参考完整文档：`DEPLOY_GUIDE.md`

---

**Powered by 孚普科技（北京）有限公司**  
🤖 AI驱动的MVP快速迭代解决方案
