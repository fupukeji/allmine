# TimeValue 登录问题快速诊断和修复
$SERVER = "root@60.205.161.210"

Write-Host "========== TimeValue 登录问题诊断 ==========" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. 检查容器状态..." -ForegroundColor Yellow
ssh $SERVER "docker ps -a | grep timevalue"

Write-Host ""
Write-Host "2. 检查后端日志..." -ForegroundColor Yellow
ssh $SERVER "docker logs timevalue-backend --tail 100 2>&1 | grep -i error" 

Write-Host ""
Write-Host "3. 测试数据库连接..." -ForegroundColor Yellow
ssh $SERVER "docker exec timevalue-backend python -c 'from database import db; from app import create_app; app=create_app(); app.app_context().push(); db.session.execute(\"SELECT 1\"); print(\"数据库连接成功\")' 2>&1"

Write-Host ""
Write-Host "4. 检查用户表..." -ForegroundColor Yellow  
ssh $SERVER "docker exec timevalue-backend python -c 'from database import db; from models.user import User; from app import create_app; app=create_app(); app.app_context().push(); print(f\"用户总数: {User.query.count()}\"); admin=User.query.filter_by(username=\"admin\").first(); print(f\"管理员存在: {admin is not None}\")' 2>&1"

Write-Host ""
Write-Host "========== 诊断完成 ==========" -ForegroundColor Green
Write-Host ""
Write-Host "如果数据库连接失败，请检查以下内容：" -ForegroundColor Yellow
Write-Host "1. MySQL服务是否运行" 
Write-Host "2. 数据库timevalue是否存在"
Write-Host "3. 用户timevalue是否有权限"
Write-Host "4. Docker容器是否能访问宿主机MySQL"
