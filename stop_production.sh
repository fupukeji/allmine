#!/bin/bash

################################################################################
# TimeValue 生产环境停止脚本
# Powered by 孚普科技(北京)有限公司
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${YELLOW}🛑 停止 TimeValue 服务...${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 停止后端服务
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}停止后端服务 (PID: $BACKEND_PID)...${NC}"
        kill -15 "$BACKEND_PID"
        
        # 等待最多10秒
        for i in {1..10}; do
            if ! ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # 如果还在运行，强制终止
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            echo -e "${RED}强制终止后端服务...${NC}"
            kill -9 "$BACKEND_PID"
        fi
        
        echo -e "${GREEN}✓ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}后端服务未运行${NC}"
    fi
    rm -f "$BACKEND_PID_FILE"
else
    echo -e "${YELLOW}未找到后端PID文件${NC}"
fi

# 停止前端服务
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}停止前端服务 (PID: $FRONTEND_PID)...${NC}"
        kill -15 "$FRONTEND_PID"
        
        # 等待最多10秒
        for i in {1..10}; do
            if ! ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # 如果还在运行，强制终止
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            echo -e "${RED}强制终止前端服务...${NC}"
            kill -9 "$FRONTEND_PID"
        fi
        
        echo -e "${GREEN}✓ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}前端服务未运行${NC}"
    fi
    rm -f "$FRONTEND_PID_FILE"
else
    echo -e "${YELLOW}未找到前端PID文件${NC}"
fi

# 清理可能的残留进程
echo ""
echo -e "${YELLOW}清理可能的残留进程...${NC}"

# 查找并终止Python app.py进程
PYTHON_PIDS=$(pgrep -f "python.*app.py")
if [ ! -z "$PYTHON_PIDS" ]; then
    echo -e "${YELLOW}发现Python残留进程: $PYTHON_PIDS${NC}"
    kill -9 $PYTHON_PIDS 2>/dev/null
    echo -e "${GREEN}✓ 已清理Python进程${NC}"
fi

# 查找并终止npm preview进程
NPM_PIDS=$(pgrep -f "vite.*preview")
if [ ! -z "$NPM_PIDS" ]; then
    echo -e "${YELLOW}发现npm残留进程: $NPM_PIDS${NC}"
    kill -9 $NPM_PIDS 2>/dev/null
    echo -e "${GREEN}✓ 已清理npm进程${NC}"
fi

echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}✅ TimeValue 服务已完全停止${NC}"
echo -e "${BLUE}================================================================================================${NC}"
