"""
智谱AI GLM大模型API调用服务
用于生成资产分析报告
"""

import json
from zai import ZhipuAiClient
from datetime import datetime, timedelta
from decimal import Decimal

class ZhipuAiService:
    """智谱AI GLM模型服务类"""
    
    def __init__(self, api_token):
        """
        初始化服务
        :param api_token: 智谱AI API Key
        """
        self.api_token = api_token
        # 使用智谱AI SDK
        self.client = ZhipuAiClient(api_key=api_token)
        self.model = "glm-4.6"  # 使用GLM-4.6模型
    
    def _call_api(self, prompt, max_tokens=2000):
        """
        调用智谱AI GLM API
        :param prompt: 提示词
        :param max_tokens: 最大token数
        :return: API响应内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位专业的个人资产管理顾问，擅长分析用户的资产配置、收益情况和风险控制。请用专业、客观的语言为用户提供深度分析和建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # 提取生成的文本
            return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def prepare_asset_data(self, user_id, start_date, end_date):
        """
        准备用户资产数据用于分析（含固定资产和虚拟资产）
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 格式化的资产数据
        """
        from models.fixed_asset import FixedAsset
        from models.asset_income import AssetIncome
        from models.category import Category
        from models.project import Project
        from datetime import datetime
        
        # ========== 固定资产分析 ==========
        # 获取用户的固定资产
        assets = FixedAsset.query.filter_by(user_id=user_id).all()
        
        # 获取时间范围内的收入数据
        incomes = AssetIncome.query.join(FixedAsset).filter(
            FixedAsset.user_id == user_id,
            AssetIncome.income_date >= start_date,
            AssetIncome.income_date <= end_date
        ).all()
        
        # 获取分类信息
        categories = Category.query.filter_by(user_id=user_id).all()
        
        # 固定资产统计数据
        total_assets = len(assets)
        total_original_value = sum(float(asset.original_value) for asset in assets)
        total_current_value = sum(float(asset.current_value) for asset in assets)
        total_income = sum(float(income.amount) for income in incomes)
        
        # 按分类统计
        category_stats = {}
        for category in categories:
            cat_assets = [a for a in assets if a.category_id == category.id]
            if cat_assets:
                category_stats[category.name] = {
                    'count': len(cat_assets),
                    'total_value': sum(float(a.current_value) for a in cat_assets),
                    'original_value': sum(float(a.original_value) for a in cat_assets)
                }
        
        # 按状态统计
        status_stats = {}
        for asset in assets:
            status = asset.get_status_text()
            if status not in status_stats:
                status_stats[status] = 0
            status_stats[status] += 1
        
        # ========== 虚拟资产（随风而逝）分析 ==========
        # 获取所有虚拟资产项目
        projects = Project.query.filter_by(user_id=user_id).all()
        
        # 统计虚拟资产数据
        total_projects = len(projects)
        total_project_amount = sum(float(p.total_amount) for p in projects)
        
        # 按状态分类
        active_projects = []  # 消耗中
        expired_projects = []  # 已过期
        not_started_projects = []  # 未开始
        
        total_used_value = 0  # 已消耗总价值
        total_remaining_value = 0  # 剩余总价值
        total_wasted_value = 0  # 浪费总价值（过期未用完）
        
        for project in projects:
            status = project.get_status()
            values = project.calculate_values()
            
            if status == 'active':
                active_projects.append(project)
                total_used_value += values['used_cost']
                total_remaining_value += values['remaining_value']
            elif status == 'expired':
                expired_projects.append(project)
                total_used_value += values['used_cost']
                # 过期项目的剩余价值视为浪费
                total_wasted_value += values['remaining_value']
            else:  # not_started
                not_started_projects.append(project)
                total_remaining_value += float(project.total_amount)
        
        # 即将过期的项目（7天内）
        expiring_soon = []
        now = datetime.utcnow()
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
            cat_projects = [p for p in projects if p.category_id == category.id]
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
        
        # 虚拟资产利用率
        utilization_rate = ((total_used_value / total_project_amount * 100) 
                          if total_project_amount > 0 else 0)
        
        # 浪费率
        waste_rate = ((total_wasted_value / total_project_amount * 100) 
                     if total_project_amount > 0 else 0)
        
        return {
            # 固定资产数据
            'fixed_assets': {
                'total_assets': total_assets,
                'total_original_value': round(total_original_value, 2),
                'total_current_value': round(total_current_value, 2),
                'total_depreciation': round(total_original_value - total_current_value, 2),
                'total_income': round(total_income, 2),
                'depreciation_rate': round((total_original_value - total_current_value) / total_original_value * 100, 2) if total_original_value > 0 else 0,
                'category_stats': category_stats,
                'status_stats': status_stats
            },
            # 虚拟资产数据（随风而逝）
            'virtual_assets': {
                'total_projects': total_projects,
                'total_amount': round(total_project_amount, 2),
                'active_count': len(active_projects),
                'expired_count': len(expired_projects),
                'not_started_count': len(not_started_projects),
                'total_used_value': round(total_used_value, 2),
                'total_remaining_value': round(total_remaining_value, 2),
                'total_wasted_value': round(total_wasted_value, 2),
                'utilization_rate': round(utilization_rate, 2),
                'waste_rate': round(waste_rate, 2),
                'expiring_soon': expiring_soon,
                'category_stats': project_category_stats
            },
            # 综合指标
            '综合资产': {
                'total_value': round(total_current_value + total_remaining_value, 2),
                'total_investment': round(total_original_value + total_project_amount, 2),
                'fixed_ratio': round(total_current_value / (total_current_value + total_remaining_value) * 100, 2) if (total_current_value + total_remaining_value) > 0 else 0,
                'virtual_ratio': round(total_remaining_value / (total_current_value + total_remaining_value) * 100, 2) if (total_current_value + total_remaining_value) > 0 else 0
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            }
        }
    
    def generate_weekly_report(self, user_id, start_date, end_date):
        """
        生成周报
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 报告内容（JSON格式）
        """
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        
        prompt = f"""
