#!/bin/bash

################################################################################
# TimeValue Node.js 生产环境启动脚本
# Powered by 孚普科技(北京)有限公司
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend-node"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
LOG_DIR="${PROJECT_ROOT}/logs"

mkdir -p "$LOG_DIR"

BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🚀 TimeValue Node.js 生产环境启动脚本${NC}"
echo -e "${GREEN}💰 恒产生金 - 让每一份资产都创造价值${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 停止已运行的服务
stop_services() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            kill -15 "$BACKEND_PID"
            sleep 2
            if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                kill -9 "$BACKEND_PID"
            fi
            echo -e "${GREEN}✓ 已停止旧的后端服务${NC}"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            kill -15 "$FRONTEND_PID"
            sleep 2
            if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
                kill -9 "$FRONTEND_PID"
            fi
            echo -e "${GREEN}✓ 已停止旧的前端服务${NC}"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
}

# 检查Node.js环境
check_node() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ 未找到Node.js，请先安装Node.js 18+${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js版本: $NODE_VERSION${NC}"
}

# 安装依赖
install_deps() {
    if [ "$1" == "--install" ] || [ "$1" == "-i" ]; then
        echo -e "${BLUE}📦 安装后端依赖...${NC}"
        cd "$BACKEND_DIR"
        npm install
        echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
        
        echo -e "${BLUE}📦 检查前端依赖...${NC}"
        cd "$FRONTEND_DIR"
        if [ ! -d "node_modules" ]; then
            npm install
            echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
        else
            echo -e "${GREEN}✓ 前端依赖已安装${NC}"
        fi
    fi
}

# 启动后端服务
start_backend() {
    echo -e "${BLUE}🚀 启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    
    nohup node server.js > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    
    sleep 3
    
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
        echo -e "${GREEN}  - 访问地址: http://0.0.0.0:5000${NC}"
        echo -e "${GREEN}  - 日志文件: $BACKEND_LOG${NC}"
    else
        echo -e "${RED}✗ 后端服务启动失败，请查看日志: $BACKEND_LOG${NC}"
        cat "$BACKEND_LOG"
        exit 1
    fi
}

# 启动前端服务
start_frontend() {
    echo -e "${BLUE}🚀 启动前端服务...${NC}"
    cd "$FRONTEND_DIR"
    
    if [ ! -d "dist" ]; then
        echo -e "${YELLOW}构建前端生产版本...${NC}"
        npm run build
    fi
    
    nohup npm run preview -- --host 0.0.0.0 --port 3000 > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    
    sleep 3
    
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
        echo -e "${GREEN}  - 访问地址: http://0.0.0.0:3000${NC}"
        echo -e "${GREEN}  - 日志文件: $FRONTEND_LOG${NC}"
    else
        echo -e "${RED}✗ 前端服务启动失败，请查看日志: $FRONTEND_LOG${NC}"
        cat "$FRONTEND_LOG"
        exit 1
    fi
}

# 显示服务信息
show_info() {
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${GREEN}🎉 TimeValue 服务启动完成！${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}📊 服务状态:${NC}"
    echo -e "  后端服务 (Node.js): ${GREEN}运行中${NC} (PID: $(cat $BACKEND_PID_FILE))"
    echo -e "  前端服务 (React): ${GREEN}运行中${NC} (PID: $(cat $FRONTEND_PID_FILE))"
    echo -e "  数据库: ${GREEN}PostgreSQL${NC}"
    echo ""
    echo -e "${YELLOW}🌐 访问地址:${NC}"
    
    SERVER_IP=$(hostname -I | awk '{print $1}')
    if [ -z "$SERVER_IP" ]; then
        SERVER_IP="localhost"
    fi
    
    echo -e "  本地访问: ${BLUE}http://localhost:3000${NC}"
    echo -e "  局域网访问: ${BLUE}http://${SERVER_IP}:3000${NC}"
    
    PUBLIC_IP=$(curl -s --connect-timeout 2 ifconfig.me 2>/dev/null || echo "")
    if [ ! -z "$PUBLIC_IP" ]; then
        echo -e "  公网访问: ${BLUE}http://${PUBLIC_IP}:3000${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}👤 默认管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
}

# 主流程
main() {
    check_node
    stop_services
    install_deps "$@"
    start_backend
    start_frontend
    show_info
}

main "$@"
