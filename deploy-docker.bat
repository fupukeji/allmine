@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM TimeValue Docker 快速部署脚本 - Windows版本

echo.
echo ════════════════════════════════════════════════
echo          ████████ ██ ███    ███ ███████         
echo             ██    ██ ████  ████ ██              
echo             ██    ██ ██ ████ ██ █████           
echo             ██    ██ ██  ██  ██ ██              
echo             ██    ██ ██      ██ ███████         
echo.
echo               ██    ██  █████  ██      ██   ██  
echo               ██    ██ ██   ██ ██      ██   ██  
echo               ██    ██ ███████ ██      ██   ██  
echo                ██  ██  ██   ██ ██      ██   ██  
echo                 ████   ██   ██ ███████  █████   
echo.
echo          🏢 Powered by 孚普科技（北京）有限公司
echo          💰 恒产生金 - 让每一份资产都创造价值
echo.
echo ════════════════════════════════════════════════
echo.

REM 检查Docker是否安装
echo [INFO] 检查Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose未安装
    pause
    exit /b 1
)

echo [SUCCESS] Docker环境检查通过
docker --version
docker-compose --version
echo.

REM 检查环境配置文件
echo [INFO] 检查环境配置...
if not exist .env.docker (
    echo [WARNING] 环境配置文件不存在，正在创建...
    copy .env.docker .env.docker >nul 2>&1
    
    REM 生成随机密钥（Windows PowerShell）
    for /f %%i in ('powershell -Command "[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))"') do set SECRET_KEY=%%i
    for /f %%i in ('powershell -Command "[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))"') do set JWT_SECRET_KEY=%%i
    
    echo [SUCCESS] 环境配置文件已创建
    echo [WARNING] ⚠️  请编辑 .env.docker 修改数据库密码！
    echo.
    
    set /p EDIT_CONFIG="是否现在编辑配置文件? [Y/N]: "
    if /i "!EDIT_CONFIG!"=="Y" (
        notepad .env.docker
    )
) else (
    echo [SUCCESS] 环境配置文件已存在
)
echo.

REM 构建镜像
echo [INFO] 开始构建Docker镜像...
echo [INFO] 这可能需要几分钟，请耐心等待...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Docker镜像构建失败
    pause
    exit /b 1
)
echo [SUCCESS] Docker镜像构建成功
echo.

REM 启动服务
echo [INFO] 启动TimeValue服务...
docker-compose --env-file .env.docker up -d
if errorlevel 1 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)
echo [SUCCESS] 服务启动成功
echo.

REM 等待服务就绪
echo [INFO] 等待服务就绪...
timeout /t 5 /nobreak >nul

echo [INFO] 检查MySQL状态...
set MYSQL_READY=0
for /l %%i in (1,1,30) do (
    docker-compose exec -T mysql mysqladmin ping -h localhost -u root --silent >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] MySQL已就绪
        set MYSQL_READY=1
        goto :mysql_ready
    )
    echo 等待MySQL启动... %%i/30
    timeout /t 1 /nobreak >nul
)
:mysql_ready

echo.
echo [INFO] 检查后端状态...
set BACKEND_READY=0
for /l %%i in (1,1,30) do (
    curl -f http://localhost:5000/api/health >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] 后端已就绪
        set BACKEND_READY=1
        goto :backend_ready
    )
    echo 等待后端启动... %%i/30
    timeout /t 1 /nobreak >nul
)
:backend_ready

REM 显示服务信息
echo.
echo ════════════════════════════════════════════════
echo   🎉 TimeValue 部署成功！
echo ════════════════════════════════════════════════
echo.
echo 📊 服务访问地址:
echo   • 后端API:     http://localhost:5000
echo   • 健康检查:    http://localhost:5000/api/health
echo   • 前端Web:     http://localhost:3000
echo.
echo 🔑 默认管理员账户:
echo   • 用户名:      admin
echo   • 密码:        admin123
echo   ⚠️  首次登录后请立即修改密码！
echo.
echo 🛠️  常用命令:
echo   • 查看日志:    docker-compose logs -f
echo   • 停止服务:    docker-compose down
echo   • 重启服务:    docker-compose restart
echo   • 查看状态:    docker-compose ps
echo.
echo 📚 文档:
echo   • 完整部署文档: DOCKER_DEPLOYMENT.md
echo   • GitHub:      https://github.com/fupukeji/timevalue
echo.
echo ════════════════════════════════════════════════
echo.

pause
