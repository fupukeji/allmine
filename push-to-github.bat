@echo off
chcp 65001 >nul
echo =====================================
echo   TimeValue 推送到GitHub并自动部署
echo =====================================
echo.

echo GitHub仓库: https://github.com/fupukej/mymoney
echo 云托管地址: https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com
echo.

echo [1/5] 检查Git状态...
git status --short
echo.

echo [2/5] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/fupukej/mymoney.git
git remote -v
echo.

echo [3/5] 添加文件...
git add .
echo ✅ 已添加所有文件
echo.

echo [4/5] 提交更改...
set /p commit_msg="请输入提交信息（直接回车使用默认）: "
if "%commit_msg%"=="" set commit_msg=TimeValue H5版本 - 微信登录 + 云托管部署

git commit -m "%commit_msg%"
echo.

echo [5/5] 推送到GitHub...
echo ⚠️  首次推送将覆盖远程仓库内容
echo.
choice /C YN /M "确认推送吗？"
if errorlevel 2 (
    echo ❌ 已取消推送
    pause
    exit /b 0
)

echo.
echo 正在推送...
git push -f origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ 推送失败
    echo.
    echo 可能的原因：
    echo   1. 需要GitHub认证（首次推送）
    echo   2. 网络连接问题
    echo   3. 没有仓库访问权限
    echo.
    echo 解决方法：
    echo   1. 配置GitHub Personal Access Token
    echo   2. 或使用SSH密钥认证
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================
echo   🎉 推送成功！
echo =====================================
echo.
echo 下一步：
echo   1. 查看GitHub Actions部署进度
echo      https://github.com/fupukej/mymoney/actions
echo.
echo   2. 等待5-10分钟后测试接口
echo      curl https://flask-rvx7-224477-6-1403315737.sh.run.tcloudbase.com/api/health
echo.
echo   3. 如果部署失败，请配置GitHub Secrets:
echo      https://github.com/fupukej/mymoney/settings/secrets/actions
echo      需要添加: CLOUDBASE_SECRET_ID 和 CLOUDBASE_SECRET_KEY
echo.

choice /C YN /M "是否打开GitHub仓库页面？"
if errorlevel 2 goto :end
start https://github.com/fupukej/mymoney

:end
echo.
pause
