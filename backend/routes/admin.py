from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from database import db
from datetime import datetime
import re

admin_bp = Blueprint('admin', __name__)

def get_current_user():
    """获取当前用户"""
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)

def require_admin():
    """检查管理员权限装饰器"""
    user = get_current_user()
    if not user or not user.is_admin():
        return jsonify({'code': 403, 'message': '权限不足，需要管理员权限'}), 403
    return None

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    return True, ""

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表（仅管理员）"""
    try:
        # 检查权限
        auth_result = require_admin()
        if auth_result:
            return auth_result
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status')  # active, inactive
        role = request.args.get('role')  # admin, user
        
        # 构建查询
        query = User.query
        
        if search:
            query = query.filter(
                (User.username.contains(search)) | 
                (User.email.contains(search))
            )
        
        if status == 'active':
            query = query.filter(User.is_active == True)
        elif status == 'inactive':
            query = query.filter(User.is_active == False)
            
        if role:
            query = query.filter(User.role == role)
        
        # 排序和分页
        query = query.order_by(User.created_at.desc())
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            user_dict = user.to_dict()
            # 添加统计信息
            user_dict['project_count'] = len(user.projects)
            user_dict['category_count'] = len(user.categories)
            users_data.append(user_dict)
        
        return jsonify({
            'code': 200,
            'data': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取用户列表失败：{str(e)}'}), 500

@admin_bp.route('/admin/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户（仅管理员）"""
    try:
        # 检查权限
        auth_result = require_admin()
        if auth_result:
            return auth_result
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段：{field}'
                }), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data.get('role', 'user')
        
        # 验证数据格式
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'code': 400,
                'message': '用户名长度应在3-20个字符之间'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'code': 400,
                'message': '邮箱格式不正确'
            }), 400
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'code': 400,
                'message': error_msg
            }), 400
        
        if role not in ['admin', 'user']:
            return jsonify({
                'code': 400,
                'message': '角色必须是admin或user'
            }), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({
                'code': 400,
                'message': '用户名已存在'
            }), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({
                'code': 400,
                'message': '邮箱已被注册'
            }), 400
        
        # 创建新用户
        user = User(username=username, email=email, password=password)
        user.role = role
        user.is_active = data.get('is_active', True)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '用户创建成功',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建用户失败：{str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息（仅管理员）"""
    try:
        # 检查权限
        auth_result = require_admin()
        if auth_result:
            return auth_result
        
        current_user = get_current_user()
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 防止管理员禁用自己
        if target_user.id == current_user.id:
            data = request.get_json()
            if 'is_active' in data and not data['is_active']:
                return jsonify({
                    'code': 400,
                    'message': '不能禁用自己的账户'
                }), 400
        
        data = request.get_json()
        
        # 更新邮箱
        if 'email' in data:
            email = data['email'].strip().lower()
            if not validate_email(email):
                return jsonify({
                    'code': 400,
                    'message': '邮箱格式不正确'
                }), 400
            
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == email,
                User.id != user_id
            ).first()
            
            if existing_user:
                return jsonify({
                    'code': 400,
                    'message': '该邮箱已被其他用户使用'
                }), 400
            
            target_user.email = email
        
        # 更新密码
        if 'password' in data:
            password = data['password']
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                return jsonify({
                    'code': 400,
                    'message': error_msg
                }), 400
            
            target_user.set_password(password)
        
        # 更新角色
        if 'role' in data:
            role = data['role']
            if role not in ['admin', 'user']:
                return jsonify({
                    'code': 400,
                    'message': '角色必须是admin或user'
                }), 400
            target_user.role = role
        
        # 更新状态
        if 'is_active' in data:
            target_user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '用户更新成功',
            'data': target_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新用户失败：{str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_user_status(user_id):
    """切换用户状态（启用/禁用）"""
    try:
        # 检查权限
        auth_result = require_admin()
        if auth_result:
            return auth_result
        
        current_user = get_current_user()
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 防止管理员禁用自己
        if target_user.id == current_user.id:
            return jsonify({
                'code': 400,
                'message': '不能操作自己的账户状态'
            }), 400
        
        # 切换状态
        target_user.is_active = not target_user.is_active
        db.session.commit()
        
        action = '启用' if target_user.is_active else '禁用'
        
        return jsonify({
            'code': 200,
            'message': f'用户{action}成功',
            'data': target_user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'切换用户状态失败：{str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户（仅管理员）"""
    try:
        # 检查权限
        auth_result = require_admin()
        if auth_result:
            return auth_result
        
        current_user = get_current_user()
        target_user = User.query.get(user_id)
        
        if not target_user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 防止管理员删除自己
        if target_user.id == current_user.id:
            return jsonify({
                'code': 400,
                'message': '不能删除自己的账户'
            }), 400
        
        # 检查是否有关联数据
        if target_user.projects or target_user.categories:
            return jsonify({
                'code': 400,
                'message': '该用户还有关联的项目或分类，请先处理这些数据'
            }), 400
        
        username = target_user.username
        db.session.delete(target_user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'用户 {username} 删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除用户失败：{str(e)}'}), 500

@admin_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    """获取管理员统计数据"""
    try:
        # 检查权限
        auth_result = require_admin()
        if auth_result:
            return auth_result
        
        # 用户统计
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        # 项目和分类统计
        from models.project import Project
        from models.category import Category
        
        total_projects = Project.query.count()
        total_categories = Category.query.count()
        
        # 按月统计新用户
        from sqlalchemy import extract
        current_year = datetime.now().year
        monthly_users = []
        
        for month in range(1, 13):
            count = User.query.filter(
                extract('year', User.created_at) == current_year,
                extract('month', User.created_at) == month
            ).count()
            monthly_users.append({
                'month': f'{current_year}-{month:02d}',
                'count': count
            })
        
        return jsonify({
            'code': 200,
            'data': {
                'user_stats': {
                    'total': total_users,
                    'active': active_users,
                    'inactive': total_users - active_users,
                    'admins': admin_users
                },
                'content_stats': {
                    'total_projects': total_projects,
                    'total_categories': total_categories
                },
                'monthly_users': monthly_users
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取统计数据失败：{str(e)}'}), 500