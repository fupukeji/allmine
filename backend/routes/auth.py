from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from database import db
from services.category_service import initialize_user_categories
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
        data = request.get_json(force=True)
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password']
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
            
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
        
        # 初始化默认分类
        initialize_user_categories(user.id)
        
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
    import traceback
    try:
        data = request.get_json(force=True)
        
        # 验证必填字段
        if not data or not data.get('username') or not data.get('password'):
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
                'token': access_token,
                'access_token': access_token  # 兼容字段
            }
        })
        
    except Exception as e:
        print(f"[登录错误] {str(e)}")
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f'登录失败：{str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@auth_bp.route('/user', methods=['GET'])  # 别名，兼容H5
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

@auth_bp.route('/reset-database', methods=['POST'])
@jwt_required()
def reset_database():
    """清空数据库（需要密码验证）"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'code': 400,
                'message': '请输入登录密码'
            }), 400
        
        # 验证密码
        if not user.check_password(password):
            return jsonify({
                'code': 401,
                'message': '密码错误'
            }), 401
        
        # 清空数据库
        from models.category import Category
        from models.project import Project
        from models.fixed_asset import FixedAsset
        from models.asset_income import AssetIncome
        from models.asset_maintenance import AssetMaintenance, MaintenanceReminder
        from models.ai_report import AIReport
        
        # 删除所有数据（保留用户表）
        db.session.query(MaintenanceReminder).delete()
        db.session.query(AssetMaintenance).delete()
        db.session.query(AssetIncome).delete()
        db.session.query(FixedAsset).delete()
        db.session.query(Project).delete()
        db.session.query(AIReport).delete()
        
        # 先删除所有子分类，再删除父分类
        # 获取所有分类并按层级倒序删除
        all_categories = db.session.query(Category).all()
        # 按层级深度排序（深度大的先删除）
        categories_by_level = {}
        for cat in all_categories:
            level = cat.get_level()
            if level not in categories_by_level:
                categories_by_level[level] = []
            categories_by_level[level].append(cat)
        
        # 从最深层级开始删除
        for level in sorted(categories_by_level.keys(), reverse=True):
            for cat in categories_by_level[level]:
                db.session.delete(cat)
        
        # 删除所有非管理员用户
        db.session.query(User).filter(User.role != 'admin').delete()
        
        # 重置当前用户的API Token
        user.aliyun_api_token_encrypted = None
        
        db.session.commit()
        
        # 重新创建默认分类
        initialize_user_categories(user.id)
        
        return jsonify({
            'code': 200,
            'message': '数据库已清空，默认分类已重建'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'清空数据库失败：{str(e)}'
        }), 500

@auth_bp.route('/deactivate-account', methods=['POST'])
@jwt_required()
def deactivate_account():
    """用户注销自己的账户 - 需要输入用户名和密码确认"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        confirm_username = data.get('username', '').strip()
        confirm_password = data.get('password', '')
        
        # 验证必填字段
        if not confirm_username or not confirm_password:
            return jsonify({
                'code': 400,
                'message': '请输入用户名和密码进行确认'
            }), 400
        
        # 验证用户名是否匹配
        if confirm_username != user.username:
            return jsonify({
                'code': 400,
                'message': '输入的用户名与当前用户不匹配'
            }), 400
        
        # 验证密码
        if not user.check_password(confirm_password):
            return jsonify({
                'code': 401,
                'message': '密码错误'
            }), 401
        
        # 删除用户的所有关联数据
        from models.project import Project
        from models.category import Category
        from models.fixed_asset import FixedAsset
        from models.asset_income import AssetIncome
        from models.asset_maintenance import AssetMaintenance, MaintenanceReminder
        from models.ai_report import AIReport
        
        # 删除该用户的所有固定资产相关数据
        assets = FixedAsset.query.filter_by(user_id=user.id).all()
        for asset in assets:
            # 删除资产的收入记录
            AssetIncome.query.filter_by(asset_id=asset.id).delete()
            # 删除资产的维护记录
            AssetMaintenance.query.filter_by(asset_id=asset.id).delete()
            # 删除资产的维护提醒
            MaintenanceReminder.query.filter_by(asset_id=asset.id).delete()
        
        # 删除该用户的所有固定资产
        FixedAsset.query.filter_by(user_id=user.id).delete()
        
        # 删除该用户的所有虚拟资产（项目）
        Project.query.filter_by(user_id=user.id).delete()
        
        # 删除该用户的所有分类（按层级倒序删除）
        user_categories = Category.query.filter_by(user_id=user.id).all()
        categories_by_level = {}
        for cat in user_categories:
            level = cat.get_level()
            if level not in categories_by_level:
                categories_by_level[level] = []
            categories_by_level[level].append(cat)
        
        for level in sorted(categories_by_level.keys(), reverse=True):
            for cat in categories_by_level[level]:
                db.session.delete(cat)
        
        # 删除该用户的AI报告
        AIReport.query.filter_by(user_id=user.id).delete()
        
        username = user.username
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'账户 {username} 及其所有数据已注销'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'注销账户失败：{str(e)}'
        }), 500