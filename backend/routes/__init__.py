# 路由包初始化
from .auth import auth_bp
from .categories import categories_bp
from .projects import projects_bp

__all__ = ['auth_bp', 'categories_bp', 'projects_bp']