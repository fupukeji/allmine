@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================================
echo 🚀 TimeValue 个人资产管理系统 - Windows 后端启动
echo 💰 恒产生金 - 让每一份资产都创造价值
echo.
echo 🏢 Powered by 孚普科技（北京）有限公司
echo ================================================================
echo.

REM 切换到backend目录
cd /d "%~dp0backend"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version

REM 确保数据目录存在
if not exist "..\data" mkdir "..\data"
if not exist "..\data\backups" mkdir "..\data\backups"
echo ✅ 数据目录已创建

REM 检查是否需要安装依赖
if not exist "venv" (
    echo 📦 首次运行，正在创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo 🚀 正在启动后端服务...
echo 📖 访问地址: http://localhost:5000
echo 💡 按 Ctrl+C 可以停止服务
echo.

python app.py

pause
