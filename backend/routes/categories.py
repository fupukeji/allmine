from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models.project import Project
from database import db
from services.category_service import (
    initialize_user_categories,
    reset_user_categories,
    get_category_tree,
    get_all_leaf_categories
)

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取分类列表（支持树形结构）"""
    try:
        user_id = int(get_jwt_identity())
        tree = request.args.get('tree', 'false').lower() == 'true'  # 是否返回树形结构
        
        if tree:
            # 返回树形结构：只返回顶级分类，包含其子分类
            categories = Category.query.filter_by(
                user_id=user_id, 
                parent_id=None
            ).order_by(Category.sort_order, Category.name).all()
            
            return jsonify({
                'code': 200,
                'data': [category.to_dict(include_children=True) for category in categories]
            })
        else:
            # 返回平面列表
            categories = Category.query.filter_by(user_id=user_id).order_by(Category.created_at.desc()).all()
            
            return jsonify({
                'code': 200,
                'data': [category.to_dict() for category in categories]
            })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分类列表失败：{str(e)}'
        }), 500

@categories_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """创建分类（支持层级）"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'message': '分类名称不能为空'
            }), 400
        
        name = data['name'].strip()
        parent_id = data.get('parent_id')  # 父分类ID
        
        # 验证分类名称长度
        if len(name) > 50:
            return jsonify({
                'code': 400,
                'message': '分类名称不能超过50个字符'
            }), 400
        
        # 如果有父分类，验证父分类是否存在
        if parent_id:
            parent_category = Category.query.filter_by(
                id=parent_id,
                user_id=user_id
            ).first()
            
            if not parent_category:
                return jsonify({
                    'code': 404,
                    'message': '父分类不存在'
                }), 404
            
            # 限制层级深度（最多3级）
            if parent_category.get_level() >= 2:
                return jsonify({
                    'code': 400,
                    'message': '分类层级最多支持3级'
                }), 400
        
        # 检查同一父级下分类名称是否已存在
        existing_category = Category.query.filter_by(
            user_id=user_id,
            parent_id=parent_id,
            name=name
        ).first()
        
        if existing_category:
            return jsonify({
                'code': 400,
                'message': '该层级下已存在同名分类'
            }), 400
        
        # 创建分类
        category = Category(
            name=name,
            color=data.get('color', '#1890ff'),
            icon=data.get('icon', 'folder'),
            description=data.get('description'),
            sort_order=data.get('sort_order', 0),
            parent_id=parent_id,
            user_id=user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '分类创建成功',
            'data': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建分类失败：{str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """更新分类"""
    try:
        user_id = int(get_jwt_identity())
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        
        if not category:
            return jsonify({
                'code': 404,
                'message': '分类不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新分类名称
        if 'name' in data:
            name = data['name'].strip()
            
            if not name:
                return jsonify({
                    'code': 400,
                    'message': '分类名称不能为空'
                }), 400
            
            if len(name) > 50:
                return jsonify({
                    'code': 400,
                    'message': '分类名称不能超过50个字符'
                }), 400
            
            # 检查同一父级下分类名称是否已存在（排除当前分类）
            existing_category = Category.query.filter(
                Category.user_id == user_id,
                Category.parent_id == category.parent_id,
                Category.name == name,
                Category.id != category_id
            ).first()
            
            if existing_category:
                return jsonify({
                    'code': 400,
                    'message': '该层级下已存在同名分类'
                }), 400
            
            category.name = name
        
        # 更新父分类
        if 'parent_id' in data:
            new_parent_id = data['parent_id']
            
            # 不能把分类移动到自己下面
            if new_parent_id == category_id:
                return jsonify({
                    'code': 400,
                    'message': '不能将分类移动到自己下面'
                }), 400
            
            # 如果有新父分类，验证存在性
            if new_parent_id:
                parent_category = Category.query.filter_by(
                    id=new_parent_id,
                    user_id=user_id
                ).first()
                
                if not parent_category:
                    return jsonify({
                        'code': 404,
                        'message': '父分类不存在'
                    }), 404
                
                # 限制层级深度
                if parent_category.get_level() >= 2:
                    return jsonify({
                        'code': 400,
                        'message': '分类层级最多支持3级'
                    }), 400
            
            category.parent_id = new_parent_id
        
        # 更新其他字段
        if 'color' in data:
            category.color = data['color']
        
        if 'icon' in data:
            category.icon = data['icon']
        
        if 'description' in data:
            category.description = data['description']
        
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '分类更新成功',
            'data': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新分类失败：{str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """删除分类"""
    try:
        user_id = int(get_jwt_identity())
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        
        if not category:
            return jsonify({
                'code': 404,
                'message': '分类不存在'
            }), 404
        
        # 检查是否有子分类
        child_count = category.children.count()
        if child_count > 0:
            return jsonify({
                'code': 400,
                'message': f'该分类下还有{child_count}个子分类，请先删除子分类'
            }), 400
        
        # 检查是否有关联的项目
        project_count = Project.query.filter_by(category_id=category_id).count()
        if project_count > 0:
            return jsonify({
                'code': 400,
                'message': f'该分类下还有{project_count}个项目，请先转移或删除这些项目'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '分类删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除分类失败：{str(e)}'
        }), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """获取单个分类详情"""
    try:
        user_id = int(get_jwt_identity())
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        
        if not category:
            return jsonify({
                'code': 404,
                'message': '分类不存在'
            }), 404
        
        # 获取该分类下的项目
        projects = Project.query.filter_by(category_id=category_id).all()
        category_data = category.to_dict(include_children=True)
        category_data['projects'] = [project.to_dict() for project in projects]
        category_data['full_path'] = category.get_full_path()
        category_data['level'] = category.get_level()
        
        return jsonify({
            'code': 200,
            'data': category_data
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分类详情失败：{str(e)}'
        }), 500

@categories_bp.route('/categories/initialize', methods=['POST'])
@jwt_required()
def initialize_categories():
    """初始化用户默认分类"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        force = data.get('force', False)
        
        success = initialize_user_categories(user_id, skip_if_exists=not force)
        
        if success:
            return jsonify({'code': 200, 'message': '默认分类初始化成功'})
        
        count = Category.query.filter_by(user_id=user_id).count()
        return jsonify({
            'code': 400,
            'message': f'已有{count}个分类。新分类已合并，重复的已跳过'
        }), 400
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'初始化失败: {str(e)}'}), 500

@categories_bp.route('/categories/reset', methods=['POST'])
@jwt_required()
def reset_categories():
    """重置用户分类为默认分类"""
    try:
        user_id = int(get_jwt_identity())
        
        project_count = Project.query.join(Category).filter(
            Category.user_id == user_id
        ).count()
        
        if project_count > 0:
            return jsonify({
                'code': 400,
                'message': f'有{project_count}个项目关联到现有分类，无法重置'
            }), 400
        
        success = reset_user_categories(user_id)
        return jsonify({
            'code': 200 if success else 500,
            'message': '分类已重置' if success else '重置失败'
        }), 200 if success else 500
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'重置失败: {str(e)}'}), 500

@categories_bp.route('/categories/leaf', methods=['GET'])
@jwt_required()
def get_leaf_categories():
    """获取所有叶子分类"""
    try:
        user_id = int(get_jwt_identity())
        return jsonify({
            'code': 200,
            'data': get_all_leaf_categories(user_id)
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500