#!/bin/bash

# =================================================================
# TimeValue Nginx配置功能测试脚本
# 用于验证Nginx动态配置功能是否正常
# =================================================================

set -e

echo "================================================================"
echo "🧪 TimeValue Nginx配置功能测试"
echo "================================================================"
echo ""

# 检查是否提供了访问令牌
if [ -z "$1" ]; then
    echo "⚠️  未提供访问令牌"
    echo "💡 使用方法: bash test_nginx_api.sh <ACCESS_TOKEN>"
    echo ""
    echo "📝 获取令牌步骤："
    echo "   1. 启动应用: bash start_production.sh"
    echo "   2. 登录系统获取token"
    echo "   3. 运行: bash test_nginx_api.sh YOUR_TOKEN"
    echo ""
    exit 1
fi

TOKEN=$1
BASE_URL="${2:-http://localhost:5000}"

echo "🔑 使用令牌: ${TOKEN:0:20}..."
echo "🌐 API地址: $BASE_URL"
echo ""

# 测试1：获取Nginx状态
echo "1️⃣ 测试：获取Nginx状态"
echo "   请求: GET /api/nginx/status"
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/nginx/status")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ 状态码: $HTTP_CODE"
    echo "   📄 响应: $BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "   ❌ 失败，状态码: $HTTP_CODE"
    echo "   📄 响应: $BODY"
fi
echo ""

# 测试2：创建Nginx配置
echo "2️⃣ 测试：创建Nginx配置"
echo "   请求: POST /api/nginx/configs"

CONFIG_DATA='{
  "server_name": "test.example.com",
  "listen_port": 80,
  "ssl_enabled": false,
  "frontend_port": 3000,
  "backend_port": 5000,
  "gzip_enabled": true,
  "access_log_enabled": true
}'

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CONFIG_DATA" \
    "$BASE_URL/api/nginx/configs")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
    echo "   ✅ 状态码: $HTTP_CODE"
    CONFIG_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null || echo "")
    echo "   📄 配置ID: $CONFIG_ID"
    echo "   📄 响应: $BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "   ❌ 失败，状态码: $HTTP_CODE"
    echo "   📄 响应: $BODY"
    CONFIG_ID=""
fi
echo ""

# 测试3：获取配置列表
echo "3️⃣ 测试：获取配置列表"
echo "   请求: GET /api/nginx/configs"
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL/api/nginx/configs")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ 状态码: $HTTP_CODE"
    COUNT=$(echo "$BODY" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['data']))" 2>/dev/null || echo "0")
    echo "   📊 配置数量: $COUNT"
    echo "   📄 响应: $BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "   ❌ 失败，状态码: $HTTP_CODE"
    echo "   📄 响应: $BODY"
fi
echo ""

# 测试4：预览配置（如果有配置ID）
if [ -n "$CONFIG_ID" ] && [ "$CONFIG_ID" != "null" ]; then
    echo "4️⃣ 测试：预览配置"
    echo "   请求: GET /api/nginx/configs/$CONFIG_ID/preview"
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$BASE_URL/api/nginx/configs/$CONFIG_ID/preview")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ 状态码: $HTTP_CODE"
        echo "   📄 配置预览:"
        echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['content'])" 2>/dev/null || echo "$BODY"
    else
        echo "   ❌ 失败，状态码: $HTTP_CODE"
        echo "   📄 响应: $BODY"
    fi
    echo ""
    
    # 测试5：删除配置
    echo "5️⃣ 测试：删除配置"
    echo "   请求: DELETE /api/nginx/configs/$CONFIG_ID"
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X DELETE \
        -H "Authorization: Bearer $TOKEN" \
        "$BASE_URL/api/nginx/configs/$CONFIG_ID")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ 状态码: $HTTP_CODE"
        echo "   📄 响应: $BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    else
        echo "   ❌ 失败，状态码: $HTTP_CODE"
        echo "   📄 响应: $BODY"
    fi
    echo ""
fi

echo "================================================================"
echo "✅ 测试完成！"
echo "================================================================"
echo ""
echo "💡 提示："
echo "   • 以上测试仅验证API接口功能"
echo "   • 实际应用配置需要管理员权限"
echo "   • 完整测试请访问Web界面: $BASE_URL"
echo ""