请基于以下数据生成一份专业的个人资产周报（{asset_data['period']['start_date']} 至 {asset_data['period']['end_date']}）：

【固定资产概况】
- 资产总数：{asset_data['fixed_assets']['total_assets']} 项
- 原始总值：¥{asset_data['fixed_assets']['total_original_value']:,.2f}
- 当前总值：¥{asset_data['fixed_assets']['total_current_value']:,.2f}
- 累计折旧：¥{asset_data['fixed_assets']['total_depreciation']:,.2f}
- 折旧率：{asset_data['fixed_assets']['depreciation_rate']}%
- 周期收入：¥{asset_data['fixed_assets']['total_income']:,.2f}

【虚拟资产概况（随风而逝）】
- 项目总数：{asset_data['virtual_assets']['total_projects']} 项
- 总投入：¥{asset_data['virtual_assets']['total_amount']:,.2f}
- 消耗中：{asset_data['virtual_assets']['active_count']} 项
- 已过期：{asset_data['virtual_assets']['expired_count']} 项
- 未开始：{asset_data['virtual_assets']['not_started_count']} 项
- 已消耗价值：¥{asset_data['virtual_assets']['total_used_value']:,.2f}
- 剩余价值：¥{asset_data['virtual_assets']['total_remaining_value']:,.2f}
- 浪费价值（过期未用完）：¥{asset_data['virtual_assets']['total_wasted_value']:,.2f}
- 利用率：{asset_data['virtual_assets']['utilization_rate']}%
- 浪费率：{asset_data['virtual_assets']['waste_rate']}%
- 即将过期（7天内）：{len(asset_data['virtual_assets']['expiring_soon'])} 项

【综合资产指标】
- 资产总值：¥{asset_data['综合资产']['total_value']:,.2f}
- 总投资：¥{asset_data['综合资产']['total_investment']:,.2f}
- 固定资产占比：{asset_data['综合资产']['fixed_ratio']}%
- 虚拟资产占比：{asset_data['综合资产']['virtual_ratio']}%

完整数据：
{json.dumps(asset_data, ensure_ascii=False, indent=2)}

请按以下结构生成报告（使用JSON格式）：
{{
    "executive_summary": "200字以内的执行摘要，突出重点指标和关键洞察",
    "key_insights": [
        "关键洞察1：虚拟资产浪费情况",
        "关键洞察2：资产健康度评估",
        "关键洞察3：需要关注的问题"
    ],
    "fixed_asset_analysis": {{
        "overall_health": "固定资产整体健康度评估",
        "value_trends": "价值变化趋势分析",
        "depreciation_analysis": "折旧情况分析"
    }},
    "virtual_asset_analysis": {{
        "usage_status": "虚拟资产使用情况分析（已使用、未使用、即将过期）",
        "waste_assessment": "浪费情况评估（过期或未及时使用造成的损失）",
        "utilization_rate": "利用率分析及建议",
        "expiring_alerts": "即将过期预警及处理建议"
    }},
    "comprehensive_health": {{
        "overall_score": "0-100分，综合资产健康度评分",
        "score_breakdown": "评分细分解释（固定资产、虚拟资产、收益性、风险控制）",
        "asset_allocation": "资产配置合理性分析"
    }},
    "income_analysis": {{
        "income_performance": "收入表现分析",
        "roi_estimation": "投资回报率估算"
    }},
    "risk_assessment": {{
        "risk_level": "low/medium/high",
        "risk_factors": ["风险因素1", "风险因素2"],
        "urgent_actions": ["紧急行动项1", "紧急行动项2"]
    }},
    "actionable_recommendations": [
        "具体可执行建议1：关于虚拟资产使用",
        "具体可执行建议2：关于过期预防",
        "具体可执行建议3：关于资产配置优化"
    ],
    "next_week_focus": ["下周关注点1", "下周关注点2"]
}}

