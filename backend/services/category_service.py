"""
分类服务
提供分类的初始化、管理等功能
"""

from models.category import Category
from database import db
from config.default_categories import DEFAULT_CATEGORIES


def initialize_user_categories(user_id, skip_if_exists=True):
    """
    为新用户初始化默认分类
    
    Args:
        user_id: 用户ID
        skip_if_exists: 如果用户已有分类是否跳过（默认True）
    
    Returns:
        bool: 是否成功初始化
    """
    try:
        # 检查用户是否已有分类
        existing_count = Category.query.filter_by(user_id=user_id).count()
        if existing_count > 0 and skip_if_exists:
            print(f"用户 {user_id} 已有 {existing_count} 个分类，跳过初始化")
            return False
        
        # 创建默认分类
        for parent_data in DEFAULT_CATEGORIES:
            # 检查是否已存在同名的一级分类
            existing_parent = Category.query.filter_by(
                user_id=user_id,
                parent_id=None,
                name=parent_data['name']
            ).first()
            
            if existing_parent:
                print(f"一级分类 '{parent_data['name']}' 已存在，跳过")
                parent_category = existing_parent
            else:
                # 创建一级分类
                parent_category = Category(
                    name=parent_data['name'],
                    color=parent_data['color'],
                    icon=parent_data['icon'],
                    description=parent_data.get('description', ''),
                    sort_order=parent_data.get('sort_order', 0),
                    user_id=user_id,
                    parent_id=None
                )
                db.session.add(parent_category)
                db.session.flush()  # 获取父分类ID
            
            # 创建二级分类
            for child_data in parent_data.get('children', []):
                # 检查是否已存在同名的二级分类
                existing_child = Category.query.filter_by(
                    user_id=user_id,
                    parent_id=parent_category.id,
                    name=child_data['name']
                ).first()
                
                if existing_child:
                    print(f"二级分类 '{parent_data['name']} > {child_data['name']}' 已存在，跳过")
                    continue
                    
                child_category = Category(
                    name=child_data['name'],
                    color=child_data['color'],
                    icon=child_data['icon'],
                    description=child_data.get('description', ''),
                    sort_order=child_data.get('sort_order', 0),
                    user_id=user_id,
                    parent_id=parent_category.id
                )
                db.session.add(child_category)
        
        db.session.commit()
        print(f"成功为用户 {user_id} 初始化默认分类")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"初始化用户分类失败：{str(e)}")
        return False


def reset_user_categories(user_id):
    """
    重置用户的分类为默认分类（慎用！会删除现有分类）
    
    Args:
        user_id: 用户ID
    
    Returns:
        bool: 是否成功重置
    """
    try:
        # 删除用户现有的所有分类
        Category.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        # 重新初始化
        return initialize_user_categories(user_id)
        
    except Exception as e:
        db.session.rollback()
        print(f"重置用户分类失败：{str(e)}")
        return False


def get_category_tree(user_id):
    """
    获取用户的完整分类树
    
    Args:
        user_id: 用户ID
    
    Returns:
        list: 分类树列表
    """
    try:
        # 获取所有顶级分类
        top_categories = Category.query.filter_by(
            user_id=user_id,
            parent_id=None
        ).order_by(Category.sort_order, Category.name).all()
        
        return [category.to_dict(include_children=True) for category in top_categories]
        
    except Exception as e:
        print(f"获取分类树失败：{str(e)}")
        return []


def get_all_leaf_categories(user_id):
    """
    获取用户的所有叶子分类（没有子分类的分类，通常用于项目选择）
    
    Args:
        user_id: 用户ID
    
    Returns:
        list: 叶子分类列表
    """
    try:
        all_categories = Category.query.filter_by(user_id=user_id).all()
        
        # 筛选出没有子分类的分类
        leaf_categories = []
        for category in all_categories:
            if category.children.count() == 0:
                cat_dict = category.to_dict()
                cat_dict['full_path'] = category.get_full_path()
                cat_dict['level'] = category.get_level()
                leaf_categories.append(cat_dict)
        
        # 按层级和排序顺序排序
        leaf_categories.sort(key=lambda x: (x['level'], x['sort_order'], x['name']))
        
        return leaf_categories
        
    except Exception as e:
        print(f"获取叶子分类失败：{str(e)}")
        return []
