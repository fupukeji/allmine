@echo off
chcp 65001 >nul
REM ================================================================================
REM TimeValue Git 初始化脚本 (Windows版本)
REM 首次配置Git并连接到阿里云Codeup
REM Powered by 孚普科技(北京)有限公司
REM ================================================================================

echo ================================================================================
echo 🔧 TimeValue Git 初始化脚本
echo ================================================================================
echo.

REM 检查Git是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Git，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✓ Git已安装
echo.

REM 配置Git用户信息
echo 📝 配置Git用户信息
echo.

set /p GIT_NAME="请输入你的名字: "
set /p GIT_EMAIL="请输入你的邮箱: "

git config --global user.name "%GIT_NAME%"
git config --global user.email "%GIT_EMAIL%"

echo.
echo ✓ Git用户信息配置完成
echo   用户名: %GIT_NAME%
echo   邮箱: %GIT_EMAIL%
echo.

REM 初始化Git仓库
if not exist ".git\" (
    echo 📦 初始化Git仓库...
    git init
    git branch -M main
    echo ✓ Git仓库初始化完成
    echo.
) else (
    echo ✓ Git仓库已存在
    echo.
)

REM 配置远程仓库
set REMOTE_URL=https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git

git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔗 添加远程仓库...
    git remote add origin %REMOTE_URL%
    echo ✓ 远程仓库添加成功
) else (
    echo 🔗 更新远程仓库地址...
    git remote set-url origin %REMOTE_URL%
    echo ✓ 远程仓库地址更新成功
)

echo.
echo ================================================================================
echo ✅ Git初始化完成！
echo ================================================================================
echo.
echo 📋 配置信息:
echo   用户名: %GIT_NAME%
echo   邮箱: %GIT_EMAIL%
echo   远程仓库: %REMOTE_URL%
echo   主分支: main
echo.
echo 🚀 下一步操作:
echo   1. 运行 git_push.bat 推送代码
echo   2. 访问仓库: https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue
echo.
echo 💡 提示:
echo   首次推送需要输入阿里云账号和访问令牌（作为密码）
echo   创建访问令牌: https://codeup.aliyun.com/settings/personal_access_tokens
echo.
echo ================================================================================
echo.

pause
