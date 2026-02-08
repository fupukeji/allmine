from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.fixed_asset import FixedAsset
from models.project import Project
from models.category import Category
from models.asset_income import AssetIncome
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
import uuid

assets_bp = Blueprint('assets', __name__)

@assets_bp.route('/assets/expiring', methods=['GET'])
@jwt_required()
def get_expiring_alerts():
    """获取快到期提醒（30天内）"""
    try:
        current_user_id = get_jwt_identity()
        today = datetime.now().date()
        alert_date = today + timedelta(days=30)
        
        alerts = []
        
        # 1. 检查固定资产到期（购买日期 + 使用年限）
        all_assets = FixedAsset.query.filter(
            FixedAsset.user_id == current_user_id,
            FixedAsset.purchase_date.isnot(None),
            FixedAsset.useful_life_years.isnot(None)
        ).all()
        
        for asset in all_assets:
            # 计算到期日期 = 购买日期 + 使用年限
            expiry_date = asset.purchase_date + timedelta(days=asset.useful_life_years * 365)
            
            # 判断是否在30天内到期
            if today <= expiry_date <= alert_date:
                days_left = (expiry_date - today).days
                alerts.append({
                    'id': asset.id,
                    'type': 'fixed_asset',
                    'name': asset.name,
                    'expiry_date': expiry_date.isoformat(),
                    'days_left': days_left,
                    'category': asset.category.name if asset.category else '未分类',
                    'purchase_price': float(asset.original_value) if asset.original_value else 0
                })
        
        # 2. 检查虚拟资产（项目）到期
        expiring_projects = Project.query.filter(
            Project.user_id == current_user_id,
            Project.end_time.isnot(None)
        ).all()
        
        for project in expiring_projects:
            project_end_date = project.end_time.date() if isinstance(project.end_time, datetime) else project.end_time
            
            # 判断是否在30天内到期
            if today <= project_end_date <= alert_date:
                days_left = (project_end_date - today).days
                alerts.append({
                    'id': project.id,
                    'type': 'project',
                    'name': project.name,
                    'expiry_date': project_end_date.isoformat(),
                    'days_left': days_left,
                    'category': project.category.name if project.category else '未分类',
                    'total_amount': float(project.total_amount) if project.total_amount else 0
                })
        
        # 按剩余天数排序
        alerts.sort(key=lambda x: x['days_left'])
        
        return jsonify({
            'code': 200,
            'data': alerts
        })
        
    except Exception as e:
        import traceback
        print(f'获取到期提醒失败: {str(e)}')
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500

@assets_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_assets():
    """获取固定资产列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取查询参数
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = FixedAsset.query.filter_by(user_id=current_user_id)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(
                db.or_(
                    FixedAsset.name.ilike(f'%{search}%'),
                    FixedAsset.asset_code.ilike(f'%{search}%'),
                    FixedAsset.description.ilike(f'%{search}%')
                )
            )
        
        # 排序和分页
        query = query.order_by(FixedAsset.created_at.desc())
        
        if per_page > 0:
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            assets = pagination.items
            total = pagination.total
        else:
            assets = query.all()
            total = len(assets)
        
        # 转换为字典
        assets_data = [asset.to_dict() for asset in assets]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': assets_data,
            'total': total,
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取固定资产列表失败: {str(e)}'
        }), 500

@assets_bp.route('/assets', methods=['POST'])
@jwt_required()
def create_asset():
    """创建固定资产"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'category_id', 'original_value', 'purchase_date', 
                          'useful_life_years', 'depreciation_start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 验证分类是否存在
        category = Category.query.filter_by(
            id=data['category_id'], 
            user_id=current_user_id
        ).first()
        if not category:
            return jsonify({
                'code': 400,
                'message': '分类不存在'
            }), 400
        
        # 生成资产编号
        if not data.get('asset_code'):
            data['asset_code'] = f"FA{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        
        # 检查资产编号是否重复
        existing_asset = FixedAsset.query.filter_by(asset_code=data['asset_code']).first()
        if existing_asset:
            return jsonify({
                'code': 400,
                'message': '资产编号已存在'
            }), 400
        
        # 转换日期字段
        try:
            purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
            depreciation_start_date = datetime.strptime(data['depreciation_start_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'code': 400,
                'message': '日期格式错误，请使用 YYYY-MM-DD 格式'
            }), 400
        
        # 创建固定资产
        asset = FixedAsset(
            asset_code=data['asset_code'],
            name=data['name'],
            description=data.get('description', ''),
            category_id=data['category_id'],
            original_value=data['original_value'],
            current_value=data['original_value'],  # 初始时当前价值等于原值
            residual_rate=data.get('residual_rate', 5.0),
            purchase_date=purchase_date,
            useful_life_years=data['useful_life_years'],
            depreciation_start_date=depreciation_start_date,
            depreciation_method=data.get('depreciation_method', 'straight_line'),
            status=data.get('status', 'in_use'),
            location=data.get('location', ''),
            responsible_person=data.get('responsible_person', ''),
            user_id=current_user_id
        )
        
        db.session.add(asset)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': asset.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建固定资产失败: {str(e)}'
        }), 500

