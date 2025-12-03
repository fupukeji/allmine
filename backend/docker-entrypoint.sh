#!/bin/bash
set -e

echo "================================"
echo "🚀 TimeValue Backend Starting..."
echo "================================"

# 等待MySQL就绪
echo "⏳ Waiting for MySQL to be ready..."
echo "🔍 DB_HOST=$DB_HOST, DB_PORT=$DB_PORT, DB_USER=$DB_USER, DB_NAME=$DB_NAME"
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -c "
import pymysql
import os
try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'mysql'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'timevalue'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'timevalue')
    )
    conn.close()
    exit(0)
except Exception as e:
    print(f'Error: {e}', file=__import__('sys').stderr)
    exit(1)
" 2>/dev/null; then
        echo "✅ MySQL is ready!"
        break
    else
        retry_count=$((retry_count + 1))
        echo "   Attempt $retry_count/$max_retries - MySQL not ready yet..."
        sleep 2
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ MySQL connection failed after $max_retries attempts"
    exit 1
fi

# 初始化数据库（如果需要）
echo "🔧 Initializing database..."
python init_db.py || echo "⚠️  Database initialization warning (may already exist)"

# 启动应用
echo "✅ Starting Gunicorn server..."
exec "$@"
