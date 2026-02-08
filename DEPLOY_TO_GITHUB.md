# TimeValue 推送到GitHub并自动部署

## 📋 您的GitHub仓库

```
仓库地址:   https://github.com/fupukej/mymoney
仓库名称:   mymoney (wxcloudrun-flask)
状态:       ✅ 已创建，支持CI/CD
```

## 🚀 一键部署流程

### 步骤1：添加远程仓库

```bash
cd C:\Users\Administrator\Desktop\timevalue

# 检查现有远程仓库
git remote -v

# 如果已有origin，先删除
git remote remove origin

# 添加您的GitHub仓库
git remote add origin https://github.com/fupukej/mymoney.git
```

### 步骤2：配置GitHub Secrets

1. 访问：https://github.com/fupukej/mymoney/settings/secrets/actions

2. 点击 **New repository secret**，添加两个密钥：

**密钥1：CLOUDBASE_SECRET_ID**
- 获取方式：访问 [腾讯云访问密钥](https://console.cloud.tencent.com/cam/capi)
- 点击“新建密钥”或使用现有密钥
- 复制 **SecretId**

**密钥2：CLOUDBASE_SECRET_KEY**
- 复制上面的 **SecretKey**

**✅ 数据库配置已完成**：使用云托管内置MYSQL，无需配置数据库环境变量！

### 步骤3：推送代码

```bash
# 添加所有文件
git add .

# 提交
git commit -m "TimeValue H5版本 - 集成微信登录和云托管部署"

# 推送到GitHub（首次需要强制推送）
git push -f origin main
```

### 步骤4：查看自动部署

1. 访问：https://github.com/fupukej/mymoney/actions

2. 查看 **Deploy to Tencent CloudBase** 工作流

3. 等待部署完成（约5-10分钟）

### 步骤5：验证部署

```bash
# 测试健康检查
curl https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com/api/health

# 预期返回
{"status":"healthy"}
```

---

## 🔄 后续更新流程

每次修改代码后：

```bash
git add .
git commit -m "更新说明"
git push origin main
```

推送后自动触发部署，无需手动操作！

---

## 📝 GitHub Actions配置说明

已创建的工作流文件：`.github/workflows/deploy-cloudbase.yml`

**触发条件**：
- 推送到 main/master 分支
- 修改了 backend/ 目录下的文件
- 手动触发

**部署步骤**：
1. 检出代码
2. 安装CloudBase CLI
3. 登录云托管
4. 构建并部署Docker镜像
5. 通知部署结果

---

## ⚠️ 重要提示

1. **首次推送需要强制推送**
   ```bash
   git push -f origin main
   ```
   因为GitHub仓库已有初始文件，需要覆盖。

2. **必须配置GitHub Secrets**
   否则自动部署会失败。

3. **构建时间较长**
   首次部署需要5-10分钟，请耐心等待。

4. **查看构建日志**
   在GitHub Actions页面可以查看详细日志。

---

## 🎯 完整命令集

```bash
# 1. 进入项目目录
cd C:\Users\Administrator\Desktop\timevalue

# 2. 删除旧的远程仓库（如果有）
git remote remove origin

# 3. 添加新的远程仓库
git remote add origin https://github.com/fupukej/mymoney.git

# 4. 添加所有文件
git add .

# 5. 提交
git commit -m "TimeValue H5版本 - 微信登录 + 云托管部署"

# 6. 推送（首次强制推送）
git push -f origin main

# 7. 查看远程仓库
start https://github.com/fupukej/mymoney

# 8. 查看Actions（部署进度）
start https://github.com/fupukej/mymoney/actions
```

---

## 📚 相关链接

- **GitHub仓库**: https://github.com/fupukej/mymoney
- **云托管控制台**: https://console.cloud.tencent.com/tcb/env/index?envId=prod-4gqjqr6g0c81bd5a
- **腾讯云密钥管理**: https://console.cloud.tencent.com/cam/capi
- **应用访问地址**: https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com

---

**准备好后，按照步骤操作即可完成自动部署！** 🎉
