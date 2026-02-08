"""
初始化固定资产专属分类
固定资产是长期持有的实物资产：房产、车辆、设备等
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models.category import Category
from models.user import User

# 固定资产专属分类 - 符合人生常用配置
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

def init_fixed_categories():
    app = create_app()
    with app.app_context():
        try:
            users = User.query.all()
            
            for user in users:
                print(f"为用户 {user.username} 重置固定资产分类...")
                
                # 删除旧的固定资产分类（没有关联资产的）
                old_cats = Category.query.filter_by(user_id=user.id, asset_type='fixed').all()
                for cat in old_cats:
                    if len(cat.projects) == 0:
                        db.session.delete(cat)
                        print(f"  - 删除: {cat.name}")
                
                db.session.flush()
                
                # 创建新分类
                for cat_data in FIXED_ASSET_CATEGORIES:
                    existing = Category.query.filter_by(
                        user_id=user.id,
                        name=cat_data['name'],
                        asset_type='fixed'
                    ).first()
                    
                    if existing:
                        print(f"  ~ {cat_data['name']} 已存在")
                        continue
                    
                    category = Category(
                        name=cat_data['name'],
                        icon=cat_data['icon'],
                        color=cat_data['color'],
                        description=cat_data['description'],
                        sort_order=cat_data['sort_order'],
                        asset_type='fixed',
                        user_id=user.id
                    )
                    db.session.add(category)
                    print(f"  + 添加: {cat_data['name']}")
                
            db.session.commit()
            print("\n✅ 固定资产分类重置完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 初始化失败: {e}")
            raise

if __name__ == '__main__':
    init_fixed_categories()

