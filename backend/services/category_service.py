"""分类服务"""

from models.category import Category
from database import db
from config.default_categories import DEFAULT_CATEGORIES

# 固定资产专属分类
FIXED_ASSET_CATEGORIES = [
    {'name': '房产', 'icon': 'home', 'color': '#1890ff', 'description': '住宅、商铺、公寓等不动产', 'sort_order': 1},
    {'name': '车辆', 'icon': 'car', 'color': '#52c41a', 'description': '汽车、摩托车、电动车等', 'sort_order': 2},
    {'name': '电子设备', 'icon': 'laptop', 'color': '#722ed1', 'description': '手机、电脑、平板、相机等', 'sort_order': 3},
    {'name': '家具家电', 'icon': 'appstore', 'color': '#fa8c16', 'description': '电视、冰箱、洗衣机、沙发等', 'sort_order': 4},
    {'name': '珠宝首饰', 'icon': 'skin', 'color': '#eb2f96', 'description': '黄金、钻石、玉石、手表等', 'sort_order': 5},
    {'name': '收藏品', 'icon': 'gift', 'color': '#13c2c2', 'description': '字画、古董、邮票、纪念币等', 'sort_order': 6},
    {'name': '运动器材', 'icon': 'trophy', 'color': '#f5222d', 'description': '健身器材、自行车、球类等', 'sort_order': 7},
    {'name': '其他', 'icon': 'folder', 'color': '#8c8c8c', 'description': '其他固定资产', 'sort_order': 99},
]

# 虚拟资产专属分类
VIRTUAL_ASSET_CATEGORIES = [
    {'name': '订阅服务', 'icon': 'sync', 'color': '#667eea', 'description': 'Netflix、Spotify、视频网站等订阅', 'sort_order': 1},
    {'name': '会员权益', 'icon': 'crown', 'color': '#722ed1', 'description': '电商会员、视频会员、购物权益等', 'sort_order': 2},
    {'name': '保险保障', 'icon': 'safety', 'color': '#13c2c2', 'description': '车险、医疗险、意外险等', 'sort_order': 3},
    {'name': '域名证书', 'icon': 'global', 'color': '#1890ff', 'description': '域名、SSL证书、托管服务等', 'sort_order': 4},
    {'name': '软件授权', 'icon': 'laptop', 'color': '#52c41a', 'description': 'Office、Adobe、专业软件许可等', 'sort_order': 5},
    {'name': '云服务', 'icon': 'cloud', 'color': '#eb2f96', 'description': '云存储、服务器、API服务等', 'sort_order': 6},
    {'name': '通讯服务', 'icon': 'phone', 'color': '#fa8c16', 'description': '手机套餐、宽带、VPN等', 'sort_order': 7},
    {'name': '其他', 'icon': 'folder', 'color': '#8c8c8c', 'description': '其他有时效性的虚拟资产', 'sort_order': 99},
]


def initialize_user_categories(user_id, skip_if_exists=True):
    """为用户初始化默认分类（固定资产+虚拟资产）"""
    try:
        if skip_if_exists and Category.query.filter_by(user_id=user_id).count() > 0:
            return False
        
        # 初始化固定资产分类
        for cat_data in FIXED_ASSET_CATEGORIES:
            existing = Category.query.filter_by(
                user_id=user_id,
                name=cat_data['name'],
                asset_type='fixed'
            ).first()
            
            if not existing:
                category = Category(
                    name=cat_data['name'],
                    icon=cat_data['icon'],
                    color=cat_data['color'],
                    description=cat_data['description'],
                    sort_order=cat_data['sort_order'],
                    asset_type='fixed',
                    user_id=user_id,
                    parent_id=None
                )
                db.session.add(category)
        
        # 初始化虚拟资产分类
        for cat_data in VIRTUAL_ASSET_CATEGORIES:
            existing = Category.query.filter_by(
                user_id=user_id,
                name=cat_data['name'],
                asset_type='virtual'
            ).first()
            
            if not existing:
                category = Category(
                    name=cat_data['name'],
                    icon=cat_data['icon'],
                    color=cat_data['color'],
                    description=cat_data['description'],
                    sort_order=cat_data['sort_order'],
                    asset_type='virtual',
                    user_id=user_id,
                    parent_id=None
                )
                db.session.add(category)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"初始化分类失败: {e}")
        return False


def reset_user_categories(user_id):
    """重置用户分类"""
    try:
        Category.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return initialize_user_categories(user_id)
    except Exception as e:
        db.session.rollback()
        print(f"重置分类失败: {e}")
        return False


def get_category_tree(user_id):
    """获取用户的分类树"""
    categories = Category.query.filter_by(
        user_id=user_id,
        parent_id=None
    ).order_by(Category.sort_order, Category.name).all()
    
    return [cat.to_dict(include_children=True) for cat in categories]


def get_all_leaf_categories(user_id):
    """获取所有叶子分类"""
    categories = Category.query.filter_by(user_id=user_id).all()
    
    leaf_categories = [
        {
            **cat.to_dict(),
            'full_path': cat.get_full_path(),
            'level': cat.get_level()
        }
        for cat in categories
        if cat.children.count() == 0
    ]
    
    return sorted(leaf_categories, key=lambda x: (x['level'], x['sort_order'], x['name']))
