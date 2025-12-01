# TimeValue 后端服务 Dockerfile
# 多阶段构建，优化镜像大小

# ================================
# 阶段1: 基础镜像
# ================================
FROM python:3.11-slim as base

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# ================================
# 阶段2: 依赖安装
# ================================
FROM base as dependencies

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install gunicorn==21.2.0 python-json-logger==2.0.7 -i https://pypi.tuna.tsinghua.edu.cn/simple

# ================================
# 阶段3: 生产镜像
# ================================
FROM base as production

# 创建非root用户
RUN useradd -m -u 1000 timevalue && \
    mkdir -p /app/logs && \
    chown -R timevalue:timevalue /app

# 从依赖阶段复制已安装的包
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# 复制应用代码
COPY --chown=timevalue:timevalue . .

# 复制并设置启动脚本权限
COPY --chown=timevalue:timevalue docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 切换到非root用户
USER timevalue

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health', timeout=5)"

# 暴露端口
EXPOSE 5000

# 使用entrypoint脚本
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# 启动命令（生产环境使用gunicorn）
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:create_app()"]
