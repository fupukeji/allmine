from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.asset_maintenance import AssetMaintenance, MaintenanceReminder
from models.fixed_asset import FixedAsset
from datetime import datetime, date, timedelta

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/assets/<int:asset_id>/maintenances', methods=['GET'])
@jwt_required()
def get_asset_maintenances(asset_id):
    """获取资产维护记录列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        maintenance_type = request.args.get('maintenance_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = AssetMaintenance.query.filter_by(asset_id=asset_id)
        
        if maintenance_type:
            query = query.filter_by(maintenance_type=maintenance_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date:
            query = query.filter(AssetMaintenance.maintenance_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(AssetMaintenance.maintenance_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        # 排序和分页
        query = query.order_by(AssetMaintenance.maintenance_date.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        maintenances_data = [maintenance.to_dict() for maintenance in pagination.items]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': maintenances_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取维护记录失败: {str(e)}'}), 500

@maintenance_bp.route('/assets/<int:asset_id>/maintenances', methods=['POST'])
@jwt_required()
def create_asset_maintenance(asset_id):
    """创建资产维护记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['maintenance_type', 'title', 'maintenance_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'code': 400, 'message': f'缺少必填字段: {field}'}), 400
        
        # 转换日期字段
        try:
            maintenance_date = datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date()
            next_maintenance_date = None
            if data.get('next_maintenance_date'):
                next_maintenance_date = datetime.strptime(data['next_maintenance_date'], '%Y-%m-%d').date()
            warranty_end_date = None
            if data.get('warranty_end_date'):
                warranty_end_date = datetime.strptime(data['warranty_end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误，请使用 YYYY-MM-DD 格式'}), 400
        
        # 创建维护记录
        maintenance = AssetMaintenance(
            asset_id=asset_id,
            maintenance_type=data['maintenance_type'],
            title=data['title'],
            description=data.get('description', ''),
            maintenance_date=maintenance_date,
            cost=data.get('cost', 0),
            next_maintenance_date=next_maintenance_date,
            maintenance_interval=data.get('maintenance_interval'),
            provider=data.get('provider', ''),
            warranty_end_date=warranty_end_date,
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'planned')
        )
        
        db.session.add(maintenance)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '维护记录创建成功',
            'data': maintenance.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建维护记录失败: {str(e)}'}), 500

@maintenance_bp.route('/assets/<int:asset_id>/maintenances/<int:maintenance_id>', methods=['PUT'])
@jwt_required()
def update_asset_maintenance(asset_id, maintenance_id):
    """更新资产维护记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        maintenance = AssetMaintenance.query.filter_by(id=maintenance_id, asset_id=asset_id).first()
        if not maintenance:
            return jsonify({'code': 404, 'message': '维护记录不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        updatable_fields = [
            'maintenance_type', 'title', 'description', 'cost',
            'maintenance_interval', 'provider', 'priority', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(maintenance, field, data[field])
        
        # 处理日期字段
        date_fields = ['maintenance_date', 'next_maintenance_date', 'warranty_end_date']
        for field in date_fields:
            if field in data and data[field]:
                try:
                    setattr(maintenance, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({'code': 400, 'message': f'{field} 日期格式错误'}), 400
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '维护记录更新成功',
            'data': maintenance.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新维护记录失败: {str(e)}'}), 500

@maintenance_bp.route('/assets/<int:asset_id>/maintenances/<int:maintenance_id>', methods=['DELETE'])
@jwt_required()
def delete_asset_maintenance(asset_id, maintenance_id):
    """删除资产维护记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        maintenance = AssetMaintenance.query.filter_by(id=maintenance_id, asset_id=asset_id).first()
        if not maintenance:
            return jsonify({'code': 404, 'message': '维护记录不存在'}), 404
        
        db.session.delete(maintenance)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '维护记录删除成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除维护记录失败: {str(e)}'}), 500

