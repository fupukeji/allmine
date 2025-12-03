# 远程服务器重新部署脚本 (PowerShell)
$SERVER = "root@60.205.161.210"
$PROJECT_DIR = "/root/timevalue"

Write-Host "========== 开始重新部署 ==========" -ForegroundColor Cyan
Write-Host ""

# 创建SSH命令脚本
$sshCommands = @"
cd /root/timevalue
echo "1. 拉取最新代码..."
git pull
echo ""
echo "2. 停止旧容器..."
docker-compose -f docker-compose.server.yml down
echo ""
echo "3. 重新构建镜像..."
docker-compose -f docker-compose.server.yml build --no-cache backend
echo ""
echo "4. 启动新容器..."
docker-compose -f docker-compose.server.yml up -d
echo ""
echo "5. 等待容器启动..."
sleep 15
echo ""
echo "6. 查看容器状态..."
docker ps | grep timevalue
echo ""
echo "7. 查看后端日志（最后50行）..."
docker logs timevalue-backend --tail 50
"@

# 执行SSH命令
ssh $SERVER $sshCommands

Write-Host ""
Write-Host "========== 部署完成 ==========" -ForegroundColor Green
