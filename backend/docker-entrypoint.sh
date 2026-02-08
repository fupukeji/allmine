#!/bin/bash
set -e

echo "================================"
echo "🚀 TimeValue Backend Starting..."
echo "================================"
echo "🔍 DB_HOST=$DB_HOST, DB_PORT=$DB_PORT, DB_USER=$DB_USER, DB_NAME=$DB_NAME"

# 初始化数据库表
echo "🔧 Initializing database tables..."
python init_db.py || echo "⚠️ Database init warning (may already exist)"

# 启动应用
echo "✅ Starting Gunicorn server..."
exec "$@"
