from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.project import Project
from models.category import Category
from database import db
from datetime import datetime
from decimal import Decimal

projects_bp = Blueprint('projects', __name__)

def parse_datetime(datetime_str):
    """解析日期时间字符串"""
    try:
        # 支持多种日期格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"无法解析日期格式：{datetime_str}")
        
    except Exception as e:
        raise ValueError(f"日期格式错误：{str(e)}")

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """获取项目列表"""
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')  # not_started, active, expired
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, remaining_value, progress
        order = request.args.get('order', 'desc')  # asc, desc
        
        # 构建查询
        query = Project.query.filter_by(user_id=user_id)
        
        # 按分类筛选
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 获取所有项目
        projects = query.all()
        
        # 转换为字典并计算值
        projects_data = []
        for project in projects:
            project_data = project.to_dict(include_calculations=True)
            projects_data.append(project_data)
        
        # 按状态筛选
        if status:
            projects_data = [p for p in projects_data if p['status'] == status]
        
        # 排序
        reverse = (order == 'desc')
        if sort_by == 'remaining_value':
            projects_data.sort(key=lambda x: x['remaining_value'], reverse=reverse)
        elif sort_by == 'progress':
            projects_data.sort(key=lambda x: x['progress'], reverse=reverse)
        elif sort_by == 'total_amount':
            projects_data.sort(key=lambda x: x['total_amount'], reverse=reverse)
        else:  # created_at
            projects_data.sort(key=lambda x: x['created_at'], reverse=reverse)
        
        return jsonify({
            'code': 200,
            'data': projects_data
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目列表失败：{str(e)}'
        }), 500

@projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """创建项目"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'total_amount', 'start_time', 'end_time', 'category_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段：{field}'
                }), 400
        
        name = data['name'].strip()
        
        # 验证项目名称
        if not name:
            return jsonify({
                'code': 400,
                'message': '项目名称不能为空'
            }), 400
        
        if len(name) > 100:
            return jsonify({
                'code': 400,
                'message': '项目名称不能超过100个字符'
            }), 400
        
        # 验证金额
        try:
            total_amount = Decimal(str(data['total_amount']))
            if total_amount <= 0:
                return jsonify({
                    'code': 400,
                    'message': '总金额必须大于0'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'code': 400,
                'message': '总金额格式不正确'
            }), 400
        
        # 验证分类是否存在且属于当前用户
        category = Category.query.filter_by(
            id=data['category_id'],
            user_id=user_id
        ).first()
        
        if not category:
            return jsonify({
                'code': 400,
                'message': '分类不存在或无权限'
            }), 400
        
        # 解析时间
        try:
            start_time = parse_datetime(data['start_time'])
            end_time = parse_datetime(data['end_time'])
        except ValueError as e:
            return jsonify({
                'code': 400,
                'message': str(e)
            }), 400
        
        # 验证时间逻辑
        if start_time >= end_time:
            return jsonify({
                'code': 400,
                'message': '开始时间必须早于结束时间'
            }), 400
        
        # 解析购买时间（可选）
        purchase_time = None
        if data.get('purchase_time'):
            try:
                purchase_time = parse_datetime(data['purchase_time'])
            except ValueError as e:
                return jsonify({
                    'code': 400,
                    'message': f'购买时间格式错误：{str(e)}'
                }), 400
        
        # 创建项目
        project = Project(
            name=name,
            total_amount=total_amount,
            purchase_time=purchase_time,
            start_time=start_time,
            end_time=end_time,
            purpose=data.get('purpose', '').strip()[:500],  # 限制500字符
            account_username=data.get('account_username', '').strip()[:100] if data.get('account_username') else None,
            account_password=data.get('account_password', '').strip()[:200] if data.get('account_password') else None,
            user_id=user_id,
            category_id=data['category_id']
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目创建成功',
            'data': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建项目失败：{str(e)}'
        }), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """获取项目详情"""
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'data': project.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目详情失败：{str(e)}'
        }), 500

@projects_bp.route('/projects/<int:project_id>/calculate', methods=['GET'])
@jwt_required()
def calculate_project(project_id):
    """计算项目价值（支持自定义基准时间）"""
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        # 获取自定义基准时间
        base_time = None
        base_time_str = request.args.get('base_time')
        if base_time_str:
            try:
                base_time = parse_datetime(base_time_str)
            except ValueError as e:
                return jsonify({
                    'code': 400,
                    'message': f'基准时间格式错误：{str(e)}'
                }), 400
        
        # 计算价值
        calculation_data = project.calculate_values(base_time)
        
        return jsonify({
            'code': 200,
            'data': calculation_data
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'计算项目价值失败：{str(e)}'
        }), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """更新项目"""
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新项目名称
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({
                    'code': 400,
                    'message': '项目名称不能为空'
                }), 400
            
            if len(name) > 100:
                return jsonify({
                    'code': 400,
                    'message': '项目名称不能超过100个字符'
                }), 400
            
            project.name = name
        
        # 更新总金额
        if 'total_amount' in data:
            try:
                total_amount = Decimal(str(data['total_amount']))
                if total_amount <= 0:
                    return jsonify({
                        'code': 400,
                        'message': '总金额必须大于0'
                    }), 400
                project.total_amount = total_amount
            except (ValueError, TypeError):
                return jsonify({
                    'code': 400,
                    'message': '总金额格式不正确'
                }), 400
        
        # 更新分类
        if 'category_id' in data:
            category = Category.query.filter_by(
                id=data['category_id'],
                user_id=user_id
            ).first()
            
            if not category:
                return jsonify({
                    'code': 400,
                    'message': '分类不存在或无权限'
                }), 400
            
            project.category_id = data['category_id']
        
        # 更新时间
        if 'start_time' in data:
            try:
                start_time = parse_datetime(data['start_time'])
                if 'end_time' in data:
                    end_time = parse_datetime(data['end_time'])
                else:
                    end_time = project.end_time
                
                if start_time >= end_time:
                    return jsonify({
                        'code': 400,
                        'message': '开始时间必须早于结束时间'
                    }), 400
                
                project.start_time = start_time
            except ValueError as e:
                return jsonify({
                    'code': 400,
                    'message': str(e)
                }), 400
        
        if 'end_time' in data:
            try:
                end_time = parse_datetime(data['end_time'])
                start_time = project.start_time
                
                if start_time >= end_time:
                    return jsonify({
                        'code': 400,
                        'message': '结束时间必须晚于开始时间'
                    }), 400
                
                project.end_time = end_time
            except ValueError as e:
                return jsonify({
                    'code': 400,
                    'message': str(e)
                }), 400
        
        # 更新购买时间
        if 'purchase_time' in data:
            if data['purchase_time']:
                try:
                    project.purchase_time = parse_datetime(data['purchase_time'])
                except ValueError as e:
                    return jsonify({
                        'code': 400,
                        'message': f'购买时间格式错误：{str(e)}'
                    }), 400
            else:
                project.purchase_time = None
        
        # 更新购买目的
        if 'purpose' in data:
            project.purpose = data['purpose'].strip()[:500] if data['purpose'] else None
        
        # 更新账号信息
        if 'account_username' in data:
            project.account_username = data['account_username'].strip()[:100] if data['account_username'] else None
        
        if 'account_password' in data:
            project.account_password = data['account_password'].strip()[:200] if data['account_password'] else None
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目更新成功',
            'data': project.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新项目失败：{str(e)}'
        }), 500

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """删除项目"""
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除项目失败：{str(e)}'
        }), 500

@projects_bp.route('/projects/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete_projects():
    """批量删除项目"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('project_ids') or not isinstance(data['project_ids'], list):
            return jsonify({
                'code': 400,
                'message': '请提供要删除的项目ID列表'
            }), 400
        
        project_ids = data['project_ids']
        
        # 验证所有项目都属于当前用户
        projects = Project.query.filter(
            Project.id.in_(project_ids),
            Project.user_id == user_id
        ).all()
        
        if len(projects) != len(project_ids):
            return jsonify({
                'code': 400,
                'message': '部分项目不存在或无权限删除'
            }), 400
        
        # 批量删除
        for project in projects:
            db.session.delete(project)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'成功删除{len(projects)}个项目'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'批量删除失败：{str(e)}'
        }), 500

@projects_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取统计数据"""
    try:
        user_id = get_jwt_identity()
        projects = Project.query.filter_by(user_id=user_id).all()
        
        if not projects:
            return jsonify({
                'code': 200,
                'data': {
                    'total_projects': 0,
                    'total_amount': 0,
                    'total_used_cost': 0,
                    'total_remaining_value': 0,
                    'status_distribution': {
                        'not_started': 0,
                        'active': 0,
                        'expired': 0
                    }
                }
            })
        
        # 计算统计数据
        total_amount = 0
        total_used_cost = 0
        total_remaining_value = 0
        status_distribution = {'not_started': 0, 'active': 0, 'expired': 0}
        
        for project in projects:
            calculations = project.calculate_values()
            total_amount += float(project.total_amount)
            total_used_cost += calculations['used_cost']
            total_remaining_value += calculations['remaining_value']
            status_distribution[calculations['status']] += 1
        
        return jsonify({
            'code': 200,
            'data': {
                'total_projects': len(projects),
                'total_amount': round(total_amount, 2),
                'total_used_cost': round(total_used_cost, 2),
                'total_remaining_value': round(total_remaining_value, 2),
                'status_distribution': status_distribution
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取统计数据失败：{str(e)}'
        }), 500