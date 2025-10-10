from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category
from models.project import Project
from database import db

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取分类列表"""
    try:
        user_id = int(get_jwt_identity())
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
    """创建分类"""
    try:
        print("Debug: create_category called")
        user_id = int(get_jwt_identity())
        print(f"Debug: user_id = {user_id}")
        data = request.get_json()
        print(f"Debug: data = {data}")
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'message': '分类名称不能为空'
            }), 400
        
        name = data['name'].strip()
        
        # 验证分类名称长度
        if len(name) > 50:
            return jsonify({
                'code': 400,
                'message': '分类名称不能超过50个字符'
            }), 400
        
        # 检查分类名称是否已存在
        existing_category = Category.query.filter_by(
            user_id=user_id,
            name=name
        ).first()
        
        if existing_category:
            return jsonify({
                'code': 400,
                'message': '分类名称已存在'
            }), 400
        
        # 创建分类
        category = Category(
            name=name,
            color=data.get('color', '#1890ff'),
            icon=data.get('icon', 'folder'),
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
            
            # 检查分类名称是否已存在（排除当前分类）
            existing_category = Category.query.filter(
                Category.user_id == user_id,
                Category.name == name,
                Category.id != category_id
            ).first()
            
            if existing_category:
                return jsonify({
                    'code': 400,
                    'message': '分类名称已存在'
                }), 400
            
            category.name = name
        
        # 更新颜色和图标
        if 'color' in data:
            category.color = data['color']
        
        if 'icon' in data:
            category.icon = data['icon']
        
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
        category_data = category.to_dict()
        category_data['projects'] = [project.to_dict() for project in projects]
        
        return jsonify({
            'code': 200,
            'data': category_data
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分类详情失败：{str(e)}'
        }), 500