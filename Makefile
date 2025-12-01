# TimeValue 项目管理Makefile
.PHONY: help build up down restart logs clean prune backup restore

# 默认目标
.DEFAULT_GOAL := help

# 颜色输出
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## help: 显示帮助信息
help:
	@echo "$(BLUE)TimeValue 项目管理命令$(NC)"
	@echo ""
	@echo "$(GREEN)使用方法:$(NC)"
	@echo "  make <command>"
	@echo ""
	@echo "$(GREEN)可用命令:$(NC)"
	@grep -E '^## ' Makefile | sed 's/^## /  /'
	@echo ""

## build: 构建Docker镜像
build:
	@echo "$(YELLOW)🔨 构建Docker镜像...$(NC)"
	docker-compose build --no-cache

## up: 启动所有服务
up:
	@echo "$(GREEN)🚀 启动TimeValue服务...$(NC)"
	docker-compose --env-file .env.docker up -d
	@echo "$(GREEN)✅ 服务已启动$(NC)"
	@echo "$(BLUE)后端API: http://localhost:5000$(NC)"
	@echo "$(BLUE)前端Web: http://localhost:3000$(NC)"

## down: 停止所有服务
down:
	@echo "$(YELLOW)⏹️  停止TimeValue服务...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ 服务已停止$(NC)"

## restart: 重启所有服务
restart: down up

## logs: 查看所有服务日志
logs:
	docker-compose logs -f

## logs-backend: 查看后端日志
logs-backend:
	docker-compose logs -f backend

## logs-mysql: 查看MySQL日志
logs-mysql:
	docker-compose logs -f mysql

## ps: 查看服务状态
ps:
	docker-compose ps

## exec-backend: 进入后端容器
exec-backend:
	docker-compose exec backend bash

## exec-mysql: 进入MySQL容器
exec-mysql:
	docker-compose exec mysql mysql -u timevalue -p

## clean: 停止服务并删除容器（保留数据）
clean:
	@echo "$(YELLOW)🧹 清理容器...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ 容器已删除（数据保留）$(NC)"

## prune: 完全清理（删除容器和数据卷）
prune:
	@echo "$(RED)⚠️  警告: 这将删除所有数据！$(NC)"
	@read -p "确认删除? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	@echo "$(GREEN)✅ 所有数据已删除$(NC)"

## backup: 备份MySQL数据库
backup:
	@echo "$(YELLOW)💾 备份数据库...$(NC)"
	@mkdir -p backups
	@docker-compose exec -T mysql mysqldump -u root -p$$(grep DB_ROOT_PASSWORD .env.docker | cut -d '=' -f2) timevalue > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ 备份完成: backups/backup_$$(date +%Y%m%d_%H%M%S).sql$(NC)"

## restore: 从备份恢复数据库
restore:
	@echo "$(YELLOW)📥 恢复数据库...$(NC)"
	@echo "可用备份:"
	@ls -lh backups/*.sql 2>/dev/null || echo "  无可用备份"
	@read -p "请输入备份文件名: " backup_file && \
	docker-compose exec -T mysql mysql -u root -p$$(grep DB_ROOT_PASSWORD .env.docker | cut -d '=' -f2) timevalue < backups/$$backup_file
	@echo "$(GREEN)✅ 数据库恢复完成$(NC)"

## init: 初始化项目（首次部署）
init:
	@echo "$(BLUE)🎉 初始化TimeValue项目$(NC)"
	@if [ ! -f .env.docker ]; then \
		echo "$(YELLOW)📝 创建环境配置文件...$(NC)"; \
		cp .env.docker .env.docker; \
		echo "$(RED)⚠️  请编辑 .env.docker 修改默认密码！$(NC)"; \
	else \
		echo "$(GREEN)✅ 环境配置文件已存在$(NC)"; \
	fi
	@echo "$(YELLOW)🔨 构建镜像...$(NC)"
	@make build
	@echo "$(GREEN)✅ 初始化完成，运行 'make up' 启动服务$(NC)"

## dev: 开发模式启动
dev:
	@echo "$(BLUE)🔧 开发模式启动...$(NC)"
	docker-compose --env-file .env.docker up

## prod: 生产模式启动
prod:
	@echo "$(GREEN)🚀 生产模式启动...$(NC)"
	@if grep -q "FLASK_ENV=development" .env.docker; then \
		echo "$(RED)⚠️  警告: 环境配置为开发模式！$(NC)"; \
		exit 1; \
	fi
	docker-compose --env-file .env.docker up -d
	@echo "$(GREEN)✅ 生产服务已启动$(NC)"

## health: 检查服务健康状态
health:
	@echo "$(BLUE)🏥 检查服务健康状态...$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)后端健康检查:$(NC)"
	@curl -f http://localhost:5000/api/health 2>/dev/null && echo "$(GREEN)✅ 后端正常$(NC)" || echo "$(RED)❌ 后端异常$(NC)"

## update: 更新并重启服务
update:
	@echo "$(YELLOW)🔄 更新服务...$(NC)"
	git pull
	make build
	make restart
	@echo "$(GREEN)✅ 服务已更新$(NC)"