请确保返回有效的JSON格式，不要包含其他文字说明。
"""
        
        response_text = self._call_api(prompt, max_tokens=3000)
        
        # 尝试解析JSON
        try:
            # 提取JSON部分（如果API返回了额外文字）
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                report_content = json.loads(json_text)
            else:
                # 如果没有JSON，使用原文本
                report_content = {
                    "executive_summary": response_text[:200],
                    "raw_response": response_text
                }
        except:
            report_content = {
                "executive_summary": "报告生成成功，但格式解析失败",
                "raw_response": response_text
            }
        
        # 添加数据快照
        report_content['data_snapshot'] = asset_data
        
        return json.dumps(report_content, ensure_ascii=False)
    
    def generate_monthly_report(self, user_id, start_date, end_date):
        """
        生成月报
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 报告内容（JSON格式）
        """
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        
        prompt = f"""
请基于以下数据生成一份详细的个人资产月报（{asset_data['period']['start_date']} 至 {asset_data['period']['end_date']}）：

【固定资产概况】
- 资产总数：{asset_data['fixed_assets']['total_assets']} 项
- 原始总值：¥{asset_data['fixed_assets']['total_original_value']:,.2f}
- 当前总值：¥{asset_data['fixed_assets']['total_current_value']:,.2f}
- 累计折旧：¥{asset_data['fixed_assets']['total_depreciation']:,.2f}
- 折旧率：{asset_data['fixed_assets']['depreciation_rate']}%
- 本月收入：¥{asset_data['fixed_assets']['total_income']:,.2f}

【虚拟资产概况（随风而逝）】
- 项目总数：{asset_data['virtual_assets']['total_projects']} 项
- 总投入：¥{asset_data['virtual_assets']['total_amount']:,.2f}
- 消耗中：{asset_data['virtual_assets']['active_count']} 项
- 已过期：{asset_data['virtual_assets']['expired_count']} 项
- 已消耗价值：¥{asset_data['virtual_assets']['total_used_value']:,.2f}
- 剩余价值：¥{asset_data['virtual_assets']['total_remaining_value']:,.2f}
- 浪费价值：¥{asset_data['virtual_assets']['total_wasted_value']:,.2f}
- 利用率：{asset_data['virtual_assets']['utilization_rate']}%
- 浪费率：{asset_data['virtual_assets']['waste_rate']}%

【综合资产指标】
- 资产总值：¥{asset_data['综合资产']['total_value']:,.2f}
- 总投资：¥{asset_data['综合资产']['total_investment']:,.2f}

完整数据：
{json.dumps(asset_data, ensure_ascii=False, indent=2)}

请按以下结构生成详细月报（使用JSON格式）：
{{
    "executive_summary": "300字以内的执行摘要，全面概括本月资产状况",
    "monthly_highlights": ["本月亮点1", "本月亮点2", "本月亮点3"],
    "fixed_asset_analysis": {{
        "portfolio_composition": "资产组合构成分析",
        "value_changes": "价值变动详细分析",
        "depreciation_details": "折旧详情分析",
        "category_performance": "各分类表现对比"
    }},
    "virtual_asset_analysis": {{
        "monthly_usage": "本月虚拟资产使用情况详细分析",
        "waste_details": "浪费详情及根因分析",
        "optimization_suggestions": "优化建议",
        "category_comparison": "各分类虚拟资产对比分析"
    }},
    "comprehensive_analysis": {{
        "health_score": "综合健康度评分（0-100）",
        "asset_allocation_review": "资产配置合理性审查",
        "utilization_efficiency": "整体资产利用效率分析",
        "improvement_areas": ["需要改进的方面1", "需要改进的方面2"]
    }},
    "income_analysis": {{
        "total_income": "总收入分析",
        "income_sources": "收入来源分析",
        "roi_analysis": "ROI深度分析",
        "comparison_with_goals": "与目标对比"
    }},
    "risk_assessment": {{
        "overall_risk_level": "low/medium/high",
        "detailed_risks": [
            {{"risk": "风险描述", "impact": "影响", "mitigation": "缓解措施"}}
        ],
        "expiring_warnings": "即将过期的虚拟资产警告"
    }},
    "performance_metrics": {{
        "asset_utilization": "资产利用率",
        "return_on_investment": "投资回报率",
        "waste_prevention_score": "浪费预防得分"
    }},
    "recommendations": {{
        "immediate_actions": ["立即执行建议1", "立即执行建议2"],
        "short_term": ["短期建议1", "短期建议2"],
        "long_term": ["长期建议1", "长期建议2"]
    }},
    "next_month_plan": ["下月计划1", "下月计划2", "下月计划3"]
}}

