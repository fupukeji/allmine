"""
资产费用管理路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.asset_expense import AssetExpense
from models.fixed_asset import FixedAsset
from datetime import datetime, date

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/assets/<int:asset_id>/expenses', methods=['GET'])
@jwt_required()
def get_expenses(asset_id):
    """获取资产的费用列表"""
    try:
        user_id = int(get_jwt_identity())
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        # 获取费用列表
        expenses = AssetExpense.query.filter_by(
            asset_id=asset_id, 
            user_id=user_id
        ).order_by(AssetExpense.expense_date.desc()).all()
        
        # 计算费用统计
        total_amount = sum(float(e.amount) for e in expenses)
        
        return jsonify({
            'code': 200,
            'data': {
                'items': [e.to_dict() for e in expenses],
                'total': len(expenses),
                'total_amount': round(total_amount, 2)
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取费用列表失败: {str(e)}'}), 500


@expenses_bp.route('/assets/<int:asset_id>/expenses', methods=['POST'])
@jwt_required()
def create_expense(asset_id):
    """添加费用记录"""
    try:
        user_id = int(get_jwt_identity())
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        data = request.get_json()
        
        # 解析日期
        expense_date = data.get('expense_date')
        if expense_date:
            expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
        else:
            expense_date = date.today()
        
        next_due_date = data.get('next_due_date')
        if next_due_date:
            next_due_date = datetime.strptime(next_due_date, '%Y-%m-%d').date()
        
        expense = AssetExpense(
            asset_id=asset_id,
            user_id=user_id,
            expense_type=data.get('expense_type', 'other'),
            expense_name=data.get('expense_name', ''),
            amount=data.get('amount', 0),
            expense_date=expense_date,
            is_recurring=data.get('is_recurring', False),
            recurring_period=data.get('recurring_period'),
            next_due_date=next_due_date,
            description=data.get('description')
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '费用添加成功',
            'data': expense.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'添加费用失败: {str(e)}'}), 500


@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """更新费用记录"""
    try:
        user_id = int(get_jwt_identity())
        
        expense = AssetExpense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            return jsonify({'code': 404, 'message': '费用记录不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'expense_type' in data:
            expense.expense_type = data['expense_type']
        if 'expense_name' in data:
            expense.expense_name = data['expense_name']
        if 'amount' in data:
            expense.amount = data['amount']
        if 'expense_date' in data:
            expense.expense_date = datetime.strptime(data['expense_date'], '%Y-%m-%d').date()
        if 'is_recurring' in data:
            expense.is_recurring = data['is_recurring']
        if 'recurring_period' in data:
            expense.recurring_period = data['recurring_period']
        if 'next_due_date' in data and data['next_due_date']:
            expense.next_due_date = datetime.strptime(data['next_due_date'], '%Y-%m-%d').date()
        if 'description' in data:
            expense.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '费用更新成功',
            'data': expense.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新费用失败: {str(e)}'}), 500


@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """删除费用记录"""
    try:
        user_id = int(get_jwt_identity())
        
        expense = AssetExpense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            return jsonify({'code': 404, 'message': '费用记录不存在'}), 404
        
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'code': 200, 'message': '费用删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除费用失败: {str(e)}'}), 500


@expenses_bp.route('/expense-types', methods=['GET'])
@jwt_required()
def get_expense_types():
    """获取费用类型列表"""
    try:
        category_name = request.args.get('category')
        expense_types = AssetExpense.get_expense_types(category_name)
        
        return jsonify({
            'code': 200,
            'data': expense_types
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取费用类型失败: {str(e)}'}), 500


@expenses_bp.route('/assets/<int:asset_id>/expenses/summary', methods=['GET'])
@jwt_required()
def get_expense_summary(asset_id):
    """获取资产费用统计摘要"""
    try:
        user_id = int(get_jwt_identity())
        
        # 验证资产所有权
        asset = FixedAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not asset:
            return jsonify({'code': 404, 'message': '资产不存在'}), 404
        
        expenses = AssetExpense.query.filter_by(asset_id=asset_id, user_id=user_id).all()
        
        # 按类型统计
        type_summary = {}
        for e in expenses:
            if e.expense_type not in type_summary:
                type_summary[e.expense_type] = 0
            type_summary[e.expense_type] += float(e.amount)
        
        # 按年统计
        year_summary = {}
        for e in expenses:
            year = e.expense_date.year
            if year not in year_summary:
                year_summary[year] = 0
            year_summary[year] += float(e.amount)
        
        return jsonify({
            'code': 200,
            'data': {
                'total_amount': sum(float(e.amount) for e in expenses),
                'total_count': len(expenses),
                'by_type': type_summary,
                'by_year': year_summary
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取费用统计失败: {str(e)}'}), 500