@maintenance_bp.route('/assets/<int:asset_id>/maintenance-stats', methods=['GET'])
@jwt_required()
def get_asset_maintenance_stats(asset_id):
    """获取资产维护统计"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        stats = AssetMaintenance.get_asset_maintenance_stats(asset_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': stats
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取维护统计失败: {str(e)}'}), 500

@maintenance_bp.route('/maintenance-overview', methods=['GET'])
@jwt_required()
def get_maintenance_overview():
    """获取用户所有资产维护概览"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取用户所有资产
        user_assets = FixedAsset.query.filter_by(user_id=current_user_id).all()
        asset_ids = [asset.id for asset in user_assets]
        
        if not asset_ids:
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'total_maintenance_cost': 0,
                    'total_maintenance_count': 0,
                    'overdue_count': 0,
                    'upcoming_count': 0,
                    'overdue_maintenances': [],
                    'upcoming_maintenances': []
                }
            })
        
        # 总维护统计
        from sqlalchemy import func
        total_stats = db.session.query(
            func.count(AssetMaintenance.id).label('total_count'),
            func.sum(AssetMaintenance.cost).label('total_cost')
        ).filter(
            AssetMaintenance.asset_id.in_(asset_ids),
            AssetMaintenance.status == 'completed'
        ).first()
        
        # 过期维护
        overdue_maintenances = AssetMaintenance.get_overdue_maintenances(asset_ids)
        
        # 即将到期的维护（30天内）
        upcoming_maintenances = AssetMaintenance.query.filter(
            AssetMaintenance.asset_id.in_(asset_ids),
            AssetMaintenance.status.in_(['planned', 'in_progress']),
            AssetMaintenance.next_maintenance_date.isnot(None),
            AssetMaintenance.next_maintenance_date.between(
                date.today() + timedelta(days=1),
                date.today() + timedelta(days=30)
            )
        ).order_by(AssetMaintenance.next_maintenance_date).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total_maintenance_cost': float(total_stats.total_cost) if total_stats and total_stats.total_cost else 0,
                'total_maintenance_count': total_stats.total_count or 0 if total_stats else 0,
                'overdue_count': len(overdue_maintenances),
                'upcoming_count': len(upcoming_maintenances),
                'overdue_maintenances': [maintenance.to_dict() for maintenance in overdue_maintenances],
                'upcoming_maintenances': [maintenance.to_dict() for maintenance in upcoming_maintenances]
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取维护概览失败: {str(e)}'}), 500

@maintenance_bp.route('/maintenance-calendar', methods=['GET'])
@jwt_required()
def get_maintenance_calendar():
    """获取维护日历"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取查询参数
        start_date_str = request.args.get('start_date', (date.today() - timedelta(days=30)).isoformat())
        end_date_str = request.args.get('end_date', (date.today() + timedelta(days=60)).isoformat())
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误'}), 400
        
        # 获取用户所有资产
        user_assets = FixedAsset.query.filter_by(user_id=current_user_id).all()
        asset_ids = [asset.id for asset in user_assets]
        
        if not asset_ids:
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {}
            })
        
        calendar_data = AssetMaintenance.get_maintenance_calendar(asset_ids, start_date, end_date)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': calendar_data
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取维护日历失败: {str(e)}'}), 500

# 维护提醒相关API
@maintenance_bp.route('/maintenance-reminders', methods=['GET'])
@jwt_required()
def get_maintenance_reminders():
    """获取维护提醒列表"""
    try:
        current_user_id = get_jwt_identity()
        
        reminders = MaintenanceReminder.query.filter_by(user_id=current_user_id).order_by(
            MaintenanceReminder.next_reminder_date
        ).all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [reminder.to_dict() for reminder in reminders]
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取提醒列表失败: {str(e)}'}), 500

@maintenance_bp.route('/maintenance-reminders', methods=['POST'])
@jwt_required()
def create_maintenance_reminder():
    """创建维护提醒"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['asset_id', 'name', 'interval_days', 'next_reminder_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'code': 400, 'message': f'缺少必填字段: {field}'}), 400
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=data['asset_id'], user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        # 转换日期
        try:
            next_reminder_date = datetime.strptime(data['next_reminder_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误'}), 400
        
        reminder = MaintenanceReminder(
            asset_id=data['asset_id'],
            user_id=current_user_id,
            reminder_type=data.get('reminder_type', 'custom'),
            name=data['name'],
            description=data.get('description', ''),
            interval_days=data['interval_days'],
            advance_days=data.get('advance_days', 7),
            next_reminder_date=next_reminder_date,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '提醒创建成功',
            'data': reminder.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建提醒失败: {str(e)}'}), 500

@maintenance_bp.route('/maintenance-reminders/due', methods=['GET'])
@jwt_required()
def get_due_reminders():
    """获取到期的提醒"""
    try:
        current_user_id = get_jwt_identity()
        
        due_reminders = MaintenanceReminder.get_due_reminders(current_user_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [reminder.to_dict() for reminder in due_reminders]
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取到期提醒失败: {str(e)}'}), 500