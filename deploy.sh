#!/bin/bash

# TimeValue 快速部署脚本 - 阿里云ECS版本
# Powered by 孚普科技（北京）有限公司

set -e  # 遇到错误立即退出

echo "================================================================"
echo "🚀 TimeValue 个人资产管理系统部署脚本"
echo "💰 恒产生金 - 让每一份资产都创造价值"
echo ""
echo "🏢 Powered by 孚普科技（北京）有限公司"
echo "🤖 AI驱动的MVP快速迭代解决方案"
echo "🌐 https://fupukeji.com"
echo "📦 适配阿里云ECS环境自动部署"
echo "================================================================"
echo ""

# 检测操作系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
        echo "📌 检测到操作系统: $PRETTY_NAME"
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
        echo "📌 检测到操作系统: Red Hat Enterprise Linux"
    else
        OS="unknown"
        echo "⚠️  无法识别操作系统类型"
    fi
}

# 安装Python3
install_python3() {
    echo "📦 正在安装Python3..."
    case "$OS" in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        centos|rhel|alinux)
            sudo yum install -y python3 python3-pip
            ;;
        *)
            echo "❌ 不支持的操作系统类型，请手动安装Python3"
            exit 1
            ;;
    esac
    echo "✅ Python3 安装完成"
}

# 安装Node.js
install_nodejs() {
    echo "📦 正在安装Node.js..."
    case "$OS" in
        ubuntu|debian)
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        centos|rhel|alinux)
            curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
            sudo yum install -y nodejs
            ;;
        *)
            echo "❌ 不支持的操作系统类型，请手动安装Node.js"
            exit 1
            ;;
    esac
    echo "✅ Node.js 安装完成"
}

# 检测操作系统
detect_os

# 检查并安装Python3
if ! command -v python3 &> /dev/null; then
    echo "⚠️  未检测到Python3，准备自动安装..."
    install_python3
else
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python3 已安装: $PYTHON_VERSION"
fi

# 检查并安装Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️  未检测到Node.js，准备自动安装..."
    install_nodejs
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js 已安装: $NODE_VERSION"
fi

echo "✅ 环境检查通过"

# 创建数据持久化目录
echo "📁 正在创建数据持久化目录..."
mkdir -p data/backups
echo "✅ 数据目录创建完成"

# 生成安全密钥
echo "🔐 正在生成安全密钥..."
cd backend
python3 generate_keys.py << EOF
2
EOF
cd ..

# 升级pip
echo "📦 正在升级pip..."
python3 -m pip install --upgrade pip

# 安装后端依赖
echo "📦 正在安装后端依赖..."
cd backend
pip3 install -r requirements.txt
cd ..

# 安装前端依赖
echo "📦 正在安装前端依赖..."
cd frontend
npm install --legacy-peer-deps
cd ..

echo ""
echo "🎉 部署完成！"
echo ""
echo "🚀 启动方法："
echo "  生产环境: ./start_production.sh"
echo "  开发环境: python3 start_timevalue.py"
echo ""
echo "📱 默认访问地址: http://localhost:3000"
echo "📱 生产环境地址: http://<您的ECS公网IP>"
echo ""
echo "📋 下一步操作："
echo "  1. 配置防火墙开放3000和5000端口"
echo "  2. （可选）配置域名和SSL证书"
echo "  3. （可选）使用nginx进行反向代理"
echo ""
echo "================================================================"
echo "🙏 感谢使用孚普科技的AI代码生成系统"
echo "💡 了解更多AI产品和服务: https://fupukeji.com"
echo "📧 商务合作: contact@fupukeji.com"
echo "================================================================"