@assets_bp.route('/assets/<int:asset_id>', methods=['GET'])
@jwt_required()
def get_asset(asset_id):
    """获取单个固定资产详情"""
    try:
        current_user_id = get_jwt_identity()
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        
        if not asset:
            return jsonify({
                'code': 404,
                'message': '固定资产不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': asset.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取固定资产详情失败: {str(e)}'
        }), 500

@assets_bp.route('/assets/<int:asset_id>', methods=['PUT'])
@jwt_required()
def update_asset(asset_id):
    """更新固定资产"""
    try:
        current_user_id = get_jwt_identity()
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        
        if not asset:
            return jsonify({
                'code': 404,
                'message': '固定资产不存在'
            }), 404
        
        data = request.get_json()
        
        # 验证分类是否存在（如果提供了category_id）
        if 'category_id' in data:
            category = Category.query.filter_by(
                id=data['category_id'], 
                user_id=current_user_id
            ).first()
            if not category:
                return jsonify({
                    'code': 400,
                    'message': '分类不存在'
                }), 400
        
        # 检查资产编号是否重复（如果修改了资产编号）
        if 'asset_code' in data and data['asset_code'] != asset.asset_code:
            existing_asset = FixedAsset.query.filter_by(asset_code=data['asset_code']).first()
            if existing_asset:
                return jsonify({
                    'code': 400,
                    'message': '资产编号已存在'
                }), 400
        
        # 更新字段
        updatable_fields = [
            'asset_code', 'name', 'description', 'category_id',
            'original_value', 'residual_rate', 'useful_life_years',
            'depreciation_method', 'status', 'location', 'responsible_person',
            'rent_price', 'rent_deposit', 'rent_due_day', 'tenant_name', 'tenant_phone',
            'sell_price', 'dispose_note'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(asset, field, data[field])
        
        # 处理日期字段
        date_fields = ['purchase_date', 'depreciation_start_date', 'dispose_date', 'rent_start_date', 'rent_end_date']
        for field in date_fields:
            if field in data and data[field]:
                try:
                    setattr(asset, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({
                        'code': 400,
                        'message': f'{field} 日期格式错误，请使用 YYYY-MM-DD 格式'
                    }), 400
        
        # 如果修改了影响折旧计算的字段，重新计算折旧数据
        if any(field in data for field in ['original_value', 'useful_life_years', 'residual_rate']):
            asset.calculate_depreciation_data()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': asset.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新固定资产失败: {str(e)}'
        }), 500

@assets_bp.route('/assets/<int:asset_id>', methods=['DELETE'])
@jwt_required()
def delete_asset(asset_id):
    """删除固定资产"""
    try:
        current_user_id = get_jwt_identity()
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        
        if not asset:
            return jsonify({
                'code': 404,
                'message': '固定资产不存在'
            }), 404
        
        db.session.delete(asset)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除固定资产失败: {str(e)}'
        }), 500

