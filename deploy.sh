#!/bin/bash

################################################################################
# TimeValue 一键部署脚本
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

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🚀 TimeValue 一键部署脚本${NC}"
echo -e "${GREEN}💰 恒产生金 - 让每一份资产都创造价值${NC}"
echo ""
echo -e "${BLUE}🏢 Powered by 孚普科技（北京）有限公司${NC}"
echo -e "${BLUE}🤖 AI驱动的MVP快速迭代解决方案${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        echo -e "${GREEN}✓ 检测到操作系统: $PRETTY_NAME${NC}"
    else
        echo -e "${RED}✗ 无法检测操作系统类型${NC}"
        exit 1
    fi
}

# 安装Python3
install_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✓ Python已安装: $PYTHON_VERSION${NC}"
        return
    fi
    
    echo -e "${YELLOW}📦 安装Python3...${NC}"
    
    case $OS in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            ;;
        centos|rhel|alinux)
            sudo yum install -y python3 python3-pip
            ;;
        *)
            echo -e "${RED}✗ 不支持的操作系统: $OS${NC}"
            exit 1
            ;;
    esac
    
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓ Python3安装成功${NC}"
    else
        echo -e "${RED}✗ Python3安装失败${NC}"
        exit 1
    fi
}

# 安装Node.js
install_nodejs() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}✓ Node.js已安装: $NODE_VERSION${NC}"
        return
    fi
    
    echo -e "${YELLOW}📦 安装Node.js...${NC}"
    
    # 使用NodeSource仓库安装Node.js 18.x LTS
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - 2>/dev/null || \
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - 2>/dev/null
    
    case $OS in
        ubuntu|debian)
            sudo apt install -y nodejs
            ;;
        centos|rhel|alinux)
            sudo yum install -y nodejs
            ;;
    esac
    
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✓ Node.js安装成功${NC}"
    else
        echo -e "${RED}✗ Node.js安装失败${NC}"
        exit 1
    fi
}

# 创建数据目录
create_directories() {
    echo -e "${YELLOW}📁 创建必要目录...${NC}"
    mkdir -p "${PROJECT_ROOT}/data"
    mkdir -p "${PROJECT_ROOT}/logs"
    mkdir -p "${PROJECT_ROOT}/data/backup"
    chmod 755 "${PROJECT_ROOT}/data"
    chmod 755 "${PROJECT_ROOT}/logs"
    echo -e "${GREEN}✓ 目录创建完成${NC}"
}

# 生成密钥
generate_keys() {
    echo -e "${YELLOW}🔑 生成安全密钥...${NC}"
    cd "${PROJECT_ROOT}/backend"
    
    if [ -f ".env" ]; then
        echo -e "${YELLOW}密钥文件已存在，跳过生成${NC}"
    else
        python3 generate_keys.py
        echo -e "${GREEN}✓ 密钥生成完成${NC}"
    fi
}

# 安装后端依赖
install_backend() {
    echo -e "${YELLOW}📦 安装后端依赖...${NC}"
    cd "${PROJECT_ROOT}/backend"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip -q
    
    # 安装依赖
    pip install -r requirements.txt -q
    
    echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
}

# 安装前端依赖
install_frontend() {
    echo -e "${YELLOW}📦 安装前端依赖...${NC}"
    cd "${PROJECT_ROOT}/frontend"
    
    # 清理可能的npm缓存
    npm cache clean --force 2>/dev/null || true
    
    # 安装依赖
    npm install
    
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
}

# 设置脚本权限
set_permissions() {
    echo -e "${YELLOW}🔧 设置脚本权限...${NC}"
    cd "${PROJECT_ROOT}"
    
    chmod +x start_production.sh
    chmod +x stop_production.sh
    chmod +x check_status.sh
    chmod +x deploy.sh
    
    echo -e "${GREEN}✓ 权限设置完成${NC}"
}

# 显示完成信息
show_completion() {
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${GREEN}🎉 TimeValue 部署完成！${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo ""
    echo -e "${YELLOW}📋 下一步操作:${NC}"
    echo ""
    echo -e "  1. 启动生产服务:"
    echo -e "     ${BLUE}./start_production.sh${NC}"
    echo ""
    echo -e "  2. 查看服务状态:"
    echo -e "     ${BLUE}./check_status.sh${NC}"
    echo ""
    echo -e "  3. 停止服务:"
    echo -e "     ${BLUE}./stop_production.sh${NC}"
    echo ""
    echo -e "${YELLOW}🌐 访问应用:${NC}"
    
    SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    echo -e "  本地: ${BLUE}http://localhost:3000${NC}"
    echo -e "  局域网: ${BLUE}http://${SERVER_IP}:3000${NC}"
    
    PUBLIC_IP=$(curl -s --connect-timeout 2 ifconfig.me 2>/dev/null || echo "")
    if [ ! -z "$PUBLIC_IP" ]; then
        echo -e "  公网: ${BLUE}http://${PUBLIC_IP}:3000${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  请确保阿里云安全组已开放端口 3000 和 5000${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}👤 默认管理员:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
}

# 主流程
main() {
    detect_os
    install_python
    install_nodejs
    create_directories
    generate_keys
    install_backend
    install_frontend
    set_permissions
    show_completion
}

# 执行主流程
main
