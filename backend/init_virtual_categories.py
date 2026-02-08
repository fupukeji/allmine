"""
初始化虚拟资产专属分类
虚拟资产是有时效性的资产：会员、订阅、保险、域名等
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models.category import Category
from models.user import User

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

def init_virtual_categories():
    app = create_app()
    with app.app_context():
        try:
            # 获取所有用户
            users = User.query.all()
            
            for user in users:
                print(f"为用户 {user.username} 初始化虚拟资产分类...")
                
                for cat_data in VIRTUAL_ASSET_CATEGORIES:
                    # 检查是否已存在同名的虚拟资产分类
                    existing = Category.query.filter_by(
                        user_id=user.id,
                        name=cat_data['name'],
                        asset_type='virtual'
                    ).first()
                    
                    if existing:
                        print(f"  - {cat_data['name']} 已存在，跳过")
                        continue
                    
                    # 创建新分类
                    category = Category(
                        name=cat_data['name'],
                        icon=cat_data['icon'],
                        color=cat_data['color'],
                        description=cat_data['description'],
                        sort_order=cat_data['sort_order'],
                        asset_type='virtual',
                        user_id=user.id
                    )
                    db.session.add(category)
                    print(f"  + 添加: {cat_data['name']}")
                
            db.session.commit()
            print("\n✅ 虚拟资产分类初始化完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 初始化失败: {e}")
            raise

if __name__ == '__main__':
    init_virtual_categories()
