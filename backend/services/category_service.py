"""分类服务"""

from models.category import Category
from database import db
from config.default_categories import DEFAULT_CATEGORIES


def initialize_user_categories(user_id, skip_if_exists=True):
    """为用户初始化默认分类"""
    try:
        if skip_if_exists and Category.query.filter_by(user_id=user_id).count() > 0:
            return False
        
        for parent_data in DEFAULT_CATEGORIES:
            parent = Category.query.filter_by(
                user_id=user_id,
                parent_id=None,
                name=parent_data['name']
            ).first()
            
            if not parent:
                parent = Category(
                    name=parent_data['name'],
                    color=parent_data['color'],
                    icon=parent_data['icon'],
                    description=parent_data.get('description', ''),
                    sort_order=parent_data.get('sort_order', 0),
                    user_id=user_id,
                    parent_id=None
                )
                db.session.add(parent)
                db.session.flush()
            
            for child_data in parent_data.get('children', []):
                if not Category.query.filter_by(
                    user_id=user_id,
                    parent_id=parent.id,
                    name=child_data['name']
                ).first():
                    child = Category(
                        name=child_data['name'],
                        color=child_data['color'],
                        icon=child_data['icon'],
                        description=child_data.get('description', ''),
                        sort_order=child_data.get('sort_order', 0),
                        user_id=user_id,
                        parent_id=parent.id
                    )
                    db.session.add(child)
        
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
