@echo off
chcp 65001 >nul
REM ================================================================================
REM TimeValue Git 推送脚本 (Windows版本)
REM 将项目推送到阿里云Codeup仓库
REM Powered by 孚普科技(北京)有限公司
REM ================================================================================

setlocal enabledelayedexpansion

set REMOTE_URL=https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git

echo ================================================================================
echo 🚀 TimeValue Git 推送脚本
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

REM 检查是否已初始化Git
if not exist ".git\" (
    echo 📦 初始化Git仓库...
    git init
    echo ✓ Git仓库初始化完成
    echo.
) else (
    echo ✓ Git仓库已存在
    echo.
)

REM 检查并配置远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔗 添加远程仓库...
    git remote add origin %REMOTE_URL%
    echo ✓ 远程仓库添加成功
) else (
    echo 🔗 更新远程仓库地址...
    git remote set-url origin %REMOTE_URL%
    echo ✓ 远程仓库地址已设置
)
echo.

REM 显示当前状态
echo 📝 查看待提交的文件...
git status --short
echo.

REM 添加文件
set /p ADD_FILES="是否要添加所有文件到暂存区？ [Y/n]: "
if /i "!ADD_FILES!"=="n" (
    echo 跳过添加文件
) else (
    echo 📦 添加文件到暂存区...
    git add .
    echo ✓ 文件已添加到暂存区
)
echo.

REM 显示暂存区状态
echo 📋 当前暂存区状态:
git status --short
echo.

REM 提交代码
set /p COMMIT_MSG="请输入提交信息 [默认: Update code]: "
if "!COMMIT_MSG!"=="" set COMMIT_MSG=Update code

echo 💾 提交代码...
git commit -m "!COMMIT_MSG!"
if %errorlevel% neq 0 (
    echo ⚠️  没有需要提交的更改或提交失败
)
echo.

REM 检查当前分支
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%i
if "!CURRENT_BRANCH!"=="" (
    set CURRENT_BRANCH=main
    git branch -M main
)

echo 🌐 推送到远程仓库...
echo 远程地址: %REMOTE_URL%
echo 当前分支: !CURRENT_BRANCH!
echo.

REM 推送代码
echo 开始推送...
git push -u origin !CURRENT_BRANCH!

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo ✅ 代码推送成功！
    echo ================================================================================
    echo   仓库地址: %REMOTE_URL%
    echo   分支名称: !CURRENT_BRANCH!
    echo   提交信息: !COMMIT_MSG!
    echo.
    echo 🌐 访问仓库:
    echo   https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo ❌ 推送失败！
    echo ================================================================================
    echo.
    echo 可能的原因:
    echo   1. 需要配置Git凭据
    echo   2. 网络连接问题
    echo   3. 分支冲突
    echo.
    echo 解决方案:
    echo   1. 配置Git用户信息:
    echo      git config --global user.name "Your Name"
    echo      git config --global user.email "your.email@example.com"
    echo.
    echo   2. 如果需要拉取远程更改:
    echo      git pull origin !CURRENT_BRANCH! --rebase
    echo.
    echo   3. 配置阿里云Codeup凭据:
    echo      访问: https://codeup.aliyun.com/settings/personal_access_tokens
    echo.
)

echo.
pause
