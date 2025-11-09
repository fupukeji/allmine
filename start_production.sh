#!/bin/bash

# TimeValue 生产环境启动脚本
# Powered by 孚普科技（北京）有限公司
# 适用于阿里云ECS环境

set -e

echo "================================================================"
echo "🚀 TimeValue 个人资产管理系统 - 生产环境启动"
echo "💰 恒产生金 - 让每一份资产都创造价值"
echo ""
echo "🏢 Powered by 孚普科技（北京）有限公司"
echo "================================================================"
echo ""

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 确保数据目录存在
mkdir -p data/backups

# 检查是否已经在运行
check_running() {
    if [ -f "backend.pid" ]; then
        PID=$(cat backend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  后端服务已在运行 (PID: $PID)"
            return 0
        else
            rm -f backend.pid
        fi
    fi
    
    if [ -f "frontend.pid" ]; then
        PID=$(cat frontend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  前端服务已在运行 (PID: $PID)"
            return 0
        else
            rm -f frontend.pid
        fi
    fi
    
    return 1
}

# 停止已有服务
stop_services() {
    echo "🛑 正在停止现有服务..."
    
    if [ -f "backend.pid" ]; then
        PID=$(cat backend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo "✅ 后端服务已停止 (PID: $PID)"
        fi
        rm -f backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        PID=$(cat frontend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo "✅ 前端服务已停止 (PID: $PID)"
        fi
        rm -f frontend.pid
    fi
    
    # 确保端口释放
    sleep 2
}

# 启动后端服务
start_backend() {
    echo "🚀 正在启动后端服务..."
    cd backend
    
    # 使用nohup后台运行
    nohup python3 app.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID, 端口: 5000)"
    echo "📝 日志文件: logs/backend.log"
}

# 构建前端
build_frontend() {
    echo "🏗️  正在构建前端静态资源..."
    cd frontend
    npm run build
    cd ..
    echo "✅ 前端构建完成"
}

# 启动前端服务（开发模式）
start_frontend_dev() {
    echo "🚀 正在启动前端服务（开发模式）..."
    cd frontend
    
    # 使用nohup后台运行
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID, 端口: 3000)"
    echo "📝 日志文件: logs/frontend.log"
}

# 主启动流程
main() {
    # 创建日志目录
    mkdir -p logs
    
    # 检查是否已运行
    if check_running; then
        echo ""
        read -p "是否要重启服务？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "取消操作"
            exit 0
        fi
        stop_services
    fi
    
    echo "开始启动服务..."
    echo ""
    
    # 启动后端
    start_backend
    
    # 等待后端启动
    sleep 3
    
    # 检查后端是否成功启动
    if ! ps -p $(cat backend.pid) > /dev/null 2>&1; then
        echo "❌ 后端服务启动失败，请查看日志: logs/backend.log"
        exit 1
    fi
    
    # 启动前端（开发模式）
    start_frontend_dev
    
    # 等待前端启动
    sleep 3
    
    # 检查前端是否成功启动
    if ! ps -p $(cat frontend.pid) > /dev/null 2>&1; then
        echo "❌ 前端服务启动失败，请查看日志: logs/frontend.log"
        stop_services
        exit 1
    fi
    
    echo ""
    echo "================================================================"
    echo "🎉 TimeValue 系统启动成功！"
    echo ""
    echo "🌐 访问地址:"
    echo "  - 本地访问: http://localhost:3000"
    echo "  - 远程访问: http://$(curl -s ifconfig.me):3000"
    echo ""
    echo "📊 API 地址: http://localhost:5000"
    echo ""
    echo "📖 管理命令:"
    echo "  - 查看状态: ./check-status.sh"
    echo "  - 停止服务: ./stop_production.sh"
    echo "  - 查看日志: tail -f logs/backend.log 或 logs/frontend.log"
    echo ""
    echo "📝 进程信息:"
    echo "  - 后端 PID: $(cat backend.pid)"
    echo "  - 前端 PID: $(cat frontend.pid)"
    echo ""
    echo "================================================================"
    echo "🚀 Powered by 孚普科技（北京）有限公司"
    echo "🌐 https://fupukeji.com"
    echo "================================================================"
}

# 执行主流程
main
