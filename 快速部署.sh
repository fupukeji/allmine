#!/bin/bash
# TimeValue 服务器快速部署脚本
# 适用于已安装MySQL的服务器

set -e

echo "========================================"
echo "  TimeValue 服务器快速部署脚本"
echo "========================================"
echo ""

# 检查是否在项目目录
if [ ! -f "docker-compose.server.yml" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 步骤1: 检查Docker
echo "步骤1: 检查Docker环境..."
if ! command -v docker &> /dev/null; then
    echo "Docker未安装，开始安装..."
    sudo yum install -y yum-utils
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "✅ Docker安装完成"
else
    echo "✅ Docker已安装: $(docker --version)"
fi

# 步骤2: 检查Docker Compose
echo ""
echo "步骤2: 检查Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose未安装，开始安装..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose安装完成"
else
    echo "✅ Docker Compose已安装: $(docker-compose --version)"
fi

# 步骤3: 检查MySQL连接
echo ""
echo "步骤3: 检查MySQL连接..."
if command -v mysql &> /dev/null; then
    if mysql -u timevalue -psdA3GThaTaDx3h8S -e "USE timevalue; SELECT 1;" &> /dev/null; then
        echo "✅ MySQL连接成功"
    else
        echo "⚠️  MySQL连接失败，请检查:"
        echo "   1. MySQL是否运行: sudo systemctl status mysqld"
        echo "   2. 用户权限是否正确"
        echo "   3. 密码是否正确"
        read -p "是否继续? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  MySQL客户端未安装，跳过连接测试"
fi

# 步骤4: 配置防火墙
echo ""
echo "步骤4: 配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state &> /dev/null; then
        echo "开放端口5000..."
        sudo firewall-cmd --permanent --add-port=5000/tcp || true
        sudo firewall-cmd --reload
        echo "✅ 防火墙配置完成"
    else
        echo "ℹ️  防火墙未运行"
    fi
else
    echo "ℹ️  firewalld未安装"
fi

# 步骤5: 构建Docker镜像
echo ""
echo "步骤5: 构建Docker镜像..."
echo "这可能需要几分钟..."
docker-compose -f docker-compose.server.yml build --no-cache
echo "✅ Docker镜像构建完成"

# 步骤6: 启动服务
echo ""
echo "步骤6: 启动服务..."
docker-compose -f docker-compose.server.yml --env-file .env.docker up -d
echo "✅ 服务启动成功"

# 步骤7: 等待服务就绪
echo ""
echo "步骤7: 等待服务就绪..."
sleep 5

# 检查健康状态
echo "检查服务健康状态..."
for i in {1..30}; do
    if curl -f http://localhost:5000/api/health &> /dev/null; then
        echo "✅ 服务健康检查通过"
        break
    fi
    echo "等待服务启动... $i/30"
    sleep 2
done

# 步骤8: 显示部署信息
echo ""
echo "========================================"
echo "  🎉 部署成功！"
echo "========================================"
echo ""
echo "📊 服务信息:"
echo "  • 后端API:     http://$(hostname -I | awk '{print $1}'):5000"
echo "  • 健康检查:    http://$(hostname -I | awk '{print $1}'):5000/api/health"
echo "  • 默认账户:    admin / admin123"
echo ""
echo "🛠️  管理命令:"
echo "  • 查看日志:    docker-compose -f docker-compose.server.yml logs -f"
echo "  • 重启服务:    docker-compose -f docker-compose.server.yml restart"
echo "  • 停止服务:    docker-compose -f docker-compose.server.yml down"
echo "  • 查看状态:    docker-compose -f docker-compose.server.yml ps"
echo ""
echo "📚 详细文档: 服务器Docker部署指南.md"
echo ""
echo "========================================"
