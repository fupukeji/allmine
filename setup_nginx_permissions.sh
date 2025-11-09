#!/bin/bash

# =================================================================
# TimeValue Nginx权限设置脚本
# 用于配置必要的权限，使应用能够动态管理Nginx配置
# =================================================================

set -e

echo "================================================================"
echo "🔧 TimeValue Nginx权限设置"
echo "================================================================"
echo ""

# 检测当前用户
CURRENT_USER=$(whoami)
echo "📌 当前用户: $CURRENT_USER"

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 此脚本需要root权限运行"
    echo "💡 请使用: sudo bash setup_nginx_permissions.sh"
    exit 1
fi

echo ""
echo "1️⃣ 创建TimeValue配置目录..."

# 创建Nginx配置目录
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

echo "✅ 配置目录创建完成"

echo ""
echo "2️⃣ 配置应用用户权限..."

# 获取实际运行应用的用户（非root）
if [ -n "$SUDO_USER" ]; then
    APP_USER=$SUDO_USER
else
    read -p "请输入运行应用的用户名: " APP_USER
fi

echo "📌 应用用户: $APP_USER"

# 创建应用用户组（如果不存在）
if ! getent group timevalue > /dev/null 2>&1; then
    groupadd timevalue
    echo "✅ 创建用户组: timevalue"
fi

# 将应用用户添加到timevalue组
usermod -a -G timevalue $APP_USER
echo "✅ 用户 $APP_USER 已添加到 timevalue 组"

echo ""
echo "3️⃣ 设置Nginx配置目录权限..."

# 设置目录所有权
chown -R root:timevalue /etc/nginx/sites-available
chown -R root:timevalue /etc/nginx/sites-enabled

# 设置目录权限（允许组写入）
chmod 775 /etc/nginx/sites-available
chmod 775 /etc/nginx/sites-enabled

echo "✅ 目录权限设置完成"

echo ""
echo "4️⃣ 配置sudo权限..."

# 创建sudoers配置文件
SUDOERS_FILE="/etc/sudoers.d/timevalue-nginx"

cat > $SUDOERS_FILE << EOF
# TimeValue Nginx管理权限
# 允许timevalue组用户执行nginx相关命令

%timevalue ALL=(ALL) NOPASSWD: /usr/sbin/nginx -t
%timevalue ALL=(ALL) NOPASSWD: /usr/sbin/nginx -s reload
%timevalue ALL=(ALL) NOPASSWD: /bin/systemctl is-active nginx
%timevalue ALL=(ALL) NOPASSWD: /bin/systemctl status nginx
%timevalue ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx
EOF

# 设置正确的权限
chmod 440 $SUDOERS_FILE

echo "✅ sudo权限配置完成"

echo ""
echo "5️⃣ 验证Nginx安装..."

if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | cut -d'/' -f2)
    echo "✅ Nginx已安装: $NGINX_VERSION"
    
    # 测试Nginx配置
    nginx -t && echo "✅ Nginx配置有效"
else
    echo "⚠️  Nginx未安装，正在安装..."
    
    # 检测操作系统并安装Nginx
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                apt-get update
                apt-get install -y nginx
                ;;
            centos|rhel|alinux)
                yum install -y nginx
                ;;
            *)
                echo "❌ 不支持的操作系统，请手动安装Nginx"
                exit 1
                ;;
        esac
    fi
    
    echo "✅ Nginx安装完成"
fi

echo ""
echo "6️⃣ 启动Nginx服务..."

# 启动并启用Nginx
systemctl enable nginx
systemctl start nginx

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx服务运行中"
else
    echo "⚠️  Nginx启动失败，请检查配置"
fi

echo ""
echo "================================================================"
echo "✅ Nginx权限设置完成！"
echo "================================================================"
echo ""
echo "📝 配置摘要:"
echo "   • 应用用户: $APP_USER"
echo "   • 用户组: timevalue"
echo "   • 配置目录: /etc/nginx/sites-available"
echo "   • 启用目录: /etc/nginx/sites-enabled"
echo ""
echo "💡 重要提示:"
echo "   1. 用户 $APP_USER 现在可以通过Web界面管理Nginx配置"
echo "   2. 请使用此用户启动TimeValue应用"
echo "   3. 用户需要重新登录才能使组权限生效"
echo ""
echo "🔄 下一步:"
echo "   1. 退出当前会话: exit"
echo "   2. 重新登录: su - $APP_USER"
echo "   3. 启动应用: cd $(pwd) && bash start_production.sh"
echo ""
