#!/bin/bash
# 远程服务器重新部署脚本

SERVER="root@60.205.161.210"
PROJECT_DIR="/root/timevalue"

echo "========== 开始重新部署 =========="
echo ""

ssh $SERVER << 'ENDSSH'
cd /root/timevalue

echo "1. 拉取最新代码..."
git pull

echo ""
echo "2. 重新构建并启动容器..."
docker-compose -f docker-compose.server.yml down
docker-compose -f docker-compose.server.yml build --no-cache
docker-compose -f docker-compose.server.yml up -d

echo ""
echo "3. 等待容器启动..."
sleep 10

echo ""
echo "4. 查看容器状态..."
docker ps | grep timevalue

echo ""
echo "5. 查看后端日志（最后30行）..."
docker logs timevalue-backend --tail 30

echo ""
echo "========== 部署完成 =========="
ENDSSH
