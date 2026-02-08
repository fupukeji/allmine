@echo off
chcp 65001 >nul
echo =====================================
echo   TimeValue 云托管部署脚本
echo =====================================
echo.

echo 微信云托管信息：
echo   环境ID:    prod-4gqjqr6g0c81bd5a
echo   服务名称:  flask-rvx7
echo   域名:      flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
echo.

echo [1/4] 检查依赖...
where cloudbase >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装CloudBase CLI
    echo.
    echo 安装方法：
    echo   npm install -g @cloudbase/cli
    echo.
    pause
    exit /b 1
)
echo ✅ CloudBase CLI 已安装
echo.

echo [2/4] 检查登录状态...
cloudbase whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  未登录，正在打开登录页面...
    cloudbase login
    if %errorlevel% neq 0 (
        echo ❌ 登录失败
        pause
        exit /b 1
    )
)
echo ✅ 已登录
echo.

echo [3/4] 构建和部署...
echo 正在构建Docker镜像并部署到云托管...
echo 此过程可能需要5-10分钟，请耐心等待...
echo.

cloudbase run deploy --envId prod-4gqjqr6g0c81bd5a
if %errorlevel% neq 0 (
    echo ❌ 部署失败
    echo.
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. Docker镜像构建失败
    echo   3. 环境变量未配置
    echo.
    echo 请查看错误日志排查问题
    pause
    exit /b 1
)
echo.
echo ✅ 部署成功！
echo.

echo [4/4] 验证部署...
echo 正在测试健康检查接口...
curl -s https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com/api/health
echo.
echo.

echo =====================================
echo   🎉 部署完成！
echo =====================================
echo.
echo 访问地址：
echo   https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
echo.
echo 下一步：
echo   1. 配置微信公众号域名
echo   2. 更新H5前端API地址
echo   3. 测试完整登录流程
echo.
echo 查看日志：
echo   cloudbase run logs flask-rvx7 --envId prod-4gqjqr6g0c81bd5a
echo.
pause
