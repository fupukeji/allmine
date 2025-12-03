from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.asset_income import AssetIncome
from models.fixed_asset import FixedAsset
from datetime import datetime, date
from sqlalchemy import func, extract, and_

asset_income_bp = Blueprint('asset_income', __name__)

@asset_income_bp.route('/assets/<int:asset_id>/incomes', methods=['GET'])
@jwt_required()
def get_asset_incomes(asset_id):
    """获取资产收入列表"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        income_type = request.args.get('income_type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = AssetIncome.query.filter_by(asset_id=asset_id)
        
        if income_type:
            query = query.filter_by(income_type=income_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date:
            query = query.filter(AssetIncome.income_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(AssetIncome.income_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        # 排序和分页
        query = query.order_by(AssetIncome.income_date.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        incomes_data = [income.to_dict() for income in pagination.items]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': incomes_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取收入列表失败: {str(e)}'}), 500

@asset_income_bp.route('/assets/<int:asset_id>/incomes', methods=['POST'])
@jwt_required()
def create_asset_income(asset_id):
    """创建资产收入记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['income_type', 'amount', 'income_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'code': 400, 'message': f'缺少必填字段: {field}'}), 400
        
        # 转换日期字段
        try:
            income_date = datetime.strptime(data['income_date'], '%Y-%m-%d').date()
            expected_date = None
            actual_date = None
            recurring_end_date = None
            
            if data.get('expected_date'):
                expected_date = datetime.strptime(data['expected_date'], '%Y-%m-%d').date()
            if data.get('actual_date'):
                actual_date = datetime.strptime(data['actual_date'], '%Y-%m-%d').date()
            if data.get('recurring_end_date'):
                recurring_end_date = datetime.strptime(data['recurring_end_date'], '%Y-%m-%d').date()
        except ValueError as e:
            return jsonify({'code': 400, 'message': f'日期格式错误，请使用 YYYY-MM-DD 格式: {str(e)}'}), 400
        
        # 创建收入记录
        income = AssetIncome(
            asset_id=asset_id,
            income_type=data['income_type'],
            amount=data['amount'],
            expected_amount=data.get('expected_amount'),
            cost=data.get('cost', 0),
            tax_rate=data.get('tax_rate', 0),
            income_date=income_date,
            expected_date=expected_date,
            actual_date=actual_date,
            description=data.get('description', ''),
            notes=data.get('notes', ''),
            payer=data.get('payer', ''),
            payment_method=data.get('payment_method', 'bank_transfer'),
            contract_reference=data.get('contract_reference', ''),
            invoice_number=data.get('invoice_number', ''),
            is_recurring=data.get('is_recurring', False),
            recurring_frequency=data.get('recurring_frequency'),
            recurring_end_date=recurring_end_date,
            status=data.get('status', 'pending')
        )
        
        db.session.add(income)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '收入记录创建成功',
            'data': income.to_dict()
        }), 200  # 改为200状态码
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f'创建收入记录失败: {str(e)}')
        print(error_detail)
        return jsonify({'code': 500, 'message': f'创建收入记录失败: {str(e)}'}), 500

@asset_income_bp.route('/assets/<int:asset_id>/incomes/<int:income_id>', methods=['PUT'])
@jwt_required()
def update_asset_income(asset_id, income_id):
    """更新资产收入记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        income = AssetIncome.query.filter_by(id=income_id, asset_id=asset_id).first()
        if not income:
            return jsonify({'code': 404, 'message': '收入记录不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        updatable_fields = [
            'income_type', 'amount', 'expected_amount', 'description',
            'payer', 'contract_reference', 'is_recurring', 'recurring_period',
            'tax_amount', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(income, field, data[field])
        
        # 处理日期字段
        if 'income_date' in data:
            try:
                income.income_date = datetime.strptime(data['income_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'code': 400, 'message': '收入日期格式错误'}), 400
        
        if 'recurring_end_date' in data and data['recurring_end_date']:
            try:
                income.recurring_end_date = datetime.strptime(data['recurring_end_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'code': 400, 'message': '循环结束日期格式错误'}), 400
        
        # 重新计算净收入
        if income.amount and income.tax_amount:
            income.net_amount = income.amount - income.tax_amount
        elif income.amount:
            income.net_amount = income.amount
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '收入记录更新成功',
            'data': income.to_dict()
        }), 200  # 确保返回200状态码
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新收入记录失败: {str(e)}'}), 500

@asset_income_bp.route('/assets/<int:asset_id>/incomes/<int:income_id>', methods=['DELETE'])
@jwt_required()
def delete_asset_income(asset_id, income_id):
    """删除资产收入记录"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        income = AssetIncome.query.filter_by(id=income_id, asset_id=asset_id).first()
        if not income:
            return jsonify({'code': 404, 'message': '收入记录不存在'}), 404
        
        db.session.delete(income)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '收入记录删除成功'}), 200  # 确保返回200状态码
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除收入记录失败: {str(e)}'}), 500