@assets_bp.route('/assets/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete_assets():
    """批量删除固定资产"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        asset_ids = data.get('asset_ids', [])
        
        if not asset_ids:
            return jsonify({
                'code': 400,
                'message': '请提供要删除的资产ID列表'
            }), 400
        
        # 查找要删除的资产
        assets = FixedAsset.query.filter(
            FixedAsset.id.in_(asset_ids),
            FixedAsset.user_id == current_user_id
        ).all()
        
        if len(assets) != len(asset_ids):
            return jsonify({
                'code': 400,
                'message': '部分资产不存在或无权限删除'
            }), 400
        
        # 批量删除
        for asset in assets:
            db.session.delete(asset)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': f'成功删除 {len(assets)} 个固定资产'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'批量删除固定资产失败: {str(e)}'
        }), 500

@assets_bp.route('/assets/<int:asset_id>/depreciation', methods=['GET'])
@jwt_required()
def get_asset_depreciation(asset_id):
    """获取固定资产折旧详情"""
    try:
        current_user_id = get_jwt_identity()
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        
        if not asset:
            return jsonify({
                'code': 404,
                'message': '固定资产不存在'
            }), 404
        
        # 获取基准日期参数
        base_date_str = request.args.get('base_date')
        base_date = None
        if base_date_str:
            try:
                base_date = datetime.strptime(base_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 400,
                    'message': '日期格式错误，请使用 YYYY-MM-DD 格式'
                }), 400
        
        depreciation_data = asset.calculate_current_depreciation(base_date)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'asset_info': asset.to_dict(include_calculations=False),
                'depreciation': depreciation_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取折旧详情失败: {str(e)}'
        }), 500

@assets_bp.route('/assets/statistics', methods=['GET'])
@jwt_required()
def get_assets_statistics():
    """获取固定资产统计信息"""
    try:
        current_user_id = get_jwt_identity()
        
        # 基本统计
        total_assets = FixedAsset.query.filter_by(user_id=current_user_id).count()
        
        # 按状态统计
        status_stats = db.session.query(
            FixedAsset.status,
            db.func.count(FixedAsset.id).label('count'),
            db.func.sum(FixedAsset.original_value).label('total_value')
        ).filter_by(user_id=current_user_id).group_by(FixedAsset.status).all()
        
        # 按分类统计
        category_stats = db.session.query(
            Category.name.label('category_name'),
            db.func.count(FixedAsset.id).label('count'),
            db.func.sum(FixedAsset.original_value).label('total_value')
        ).join(FixedAsset).filter(FixedAsset.user_id == current_user_id)\
         .group_by(Category.id, Category.name).all()
        
        # 计算总价值和当前价值
        assets = FixedAsset.query.filter_by(user_id=current_user_id).all()
        total_original_value = sum(float(asset.original_value) for asset in assets)
        total_current_value = sum(asset.calculate_current_depreciation()['current_value'] for asset in assets)
        total_accumulated_depreciation = total_original_value - total_current_value
        
        # 收益统计
        income_stats = db.session.query(
            func.count(AssetIncome.id).label('total_income_records'),
            func.sum(AssetIncome.amount).label('total_gross_income'),
            func.sum(AssetIncome.net_amount).label('total_net_income'),
            func.sum(AssetIncome.cost).label('total_costs'),
            func.sum(AssetIncome.tax_amount).label('total_taxes')
        ).join(FixedAsset).filter(
            FixedAsset.user_id == current_user_id,
            AssetIncome.status == 'received'
        ).first()
        
        # 按收入类型统计
        income_type_stats = db.session.query(
            AssetIncome.income_type,
            func.count(AssetIncome.id).label('count'),
            func.sum(AssetIncome.net_amount).label('total_amount')
        ).join(FixedAsset).filter(
            FixedAsset.user_id == current_user_id,
            AssetIncome.status == 'received'
        ).group_by(AssetIncome.income_type).all()
        
        # ROI 分析 - 按资产计算
        roi_data = []
        for asset in assets:
            asset_income = AssetIncome.get_asset_total_income(asset.id)
            if asset_income['total_income'] > 0:
                roi = (asset_income['total_income'] / float(asset.original_value)) * 100
                roi_data.append({
                    'asset_id': asset.id,
                    'asset_name': asset.name,
                    'original_value': float(asset.original_value),
                    'total_income': asset_income['total_income'],
                    'roi': round(roi, 2),
                    'income_count': asset_income['income_count']
                })
        
        # 月度收益趋势
        monthly_income_trend = db.session.query(
            extract('year', AssetIncome.income_date).label('year'),
            extract('month', AssetIncome.income_date).label('month'),
            func.sum(AssetIncome.net_amount).label('total_amount'),
            func.count(AssetIncome.id).label('count')
        ).join(FixedAsset).filter(
            FixedAsset.user_id == current_user_id,
            AssetIncome.status == 'received',
            AssetIncome.income_date >= (datetime.now().replace(day=1, month=1) - timedelta(days=365)).date()
        ).group_by(
            extract('year', AssetIncome.income_date),
            extract('month', AssetIncome.income_date)
        ).order_by('year', 'month').all()
        
        # 即将完全折旧的资产（剩余月数小于12个月）
        expiring_assets = []
        for asset in assets:
            depreciation_data = asset.calculate_current_depreciation()
            if depreciation_data['remaining_life_months'] <= 12 and not depreciation_data['is_fully_depreciated']:
                expiring_assets.append({
                    'id': asset.id,
                    'name': asset.name,
                    'asset_code': asset.asset_code,
                    'remaining_months': depreciation_data['remaining_life_months']
                })
        
        # 顶级收益资产
        top_earning_assets = sorted(roi_data, key=lambda x: x['roi'], reverse=True)[:5]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'overview': {
                    'total_assets': total_assets,
                    'total_original_value': round(total_original_value, 2),
                    'total_current_value': round(total_current_value, 2),
                    'total_accumulated_depreciation': round(total_accumulated_depreciation, 2),
                    'depreciation_rate': round((total_accumulated_depreciation / total_original_value * 100) if total_original_value > 0 else 0, 2)
                },
                'income_overview': {
                    'total_income_records': income_stats.total_income_records if income_stats else 0,
                    'total_gross_income': float(income_stats.total_gross_income) if income_stats and income_stats.total_gross_income else 0,
                    'total_net_income': float(income_stats.total_net_income) if income_stats and income_stats.total_net_income else 0,
                    'total_costs': float(income_stats.total_costs) if income_stats and income_stats.total_costs else 0,
                    'total_taxes': float(income_stats.total_taxes) if income_stats and income_stats.total_taxes else 0,
                    'overall_roi': round((float(income_stats.total_net_income) / total_original_value * 100) if income_stats and income_stats.total_net_income and total_original_value > 0 else 0, 2)
                },
                'status_distribution': [
                    {
                        'status': item.status,
                        'count': item.count,
                        'total_value': float(item.total_value) if item.total_value else 0
                    } for item in status_stats
                ],
                'category_distribution': [
                    {
                        'category_name': item.category_name,
                        'count': item.count,
                        'total_value': float(item.total_value) if item.total_value else 0
                    } for item in category_stats
                ],
                'income_type_distribution': [
                    {
                        'income_type': item.income_type,
                        'income_type_text': AssetIncome.get_income_type_text_static(item.income_type),
                        'count': item.count,
                        'total_amount': float(item.total_amount) if item.total_amount else 0
                    } for item in income_type_stats
                ],
                'monthly_income_trend': [
                    {
                        'period': f"{int(item.year)}-{int(item.month):02d}",
                        'amount': float(item.total_amount) if item.total_amount else 0,
                        'count': item.count
                    } for item in monthly_income_trend
                ],
                'roi_analysis': roi_data,
                'top_earning_assets': top_earning_assets,
                'expiring_assets': expiring_assets
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500