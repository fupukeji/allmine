#!/bin/bash

# TimeValue 快速部署脚本
# Powered by 孚普科技（北京）有限公司

echo "================================================================"
echo "🚀 TimeValue 个人资产管理系统部署脚本"
echo "💰 恒产生金 - 让每一份资产都创造价值"
echo ""
echo "🏢 Powered by 孚普科技（北京）有限公司"
echo "🤖 AI驱动的MVP快速迭代解决方案"
echo "🌐 https://fupukeji.com"
echo "================================================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装Node.js"
    exit 1
fi

echo "✅ 环境检查通过"

# 生成安全密钥
echo "🔐 正在生成安全密钥..."
cd backend
python3 generate_keys.py << EOF
2
EOF
cd ..

# 安装后端依赖
echo "📦 正在安装后端依赖..."
cd backend
pip3 install -r requirements.txt
cd ..

# 安装前端依赖
echo "📦 正在安装前端依赖..."
cd frontend
npm install
cd ..

echo ""
echo "🎉 部署完成！"
echo ""
echo "🚀 启动方法："
echo "  方式1: python start_timevalue.py  (推荐，一键启动)"
echo "  方式2: 手动分别启动前后端服务"
echo ""
echo "📱 访问地址: http://localhost:3000"
echo ""
echo "================================================================"
echo "🙏 感谢使用孚普科技的AI代码生成系统"
echo "💡 了解更多AI产品和服务: https://fupukeji.com"
echo "📧 商务合作: contact@fupukeji.com"
echo "================================================================"
