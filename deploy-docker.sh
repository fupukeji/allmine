#!/bin/bash
# TimeValue Docker 快速部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印Logo
print_logo() {
    echo -e "${BLUE}"
    cat << "EOF"
╔════════════════════════════════════════════════╗
║                                                ║
║         ████████ ██ ███    ███ ███████         ║
║            ██    ██ ████  ████ ██              ║
║            ██    ██ ██ ████ ██ █████           ║
║            ██    ██ ██  ██  ██ ██              ║
║            ██    ██ ██      ██ ███████         ║
║                                                ║
║              ██    ██  █████  ██      ██   ██  ║
║              ██    ██ ██   ██ ██      ██   ██  ║
║              ██    ██ ███████ ██      ██   ██  ║
║               ██  ██  ██   ██ ██      ██   ██  ║
║                ████   ██   ██ ███████  █████   ║
║                                                ║
║          🏢 Powered by 孚普科技（北京）有限公司  ║
║          💰 恒产生金 - 让每一份资产都创造价值    ║
║                                                ║
╚════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 检查Docker是否安装
check_docker() {
    print_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        echo "安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        echo "安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker环境检查通过"
    docker --version
    docker-compose --version
}

# 检查环境配置文件
check_env_file() {
    print_info "检查环境配置..."
    
    if [ ! -f ".env.docker" ]; then
        print_warning "环境配置文件不存在，正在创建..."
        cp .env.docker.example .env.docker 2>/dev/null || cp .env.docker .env.docker
        
        # 生成随机密钥
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        
        # 替换默认密钥
        sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.docker
        sed -i.bak "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" .env.docker
        rm -f .env.docker.bak
        
        print_success "环境配置文件已创建"
        print_warning "⚠️  请编辑 .env.docker 修改数据库密码！"
        
        read -p "是否现在编辑配置文件? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env.docker
        fi
    else
        print_success "环境配置文件已存在"
    fi
    
    # 检查是否使用默认密码
    if grep -q "your_strong.*password" .env.docker; then
        print_warning "⚠️  检测到使用默认密码，强烈建议修改！"
    fi
}

# 构建镜像
build_images() {
    print_info "开始构建Docker镜像..."
    print_info "这可能需要几分钟，请耐心等待..."
    
    if docker-compose build --no-cache; then
        print_success "Docker镜像构建成功"
    else
        print_error "Docker镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    print_info "启动TimeValue服务..."
    
    if docker-compose --env-file .env.docker up -d; then
        print_success "服务启动成功"
    else
        print_error "服务启动失败"
        exit 1
    fi
    
    # 等待服务就绪
    print_info "等待服务就绪..."
    sleep 5
    
    # 检查MySQL
    print_info "检查MySQL状态..."
    for i in {1..30}; do
        if docker-compose exec -T mysql mysqladmin ping -h localhost -u root -p$(grep DB_ROOT_PASSWORD .env.docker | cut -d'=' -f2) --silent 2>/dev/null; then
            print_success "MySQL已就绪"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo
    
    # 检查后端
    print_info "检查后端状态..."
    for i in {1..30}; do
        if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
            print_success "后端已就绪"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo
}

# 显示服务信息
show_services_info() {
    echo
    echo -e "${GREEN}════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  🎉 TimeValue 部署成功！${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════${NC}"
    echo
    echo -e "${BLUE}📊 服务访问地址:${NC}"
    echo -e "  • 后端API:     ${GREEN}http://localhost:5000${NC}"
    echo -e "  • 健康检查:    ${GREEN}http://localhost:5000/api/health${NC}"
    echo -e "  • 前端Web:     ${GREEN}http://localhost:3000${NC}"
    echo
    echo -e "${BLUE}🔑 默认管理员账户:${NC}"
    echo -e "  • 用户名:      ${YELLOW}admin${NC}"
    echo -e "  • 密码:        ${YELLOW}admin123${NC}"
    echo -e "  ${RED}⚠️  首次登录后请立即修改密码！${NC}"
    echo
    echo -e "${BLUE}🛠️  常用命令:${NC}"
    echo -e "  • 查看日志:    ${YELLOW}make logs${NC} 或 ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  • 停止服务:    ${YELLOW}make down${NC} 或 ${YELLOW}docker-compose down${NC}"
    echo -e "  • 重启服务:    ${YELLOW}make restart${NC}"
    echo -e "  • 备份数据:    ${YELLOW}make backup${NC}"
    echo -e "  • 查看状态:    ${YELLOW}make ps${NC}"
    echo
    echo -e "${BLUE}📚 文档:${NC}"
    echo -e "  • 完整部署文档: ${GREEN}DOCKER_DEPLOYMENT.md${NC}"
    echo -e "  • GitHub:      ${GREEN}https://github.com/fupukeji/timevalue${NC}"
    echo
    echo -e "${GREEN}════════════════════════════════════════════════${NC}"
    echo
}

# 主函数
main() {
    print_logo
    
    # 检查运行模式
    MODE=${1:-full}
    
    case "$MODE" in
        check)
            check_docker
            check_env_file
            ;;
        build)
            check_docker
            build_images
            ;;
        start)
            check_docker
            start_services
            show_services_info
            ;;
        full|*)
            check_docker
            check_env_file
            build_images
            start_services
            show_services_info
            ;;
    esac
}

# 运行主函数
main "$@"
