from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from database import db
import re

auth_bp = Blueprint('auth', __name__)

def get_default_categories():
    """获取默认资产分类配置"""
    return [
        # ========== 一、随风而逝（虚拟消耗型资产）==========
        # 1.1 视频会员类
        {'name': '视频会员', 'color': '#ff6b6b', 'icon': 'play-circle'},
        {'name': '音乐会员', 'color': '#ff8787', 'icon': 'customer-service'},
        {'name': '知识付费', 'color': '#ffa94d', 'icon': 'read'},
        
        # 1.2 生活服务类
        {'name': '外卖会员', 'color': '#fab005', 'icon': 'coffee'},
        {'name': '电商会员', 'color': '#fd7e14', 'icon': 'shopping'},
        {'name': '出行服务', 'color': '#20c997', 'icon': 'car'},
        {'name': '云存储', 'color': '#1c7ed6', 'icon': 'cloud'},
        
        # 1.3 娱乐游戏类
        {'name': '游戏充值', 'color': '#74c0fc', 'icon': 'trophy'},
        {'name': '游戏道具', 'color': '#a78bfa', 'icon': 'gift'},
        {'name': '直播礼物', 'color': '#f06595', 'icon': 'heart'},
        
        # 1.4 数字内容类
        {'name': '电子书', 'color': '#fd7e14', 'icon': 'book'},
        {'name': '在线课程', 'color': '#4c6ef5', 'icon': 'experiment'},
        {'name': '软件订阅', 'color': '#868e96', 'icon': 'appstore'},
        
        # ========== 二、恒产生金（固定资产）==========
        # 2.1 不动产类
        {'name': '房产', 'color': '#5c7cfa', 'icon': 'home'},
        {'name': '车辆', 'color': '#4c6ef5', 'icon': 'car'},
        {'name': '车位车库', 'color': '#364fc7', 'icon': 'inbox'},
        
        # 2.2 珍贵物品类
        {'name': '珠宝首饰', 'color': '#7950f2', 'icon': 'gem'},
        {'name': '艺术收藏', 'color': '#9775fa', 'icon': 'picture'},
        {'name': '名包名表', 'color': '#be4bdb', 'icon': 'skin'},
        
        # 2.3 数码设备类
        {'name': '电脑设备', 'color': '#748ffc', 'icon': 'laptop'},
        {'name': '手机数码', 'color': '#339af0', 'icon': 'mobile'},
        {'name': '摄影器材', 'color': '#1c7ed6', 'icon': 'camera'},
        
        # 2.4 家居物品类
        {'name': '家用电器', 'color': '#69db7c', 'icon': 'thunderbolt'},
        {'name': '家具', 'color': '#51cf66', 'icon': 'tool'},
        {'name': '智能家居', 'color': '#37b24d', 'icon': 'bulb'},
        
        # ========== 三、金融流动资产 ==========
        # 3.1 现金类
        {'name': '银行存款', 'color': '#51cf66', 'icon': 'bank'},
        {'name': '现金', 'color': '#40c057', 'icon': 'wallet'},
        {'name': '支付宝微信', 'color': '#2f9e44', 'icon': 'alipay-circle'},
        
        # 3.2 投资理财类
        {'name': '股票', 'color': '#f03e3e', 'icon': 'stock'},
        {'name': '基金', 'color': '#22b8cf', 'icon': 'fund'},
        {'name': '债券理财', 'color': '#20c997', 'icon': 'line-chart'},
        {'name': '数字货币', 'color': '#ffd43b', 'icon': 'bitcoin'},
        
        # 3.3 保险保障类
        {'name': '人寿保险', 'color': '#ff8787', 'icon': 'heart'},
        {'name': '财产保险', 'color': '#ffa94d', 'icon': 'safety'},
        {'name': '医疗保险', 'color': '#ff6b9d', 'icon': 'medicine-box'},
        {'name': '社保公积金', 'color': '#f783ac', 'icon': 'schedule'},
        
        # ========== 四、负债管理 ==========
        {'name': '房贷', 'color': '#fa5252', 'icon': 'home'},
        {'name': '车贷', 'color': '#ff6b6b', 'icon': 'car'},
        {'name': '信用卡', 'color': '#f06595', 'icon': 'credit-card'},
        {'name': '消费贷', 'color': '#e64980', 'icon': 'account-book'},
        {'name': '经营贷款', 'color': '#e03131', 'icon': 'fund-projection-screen'},
        {'name': '私人借款', 'color': '#c92a2a', 'icon': 'file-text'},
        
        # ========== 五、其他资产 ==========
        {'name': '应收账款', 'color': '#868e96', 'icon': 'file-done'},
        {'name': '预付费用', 'color': '#adb5bd', 'icon': 'clock-circle'},
        {'name': '积分权益', 'color': '#ffd8a8', 'icon': 'star'},
        {'name': '其他资产', 'color': '#ced4da', 'icon': 'folder'}
    ]

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
        
        # 使用共享的默认分类配置
        default_categories = get_default_categories()
        
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
        db.session.query(Category).delete()
        db.session.query(AIReport).delete()
        
        # 删除所有非管理员用户
        db.session.query(User).filter(User.role != 'admin').delete()
        
        # 重置当前用户的API Token
        user.aliyun_api_token_encrypted = None
        
        db.session.commit()
        
        # 为当前用户重新创建默认分类
        default_categories = get_default_categories()
        
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
            'message': '数据库已清空，默认分类已重建'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'清空数据库失败：{str(e)}'
        }), 500