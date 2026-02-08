# Gunicorn配置文件
import multiprocessing
import os

# 服务器绑定
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:80")

# Worker进程数
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# 每个worker的线程数
threads = int(os.getenv("GUNICORN_THREADS", 2))

# Worker类型
worker_class = "sync"

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 超时时间
timeout = 120
graceful_timeout = 30
keepalive = 5

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# 进程命名
proc_name = "timevalue-backend"

# 预加载应用
preload_app = True

# 工作目录
chdir = "/app"

# Daemon模式
daemon = False

# PID文件
pidfile = "/tmp/gunicorn.pid"

# 用户和组
user = "timevalue"
group = "timevalue"

# 临时文件目录
tmp_upload_dir = "/tmp"

# 启动/关闭钩子
def on_starting(server):
    """服务器启动时调用"""
    print("=" * 60)
    print("🚀 TimeValue Backend Server Starting")
    print(f"   Workers: {workers}")
    print(f"   Threads per worker: {threads}")
    print(f"   Bind: {bind}")
    print("=" * 60)

def on_reload(server):
    """服务器重载时调用"""
    print("🔄 Server reloading...")

def when_ready(server):
    """服务器就绪时调用"""
    print("✅ TimeValue Backend is ready to serve requests")

def on_exit(server):
    """服务器退出时调用"""
    print("👋 TimeValue Backend shutting down...")

# 错误处理
def worker_abort(worker):
    """Worker异常终止时调用"""
    print(f"⚠️  Worker {worker.pid} aborted")
