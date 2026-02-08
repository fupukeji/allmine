from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.project import Project
from models.fixed_asset import FixedAsset
from models.category import Category
from database import db
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta

analytics_bp = Blueprint('analytics', __name__)

def get_current_user():
    """获取当前用户"""
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """获取首页Dashboard统计数据"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 统计虚拟资产（项目）
        projects = Project.query.filter_by(user_id=user.id).all()
        project_count = len(projects)
        virtual_asset_value = sum(float(p.total_amount) for p in projects)
        
        # 统计固定资产
        assets = FixedAsset.query.filter_by(user_id=user.id).all()
        asset_count = len(assets)
        fixed_asset_value = sum(float(a.original_value) for a in assets if a.original_value)
        
        # 总资产价值
        total_value = virtual_asset_value + fixed_asset_value

        return jsonify({
            'code': 200,
            'data': {
                'total_value': round(total_value, 2),
                'virtual_asset_value': round(virtual_asset_value, 2),
                'fixed_asset_value': round(fixed_asset_value, 2),
                'project_count': project_count,
                'asset_count': asset_count
            }
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取Dashboard数据失败：{str(e)}'}), 500

@analytics_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """获取概览统计数据"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 基础统计
        projects = Project.query.filter_by(user_id=user.id).all()
        
        total_projects = len(projects)
        total_amount = sum(float(p.total_amount) for p in projects)
        
        # 计算实时数据
        current_time = datetime.utcnow()
        total_used_cost = 0
        total_remaining_value = 0
        status_counts = {'not_started': 0, 'active': 0, 'expired': 0}
        
        for project in projects:
            values = project.calculate_values(current_time)
            total_used_cost += values['used_cost']
            total_remaining_value += values['remaining_value']
            status_counts[values['status']] += 1
        
        # 分类统计
        category_stats = {}
        for project in projects:
            if not project.category:
                continue
            cat_name = project.category.name
            if cat_name not in category_stats:
                category_stats[cat_name] = {
                    'count': 0,
                    'total_amount': 0,
                    'used_cost': 0,
                    'remaining_value': 0
                }
            
            values = project.calculate_values(current_time)
            category_stats[cat_name]['count'] += 1
            category_stats[cat_name]['total_amount'] += float(project.total_amount)
            category_stats[cat_name]['used_cost'] += values['used_cost']
            category_stats[cat_name]['remaining_value'] += values['remaining_value']

        return jsonify({
            'code': 200,
            'data': {
                'total_projects': total_projects,
                'total_amount': round(total_amount, 2),
                'total_used_cost': round(total_used_cost, 2),
                'total_remaining_value': round(total_remaining_value, 2),
                'status_distribution': status_counts,
                'category_stats': category_stats
            }
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取概览数据失败：{str(e)}'}), 500

@analytics_bp.route('/analytics/trends', methods=['GET'])
@jwt_required()
def get_trends():
    """获取趋势分析数据"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 获取查询参数
        period = request.args.get('period', 'month')  # day, week, month, year
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 设置默认时间范围
        if not start_date or not end_date:
            end_time = datetime.utcnow()
            if period == 'day':
                start_time = end_time - timedelta(days=30)
            elif period == 'week':
                start_time = end_time - timedelta(weeks=12)
            elif period == 'month':
                start_time = end_time - timedelta(days=365)
            else:  # year
                start_time = end_time - timedelta(days=365*3)
        else:
            try:
                start_time = datetime.fromisoformat(start_date)
                end_time = datetime.fromisoformat(end_date)
            except ValueError as ve:
                # 尝试其他日期格式
                try:
                    start_time = datetime.strptime(start_date, '%Y-%m-%d')
                    end_time = datetime.strptime(end_date, '%Y-%m-%d')
                except Exception:
                    return jsonify({'code': 400, 'message': '日期格式错误'}), 400

        # 获取期间内的项目
        projects = Project.query.filter(
            and_(
                Project.user_id == user.id,
                or_(
                    Project.created_at.between(start_time, end_time),
                    Project.start_time.between(start_time, end_time)
                )
            )
        ).all()

        # 按时间段统计
        trends_data = []
        current = start_time
        max_iterations = 1000  # 防止无限循环
        iteration_count = 0
        
        while current <= end_time and iteration_count < max_iterations:
            iteration_count += 1
            
            if period == 'day':
                next_period = current + timedelta(days=1)
                period_label = current.strftime('%Y-%m-%d')
            elif period == 'week':
                next_period = current + timedelta(weeks=1)
                period_label = f"{current.strftime('%Y-%m-%d')} 周"
            elif period == 'month':
                # 使用relativedelta安全地处理月份增加
                next_period = current + relativedelta(months=1)
                period_label = current.strftime('%Y-%m')
            else:  # year
                # 使用relativedelta安全地处理年份增加
                next_period = current + relativedelta(years=1)
                period_label = current.strftime('%Y')

            # 统计该时间段的数据
            period_projects = [p for p in projects if current <= p.created_at < next_period]
            period_amount = sum(float(p.total_amount) for p in period_projects)
            period_count = len(period_projects)

            trends_data.append({
                'period': period_label,
                'projects_count': period_count,
                'total_amount': round(period_amount, 2),
                'timestamp': current.isoformat()
            })

            current = next_period

        return jsonify({
            'code': 200,
            'data': {
                'period': period,
                'trends': trends_data
            }
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取趋势数据失败：{str(e)}'}), 500

@analytics_bp.route('/analytics/category-analysis', methods=['GET'])
@jwt_required()
def get_category_analysis():
    """获取分类分析数据"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 获取所有分类及其项目
        categories = Category.query.filter_by(user_id=user.id).all()
        current_time = datetime.utcnow()
        
        category_analysis = []
        
        for category in categories:
            projects = category.projects
            
            if not projects:
                continue
            
            total_amount = sum(float(p.total_amount) for p in projects)
            total_used_cost = 0
            total_remaining_value = 0
            active_count = 0
            expired_count = 0
            not_started_count = 0
            
            for project in projects:
                values = project.calculate_values(current_time)
                total_used_cost += values['used_cost']
                total_remaining_value += values['remaining_value']
                
                if values['status'] == 'active':
                    active_count += 1
                elif values['status'] == 'expired':
                    expired_count += 1
                else:
                    not_started_count += 1
            
            category_analysis.append({
                'category_id': category.id,
                'category_name': category.name,
                'category_color': category.color,
                'project_count': len(projects),
                'total_amount': round(total_amount, 2),
                'used_cost': round(total_used_cost, 2),
                'remaining_value': round(total_remaining_value, 2),
                'utilization_rate': round((total_used_cost / total_amount * 100) if total_amount > 0 else 0, 2),
                'status_breakdown': {
                    'active': active_count,
                    'expired': expired_count,
                    'not_started': not_started_count
                }
            })
        
        # 按总金额排序
        category_analysis.sort(key=lambda x: x['total_amount'], reverse=True)

        return jsonify({
            'code': 200,
            'data': category_analysis
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取分类分析失败：{str(e)}'}), 500

@analytics_bp.route('/analytics/project-details', methods=['GET'])
@jwt_required()
def get_project_details():
    """获取项目明细数据（支持筛选）"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404

        # 获取查询参数
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 构建查询
        query = Project.query.filter_by(user_id=user.id)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 获取所有项目用于状态过滤
        all_projects = query.all()
        current_time = datetime.utcnow()
        
        # 按状态过滤
        if status:
            filtered_projects = []
            for project in all_projects:
                project_status = project.calculate_values(current_time)['status']
                if project_status == status:
                    filtered_projects.append(project)
            projects = filtered_projects
        else:
            projects = all_projects
        
        # 排序
        if sort_by == 'total_amount':
            projects.sort(key=lambda x: float(x.total_amount), reverse=(order == 'desc'))
        elif sort_by == 'used_cost':
            projects.sort(key=lambda x: x.calculate_values(current_time)['used_cost'], reverse=(order == 'desc'))
        elif sort_by == 'remaining_value':
            projects.sort(key=lambda x: x.calculate_values(current_time)['remaining_value'], reverse=(order == 'desc'))
        elif sort_by == 'progress':
            projects.sort(key=lambda x: x.calculate_values(current_time)['progress'], reverse=(order == 'desc'))
        else:  # created_at
            projects.sort(key=lambda x: x.created_at, reverse=(order == 'desc'))
        
        # 分页
        total = len(projects)
        start = (page - 1) * per_page
        end = start + per_page
        projects_page = projects[start:end]
        
        # 转换为字典
        project_details = []
        for project in projects_page:
            data = project.to_dict(include_calculations=True, base_time=current_time)
            project_details.append(data)

        return jsonify({
            'code': 200,
            'data': project_details,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取项目明细失败：{str(e)}'}), 500