#!/bin/bash
set -e

echo "================================"
echo "🚀 TimeValue Backend Starting..."
echo "================================"
echo "🔍 DB_HOST=$DB_HOST, DB_PORT=$DB_PORT, DB_USER=$DB_USER, DB_NAME=$DB_NAME"

# 直接启动应用，让Flask自己处理数据库连接
echo "✅ Starting Gunicorn server..."
exec "$@"
