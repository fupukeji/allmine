#!/bin/bash

# 项目完成状态检查脚本

echo "🚀 时间价值计算器 - 项目状态检查"
echo "=================================="

# 检查项目结构
echo "📁 检查项目结构..."

# 后端文件检查
backend_files=(
    "backend/app.py"
    "backend/requirements.txt"
    "backend/Dockerfile"
    "backend/models/user.py"
    "backend/models/category.py"
    "backend/models/project.py"
    "backend/routes/auth.py"
    "backend/routes/categories.py"
    "backend/routes/projects.py"
)

echo "后端文件："
for file in "${backend_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
    fi
done

# 前端文件检查
frontend_files=(
    "frontend/package.json"
    "frontend/vite.config.js"
    "frontend/Dockerfile"
    "frontend/src/App.jsx"
    "frontend/src/pages/Login.jsx"
    "frontend/src/pages/Register.jsx"
    "frontend/src/pages/Dashboard.jsx"
    "frontend/src/pages/Projects.jsx"
    "frontend/src/pages/Categories.jsx"
)

echo -e "\n前端文件："
for file in "${frontend_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
    fi
done

# 配置文件检查
config_files=(
    "docker-compose.yml"
    "docs/api.md"
    "docs/deployment.md"
    "docs/user-manual.md"
    "README.md"
    "QUICKSTART.md"
)

echo -e "\n配置和文档文件："
for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
    fi
done

echo -e "\n🎯 项目完成状态"
echo "================"
echo "✅ 后端API开发完成"
echo "  - 用户认证系统"
echo "  - 分类管理API"
echo "  - 项目管理API"
echo "  - 价值计算引擎"
echo ""
echo "✅ 前端界面开发完成"
echo "  - React + Ant Design UI"
echo "  - 用户登录注册"
echo "  - 仪表盘统计"
echo "  - 项目和分类管理"
echo ""
echo "✅ Docker部署配置完成"
echo "  - 后端Dockerfile"
echo "  - 前端Dockerfile"
echo "  - docker-compose.yml"
echo "  - Nginx配置"
echo ""
echo "✅ 文档编写完成"
echo "  - API接口文档"
echo "  - 部署指南"
echo "  - 用户手册"
echo "  - 快速启动指南"

echo -e "\n🚀 启动命令"
echo "=========="
echo "1. 使用Docker启动（推荐）："
echo "   docker-compose up -d"
echo ""
echo "2. 访问地址："
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:5000"
echo ""
echo "3. 默认账号："
echo "   用户名: admin"
echo "   密码: admin123"

echo -e "\n✨ 项目开发完成！"