@echo off
chcp 65001 >nul
echo =====================================
echo   TimeValue H5 快速启动脚本
echo =====================================
echo.

echo [1/3] 检查环境...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装Node.js，请先安装：https://nodejs.org/
    pause
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未安装Python，请先安装：https://www.python.org/
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

echo [2/3] 启动后端服务...
cd backend
start "TimeValue Backend" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
echo ✅ 后端服务已启动（端口5000）
cd ..
echo.

echo [3/3] 启动H5前端...
cd h5
if not exist "node_modules" (
    echo 正在安装依赖（首次启动需要等待）...
    call npm install
)
start "TimeValue H5" cmd /k "npm run dev"
echo ✅ H5前端已启动（端口3001）
cd ..
echo.

echo =====================================
echo   🎉 启动完成！
echo =====================================
echo.
echo 访问地址：
echo   - 后端API：http://localhost:5000
echo   - H5前端：http://localhost:3001
echo.
echo 💡 提示：
echo   - 在微信中访问H5需要配置公众号
echo   - 详细部署文档见：H5_DEPLOYMENT_GUIDE.md
echo.
pause
