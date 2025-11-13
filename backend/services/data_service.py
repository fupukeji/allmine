"""
资产数据查询服务
负责从数据库查询和统计资产数据
"""

from datetime import datetime, timedelta
from models.fixed_asset import FixedAsset
from models.asset_income import AssetIncome
from models.category import Category
from models.project import Project


class AssetDataService:
    """资产数据查询服务类"""
    
    @staticmethod
    def query_asset_data(user_id, start_date, end_date):
        """
        查询用户资产数据(固定资产 + 虚拟资产)
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 包含固定资产、虚拟资产和综合数据的字典
        """
        print(f"[数据查询] 开始查询资产数据: {start_date} 至 {end_date}")
        
        # 查询固定资产数据
        fixed_assets_data = AssetDataService._query_fixed_assets(user_id, start_date, end_date)
        
        # 查询虚拟资产数据
        virtual_assets_data = AssetDataService._query_virtual_assets(user_id, start_date, end_date)
        
        # 计算综合指标
        comprehensive_data = AssetDataService._calculate_comprehensive_data(
            fixed_assets_data, 
            virtual_assets_data
        )
        
        print(f"[数据查询] 完成 - 固定资产:{fixed_assets_data['total_assets']}项, "
              f"虚拟资产:{virtual_assets_data['total_projects']}项")
        
        return {
            'fixed_assets': fixed_assets_data,
            'virtual_assets': virtual_assets_data,
            'comprehensive': comprehensive_data,
            'period': {
                'start_date': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
                'end_date': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
                'days': (end_date - start_date).days + 1
            }
        }
    
    @staticmethod
    def _query_fixed_assets(user_id, start_date, end_date):
        """查询固定资产数据"""
        # 获取固定资产(排除已处置,且在报告期结束前购买的)
        assets = FixedAsset.query.filter(
            FixedAsset.user_id == user_id,
            FixedAsset.status != 'disposed',
            FixedAsset.purchase_date <= end_date
        ).all()
        
        # 获取时间范围内的收入数据
        incomes = AssetIncome.query.join(FixedAsset).filter(
            FixedAsset.user_id == user_id,
            AssetIncome.income_date >= start_date,
            AssetIncome.income_date <= end_date
        ).all()
        
        # 获取分类信息
        categories = Category.query.filter_by(user_id=user_id).all()
        
        # 统计数据
        total_assets = len(assets)
        total_original_value = sum(
            float(asset.original_value) for asset in assets 
            if asset.original_value is not None
        )
        total_current_value = sum(
            float(asset.current_value) for asset in assets 
            if asset.current_value is not None
        )
        total_income = sum(
            float(income.amount) for income in incomes 
            if income.amount is not None
        )
        
        # 按分类统计
        category_stats = {}
        for category in categories:
            cat_assets = [a for a in assets if a.category_id == category.id]
            if cat_assets:
                category_stats[category.name] = {
                    'count': len(cat_assets),
                    'total_value': sum(
                        float(a.current_value) for a in cat_assets 
                        if a.current_value is not None
                    ),
                    'original_value': sum(
                        float(a.original_value) for a in cat_assets 
                        if a.original_value is not None
                    )
                }
        
        # 按状态统计
        status_stats = {}
        for asset in assets:
            status = asset.get_status_text()
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
        
        # 按分类统计收入
        income_by_category = {}
        for income in incomes:
            if income.asset and income.asset.category:
                cat_name = income.asset.category.name
                if cat_name not in income_by_category:
                    income_by_category[cat_name] = 0
                income_by_category[cat_name] += float(income.amount)
        
        return {
            'total_assets': total_assets,
            'total_original_value': round(total_original_value, 2),
            'total_current_value': round(total_current_value, 2),
            'total_depreciation': round(total_original_value - total_current_value, 2),
            'total_income': round(total_income, 2),
            'depreciation_rate': round(
                (total_original_value - total_current_value) / total_original_value * 100, 2
            ) if total_original_value > 0 else 0,
            'category_stats': category_stats,
            'status_stats': status_stats,
            'income_by_category': income_by_category
        }
    
    @staticmethod
    def _query_virtual_assets(user_id, start_date, end_date):
        """查询虚拟资产(预付权益)数据"""
        # 获取与报告期相关的虚拟资产项目(有时间交集的)
        projects = Project.query.filter(
            Project.user_id == user_id,
            Project.start_time <= end_date,  # 开始时间不晚于报告期结束
            Project.end_time >= start_date   # 结束时间不早于报告期开始
        ).all()
        
        # 过滤掉数据异常的项目
        valid_projects = [
            p for p in projects 
            if p.total_amount is not None and p.end_time >= p.start_time
        ]
        
        if len(projects) != len(valid_projects):
            print(f"[数据警告] 过滤掉 {len(projects) - len(valid_projects)} 个异常项目")
        
        # 获取分类信息
        categories = Category.query.filter_by(user_id=user_id).all()
        
        # 统计数据
        total_projects = len(valid_projects)
        total_project_amount = sum(float(p.total_amount) for p in valid_projects)
        
        # 按状态分类
        active_projects = []      # 消耗中
        expired_projects = []     # 已过期
        not_started_projects = [] # 未开始
        
        total_used_value = 0          # 已消耗总价值
        total_remaining_value = 0     # 剩余总价值(仅活跃项目)
        total_wasted_value = 0        # 浪费总价值(过期未用完)
        not_started_value = 0         # 未开始项目价值(单独统计)
        
        now = datetime.utcnow()
        for project in valid_projects:
            status = project.get_status()
            values = project.calculate_values()
            
            if status == 'active':
                active_projects.append(project)
                total_used_value += values['used_cost']
                total_remaining_value += values['remaining_value']
            elif status == 'expired':
                expired_projects.append(project)
                total_used_value += values['used_cost']
                total_wasted_value += values['remaining_value']
            else:  # not_started
                not_started_projects.append(project)
                not_started_value += float(project.total_amount)
        
        # 即将过期的项目(7天内)
        expiring_soon = []
        for project in active_projects:
            days_left = (project.end_time - now).days
            if 0 <= days_left <= 7:
                expiring_soon.append({
                    'name': project.name,
                    'days_left': days_left,
                    'remaining_value': project.calculate_values()['remaining_value']
                })
        
        # 按分类统计虚拟资产
        project_category_stats = {}
        for category in categories:
            cat_projects = [p for p in valid_projects if p.category_id == category.id]
            if cat_projects:
                cat_total = sum(float(p.total_amount) for p in cat_projects)
                cat_wasted = 0
                for p in cat_projects:
                    if p.get_status() == 'expired':
                        cat_wasted += p.calculate_values()['remaining_value']
                
                project_category_stats[category.name] = {
                    'count': len(cat_projects),
                    'total_amount': cat_total,
                    'wasted_value': cat_wasted
                }
        
        # 虚拟资产利用率(仅计算已开始的项目)
        started_amount = sum(
            float(p.total_amount) for p in (active_projects + expired_projects)
        )
        utilization_rate = (
            (total_used_value / started_amount * 100) 
            if started_amount > 0 else 0
        )
        
        # 浪费率(基于已开始的项目)
        waste_rate = (
            (total_wasted_value / started_amount * 100) 
            if started_amount > 0 else 0
        )
        
        return {
            'total_projects': total_projects,
            'total_amount': round(total_project_amount, 2),
            'active_count': len(active_projects),
            'expired_count': len(expired_projects),
            'not_started_count': len(not_started_projects),
            'total_used_value': round(total_used_value, 2),
            'total_remaining_value': round(total_remaining_value, 2),
            'total_wasted_value': round(total_wasted_value, 2),
            'not_started_value': round(not_started_value, 2),
            'utilization_rate': round(utilization_rate, 2),
            'waste_rate': round(waste_rate, 2),
            'expiring_soon': expiring_soon,
            'category_stats': project_category_stats
        }
    
    @staticmethod
    def _calculate_comprehensive_data(fixed_assets_data, virtual_assets_data):
        """计算综合数据"""
        tangible_value = fixed_assets_data['total_current_value']
        active_rights_value = virtual_assets_data['total_remaining_value']
        not_started_value = virtual_assets_data['not_started_value']
        
        return {
            'tangible_assets_value': tangible_value,
            'active_rights_value': active_rights_value,
            'not_started_rights_value': not_started_value,
            'combined_active_value': round(tangible_value + active_rights_value, 2),
            'total_value': round(tangible_value + active_rights_value + not_started_value, 2),
            'note': '有形资产+活跃权益=当前活跃价值,未开始项目单独统计'
        }
    
    @staticmethod
    def query_previous_period_data(user_id, start_date, end_date):
        """
        获取上一期的数据(同等时长)
        
        Args:
            user_id: 用户ID
            start_date: 当前期开始日期
            end_date: 当前期结束日期
        
        Returns:
            dict or None: 上期数据或None
        """
        # 计算时间跨度
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        period_length = (end_date - start_date).days
        
        # 计算上期时间范围
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_length)
        
        print(f"[上期查询] 计算上期时间: {prev_start} 至 {prev_end}")
        
        try:
            previous_data = AssetDataService.query_asset_data(user_id, prev_start, prev_end)
            return previous_data
        except Exception as e:
            print(f"[上期查询] 未找到上期数据: {str(e)}")
            return None
