#!/bin/bash
# TimeValue 服务器快速部署脚本（宝塔/命令行通用）

set -e

echo "========================================="
echo "  TimeValue 服务器部署脚本"
echo "========================================="
echo ""

# 检查是否在项目目录
if [ ! -f "docker-compose.server.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   当前目录: $(pwd)"
    echo "   应在目录: /opt/timevalue"
    exit 1
fi

echo "✅ 项目目录检查通过"
echo ""

# 检查 .env.docker 文件
if [ ! -f ".env.docker" ]; then
    echo "❌ 错误: .env.docker 文件不存在"
    exit 1
fi

echo "✅ 环境配置文件存在"
echo ""

# 步骤1: 构建镜像
echo "步骤1: 构建Docker镜像..."
echo "----------------------------------------"
docker-compose -f docker-compose.server.yml --env-file .env.docker build

echo ""
echo "✅ 镜像构建成功"
echo ""

# 步骤2: 启动容器
echo "步骤2: 启动容器..."
echo "----------------------------------------"
docker-compose -f docker-compose.server.yml --env-file .env.docker up -d

echo ""
echo "✅ 容器启动成功"
echo ""

# 步骤3: 等待服务就绪
echo "步骤3: 等待服务就绪..."
echo "----------------------------------------"
sleep 5

# 检查容器状态
if docker ps | grep -q timevalue-backend; then
    echo "✅ 容器正在运行"
else
    echo "⚠️  容器未运行，查看日志:"
    docker-compose -f docker-compose.server.yml logs --tail=50 backend
    exit 1
fi

echo ""

# 步骤4: 健康检查
echo "步骤4: 健康检查..."
echo "----------------------------------------"
for i in {1..15}; do
    if curl -f http://localhost:5000/api/health &> /dev/null; then
        echo "✅ 健康检查通过"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "⚠️  健康检查超时，查看日志:"
        docker-compose -f docker-compose.server.yml logs --tail=30 backend
        exit 1
    fi
    echo "等待服务启动... $i/15"
    sleep 2
done

echo ""
echo "========================================="
echo "  🎉 部署成功！"
echo "========================================="
echo ""
echo "📊 服务信息:"
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "  • 后端API:     http://$SERVER_IP:5000"
echo "  • 健康检查:    http://$SERVER_IP:5000/api/health"
echo "  • 管理员:      admin / admin123"
echo ""
echo "🛠️  管理命令:"
echo "  • 查看状态:    docker-compose -f docker-compose.server.yml ps"
echo "  • 查看日志:    docker-compose -f docker-compose.server.yml logs -f"
echo "  • 重启服务:    docker-compose -f docker-compose.server.yml restart"
echo "  • 停止服务:    docker-compose -f docker-compose.server.yml down"
echo ""
echo "📋 下一步:"
echo "  1. 访问健康检查: curl http://localhost:5000/api/health"
echo "  2. 修改管理员密码"
echo "  3. 配置定时备份"
echo ""
echo "========================================="
