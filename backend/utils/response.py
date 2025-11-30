"""
通用响应工具模块
提供统一的API响应格式
"""
from flask import jsonify
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


class APIResponse:
    """API响应封装类"""
    
    @staticmethod
    def success(data=None, message="操作成功", code=200):
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            code: 状态码
            
        Returns:
            JSON响应
        """
        response = {
            'code': code,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), code
    
    @staticmethod
    def error(message="操作失败", code=400, errors=None):
        """
        错误响应
        
        Args:
            message: 错误消息
            code: 错误码
            errors: 详细错误信息
            
        Returns:
            JSON响应
        """
        response = {
            'code': code,
            'message': message
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), code
    
    @staticmethod
    def paginated(items, total, page, per_page, message="查询成功"):
        """
        分页响应
        
        Args:
            items: 数据列表
            total: 总数
            page: 当前页码
            per_page: 每页数量
            message: 响应消息
            
        Returns:
            JSON响应
        """
        return APIResponse.success(
            data={
                'items': items,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
            },
            message=message
        )


def require_jwt(fn):
    """
    JWT认证装饰器
    
    Usage:
        @app.route('/api/protected')
        @require_jwt
        def protected():
            user_id = get_jwt_identity()
            return {'user_id': user_id}
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return APIResponse.error(message="认证失败", code=401)
    return wrapper


def handle_exceptions(fn):
    """
    异常处理装饰器
    
    Usage:
        @app.route('/api/something')
        @handle_exceptions
        def something():
            # Your code here
            pass
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            return APIResponse.error(message=str(e), code=400)
        except PermissionError as e:
            return APIResponse.error(message=str(e), code=403)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return APIResponse.error(message="服务器内部错误", code=500)
    return wrapper


def get_current_user_id():
    """
    获取当前登录用户ID
    
    Returns:
        用户ID（整数）
        
    Raises:
        ValueError: 如果JWT无效
    """
    try:
        return int(get_jwt_identity())
    except (ValueError, TypeError):
        raise ValueError("无效的用户认证信息")
