from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from database import db
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'timevalue-backend'
    }), 200

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
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
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'code': 400,
                'message': '用户名长度应在3-20个字符之间'
            }), 400
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({
                'code': 400,
                'message': '邮箱格式不正确'
            }), 400
        
        # 验证密码强度
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'code': 400,
                'message': error_msg
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
        db.session.add(user)
        db.session.commit()
        
        # 创建默认分类
        from models.category import Category
        default_categories = [
            {'name': '运动健身', 'color': '#52c41a', 'icon': 'trophy'},
            {'name': '技术工具', 'color': '#1890ff', 'icon': 'code'},
            {'name': '生活服务', 'color': '#faad14', 'icon': 'home'},
            {'name': '娱乐休闲', 'color': '#eb2f96', 'icon': 'smile'}
        ]
        
        for cat_data in default_categories:
            category = Category(
                name=cat_data['name'],
                color=cat_data['color'],
                icon=cat_data['icon'],
                user_id=user.id
            )
            db.session.add(category)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'注册失败：{str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'code': 403,
                'message': '账户已被禁用'
            }), 403
        
        # 创建访问令牌
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'user': user.to_dict(),
                'access_token': access_token
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'登录失败：{str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'data': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取用户信息失败：{str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新用户名
        if 'username' in data:
            username = data['username'].strip()
            if len(username) < 3 or len(username) > 20:
                return jsonify({
                    'code': 400,
                    'message': '用户名长度应在3-20个字符之间'
                }), 400
            
            # 检查用户名是否已被其他用户使用
            existing_user = User.query.filter(
                User.username == username,
                User.id != user_id
            ).first()
            
            if existing_user:
                return jsonify({
                    'code': 400,
                    'message': '该用户名已被其他用户使用'
                }), 400
            
            user.username = username
        
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
            
            user.email = email
        
        # 更新其他个人信息字段
        updatable_fields = ['phone', 'location', 'bio', 'website', 'company', 
                          'language', 'timezone', 'theme', 'email_notifications', 
                          'sms_notifications', 'avatar']
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 更新密码
        if 'password' in data:
            password = data['password']
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                return jsonify({
                    'code': 400,
                    'message': error_msg
                }), 400
            
            user.set_password(password)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新失败：{str(e)}'
        }), 500

@auth_bp.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    """验证token有效性"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'code': 401,
                'message': 'Token无效'
            }), 401
        
        return jsonify({
            'code': 200,
            'message': 'Token有效',
            'data': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'code': 401,
            'message': 'Token无效'
        }), 401