请确保返回有效的JSON格式，不要包含其他文字说明。
"""
        
        response_text = self._call_api(prompt, max_tokens=4000)
        
        # 尝试解析JSON（增强版）
        try:
            # 先尝试直接解析
            try:
                report_content = json.loads(response_text)
            except:
                # 提取JSON部分（如果API返回了额外文字）
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    # 清理可能的控制字符
                    json_text = json_text.replace('\n', '\\n').replace('\r', '\\r')
                    report_content = json.loads(json_text)
                else:
                    raise ValueError("未找到有效的JSON结构")
        except Exception as e:
            # 解析失败，但保留原始响应
            report_content = {
                "executive_summary": "报告生成成功，但格式解析失败",
                "error_message": str(e),
                "raw_response": response_text[:1000]  # 只保留前1000字符
            }
        
        # 添加数据快照
        report_content['data_snapshot'] = asset_data
        
        return json.dumps(report_content, ensure_ascii=False)
    
    def generate_custom_report(self, user_id, start_date, end_date, focus_areas=None):
        """
        生成自定义报告
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param focus_areas: 关注领域列表
        :return: 报告内容（JSON格式）
        """
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\n【特别关注】\n请重点分析以下方面：{', '.join(focus_areas)}"
        
        prompt = f"""
请基于以下数据生成一份自定义时间段的个人资产分析报告（{asset_data['period']['start_date']} 至 {asset_data['period']['end_date']}，共{asset_data['period']['days']}天）：

【固定资产概况】
- 资产总数：{asset_data['fixed_assets']['total_assets']} 项
- 原始总值：¥{asset_data['fixed_assets']['total_original_value']:,.2f}
- 当前总值：¥{asset_data['fixed_assets']['total_current_value']:,.2f}
- 累计折旧：¥{asset_data['fixed_assets']['total_depreciation']:,.2f}
- 期间收入：¥{asset_data['fixed_assets']['total_income']:,.2f}

【虚拟资产概况（随风而逝）】
- 项目总数：{asset_data['virtual_assets']['total_projects']} 项
- 总投入：¥{asset_data['virtual_assets']['total_amount']:,.2f}
- 利用率：{asset_data['virtual_assets']['utilization_rate']}%
- 浪费率：{asset_data['virtual_assets']['waste_rate']}%
- 浪费价值：¥{asset_data['virtual_assets']['total_wasted_value']:,.2f}

完整数据：
{json.dumps(asset_data, ensure_ascii=False, indent=2)}
{focus_text}

请按以下结构生成报告（使用JSON格式）：
{{
    "period_summary": "时间段总结，突出重点发现",
    "key_findings": [
        "关键发现1：固定资产方面",
        "关键发现2：虚拟资产利用情况",
        "关键发现3：潜在风险或机会"
    ],
    "fixed_asset_analysis": "固定资产详细分析",
    "virtual_asset_analysis": {{
        "usage_effectiveness": "虚拟资产使用效果分析",
        "waste_analysis": "浪费原因及改进建议"
    }},
    "comprehensive_insights": "综合资产洞察，固定与虚拟资产的协同分析",
    "income_analysis": "收入分析",
    "trends": "趋势分析（上升、下降、稳定）",
    "risk_assessment": {{
        "risk_level": "low/medium/high",
        "key_risks": ["风险1", "风险2"],
        "opportunities": ["机会1", "机会2"]
    }},
    "actionable_recommendations": [
        "建议1：虚拟资产优化",
        "建议2：固定资产管理",
        "建议3：整体策略调整"
    ],
    "conclusion": "总结：核心要点和行动指南"
}}

请确保返回有效的JSON格式，不要包含其他文字说明。
"""
        
        response_text = self._call_api(prompt, max_tokens=3500)
        
        # 尝试解析JSON
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                report_content = json.loads(json_text)
            else:
                report_content = {
                    "period_summary": response_text[:300],
                    "raw_response": response_text
                }
        except:
            report_content = {
                "period_summary": "报告生成成功，但格式解析失败",
                "raw_response": response_text
            }
        
        # 添加数据快照
        report_content['data_snapshot'] = asset_data
        
        return json.dumps(report_content, ensure_ascii=False)
