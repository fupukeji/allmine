#!/bin/bash

# TimeValue 生产环境停止脚本
# Powered by 孚普科技（北京）有限公司

echo "================================================================"
echo "🛑 TimeValue 个人资产管理系统 - 停止服务"
echo "================================================================"
echo ""

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 停止后端服务
if [ -f "backend.pid" ]; then
    PID=$(cat backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ 后端服务已停止 (PID: $PID)"
    else
        echo "⚠️  后端服务未运行"
    fi
    rm -f backend.pid
else
    echo "⚠️  未找到后端PID文件"
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    PID=$(cat frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ 前端服务已停止 (PID: $PID)"
    else
        echo "⚠️  前端服务未运行"
    fi
    rm -f frontend.pid
else
    echo "⚠️  未找到前端PID文件"
fi

echo ""
echo "================================================================"
echo "✅ 所有服务已停止"
echo "================================================================"
