#!/bin/bash

################################################################################
# TimeValue Node.js 部署验证脚本
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🔍 TimeValue Node.js 部署验证${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 检查Node.js
echo -e "${YELLOW}检查Node.js...${NC}"
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js: $(node --version)${NC}"
else
    echo -e "${RED}✗ Node.js未安装${NC}"
    exit 1
fi

# 检查npm
echo -e "${YELLOW}检查npm...${NC}"
if command -v npm &> /dev/null; then
    echo -e "${GREEN}✓ npm: $(npm --version)${NC}"
else
    echo -e "${RED}✗ npm未安装${NC}"
    exit 1
fi

# 检查目录结构
echo ""
echo -e "${YELLOW}检查目录结构...${NC}"
if [ -d "backend-node" ]; then
    echo -e "${GREEN}✓ backend-node目录存在${NC}"
else
    echo -e "${RED}✗ backend-node目录不存在${NC}"
    exit 1
fi

# 检查关键文件
echo -e "${YELLOW}检查关键文件...${NC}"
FILES=(
    "backend-node/server.js"
    "backend-node/package.json"
    "backend-node/.env"
    "backend-node/config/database.js"
    "backend-node/migrations/init.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file 缺失${NC}"
        if [ "$file" == "backend-node/.env" ]; then
            echo -e "${YELLOW}  提示: 请复制 .env.example 为 .env 并配置数据库连接${NC}"
        fi
        exit 1
    fi
done

# 检查依赖
echo ""
echo -e "${YELLOW}检查依赖安装...${NC}"
cd backend-node
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓ 依赖已安装${NC}"
else
    echo -e "${YELLOW}⚠ 依赖未安装，正在安装...${NC}"
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 依赖安装成功${NC}"
    else
        echo -e "${RED}✗ 依赖安装失败${NC}"
        exit 1
    fi
fi
cd ..

# 测试数据库连接
echo ""
echo -e "${YELLOW}测试数据库连接...${NC}"
cd backend-node
node -e "
const pool = require('./config/database.js').default;
pool.query('SELECT 1')
  .then(() => {
    console.log('✓ 数据库连接成功');
    process.exit(0);
  })
  .catch(err => {
    console.error('✗ 数据库连接失败:', err.message);
    process.exit(1);
  });
" 2>&1 | while IFS= read -r line; do
    if [[ $line == *"✓"* ]]; then
        echo -e "${GREEN}$line${NC}"
    else
        echo -e "${RED}$line${NC}"
    fi
done

DB_STATUS=${PIPESTATUS[0]}
cd ..

# 检查端口占用
echo ""
echo -e "${YELLOW}检查端口占用...${NC}"
if command -v netstat &> /dev/null; then
    if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
        echo -e "${YELLOW}⚠ 端口5000已被占用${NC}"
    else
        echo -e "${GREEN}✓ 端口5000可用${NC}"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
        echo -e "${YELLOW}⚠ 端口3000已被占用${NC}"
    else
        echo -e "${GREEN}✓ 端口3000可用${NC}"
    fi
fi

# 总结
echo ""
echo -e "${BLUE}================================================================================================${NC}"
if [ $DB_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ 部署环境检查通过！${NC}"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo -e "  1. 初始化数据库: ${BLUE}cd backend-node && npm run migrate${NC}"
    echo -e "  2. 启动服务: ${BLUE}./start_production_node.sh${NC}"
else
    echo -e "${RED}❌ 部署环境检查失败${NC}"
    echo ""
    echo -e "${YELLOW}请检查:${NC}"
    echo -e "  1. 数据库连接配置 (backend-node/.env)"
    echo -e "  2. 网络连接是否正常"
    echo -e "  3. PostgreSQL服务是否运行"
fi
echo -e "${BLUE}================================================================================================${NC}"
