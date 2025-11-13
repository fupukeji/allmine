"""
资产数据格式化服务
将结构化数据转换为AI可读的清晰文本格式
"""


class DataFormatter:
    """数据格式化器"""
    
    @staticmethod
    def format_asset_data(asset_data):
        """
        将结构化资产数据转换为清晰的文本格式
        
        Args:
            asset_data: 结构化的资产数据字典
        
        Returns:
            str: 格式化后的文本
        """
        lines = []
        
        # === 报告期间 ===
        period = asset_data['period']
        lines.append("="*60)
        lines.append("📅 报告期间")
        lines.append("="*60)
        lines.append(f"开始日期: {period['start_date']}")
        lines.append(f"结束日期: {period['end_date']}")
        lines.append(f"时间跨度: {period['days']}天")
        lines.append("")
        
        # === 固定资产 ===
        fa = asset_data['fixed_assets']
        lines.append("="*60)
        lines.append("🏠 固定资产概况")
        lines.append("="*60)
        lines.append(f"资产总数: {fa['total_assets']}项")
        lines.append(f"原始总值: ¥{fa['total_original_value']:,.2f}")
        lines.append(f"当前总值: ¥{fa['total_current_value']:,.2f}")
        lines.append(f"累计折旧: ¥{fa['total_depreciation']:,.2f}")
        lines.append(f"折旧率: {fa['depreciation_rate']}%")
        lines.append(f"期间收入: ¥{fa['total_income']:,.2f}")
        lines.append("")
        
        # 分类明细
        if fa['category_stats']:
            lines.append("📊 分类明细:")
            for cat_name, cat_data in fa['category_stats'].items():
                lines.append(f"  · {cat_name}:")
                lines.append(f"    - 数量: {cat_data['count']}项")
                lines.append(f"    - 原值: ¥{cat_data['original_value']:,.2f}")
                lines.append(f"    - 现值: ¥{cat_data['total_value']:,.2f}")
            lines.append("")
        
        # 状态分布
        if fa['status_stats']:
            lines.append("📈 资产状态分布:")
            for status, count in fa['status_stats'].items():
                lines.append(f"  · {status}: {count}项")
            lines.append("")
        
        # 收入分类
        if fa.get('income_by_category'):
            lines.append("💵 收入分类:")
            for cat_name, amount in fa['income_by_category'].items():
                lines.append(f"  · {cat_name}: ¥{amount:,.2f}")
            lines.append("")
        
        # === 虚拟资产 ===
        va = asset_data['virtual_assets']
        lines.append("="*60)
        lines.append("💳 虚拟资产(预付权益)概况")
        lines.append("="*60)
        lines.append(f"项目总数: {va['total_projects']}项")
        lines.append(f"总投入: ¥{va['total_amount']:,.2f}")
        lines.append("")
        
        lines.append("📊 项目状态:")
        lines.append(f"  · 活跃项目: {va['active_count']}项")
        lines.append(f"    - 剩余价值: ¥{va['total_remaining_value']:,.2f}")
        lines.append(f"  · 已过期项目: {va['expired_count']}项")
        lines.append(f"    - 浪费金额: ¥{va['total_wasted_value']:,.2f}")
        lines.append(f"  · 未开始项目: {va['not_started_count']}项")
        lines.append(f"    - 总价值: ¥{va['not_started_value']:,.2f}")
        lines.append("")
        
        lines.append("📈 使用效率:")
        lines.append(f"  · 利用率: {va['utilization_rate']}%")
        lines.append(f"  · 浪费率: {va['waste_rate']}%")
        lines.append("")
        
        # 分类统计
        if va['category_stats']:
            lines.append("📊 虚拟资产分类:")
            for cat_name, cat_data in va['category_stats'].items():
                waste_percent = (cat_data['wasted_value'] / cat_data['total_amount'] * 100) if cat_data['total_amount'] > 0 else 0
                lines.append(f"  · {cat_name}:")
                lines.append(f"    - 项目数: {cat_data['count']}项")
                lines.append(f"    - 总投入: ¥{cat_data['total_amount']:,.2f}")
                lines.append(f"    - 浪费: ¥{cat_data['wasted_value']:,.2f} ({waste_percent:.1f}%)")
            lines.append("")
        
        # 即将过期预警
        if va['expiring_soon']:
            lines.append("⚠️ 即将过期预警(7天内):")
            for proj in va['expiring_soon']:
                lines.append(f"  🔴 {proj['name']}")
                lines.append(f"     - 剩余时间: {proj['days_left']}天")
                lines.append(f"     - 剩余价值: ¥{proj['remaining_value']:,.2f}")
            lines.append("")
        
        # === 综合视图 ===
        comp = asset_data['comprehensive']
        lines.append("="*60)
        lines.append("🎯 综合视图")
        lines.append("="*60)
        lines.append(f"有形资产价值: ¥{comp['tangible_assets_value']:,.2f}")
        lines.append(f"活跃权益价值: ¥{comp['active_rights_value']:,.2f}")
        lines.append(f"未开始权益: ¥{comp['not_started_rights_value']:,.2f}")
        lines.append(f"当前活跃总值: ¥{comp['combined_active_value']:,.2f}")
        lines.append(f"资产总价值: ¥{comp['total_value']:,.2f}")
        lines.append(f"说明: {comp['note']}")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_comparison_data(current_data, previous_data):
        """
        生成当前期与上期的对比文本
        
        Args:
            current_data: 当前期数据
            previous_data: 上期数据
        
        Returns:
            str: 对比文本
        """
        if not previous_data:
            return ""
        
        lines = []
        lines.append("="*60)
        lines.append("📊 上期数据对比")
        lines.append("="*60)
        
        prev_period = previous_data['period']
        lines.append(f"上期时间: {prev_period['start_date']} 至 {prev_period['end_date']}")
        lines.append("")
        
        # 固定资产对比
        curr_fa = current_data['fixed_assets']
        prev_fa = previous_data['fixed_assets']
        
        lines.append("🏠 固定资产变化:")
        
        # 总价值变化
        value_change = curr_fa['total_current_value'] - prev_fa['total_current_value']
        value_change_pct = (value_change / prev_fa['total_current_value'] * 100) if prev_fa['total_current_value'] > 0 else 0
        trend = "📈" if value_change > 0 else "📉" if value_change < 0 else "➡️"
        lines.append(f"  · 当前总值: ¥{curr_fa['total_current_value']:,.2f}")
        lines.append(f"    上期: ¥{prev_fa['total_current_value']:,.2f}")
        lines.append(f"    变化: {trend} {'+' if value_change >= 0 else ''}{value_change:,.2f} ({'+' if value_change_pct >= 0 else ''}{value_change_pct:.1f}%)")
        
        # 收入变化
        income_change = curr_fa['total_income'] - prev_fa['total_income']
        income_change_pct = (income_change / prev_fa['total_income'] * 100) if prev_fa['total_income'] > 0 else 0
        trend = "📈" if income_change > 0 else "📉" if income_change < 0 else "➡️"
        lines.append(f"  · 期间收入: ¥{curr_fa['total_income']:,.2f}")
        lines.append(f"    上期: ¥{prev_fa['total_income']:,.2f}")
        lines.append(f"    变化: {trend} {'+' if income_change >= 0 else ''}{income_change:,.2f} ({'+' if income_change_pct >= 0 else ''}{income_change_pct:.1f}%)")
        lines.append("")
        
        # 虚拟资产对比
        curr_va = current_data['virtual_assets']
        prev_va = previous_data['virtual_assets']
        
        lines.append("💳 虚拟资产变化:")
        
        # 利用率变化
        util_change = curr_va['utilization_rate'] - prev_va['utilization_rate']
        trend = "📈" if util_change > 0 else "📉" if util_change < 0 else "➡️"
        lines.append(f"  · 利用率: {curr_va['utilization_rate']:.1f}%")
        lines.append(f"    上期: {prev_va['utilization_rate']:.1f}%")
        lines.append(f"    变化: {trend} {'+' if util_change >= 0 else ''}{util_change:.1f}%")
        
        # 浪费率变化
        waste_change = curr_va['waste_rate'] - prev_va['waste_rate']
        trend = "📉" if waste_change < 0 else "📈" if waste_change > 0 else "➡️"  # 浪费率下降是好事
        lines.append(f"  · 浪费率: {curr_va['waste_rate']:.1f}%")
        lines.append(f"    上期: {prev_va['waste_rate']:.1f}%")
        lines.append(f"    变化: {trend} {'+' if waste_change >= 0 else ''}{waste_change:.1f}%")
        
        # 浪费金额变化
        wasted_change = curr_va['total_wasted_value'] - prev_va['total_wasted_value']
        trend = "📉" if wasted_change < 0 else "📈" if wasted_change > 0 else "➡️"
        lines.append(f"  · 浪费金额: ¥{curr_va['total_wasted_value']:,.2f}")
        lines.append(f"    上期: ¥{prev_va['total_wasted_value']:,.2f}")
        lines.append(f"    变化: {trend} {'+' if wasted_change >= 0 else ''}{wasted_change:,.2f}")
        lines.append("")
        
        return "\n".join(lines)