@asset_income_bp.route('/assets/<int:asset_id>/income-analysis', methods=['GET'])
@jwt_required()
def get_asset_income_analysis(asset_id):
    """获取资产收入分析"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=current_user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        # 总收入统计
        total_stats = AssetIncome.get_asset_total_income(asset_id)
        
        # 按类型统计
        type_stats = AssetIncome.get_income_by_type(asset_id)
        
        # 月度收入趋势
        monthly_trend = AssetIncome.get_monthly_income_trend(asset_id)
        
        # 预期vs实际分析
        variance_query = db.session.query(
            func.sum(AssetIncome.amount).label('actual_total'),
            func.sum(AssetIncome.expected_amount).label('expected_total'),
            func.count(AssetIncome.id).label('total_records')
        ).filter_by(asset_id=asset_id, status='received').first()
        
        variance_analysis = {
            'actual_total': float(variance_query.actual_total) if variance_query and variance_query.actual_total else 0,
            'expected_total': float(variance_query.expected_total) if variance_query and variance_query.expected_total else 0,
            'total_records': variance_query.total_records if variance_query else 0
        }
        
        if variance_analysis['expected_total'] > 0:
            variance = variance_analysis['actual_total'] - variance_analysis['expected_total']
            variance_analysis['variance'] = variance
            variance_analysis['variance_rate'] = (variance / variance_analysis['expected_total']) * 100
        else:
            variance_analysis['variance'] = 0
            variance_analysis['variance_rate'] = 0
        
        # ROI计算
        roi_analysis = calculate_asset_roi(asset, total_stats['total_income'])
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total_stats': total_stats,
                'type_distribution': type_stats,
                'monthly_trend': monthly_trend,
                'variance_analysis': variance_analysis,
                'roi_analysis': roi_analysis
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取收入分析失败: {str(e)}'}), 500

def calculate_asset_roi(asset, total_income):
    """计算资产投资回报率"""
    try:
        original_value = float(asset.original_value)
        if original_value <= 0:
            return None
        
        # 计算ROI
        roi = (total_income / original_value) * 100
        
        # 计算年化收益率
        from datetime import datetime
        purchase_date = asset.purchase_date
        if purchase_date:
            days_held = (datetime.now().date() - purchase_date).days
            years_held = days_held / 365.25
            if years_held > 0:
                annual_return = (total_income / original_value / years_held) * 100
            else:
                annual_return = 0
        else:
            annual_return = 0
        
        # 回本周期（假设按当前月平均收入计算）
        monthly_avg = total_income / max(1, len(AssetIncome.get_monthly_income_trend(asset.id, 12)))
        if monthly_avg > 0:
            payback_months = original_value / monthly_avg
        else:
            payback_months = 0
        
        return {
            'roi': round(roi, 2),
            'annual_return': round(annual_return, 2),
            'payback_months': round(payback_months, 1),
            'total_income': total_income,
            'original_value': original_value
        }
        
    except Exception as e:
        print(f"ROI计算错误: {e}")
        return None

@asset_income_bp.route('/income-overview', methods=['GET'])
@jwt_required()
def get_income_overview():
    """获取用户所有资产收入概览"""
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
                    'total_income': 0,
                    'asset_count': 0,
                    'income_count': 0,
                    'monthly_trend': [],
                    'type_distribution': []
                }
            })
        
        # 总收入统计
        total_query = db.session.query(
            func.sum(AssetIncome.net_amount).label('total_income'),
            func.count(AssetIncome.id).label('income_count')
        ).filter(AssetIncome.asset_id.in_(asset_ids), AssetIncome.status == 'received').first()
        
        # 按类型统计
        type_stats = db.session.query(
            AssetIncome.income_type,
            func.sum(AssetIncome.net_amount).label('total_amount'),
            func.count(AssetIncome.id).label('count')
        ).filter(
            AssetIncome.asset_id.in_(asset_ids),
            AssetIncome.status == 'received'
        ).group_by(AssetIncome.income_type).all()
        
        # 月度趋势
        monthly_stats = db.session.query(
            extract('year', AssetIncome.income_date).label('year'),
            extract('month', AssetIncome.income_date).label('month'),
            func.sum(AssetIncome.net_amount).label('total_amount')
        ).filter(
            AssetIncome.asset_id.in_(asset_ids),
            AssetIncome.status == 'received'
        ).group_by(
            extract('year', AssetIncome.income_date),
            extract('month', AssetIncome.income_date)
        ).order_by('year', 'month').all()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total_income': float(total_query.total_income) if total_query.total_income else 0,
                'asset_count': len(user_assets),
                'income_count': total_query.income_count or 0,
                'monthly_trend': [
                    {
                        'period': f"{int(stat.year)}-{int(stat.month):02d}",
                        'amount': float(stat.total_amount) if stat.total_amount else 0
                    }
                    for stat in monthly_stats
                ],
                'type_distribution': [
                    {
                        'income_type': stat.income_type,
                        'income_type_text': AssetIncome.get_income_type_text_static(stat.income_type),
                        'total_amount': float(stat.total_amount) if stat.total_amount else 0,
                        'count': stat.count or 0
                    }
                    for stat in type_stats
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取收入概览失败: {str(e)}'}), 500