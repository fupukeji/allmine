#!/bin/bash

################################################################################
# TimeValue Git 推送脚本
# 将项目推送到阿里云Codeup仓库
# Powered by 孚普科技(北京)有限公司
################################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Git仓库地址
REMOTE_URL="https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue.git"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🚀 TimeValue Git 推送脚本${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""

# 检查是否已初始化Git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 初始化Git仓库...${NC}"
    git init
    echo -e "${GREEN}✓ Git仓库初始化完成${NC}"
else
    echo -e "${GREEN}✓ Git仓库已存在${NC}"
fi

# 检查远程仓库配置
CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null)
if [ -z "$CURRENT_REMOTE" ]; then
    echo -e "${YELLOW}🔗 添加远程仓库...${NC}"
    git remote add origin "$REMOTE_URL"
    echo -e "${GREEN}✓ 远程仓库添加成功${NC}"
elif [ "$CURRENT_REMOTE" != "$REMOTE_URL" ]; then
    echo -e "${YELLOW}🔗 更新远程仓库地址...${NC}"
    git remote set-url origin "$REMOTE_URL"
    echo -e "${GREEN}✓ 远程仓库地址更新成功${NC}"
else
    echo -e "${GREEN}✓ 远程仓库已配置: ${REMOTE_URL}${NC}"
fi

echo ""
echo -e "${YELLOW}📝 查看待提交的文件...${NC}"
git status --short

echo ""
read -p "$(echo -e ${YELLOW}是否要添加所有文件到暂存区？ [Y/n]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo -e "${YELLOW}📦 添加文件到暂存区...${NC}"
    git add .
    echo -e "${GREEN}✓ 文件已添加到暂存区${NC}"
else
    echo -e "${YELLOW}跳过添加文件${NC}"
fi

echo ""
echo -e "${YELLOW}📋 当前暂存区状态:${NC}"
git status --short

echo ""
read -p "$(echo -e ${YELLOW}请输入提交信息 [默认: Update code]: ${NC})" COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Update code"}

echo -e "${YELLOW}💾 提交代码...${NC}"
if git commit -m "$COMMIT_MSG"; then
    echo -e "${GREEN}✓ 代码提交成功${NC}"
else
    echo -e "${YELLOW}⚠️  没有需要提交的更改或提交失败${NC}"
fi

echo ""
echo -e "${YELLOW}🌐 推送到远程仓库...${NC}"
echo -e "${BLUE}远程地址: ${REMOTE_URL}${NC}"

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
    git branch -M main
fi

echo -e "${BLUE}当前分支: ${CURRENT_BRANCH}${NC}"

# 推送代码
echo ""
echo -e "${YELLOW}开始推送...${NC}"
if git push -u origin "$CURRENT_BRANCH"; then
    echo ""
    echo -e "${GREEN}✅ 代码推送成功！${NC}"
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${GREEN}📊 推送信息汇总${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "  仓库地址: ${BLUE}${REMOTE_URL}${NC}"
    echo -e "  分支名称: ${GREEN}${CURRENT_BRANCH}${NC}"
    echo -e "  提交信息: ${YELLOW}${COMMIT_MSG}${NC}"
    echo ""
    echo -e "${YELLOW}🌐 访问仓库:${NC}"
    echo -e "  ${BLUE}https://codeup.aliyun.com/670f88349d3c82efe37b1105/timevalue${NC}"
    echo ""
    echo -e "${BLUE}================================================================================================${NC}"
else
    echo ""
    echo -e "${RED}✗ 推送失败！${NC}"
    echo ""
    echo -e "${YELLOW}可能的原因:${NC}"
    echo -e "  1. 需要配置Git凭据"
    echo -e "  2. 网络连接问题"
    echo -e "  3. 分支冲突"
    echo ""
    echo -e "${YELLOW}解决方案:${NC}"
    echo -e "  1. 配置Git用户信息:"
    echo -e "     ${BLUE}git config --global user.name \"Your Name\"${NC}"
    echo -e "     ${BLUE}git config --global user.email \"your.email@example.com\"${NC}"
    echo ""
    echo -e "  2. 如果需要拉取远程更改:"
    echo -e "     ${BLUE}git pull origin ${CURRENT_BRANCH} --rebase${NC}"
    echo ""
    echo -e "  3. 配置阿里云Codeup凭据:"
    echo -e "     访问: ${BLUE}https://codeup.aliyun.com/settings/personal_access_tokens${NC}"
    echo ""
    exit 1
fi
