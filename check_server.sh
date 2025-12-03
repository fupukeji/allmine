#!/bin/bash
# 服务器诊断脚本

echo "========== TimeValue服务器诊断 =========="
echo ""

echo "1. Docker容器状态："
docker ps -a | grep timevalue

echo ""
echo "2. 后端容器日志（最后50行）："
docker logs timevalue-backend --tail 50

echo ""
echo "3. 健康检查："
curl -s http://localhost:5000/api/health || echo "健康检查失败"

echo ""
echo "4. 数据库连接测试："
docker exec timevalue-backend python -c "
from database import db
from app import create_app
app = create_app()
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('✓ 数据库连接成功')
    except Exception as e:
        print(f'✗ 数据库连接失败: {e}')
" 2>&1

echo ""
echo "========== 诊断完成 =========="
