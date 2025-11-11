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
        self.model = "glm-4.5-flash"  # 使用GLM-4.5-Flash模型（更快、成本更低，支持96k上下文）
    
    def _call_api(self, prompt, max_tokens=None):
        """
        调用智谱AI GLM API
        :param prompt: 提示词
        :param max_tokens: 最大token数（None表示不限制）
        :return: API响应内容
        """
        try:
            print(f"\n=== 开始调用API ===")
            print(f"Model: {self.model}")
            print(f"Max tokens: {'不限制' if max_tokens is None else max_tokens}")
            print(f"Prompt长度: {len(prompt)} 字符")
            
            # 构建API调用参数
            api_params = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的个人资产管理顾问，擅长分析用户的资产配置、收益情况和风险控制。请用专业、客观的语言为用户提供深度分析和建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            
            # 只有当max_tokens不为None时才设置
            if max_tokens is not None:
                api_params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**api_params)
            
            # 详细调试信息
            print(f"\n[API响应调试]")
            print(f"- response 类型: {type(response)}")
            print(f"- response.choices 长度: {len(response.choices)}")
            
            result = response.choices[0].message.content
            
            # 检查是否为空
            if result is None:
                print(f"⚠️ 警告: API返回内容为None")
                result = ""
            elif not result or result.strip() == "":
                print(f"⚠️ 警告: API返回空字符串")
                
            # 检查finish_reason
            if hasattr(response.choices[0], 'finish_reason'):
                finish_reason = response.choices[0].finish_reason
                print(f"- finish_reason: {finish_reason}")
                if finish_reason == 'length':
                    print(f"⚠️ 警告: 响应因达到max_tokens限制而被截断！")
                elif finish_reason == 'stop':
                    print(f"✓ 响应正常结束")
                    
            print(f"✓ API调用成功，返回内容长度: {len(result)} 字符")
            return result
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"\n✗ API调用失败")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            print(f"详细堆栈:\n{error_detail}")
            raise Exception(f"API调用失败: {str(e)}")
    
    def _preprocess_data_with_ai(self, asset_data):  
        """
        第二阶段：将结构化数据压缩成文本格式后推送给AI处理
        :param asset_data: 原始资产数据
        :return: 带有AI洞察的数据
        """
        print("\n" + "="*80)
        print("[第二阶段] AI数据梳理开始")
        print("="*80)
        
        # 检查数据是否为空
        if asset_data['fixed_assets']['total_assets'] == 0 and asset_data['virtual_assets']['total_projects'] == 0:
            print("[警告] 没有任何资产数据，跳过AI梳理")
            return asset_data
        
        # 将结构化数据压缩成文本格式
        compressed_text = self._compress_data_to_text(asset_data)
        
        print(f"\n[数据压缩] 压缩后文本长度: {len(compressed_text)} 字符")
        print(f"\n[压缩文本预览]\n{compressed_text[:500]}...\n")
        
        # 构造AI梳理提示词
        prompt = f"""你是一位专业的资产管理分析师，请对以下完整的资产数据进行全面分析。

{compressed_text}

请直接输出JSON格式，包含以下字段：
{{
    "summary": "资产整体情况总结（60字以内）",
    "highlights": ["亮点1", "亮点2", "亮点3"],
    "concerns": ["问题1", "问题2"],
    "allocation_analysis": "资产配置分析（40字）",
    "health_score": 75
}}

分析要求：
1. 全面审视所有分类和项目
2. 识别资产配置不合理之处
3. 标注高浪费率分类
4. 发现潜在风险
5. 只返回JSON，不要其他文字
"""
        
        print(f"\n[AI请求] Prompt长度: {len(prompt)} 字符")
        print(f"\n[Prompt内容]\n{prompt}")
        print("\n" + "-"*80)
        
        try:
            print("\n[调用API] 开始调用智谱AI...")
            response_text = self._call_api(prompt)  # 不限制max_tokens，让模型自由输出
            
            print(f"\n[API响应] 原始响应长度: {len(response_text)} 字符")
            print(f"\n[API原始响应]\n{response_text}")
            print("\n" + "-"*80)
            
            # 清理响应文本
            cleaned_text = response_text.strip()
            if '```json' in cleaned_text:
                cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
                print("[JSON提取] 移除了```json```标记")
            elif '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```')[1].split('```')[0].strip()
                print("[JSON提取] 移除了```标记")
            
            # 提取JSON对象
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = cleaned_text[json_start:json_end]
                print(f"\n[提取JSON] JSON段落长度: {len(json_text)} 字符")
                print(f"\n[提取的JSON]\n{json_text}")
                print("\n" + "-"*80)
                
                try:
                    ai_insights = json.loads(json_text)
                    print("\n[JSON解析] ✓ 解析成功")
                    print(f"[AI洞察] {ai_insights}")
                    
                    # 将AI洞察附加到原始数据
                    asset_data['ai_insights'] = ai_insights
                    print("\n[\u2713 成功] AI梳理完成，洞察已附加到数据中")
                    
                except json.JSONDecodeError as je:
                    print(f"\n[JSON解析] ✗ 解析失败: {je}")
                    print(f"[错误位置] 第{je.lineno}行 第{je.colno}列")
                    print(f"[问题内容] {je.msg}")
                    print("\n[降级处理] 保留原始数据，继续执行")
            else:
                print(f"\n[JSON提取] ✗ 未找到JSON结构")
                print(f"[清理后文本] {cleaned_text[:200]}")
                print("\n[降级处理] 保留原始数据，继续执行")
                
        except Exception as e:
            print(f"\n[异常] ✗ AI梳理发生错误: {e}")
            import traceback
            print(f"[堆栈信息]\n{traceback.format_exc()}")
            print("\n[降级处理] 保留原始数据，继续执行")
        
        print("\n" + "="*80)
        print("[第二阶段] AI数据梳理结束")
        print("="*80 + "\n")
        
        return asset_data
    
    def _compress_data_to_text(self, asset_data):
        """
        将结构化数据压缩为简洁的文本格式
        :param asset_data: 结构化数据
        :return: 压缩后的文本
        """
        lines = []
        
        # 报告期间
        period = asset_data['period']
        lines.append(f"【报告期间】{period['start_date']} 至 {period['end_date']} (共{period['days']}天)")
        lines.append("")
        
        # 固定资产
        fa = asset_data['fixed_assets']
        lines.append("【固定资产】")
        lines.append(f"- 资产总数: {fa['total_assets']}项")
        lines.append(f"- 原始总值: ¥{fa['total_original_value']:,.2f}")
        lines.append(f"- 当前总值: ¥{fa['total_current_value']:,.2f}")
        lines.append(f"- 累计折旧: ¥{fa['total_depreciation']:,.2f}")
        lines.append(f"- 折旧率: {fa['depreciation_rate']}%")
        lines.append(f"- 期间收入: ¥{fa['total_income']:,.2f}")
        
        # 分类明细（显示全部）
        if fa['category_stats']:
            lines.append(f"- 分类明细: {len(fa['category_stats'])}个分类")
            for cat_name, cat_data in fa['category_stats'].items():
                lines.append(f"  * {cat_name}: {cat_data['count']}项, 当前价值¥{cat_data['total_value']:,.2f}")
        
        # 状态统计
        if fa['status_stats']:
            lines.append("- 资产状态:")
            for status, count in fa['status_stats'].items():
                lines.append(f"  * {status}: {count}项")
        lines.append("")
        
        # 虚拟资产
        va = asset_data['virtual_assets']
        lines.append("【虚拟资产（预付权益）】")
        lines.append(f"- 项目总数: {va['total_projects']}项")
        lines.append(f"- 总投入: ¥{va['total_amount']:,.2f}")
        lines.append(f"- 活跃项目: {va['active_count']}项, 剩余价值¥{va['total_remaining_value']:,.2f}")
        lines.append(f"- 过期项目: {va['expired_count']}项, 浪费价值¥{va['total_wasted_value']:,.2f}")
        lines.append(f"- 未开始: {va['not_started_count']}项, 价值¥{va['not_started_value']:,.2f}")
        lines.append(f"- 利用率: {va['utilization_rate']}%")
        lines.append(f"- 浪费率: {va['waste_rate']}%")
        
        # 虚拟资产分类明细（显示全部）
        if va['category_stats']:
            lines.append(f"- 虚拟资产分类: {len(va['category_stats'])}个分类")
            for cat_name, cat_data in va['category_stats'].items():
                lines.append(f"  * {cat_name}: {cat_data['count']}项, 总投入¥{cat_data['total_amount']:,.2f}, 浪费¥{cat_data['wasted_value']:,.2f}")
        
        # 即将过期项目（显示全部）
        if va['expiring_soon']:
            lines.append(f"- 即将过期项目({len(va['expiring_soon'])}):")
            for proj in va['expiring_soon']:
                lines.append(f"  ! {proj['name']} - 还剩{proj['days_left']}天, 价值¥{proj['remaining_value']:,.2f}")
        lines.append("")
        
        # 综合视图
        comp = asset_data['comprehensive']
        lines.append("【综合视图】")
        lines.append(f"- 有形资产价值: ¥{comp['tangible_assets_value']:,.2f}")
        lines.append(f"- 活跃权益价值: ¥{comp['active_rights_value']:,.2f}")
        lines.append(f"- 未开始权益: ¥{comp['not_started_rights_value']:,.2f}")
        lines.append(f"- 综合活跃价值: ¥{comp['combined_active_value']:,.2f}")
        lines.append(f"- 说明: {comp['note']}")
        
        return "\n".join(lines)
    
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
        
        print(f"[数据查询] 开始准备资产数据: {start_date} 至 {end_date}")
        
        # ========== 固定资产分析 ==========
        # 获取用户的固定资产（排除已处置的，且在报告期结束前购买的）
        assets = FixedAsset.query.filter(
            FixedAsset.user_id == user_id,
            FixedAsset.status != 'disposed',
            FixedAsset.purchase_date <= end_date
        ).all()
        
        print(f"[数据查询] 固定资产数量: {len(assets)}")
        
        # 获取时间范围内的收入数据
        incomes = AssetIncome.query.join(FixedAsset).filter(
            FixedAsset.user_id == user_id,
            AssetIncome.income_date >= start_date,
            AssetIncome.income_date <= end_date
        ).all()
        
        print(f"[数据查询] 收入记录数量: {len(incomes)}")
        
        # 获取分类信息
        categories = Category.query.filter_by(user_id=user_id).all()
        
        # 固定资产统计数据（添加NULL值检查）
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
        
        # ========== 虚拟资产（随风而逝）分析 ==========
        # 获取与报告期相关的虚拟资产项目（有时间交集的）
        projects = Project.query.filter(
            Project.user_id == user_id,
            Project.start_time <= end_date,  # 开始时间不晚于报告期结束
            Project.end_time >= start_date   # 结束时间不早于报告期开始
        ).all()
        
        print(f"[数据查询] 虚拟资产项目数量: {len(projects)}")
        
        # 过滤掉数据异常的项目
        valid_projects = [
            p for p in projects 
            if p.total_amount is not None and p.end_time >= p.start_time
        ]
        
        if len(projects) != len(valid_projects):
            print(f"[数据警告] 过滤掉 {len(projects) - len(valid_projects)} 个异常项目")
        
        # 统计虚拟资产数据
        total_projects = len(valid_projects)
        total_project_amount = sum(float(p.total_amount) for p in valid_projects)
        
        # 按状态分类
        active_projects = []  # 消耗中
        expired_projects = []  # 已过期
        not_started_projects = []  # 未开始
        
        total_used_value = 0  # 已消耗总价值
        total_remaining_value = 0  # 剩余总价值（仅活跃项目）
        total_wasted_value = 0  # 浪费总价值（过期未用完）
        not_started_value = 0  # 未开始项目价值（单独统计）
        
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
                # 过期项目的剩余价值视为浪费
                total_wasted_value += values['remaining_value']
            else:  # not_started
                not_started_projects.append(project)
                # 未开始项目单独统计，不计入剩余价值
                not_started_value += float(project.total_amount)
        
        print(f"[数据统计] 活跃: {len(active_projects)}, 过期: {len(expired_projects)}, 未开始: {len(not_started_projects)}")
        
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
        
        # 虚拟资产利用率（仅计算已开始的项目）
        started_amount = sum(
            float(p.total_amount) for p in (active_projects + expired_projects)
        )
        utilization_rate = (
            (total_used_value / started_amount * 100) 
            if started_amount > 0 else 0
        )
        
        # 浪费率（基于已开始的项目）
        waste_rate = (
            (total_wasted_value / started_amount * 100) 
            if started_amount > 0 else 0
        )
        
        print(f"[数据统计] 利用率: {utilization_rate:.2f}%, 浪费率: {waste_rate:.2f}%")
        
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
                'total_remaining_value': round(total_remaining_value, 2),  # 仅活跃项目
                'total_wasted_value': round(total_wasted_value, 2),
                'not_started_value': round(not_started_value, 2),  # 单独统计
                'utilization_rate': round(utilization_rate, 2),
                'waste_rate': round(waste_rate, 2),
                'expiring_soon': expiring_soon,
                'category_stats': project_category_stats
            },
            # 综合视图（遵循数据逻辑隔离原则）
            'comprehensive': {
                'tangible_assets_value': round(total_current_value, 2),
                'active_rights_value': round(total_remaining_value, 2),
                'not_started_rights_value': round(not_started_value, 2),
                'combined_active_value': round(total_current_value + total_remaining_value, 2),
                'note': '有形资产+活跃权益，不包括未开始项目'
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            }
        }
    
    def generate_weekly_report(self, user_id, start_date, end_date):
        """
        生成周报（三阶段流程）
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 报告内容（JSON格式）
        """
        print("\n" + "#"*80)
        print("# 周报生成三阶段流程开始")
        print("#"*80 + "\n")
        
        # ===== 第一阶段：数据查询 =====
        print("\n" + "="*80)
        print("[第一阶段] 数据查询开始")
        print("="*80)
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        print("="*80)
        print("[第一阶段] 数据查询完成")
        print("="*80 + "\n")
        
        # ===== 第二阶段：AI数据梳理 =====
        processed_data = self._preprocess_data_with_ai(asset_data)
        
        # ===== 第三阶段：生成报告 =====
        print("\n" + "="*80)
        print("[第三阶段] 报告生成开始")
        print("="*80)
        
        # 压缩数据为文本
        compressed_text = self._compress_data_to_text(processed_data)
        print(f"\n[数据压缩] 报告用文本长度: {len(compressed_text)} 字符")
        
        # 添加AI洞察（如果有）
        ai_insights_text = ""
        if 'ai_insights' in processed_data:
            insights = processed_data['ai_insights']
            ai_insights_text = f"""

【AI洞察】
- 总结: {insights.get('summary', 'N/A')}
- 亮点: {', '.join(insights.get('highlights', []))}
- 关注: {', '.join(insights.get('concerns', []))}
- 健康分: {insights.get('health_score', 'N/A')}
"""
            print(f"[AI洞察] 已包含第二阶段的AI洞察")
        
        # 构造报告生成Prompt
        prompt = f"""你是一位资深的个人资产管理顾问，拥有10年以上的财富管理经验。请基于以下完整数据，生成一份专业、结构化、深度的个人资产周报。

{compressed_text}{ai_insights_text}

请按照以下JSON结构，进行全面深入的分析（每个字段都必须填充实质性内容）：

注意：所有文本内容请使用Markdown格式，包括表格、粗体、列表等，以便前端更好地渲染。

{{
    "executive_summary": "200-300字的执行摘要，必须包含：1)总资产规模及构成比例；2)本周最重大的3个发现；3)最紧迫的行动建议；4)整体健康度评分(0-100)",
    
    "key_insights": [
        "洞察1：固定资产方面最重要的发现（必须包含具体数据和占比）",
        "洞察2：虚拟资产使用效率的核心问题（必须包含利用率和浪费率数据）",
        "洞察3：资产配置结构的关键不平衡（必须指出具体分类及占比）",
        "洞察4：本周期内收入表现及趋势（必须包含具体金额）",
        "洞察5：需要立即关注的风险点（必须包含影响范围和紧急程度）"
    ],
    
    "fixed_asset_analysis": {{
        "overall_health": "固定资产整体健康度评价（优秀/良好/中等/较差/很差），必须说明：1)总价值及占比；2)使用状态分布；3)折旧情况；4)主要风险点",
        "value_trends": "本周价值变化详细分析，必须包含：1)总价值变动金额及百分比；2)主要变动驱动因素（新增/处置/折旧/升值）；3)与上周对比；4)趋势预测",
        "depreciation_analysis": "折旧详细分析，必须包含：1)累计折旧金额及占比；2)本周折旧金额；3)折旧率是否合理；4)高折旧资产预警",
        "category_insights": "各分类详细表现（必须逐一分析每个分类）：1)各分类资产数量、原值、现值；2)表现最好的TOP3分类及理由；3)需要关注的分类及问题；4)配置建议",
        "usage_efficiency": "资产使用效率分析，必须包含：1)在用资产占比；2)闲置资产情况；3)低效资产识别；4)优化建议"
    }},
    
    "virtual_asset_analysis": {{
        "usage_status": "虚拟资产整体使用情况，必须包含：1)总投入金额；2)整体利用率；3)活跃项目占比；4)使用趋势（上升/下降）",
        "waste_assessment": "浪费情况深度评估，必须包含：1)总浪费金额及占总投入比例；2)浪费率排名TOP3的分类；3)过期项目数量及金额；4)浪费根本原因分析",
        "category_insights": "各分类利用率详细分析（必须逐一分析）：1)各分类投入金额、利用率、浪费金额；2)表现最好的分类（利用率最高）；3)问题最严重的分类（浪费率最高）；4)针对性优化建议",
        "expiring_alerts": "即将过期项目预警，必须包含：1)30天内过期项目清单；2)剩余价值金额；3)紧急处理建议；4)预期损失评估",
        "roi_analysis": "投资回报分析，必须包含：1)虚拟资产整体ROI；2)高价值项目识别；3)低价值项目识别；4)优化配置建议"
    }},
    
    "income_performance": {{
        "period_income": "本周期收入详情，必须包含：1)总收入金额；2)收入来源分类及占比；3)与上周对比；4)收入趋势",
        "income_quality": "收入质量分析，必须包含：1)稳定性收入占比；2)一次性收入占比；3)收入集中度风险；4)收入多元化建议",
        "growth_potential": "增长潜力评估，必须包含：1)现有资产的增值潜力；2)潜在收入机会；3)增长瓶颈；4)突破策略"
    }},
    
    "asset_allocation_review": {{
        "current_structure": "当前资产配置结构全面评价，必须包含：1)固定资产vs虚拟资产比例；2)各分类占比分布；3)流动性评估；4)风险集中度",
        "imbalances": [
            "不平衡1：固定资产占比过高/过低的问题（具体占比及影响）",
            "不平衡2：虚拟资产配置失衡（哪些分类过多/过少）",
            "不平衡3：收入来源单一化风险（具体表现）",
            "不平衡4：流动性不足/过剩问题（具体影响）"
        ],
        "optimization_suggestions": "资产配置优化建议，必须包含：1)目标配置比例建议；2)需要增持的资产类别及理由；3)需要减持的资产类别及理由；4)再平衡时间表；5)预期收益改善"
    }},
    
    "actionable_recommendations": [
        "建议1：针对高浪费率分类的具体处理方案（必须包含：问题分类、当前浪费率、目标浪费率、具体行动步骤、预期节省金额、执行时间表）",
        "建议2：即将过期项目的紧急行动计划（必须包含：项目清单、剩余天数、剩余价值、使用方案、执行责任人）",
        "建议3：资产配置调整的具体措施（必须包含：调整方向、调整幅度、资金来源、执行步骤、风险控制）",
        "建议4：闲置资产盘活方案（必须包含：闲置资产清单、盘活方式、预期收益、执行难度）",
        "建议5：收入增长策略（必须包含：增长路径、所需资源、时间周期、预期收益、风险评估）"
    ],
    
    "risk_alerts": [
        "风险1：资产折旧/贬值风险（必须包含：风险资产、风险金额、发生概率、影响程度、应对措施）",
        "风险2：虚拟资产浪费风险（必须包含：高风险分类、浪费金额、根本原因、预防措施）",
        "风险3：资产配置失衡风险（必须包含：失衡表现、潜在损失、调整建议、调整难度）",
        "风险4：收入波动风险（必须包含：波动幅度、影响因素、稳定性措施、应急预案）"
    ],
    
    "health_score": {{
        "overall_score": "综合健康分(0-100)",
        "score_breakdown": {{
            "fixed_assets_score": "固定资产分(0-25)：评分依据（资产质量、使用效率、折旧合理性、配置优化度）",
            "virtual_assets_score": "虚拟资产分(0-25)：评分依据（利用率、浪费率、到期管理、ROI）",
            "income_score": "收入表现分(0-25)：评分依据（收入规模、增长性、稳定性、多元化）",
            "allocation_score": "配置合理分(0-25)：评分依据（结构平衡、流动性、风险控制、优化空间）"
        }},
        "score_trend": "评分趋势（上升/稳定/下降），与上周对比变化及原因",
        "improvement_suggestions": "提分建议：最有效的3个提升健康分的措施"
    }},
    
    "next_week_focus": [
        "下周重点1：最重要的关注事项（具体任务、完成标准、预期效果）",
        "下周重点2：次重要的关注事项（具体任务、完成标准、预期效果）",
        "下周重点3：持续优化事项（具体任务、完成标准、预期效果）"
    ],
    
    "chart_data": {{
        "asset_allocation_pie": [
            {{"name": "固定资产", "value": 固定资产总价值}},
            {{"name": "虚拟资产", "value": 虚拟资产总投入}}
        ],
        "fixed_asset_categories": [
            {{"category": "分类名", "count": 数量, "value": 现值}}
        ],
        "virtual_asset_utilization": [
            {{"category": "分类名", "utilization": 利用率百分比, "waste": 浪费率百分比}}
        ],
        "health_score_radar": [
            {{"dimension": "固定资产", "score": 得分}},
            {{"dimension": "虚拟资产", "score": 得分}},
            {{"dimension": "收入表现", "score": 得分}},
            {{"dimension": "配置合理", "score": 得分}}
        ]
    }}
}}

分析要求（必须严格遵守）：
1. 每个字段都必须填充实质性内容，禁止空洞的通用描述
2. 所有分析必须基于提供的真实数据，必须引用具体数字和占比
3. 逐一分析每个资产分类，不能遗漏任何分类
4. 必须指出具体的问题分类名称、金额、占比
5. 所有建议必须可执行，包含具体步骤和时间表
6. 风险预警必须包含严重程度（高/中/低）和紧急程度（紧急/重要/一般）
7. 健康评分必须有明确的评分依据和计算逻辑
8. 只返回JSON格式，不要任何文字标记或额外文字
9. JSON字符串值中不要换行，所有内容写在同一行内
"""
        
        print(f"\n[报告Prompt] Prompt长度: {len(prompt)} 字符")
        print(f"\n[Prompt完整内容]\n{prompt}")
        print("\n" + "-"*80)
        
        print("\n[调用API] 开始生成周报...")
        response_text = self._call_api(prompt)  # 不限制max_tokens，让模型自由输出
        
        print(f"\n[API响应] 周报原始响应长度: {len(response_text)} 字符")
        print(f"\n[周报原始响应]\n{response_text}")
        print("\n" + "-"*80)
        
        # ===== JSON解析 =====
        print("\n[JSON解析] 开始解析周报JSON...")
        try:
            # 移除``json```标记
            cleaned_text = response_text.strip()
            if '```json' in cleaned_text:
                cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
                print("[JSON清理] 移除了```json```标记")
            elif '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```')[1].split('```')[0].strip()
                print("[JSON清理] 移除了```标记")
            
            # 提取JSON内容
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = cleaned_text[json_start:json_end]
                
                # ⚠️ 关键修复：清理JSON字符串中的裸露换行符
                # 将字符串值中的换行符替换为空格，避免解析错误
                json_text = json_text.replace('\n', ' ').replace('\r', ' ')
                # 清理多余的空格
                import re
                json_text = re.sub(r'\s+', ' ', json_text)
                
                print(f"\n[提取JSON] JSON段落长度: {len(json_text)} 字符")
                print(f"\n[提取的JSON]\n{json_text[:500]}...")
                
                report_content = json.loads(json_text)
                print("\n[JSON解析] ✓ 解析成功")
                print(f"[报告字段] {list(report_content.keys())}")
            else:
                print(f"\n[JSON解析] ✗ 未找到JSON结构")
                print(f"[清理后文本] {cleaned_text[:300]}")
                report_content = {
                    "executive_summary": "报告生成成功，但格式解析失败",
                    "error": "未找到JSON格式",
                    "raw_response": response_text[:500]
                }
        except json.JSONDecodeError as e:
            print(f"\n[JSON解析] ✗ JSON解析错误: {e}")
            print(f"[错误位置] 第{e.lineno}行 第{e.colno}列")
            print(f"[错误信息] {e.msg}")
            if 'json_text' in locals():
                print(f"[问题内容] {json_text[max(0, e.pos-50):e.pos+50]}")
            report_content = {
                "executive_summary": "报告生成成功，但格式解析失败",
                "error": f"JSON解析错误: {str(e)}",
                "raw_response": response_text[:500]
            }
        except Exception as e:
            print(f"\n[JSON解析] ✗ 其他错误: {e}")
            import traceback
            print(f"[堆栈信息]\n{traceback.format_exc()}")
            report_content = {
                "executive_summary": "报告生成成功，但格式解析失败",
                "error": str(e),
                "raw_response": response_text[:500]
            }
        
        # 添加数据快照
        report_content['data_snapshot'] = processed_data
        
        print("\n" + "="*80)
        print("[第三阶段] 报告生成完成")
        print("="*80)
        
        print("\n" + "#"*80)
        print("# 周报生成三阶段流程结束")
        print("#"*80 + "\n")
        
        return json.dumps(report_content, ensure_ascii=False)
    
    def generate_monthly_report(self, user_id, start_date, end_date):
        """
        生成月报（三阶段流程）
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 报告内容（JSON格式）
        """
        # 第一阶段：数据查询
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        
        # 第二阶段：AI数据预处理
        processed_data = self._preprocess_data_with_ai(asset_data)
        
        # 第三阶段：基于数据生成报告
        compressed_text = self._compress_data_to_text(processed_data)
        
        # 添加AI洞察（如果有）
        ai_insights_text = ""
        if 'ai_insights' in processed_data:
            insights = processed_data['ai_insights']
            ai_insights_text = f"""
【AI洞察】
- 总结: {insights.get('summary', 'N/A')}
- 亮点: {', '.join(insights.get('highlights', []))}
- 关注: {', '.join(insights.get('concerns', []))}
- 健康分: {insights.get('health_score', 'N/A')}
- 配置分析: {insights.get('allocation_analysis', 'N/A')}
"""
        
        prompt = f"""你是一位资深的个人财富管理专家，请基于以下完整数据生成一份全面深入的个人资产月报。

{compressed_text}{ai_insights_text}

Please按以下JSON structure generate detailed month报：
{{
    "executive_summary": "300-400字的执行摘要，全面概括本月资产状况、重大变化和关键决策点",
    "monthly_highlights": ["本月最大的成就或进步"],
    "fixed_asset_analysis": {{
        "portfolio_composition": "资产组合构成分析",
        "value_changes": {{
            "month_change": "本月价值变动金额及百分比",
            "main_drivers": ["变动主因1"],
            "comparison": "与上月/去年同期对比"
        }},
        "depreciation_details": {{
            "total_depreciation": "累计折旧金额",
            "monthly_depreciation": "本月折旧金额",
            "depreciation_rate": "折旧率及评价",
            "optimization_suggestions": "折旧优化建议"
        }},
        "category_performance": [
            {{
                "category": "分类名称",
                "performance": "表现评价",
                "highlights": "亮点",
                "concerns": "问题"
            }}
        ]
    }},
    "virtual_asset_analysis": {{
        "monthly_usage": {{
            "overview": "本月整体使用情况概述",
            "activation_rate": "激活率",
            "completion_rate": "完成率",
            "trends": "使用趋势"
        }},
        "waste_details": {{
            "total_waste": "本月浪费总额",
            "waste_rate": "浪费率及同比",
            "root_causes": [
                {{
                    "cause": "根本原因",
                    "impact_value": "影响金额",
                    "affected_items": "受影响项目数"
                }}
            ],
            "prevention_plan": "预防措施计划"
        }},
        "optimization_suggestions": ["优化建议1"],
        "category_comparison": [
            {{
                "category": "分类名称",
                "utilization": "利用率",
                "waste_level": "浪费程度",
                "recommendation": "针对性建议"
            }}
        ]
    }},
    "comprehensive_analysis": {{
        "health_score": 85,
        "score_details": {{
            "current_score": "本月得分",
            "last_month_score": "上月得分",
            "trend": "趋势",
            "score_breakdown": {{
                "fixed_assets_score": "固定资产分(0-25)",
                "virtual_assets_score": "虚拟资产分(0-25)",
                "income_score": "收益表现分(0-25)",
                "risk_control_score": "风险控制分(0-25)"
            }}
        }},
        "asset_allocation_review": {{
            "current_allocation": "当前配置比例",
            "optimal_allocation": "建议配置比例",
            "adjustment_needed": "是否需要调整",
            "adjustment_plan": "调整计划"
        }},
        "utilization_efficiency": {{
            "overall_efficiency": "整体效率评级",
            "strong_areas": ["优势领域1"],
            "weak_areas": ["薄弱环衂1"]
        }},
        "improvement_areas": ["改进方呁1"]
    }},
    "income_analysis": {{
        "total_income": {{
            "amount": "本月总收入",
            "growth_rate": "环比增长率",
            "year_over_year": "同比增长率"
        }},
        "income_sources": [
            {{
                "source": "收入来源",
                "amount": "金额",
                "percentage": "占比",
                "stability": "稳定性评价"
            }}
        ],
        "roi_analysis": {{
            "overall_roi": "整体投资回报率",
            "best_performers": ["回报最好的资产1"],
            "underperformers": ["需改进的资产1"]
        }},
        "comparison_with_goals": "与年度目标对比及达成进度"
    }},
    "risk_assessment": {{
        "overall_risk_level": "low/medium/high",
        "detailed_risks": [
            {{
                "risk": "风险描述",
                "probability": "发生概率",
                "impact": "影响程度",
                "mitigation": "缓解措施"
            }}
        ],
        "expiring_warnings": [
            {{
                "item": "即将过期项目",
                "expiry_date": "过期日期",
                "value_at_risk": "风险价值",
                "action_plan": "行动计划"
            }}
        ],
        "market_risks": "市场环境风险评估",
        "operational_risks": "运营风险评估"
    }},
    "performance_metrics": {{
        "asset_utilization": {{
            "rate": "资产利用率",
            "benchmark": "行业基准",
            "gap_analysis": "差距分析"
        }},
        "return_on_investment": {{
            "rate": "投资回报率",
            "evaluation": "评价",
            "improvement_potential": "提升潜力"
        }},
        "waste_prevention_score": {{
            "score": "浪费预防得分(0-100)",
            "improvement": "较上月改进幅度",
            "target": "目标得分"
        }}
    }},
    "recommendations": {{
        "immediate_actions": ["立即执行1：紧急且重要的行动(24小时内)"],
        "short_term": ["短期建议1：本月内完成的优化措施"],
        "long_term": ["长期规划1：未来3-6个月的战略调整"]
    }},
    "next_month_plan": ["下月重点1：具体目标和行动计划"]
}}

撰写标准：
1. 深度分析：不仅报告数据，更要解读背后的原因和趋势
2. 前瞻性：基于当前数据预测未来可能的变化
3. 可操作性：所有建议都要具体、可执行、有时间节点
4. 对比分析：与历史数据、目标进行对比
5. 确保返回纯JSON格式，不包含其他文字标记或其他文字
"""
        
        response_text = self._call_api(prompt, max_tokens=4500)
        
        print(f"[DEBUG] 月报AI响应原文：{response_text[:500]}...")  # 调试信息
        
        # 解析JSON
        try:
            # 移除``json```标记
            cleaned_text = response_text
            if '```json' in cleaned_text:
                cleaned_text = cleaned_text.split('```json')[1].split('```')[0]
            elif '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```')[1].split('```')[0]
            
            # 提取JSON内容
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = cleaned_text[json_start:json_end]
                report_content = json.loads(json_text)
                print("[DEBUG] 月报JSON解析成功")
            else:
                print(f"[ERROR] 月报未找到JSON格式，原文：{response_text[:200]}")
                report_content = {
                    "executive_summary": "报告生成成功，但格式解析失败",
                    "error": "未找到JSON格式",
                    "raw_response": response_text[:500]
                }
        except json.JSONDecodeError as e:
            print(f"[ERROR] 月报JSON解析错误: {e}")
            print(f"[ERROR] 尝试解析的内容: {json_text[:200] if 'json_text' in locals() else 'N/A'}")
            report_content = {
                "executive_summary": "报告生成成功，但格式解析失败",
                "error": f"JSON解析错误: {str(e)}",
                "raw_response": response_text[:500]
            }
        except Exception as e:
            print(f"[ERROR] 月报其他错误: {e}")
            report_content = {
                "executive_summary": "报告生成成功，但格式解析失败",
                "error": str(e),
                "raw_response": response_text[:500]
            }
        
        # 添加数据快照
        report_content['data_snapshot'] = processed_data
        
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
        
        print(f"[DEBUG] 自定义报告AI响应原文：{response_text[:500]}...")  # 调试信息
        
        # 尝试解析JSON
        try:
            # 移除``json```标记
            cleaned_text = response_text
            if '```json' in cleaned_text:
                cleaned_text = cleaned_text.split('```json')[1].split('```')[0]
            elif '```' in cleaned_text:
                cleaned_text = cleaned_text.split('```')[1].split('```')[0]
            
            # 提取JSON内容
            json_start = cleaned_text.find('{')
            json_end = cleaned_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = cleaned_text[json_start:json_end]
                report_content = json.loads(json_text)
                print("[DEBUG] 自定义报告JSON解析成功")
            else:
                print(f"[ERROR] 自定义报告未找到JSON格式")
                report_content = {
                    "period_summary": response_text[:300],
                    "raw_response": response_text
                }
        except json.JSONDecodeError as e:
            print(f"[ERROR] 自定义报告JSON解析错误: {e}")
            report_content = {
                "period_summary": "报告生成成功，但格式解析失败",
                "error": str(e),
                "raw_response": response_text[:500]
            }
        except Exception as e:
            print(f"[ERROR] 自定义报告其他错误: {e}")
            report_content = {
                "period_summary": "报告生成成功，但格式解析失败",
                "raw_response": response_text
            }
        
        # 添加数据快照
        report_content['data_snapshot'] = asset_data
        
        return json.dumps(report_content, ensure_ascii=False)
