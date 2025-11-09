#!/bin/bash

# TimeValue 系统状态检查脚本
# Powered by 孚普科技（北京）有限公司

echo "================================================================"
echo "🔍 TimeValue 个人资产管理系统 - 状态检查"
echo "================================================================"
echo ""

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查服务运行状态
echo "📊 服务运行状态:"
echo "----------------"

# 检查后端
if [ -f "backend.pid" ]; then
    PID=$(cat backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 后端服务: 运行中 (PID: $PID)"
        # 检查端口
        if netstat -tuln 2>/dev/null | grep -q ":5000 " || ss -tuln 2>/dev/null | grep -q ":5000 "; then
            echo "   └─ 端口 5000: 正常监听"
        else
            echo "   └─ 端口 5000: ⚠️ 未监听"
        fi
    else
        echo "❌ 后端服务: 已停止 (进程不存在)"
    fi
else
    echo "❌ 后端服务: 未运行 (无PID文件)"
fi

# 检查前端
if [ -f "frontend.pid" ]; then
    PID=$(cat frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 前端服务: 运行中 (PID: $PID)"
        # 检查端口
        if netstat -tuln 2>/dev/null | grep -q ":3000 " || ss -tuln 2>/dev/null | grep -q ":3000 "; then
            echo "   └─ 端口 3000: 正常监听"
        else
            echo "   └─ 端口 3000: ⚠️ 未监听"
        fi
    else
        echo "❌ 前端服务: 已停止 (进程不存在)"
    fi
else
    echo "❌ 前端服务: 未运行 (无PID文件)"
fi

echo ""
echo "📁 数据目录状态:"
echo "----------------"
if [ -d "data" ]; then
    echo "✅ 数据目录: 存在"
    if [ -f "backend/timevalue.db" ] || [ -f "data/timevalue.db" ]; then
        echo "✅ 数据库文件: 存在"
    else
        echo "⚠️  数据库文件: 未找到"
    fi
    if [ -d "data/backups" ]; then
        BACKUP_COUNT=$(ls -1 data/backups/*.db 2>/dev/null | wc -l)
        echo "✅ 备份目录: 存在 ($BACKUP_COUNT 个备份文件)"
    else
        echo "⚠️  备份目录: 不存在"
    fi
else
    echo "❌ 数据目录: 不存在"
fi

echo ""
echo "📝 日志文件:"
echo "----------------"
if [ -d "logs" ]; then
    if [ -f "logs/backend.log" ]; then
        BACKEND_LOG_SIZE=$(du -h logs/backend.log | cut -f1)
        echo "✅ 后端日志: logs/backend.log ($BACKEND_LOG_SIZE)"
    else
        echo "⚠️  后端日志: 未找到"
    fi
    if [ -f "logs/frontend.log" ]; then
        FRONTEND_LOG_SIZE=$(du -h logs/frontend.log | cut -f1)
        echo "✅ 前端日志: logs/frontend.log ($FRONTEND_LOG_SIZE)"
    else
        echo "⚠️  前端日志: 未找到"
    fi
else
    echo "⚠️  日志目录: 不存在"
fi

echo ""
echo "🌐 网络访问:"
echo "----------------"
echo "本地访问: http://localhost:3000"
if command -v curl &> /dev/null; then
    PUBLIC_IP=$(curl -s ifconfig.me || echo "无法获取")
    echo "公网访问: http://$PUBLIC_IP:3000"
else
    echo "提示: 安装curl可显示公网IP"
fi

echo ""
echo "💻 系统资源:"
echo "----------------"
if command -v free &> /dev/null; then
    MEM_TOTAL=$(free -h | awk '/^Mem:/{print $2}')
    MEM_USED=$(free -h | awk '/^Mem:/{print $3}')
    echo "内存使用: $MEM_USED / $MEM_TOTAL"
fi
if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h . | awk 'NR==2{print $5}')
    echo "磁盘使用: $DISK_USAGE"
fi

echo ""
echo "================================================================"
echo "🚀 管理命令:"
echo "  - 启动服务: ./start_production.sh"
echo "  - 停止服务: ./stop_production.sh"
echo "  - 查看日志: tail -f logs/backend.log 或 logs/frontend.log"
echo "  - 重新部署: ./deploy.sh"
echo "================================================================"
echo "🏢 Powered by 孚普科技（北京）有限公司"
echo "🌐 https://fupukeji.com"
echo "================================================================"