#!/bin/bash

################################################################################
# TimeValue 生产环境启动脚本
# Powered by 孚普科技(北京)有限公司
# 适用于阿里云ECS Linux服务器
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
LOG_DIR="${PROJECT_ROOT}/logs"
DATA_DIR="${PROJECT_ROOT}/data"

# 创建必要目录
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"

# 日志文件
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🚀 TimeValue 生产环境启动脚本${NC}"
echo -e "${GREEN}💰 恒产生金 - 让每一份资产都创造价值${NC}"
echo ""
echo -e "${BLUE}🏢 Powered by 孚普科技（北京）有限公司${NC}"
echo -e "${BLUE}🤖 AI驱动的MVP快速迭代解决方案${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 检查是否已经在运行
check_running() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  后端服务已在运行 (PID: $BACKEND_PID)${NC}"
            return 1
        else
            rm -f "$BACKEND_PID_FILE"
        fi
    fi
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  前端服务已在运行 (PID: $FRONTEND_PID)${NC}"
            return 1
        else
            rm -f "$FRONTEND_PID_FILE"
        fi
    fi
    
    return 0
}

# 停止已运行的服务
stop_services() {
    echo -e "${YELLOW}🔄 停止已运行的服务...${NC}"
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            kill -15 "$BACKEND_PID"
            sleep 2
            if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                kill -9 "$BACKEND_PID"
            fi
            echo -e "${GREEN}✓ 后端服务已停止${NC}"
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
            echo -e "${GREEN}✓ 前端服务已停止${NC}"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
}

# 检查Python环境
check_python() {
    echo -e "${BLUE}📋 检查Python环境...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ 未找到Python3，请先安装Python 3.8+${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"
}

# 检查Node.js环境
check_node() {
    echo -e "${BLUE}📋 检查Node.js环境...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ 未找到Node.js，请先安装Node.js 16+${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js版本: $NODE_VERSION${NC}"
}

# 生成密钥
generate_keys() {
    if [ ! -f "${BACKEND_DIR}/.env" ]; then
        echo -e "${BLUE}🔑 生成安全密钥...${NC}"
        cd "$BACKEND_DIR"
        python3 generate_keys.py
        echo -e "${GREEN}✓ 密钥生成完成${NC}"
    else
        echo -e "${GREEN}✓ 密钥文件已存在${NC}"
    fi
}

# 安装后端依赖
install_backend_deps() {
    echo -e "${BLUE}📦 安装后端依赖...${NC}"
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}创建Python虚拟环境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip -q
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
        echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
    else
        echo -e "${RED}✗ 未找到requirements.txt${NC}"
        exit 1
    fi
}

# 安装前端依赖
install_frontend_deps() {
    echo -e "${BLUE}📦 检查前端依赖...${NC}"
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装前端依赖...${NC}"
        npm install
        echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
    else
        echo -e "${GREEN}✓ 前端依赖已安装${NC}"
    fi
}

# 启动后端服务
start_backend() {
    echo -e "${BLUE}🚀 启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 使用nohup后台运行
    nohup python3 app.py > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否成功启动
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
    
    # 检查是否需要构建
    if [ ! -d "dist" ]; then
        echo -e "${YELLOW}构建前端生产版本...${NC}"
        npm run build
    fi
    
    # 使用vite preview启动前端
    nohup npm run preview -- --host 0.0.0.0 --port 3000 > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否成功启动
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
    echo -e "${GREEN}🎉 TimeValue 生产环境启动完成！${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}📊 服务状态:${NC}"
    echo -e "  后端服务: ${GREEN}运行中${NC} (PID: $(cat $BACKEND_PID_FILE))"
    echo -e "  前端服务: ${GREEN}运行中${NC} (PID: $(cat $FRONTEND_PID_FILE))"
    echo ""
    echo -e "${YELLOW}🌐 访问地址:${NC}"
    
    # 获取服务器IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    if [ -z "$SERVER_IP" ]; then
        SERVER_IP="localhost"
    fi
    
    echo -e "  本地访问: ${BLUE}http://localhost:3000${NC}"
    echo -e "  局域网访问: ${BLUE}http://${SERVER_IP}:3000${NC}"
    
    # 如果是阿里云服务器，尝试获取公网IP
    PUBLIC_IP=$(curl -s --connect-timeout 2 ifconfig.me 2>/dev/null || echo "")
    if [ ! -z "$PUBLIC_IP" ]; then
        echo -e "  公网访问: ${BLUE}http://${PUBLIC_IP}:3000${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  安全提示:${NC}"
        echo -e "  请确保阿里云安全组已开放以下端口:"
        echo -e "    - ${GREEN}3000${NC} (前端服务)"
        echo -e "    - ${GREEN}5000${NC} (后端API)"
    fi
    
    echo ""
    echo -e "${YELLOW}👤 默认管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}📝 日志查看:${NC}"
    echo -e "  后端日志: ${BLUE}tail -f $BACKEND_LOG${NC}"
    echo -e "  前端日志: ${BLUE}tail -f $FRONTEND_LOG${NC}"
    echo ""
    echo -e "${YELLOW}🔧 服务管理:${NC}"
    echo -e "  查看状态: ${BLUE}./check_status.sh${NC}"
    echo -e "  停止服务: ${BLUE}./stop_production.sh${NC}"
    echo -e "  重启服务: ${BLUE}./stop_production.sh && ./start_production.sh${NC}"
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
}

# 主流程
main() {
    # 检查环境
    check_python
    check_node
    
    # 停止已运行的服务
    stop_services
    
    # 生成密钥
    generate_keys
    
    # 安装依赖（如果需要）
    if [ "$1" == "--install" ] || [ "$1" == "-i" ]; then
        install_backend_deps
        install_frontend_deps
    fi
    
    # 启动服务
    start_backend
    start_frontend
    
    # 显示信息
    show_info
}

# 执行主流程
main "$@"
