#!/bin/bash

################################################################################
# TimeValue 服务状态检查脚本
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
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}📊 TimeValue 服务状态检查${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 检查后端服务
echo -e "${YELLOW}🔍 后端服务状态:${NC}"
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo -e "  状态: ${GREEN}✓ 运行中${NC}"
        echo -e "  PID: ${BACKEND_PID}"
        echo -e "  端口: 5000"
        
        # 检查端口是否在监听
        if netstat -tuln 2>/dev/null | grep -q ":5000 " || ss -tuln 2>/dev/null | grep -q ":5000 "; then
            echo -e "  监听: ${GREEN}✓ 正常${NC}"
        else
            echo -e "  监听: ${RED}✗ 异常${NC}"
        fi
        
        # 显示进程信息
        echo -e "  进程信息:"
        ps -p "$BACKEND_PID" -o pid,vsz,rss,%cpu,%mem,etime,cmd | tail -n 1 | sed 's/^/    /'
        
        # 显示最近日志
        if [ -f "$BACKEND_LOG" ]; then
            echo -e "  最近日志 (最后5行):"
            tail -n 5 "$BACKEND_LOG" | sed 's/^/    /'
        fi
    else
        echo -e "  状态: ${RED}✗ 未运行${NC} (PID文件存在但进程不存在)"
    fi
else
    echo -e "  状态: ${RED}✗ 未运行${NC} (未找到PID文件)"
fi

echo ""

# 检查前端服务
echo -e "${YELLOW}🔍 前端服务状态:${NC}"
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
        echo -e "  状态: ${GREEN}✓ 运行中${NC}"
        echo -e "  PID: ${FRONTEND_PID}"
        echo -e "  端口: 3000"
        
        # 检查端口是否在监听
        if netstat -tuln 2>/dev/null | grep -q ":3000 " || ss -tuln 2>/dev/null | grep -q ":3000 "; then
            echo -e "  监听: ${GREEN}✓ 正常${NC}"
        else
            echo -e "  监听: ${RED}✗ 异常${NC}"
        fi
        
        # 显示进程信息
        echo -e "  进程信息:"
        ps -p "$FRONTEND_PID" -o pid,vsz,rss,%cpu,%mem,etime,cmd | tail -n 1 | sed 's/^/    /'
        
        # 显示最近日志
        if [ -f "$FRONTEND_LOG" ]; then
            echo -e "  最近日志 (最后5行):"
            tail -n 5 "$FRONTEND_LOG" | sed 's/^/    /'
        fi
    else
        echo -e "  状态: ${RED}✗ 未运行${NC} (PID文件存在但进程不存在)"
    fi
else
    echo -e "  状态: ${RED}✗ 未运行${NC} (未找到PID文件)"
fi

echo ""

# 检查端口占用
echo -e "${YELLOW}🔍 端口占用情况:${NC}"
echo -e "  后端端口 5000:"
if command -v netstat &> /dev/null; then
    netstat -tuln | grep ":5000 " | sed 's/^/    /' || echo -e "    ${YELLOW}未占用${NC}"
elif command -v ss &> /dev/null; then
    ss -tuln | grep ":5000 " | sed 's/^/    /' || echo -e "    ${YELLOW}未占用${NC}"
fi

echo -e "  前端端口 3000:"
if command -v netstat &> /dev/null; then
    netstat -tuln | grep ":3000 " | sed 's/^/    /' || echo -e "    ${YELLOW}未占用${NC}"
elif command -v ss &> /dev/null; then
    ss -tuln | grep ":3000 " | sed 's/^/    /' || echo -e "    ${YELLOW}未占用${NC}"
fi

echo ""

# 系统资源使用
echo -e "${YELLOW}🔍 系统资源使用:${NC}"
if command -v free &> /dev/null; then
    echo -e "  内存使用:"
    free -h | grep -E "Mem|内存" | sed 's/^/    /'
fi

if command -v df &> /dev/null; then
    echo -e "  磁盘使用:"
    df -h "$PROJECT_ROOT" | tail -n 1 | sed 's/^/    /'
fi

echo ""

# 访问地址
echo -e "${YELLOW}🌐 访问地址:${NC}"
SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
echo -e "  本地: ${BLUE}http://localhost:3000${NC}"
echo -e "  局域网: ${BLUE}http://${SERVER_IP}:3000${NC}"

PUBLIC_IP=$(curl -s --connect-timeout 2 ifconfig.me 2>/dev/null || echo "")
if [ ! -z "$PUBLIC_IP" ]; then
    echo -e "  公网: ${BLUE}http://${PUBLIC_IP}:3000${NC}"
fi

echo ""
echo -e "${BLUE}================================================================================================${NC}"

# 返回状态码
if [ -f "$BACKEND_PID_FILE" ] && [ -f "$FRONTEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if ps -p "$BACKEND_PID" > /dev/null 2>&1 && ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 所有服务运行正常${NC}"
        exit 0
    fi
fi

echo -e "${RED}⚠️  部分服务未运行${NC}"
exit 1
