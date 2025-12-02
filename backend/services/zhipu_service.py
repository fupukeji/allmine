"""
智谱AI GLM大模型API调用服务
用于生成资产分析报告
使用requests直接调用，避免openai SDK版本冲突
"""

import json
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from config.report_prompts import (
    get_weekly_report_prompt,
    get_monthly_report_prompt,
    get_yearly_report_prompt,
    get_custom_report_prompt,
    PROMPT_VERSION
)

class ZhipuAiService:
    """智谱AI GLM模型服务类"""
    
    def __init__(self, api_token, model="glm-4-flash"):
        """
        初始化服务
        :param api_token: 智谱AI API Key
        :param model: 模型名称（默认glm-4-flash）
        """
        self.api_token = api_token
        self.model = model
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
        print(f"✓ 智谱AI服务初始化成功 - 模型: {model}")
    
    def _call_api(self, prompt, max_tokens=None, retry_count=3, retry_delay=2):
        """
        调用智谱AI GLM API（带重试机制）
        :param prompt: 提示词
        :param max_tokens: 最大token数（None表示不限制）
        :param retry_count: 重试次数（默认3次）
        :param retry_delay: 重试延迟（秒，默认2秒）
        :return: API响应内容
        """
        import time
        
        for attempt in range(retry_count):
            try:
                if attempt > 0:
                    print(f"\n[重试] 第{attempt + 1}次尝试...")
                    time.sleep(retry_delay * attempt)  # 指数退避
                
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
                
                # 使用requests直接调用API
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{self.base_url}chat/completions",
                    headers=headers,
                    json=api_params,
                    timeout=300  # 增加到5分钟超时，适应长报告生成
                )
                
                response.raise_for_status()  # 检查HTTP错误
            
                result_json = response.json()
                
                # 详细调试信息
                print(f"\n[API响应调试]")
                print(f"- HTTP状态码: {response.status_code}")
                print(f"- 响应choices长度: {len(result_json.get('choices', []))}")
                
                if 'choices' not in result_json or len(result_json['choices']) == 0:
                    raise Exception("API返回数据格式错误")
                
                result = result_json['choices'][0]['message']['content']
                
                # 检查是否为空
                if result is None:
                    print(f"⚠️ 警告: API返回内容为None")
                    result = ""
                elif not result or result.strip() == "":
                    print(f"⚠️ 警告: API返回空字符串")
                    
                # 检查finish_reason
                if 'finish_reason' in result_json['choices'][0]:
                    finish_reason = result_json['choices'][0]['finish_reason']
                    print(f"- finish_reason: {finish_reason}")
                    if finish_reason == 'length':
                        print(f"⚠️ 警告: 响应因达到max_tokens限制而被截断！")
                    elif finish_reason == 'stop':
                        print(f"✓ 响应正常结束")
                        
                print(f"✓ API调用成功，返回内容长度: {len(result)} 字符")
                return result
                    
            except requests.exceptions.HTTPError as e:
                # 获取错误响应详情
                error_response = None
                try:
                    error_response = e.response.json()
                except:
                    error_response = e.response.text
                
                print(f"\n✗ API调用失败 (HTTP {e.response.status_code})")
                print(f"错误响应: {error_response}")
                
                # 429错误需要重试
                if e.response.status_code == 429:
                    print(f"\n⚠️ API速率限制 (429 Too Many Requests)")
                    if attempt < retry_count - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"将在{wait_time}秒后重试...")
                        continue  # 重试
                    else:
                        print(f"已达到最大重试次数")
                        raise Exception(f"API调用失败(速率限制): 请稍后再试")
                # 400错误 - 请求参数问题
                elif e.response.status_code == 400:
                    print(f"\n❌ API请求参数错误 (400 Bad Request)")
                    print(f"请求参数:")
                    print(f"- Model: {api_params.get('model')}")
                    print(f"- Temperature: {api_params.get('temperature')}")
                    print(f"- Max tokens: {api_params.get('max_tokens', 'None')}")
                    print(f"- Messages数量: {len(api_params.get('messages', []))}")
                    if error_response:
                        print(f"\n智谱AI错误详情: {error_response}")
                    raise Exception(f"API请求参数错误: {error_response}")
                else:
                    import traceback
                    error_detail = traceback.format_exc()
                    print(f"\n✗ API调用失败 (HTTP错误)")
                    print(f"错误类型: {type(e).__name__}")
                    print(f"错误信息: {str(e)}")
                    print(f"详细堆栈:\n{error_detail}")
                    raise Exception(f"API调用失败: {str(e)}")
            except requests.exceptions.RequestException as e:
                import traceback
                error_detail = traceback.format_exc()
                print(f"\n✗ API调用失败 (网络错误)")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                print(f"详细堆栈:\n{error_detail}")
                raise Exception(f"API调用失败: {str(e)}")
            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                print(f"\n✗ API调用失败")
                print(f"错误类型: {type(e).__name__}")
                print(f"错误信息: {str(e)}")
                print(f"详细堆栈:\n{error_detail}")
                raise Exception(f"API调用失败: {str(e)}")
        
        # 所有重试都失败
        raise Exception(f"API调用失败: 已达到最大重试次数")
    
    def _preprocess_data_with_ai(self, compressed_text, enable_ai_insights=False):  
        """
        第二阶段：对纯文本格式的数据进行 AI 预分析
        注意：输入和输出全部为纯文本格式，不使用 JSON
        :param compressed_text: 压缩后的纯文本数据
        :param enable_ai_insights: 是否启用AI洞察（默认关闭以节省API调用）
        :return: AI洞察的纯文本格式，如果未启用则返回空字符串
        """
        print("\n" + "="*80)
        print("[第二阶段] AI数据预分析开始")
        print("="*80)
        
        # 如果未启用AI洞察，直接返回空字符串
        if not enable_ai_insights:
            print("[跳过] AI洞察已禁用，直接进入下一阶段")
            print("[提示] 这将节省一次API调用，避免速率限制")
            print("\n" + "="*80)
            print("[第二阶段] AI数据预分析结束")
            print("="*80 + "\n")
            return ""  # 返回空字符串而不是None
        
        print(f"\n[数据输入] 文本长度: {len(compressed_text)} 字符")
        print(f"\n[文本预览]\n{compressed_text[:500]}...\n")
        
        # 构造AI预分析提示词（要求返回纯文本）
        prompt = f"""你是一位专业的资产管理分析师，请对以下资产数据进行全面分析。

{compressed_text}

请以纯文本格式返回分析结果，不要使用JSON格式。

请按以下结构输出：

【整体总结】
(用 60 字以内总结资产整体情况)

【关键亮点】
- 亮点1：...
- 亮点2：...
- 亮点3：...

【需要关注的问题】
- 问题1：...
- 问题2：...

【配置分析】
(用 40 字以内分析资产配置情况)

【健康评分】
评分：75/100

分析要求：
1. 全面审视所有分类和项目
2. 识别资产配置不合理之处
3. 标注高浪费率分类
4. 发现潜在风险
5. 只返回纯文本，不要JSON或Markdown格式
"""
        
        print(f"\n[AI请求] Prompt长度: {len(prompt)} 字符")
        print(f"\n[Prompt内容]\n{prompt}")
        print("\n" + "-"*80)
        
        try:
            print("\n[调用API] 开始调用智谱AI...")
            response_text = self._call_api(prompt)
            
            print(f"\n[API响应] 原始响应长度: {len(response_text)} 字符")
            print(f"\n[AI洞察 - 纯文本格式]\n{response_text}")
            print("\n" + "-"*80)
            
            # 清理响应文本（移除可能的代码标记）
            cleaned_text = response_text.strip()
            if '```' in cleaned_text:
                # 如果AI不听话还是返回了代码块，就提取出来
                parts = cleaned_text.split('```')
                if len(parts) >= 3:
                    cleaned_text = parts[1].strip()
                    if cleaned_text.startswith('text') or cleaned_text.startswith('plaintext'):
                        cleaned_text = '\n'.join(cleaned_text.split('\n')[1:])
                    print("[文本清理] 移除了```标记")
            
            print(f"\n[✓ 成功] AI预分析完成，返回纯文本洞察")
            print("\n" + "="*80)
            print("[第二阶段] AI数据预分析结束")
            print("="*80 + "\n")
            
            return cleaned_text
                
        except Exception as e:
            print(f"\n[异常] ✗ AI预分析发生错误: {e}")
            import traceback
            print(f"[堆栈信息]\n{traceback.format_exc()}")
            print("\n[降级处理] 返回空字符串，继续执行")
            print("\n" + "="*80)
            print("[第二阶段] AI数据预分析结束")
            print("="*80 + "\n")
            return ""
    
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
    
    def _get_previous_period_data(self, user_id, start_date, end_date):
        """
        获取上一期的数据（同等时长）
        :param user_id: 用户ID
        :param start_date: 当前期开始日期
        :param end_date: 当前期结束日期
        :return: 上期数据或None
        """
        from datetime import datetime, timedelta
        
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
            # 尝试查询上期数据
            previous_data = self.prepare_asset_data(user_id, prev_start, prev_end)
            return previous_data
        except Exception as e:
            print(f"[上期查询] 未找到上期数据: {str(e)}")
            return None
    
    def _generate_comparison_text(self, current_data, previous_data):
        """
        生成当前期与上期的对比分析文本
        :param current_data: 当前期数据
        :param previous_data: 上期数据
        :return: 对比分析文本
        """
        if not previous_data:
            return ""
        
        lines = []
        lines.append("【上期数据对比】")
        lines.append("")
        
        # 固定资产对比
        curr_fa = current_data['fixed_assets']
        prev_fa = previous_data['fixed_assets']
        
        lines.append("固定资产变化:")
        
        # 总价值对比
        value_change = curr_fa['total_current_value'] - prev_fa['total_current_value']
        value_change_pct = (value_change / prev_fa['total_current_value'] * 100) if prev_fa['total_current_value'] > 0 else 0
        lines.append(f"- 当前总值: ¥{curr_fa['total_current_value']:,.2f} (上期¥{prev_fa['total_current_value']:,.2f}, {'+' if value_change >= 0 else ''}{value_change_pct:.1f}%)")
        
        # 收入对比
        income_change = curr_fa['total_income'] - prev_fa['total_income']
        income_change_pct = (income_change / prev_fa['total_income'] * 100) if prev_fa['total_income'] > 0 else 0
        lines.append(f"- 期间收入: ¥{curr_fa['total_income']:,.2f} (上期¥{prev_fa['total_income']:,.2f}, {'+' if income_change >= 0 else ''}{income_change_pct:.1f}%)")
        
        lines.append("")
        
        # 虚拟资产对比
        curr_va = current_data['virtual_assets']
        prev_va = previous_data['virtual_assets']
        
        lines.append("虚拟资产变化:")
        
        # 利用率对比
        util_change = curr_va['utilization_rate'] - prev_va['utilization_rate']
        lines.append(f"- 利用率: {curr_va['utilization_rate']:.1f}% (上期{prev_va['utilization_rate']:.1f}%, {'+' if util_change >= 0 else ''}{util_change:.1f}%)")
        
        # 浪费率对比
        waste_change = curr_va['waste_rate'] - prev_va['waste_rate']
        lines.append(f"- 浪费率: {curr_va['waste_rate']:.1f}% (上期{prev_va['waste_rate']:.1f}%, {'+' if waste_change >= 0 else ''}{waste_change:.1f}%)")
        
        # 浪费金额对比
        wasted_change = curr_va['total_wasted_value'] - prev_va['total_wasted_value']
        lines.append(f"- 浪费金额: ¥{curr_va['total_wasted_value']:,.2f} (上期¥{prev_va['total_wasted_value']:,.2f}, {'+' if wasted_change >= 0 else ''}{wasted_change:,.2f})")
        
        return "\n".join(lines)
    
    def _generate_chart_data(self, current_data, previous_data=None):
        """
        生成前端图表所需的数据
        :param current_data: 当前期数据
        :param previous_data: 上期数据（可选）
        :return: 图表数据字典
        """
        chart_data = {}
        
        # 1. 资产配置饼图
        chart_data['asset_allocation_pie'] = [
            {
                'name': '固定资产',
                'value': float(current_data['fixed_assets']['total_current_value'])
            },
            {
                'name': '虚拟资产',
                'value': float(current_data['virtual_assets']['total_amount'])
            }
        ]
        
        # 2. 健康评分雷达图（示例数据，实际应根据分析计算）
        fa_health = min(100, (current_data['fixed_assets']['total_current_value'] / 
                              max(1, current_data['fixed_assets']['total_original_value']) * 100))
        va_health = current_data['virtual_assets']['utilization_rate']
        income_health = min(100, (current_data['fixed_assets']['total_income'] / 1000) * 100) if current_data['fixed_assets']['total_income'] > 0 else 0
        waste_health = max(0, 100 - current_data['virtual_assets']['waste_rate'] * 3)
        
        chart_data['health_score_radar'] = [
            {'dimension': '固定资产', 'score': round(fa_health * 0.25, 1)},
            {'dimension': '虚拟资产', 'score': round(va_health * 0.25, 1)},
            {'dimension': '收入表现', 'score': round(income_health * 0.25, 1)},
            {'dimension': '浪费控制', 'score': round(waste_health * 0.25, 1)}
        ]
        
        # 3. 固定资产分类柱状图
        if current_data['fixed_assets']['category_stats']:
            chart_data['fixed_asset_categories'] = [
                {
                    'category': cat_name,
                    'value': float(cat_data['total_value'])
                }
                for cat_name, cat_data in current_data['fixed_assets']['category_stats'].items()
            ]
        else:
            chart_data['fixed_asset_categories'] = []
        
        # 4. 虚拟资产利用率表格
        if current_data['virtual_assets']['category_stats']:
            chart_data['virtual_asset_utilization'] = [
                {
                    'category': cat_name,
                    'utilization': round((cat_data['total_amount'] - cat_data['wasted_value']) / 
                                        max(1, cat_data['total_amount']) * 100, 1),
                    'waste': round(cat_data['wasted_value'] / 
                                  max(1, cat_data['total_amount']) * 100, 1)
                }
                for cat_name, cat_data in current_data['virtual_assets']['category_stats'].items()
            ]
        else:
            chart_data['virtual_asset_utilization'] = []
        
        return chart_data
    
    
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
        """
        生成统一的报告Prom pt（适用于周报/月报/年报/自定义）
        :param report_type: 报告类型：weekly/monthly/yearly/custom
        :param processed_data: 处理后的数据
        :param compressed_text: 压缩后的文本
        :param ai_insights_text: AI洞察文本
        :return: Prompt字符串
        """
        report_names = {
            'weekly': '周报',
            'monthly': '月报',
            'yearly': '年报',
            'custom': '自定义报告'
        }
        
        return f"""你是专业的个人资产管理顾问。基于以下数据生成一份结构完整、数据详实、结论清晰的资产{report_names.get(report_type, '报告')}。

===== 数据源 =====
{compressed_text}{ai_insights_text}

===== 输出要求 =====
**必须返回严格的JSON格式**，包含以下所有字段：

{{
    "executive_summary": {{
        "title": "📊 执行摘要",
        "content": "200字以内：❶总资产¥XX万（固定XX%、虚拟XX%）❷最重要发现 ❸紧急行动 ❹健康评分XX/100",
        "highlight": "🔴 最重要的1-2个结论（用emoji和数据标记）"
    }},
    
    "key_conclusions": [
        {{
            "type": "critical",
            "title": "🔴 关键发现",
            "content": "具体数据+占比+影响",
            "action": "立即采取的行动"
        }},
        {{
            "type": "warning",
            "title": "⚠️ 重要警示",
            "content": "具体数据+占比+风险",
            "action": "近期需要的措施"
        }},
        {{
            "type": "opportunity",
            "title": "✅ 积极信号",
            "content": "具体数据+占比+潜力",
            "action": "优化建议"
        }}
    ],
    
    "fixed_asset_analysis": {{
        "summary": "固定资产总览：总价值¥XX，共XX项，在用XX%，闲置XX%，折旧¥XX",
        "health_status": {{
            "score": 85,
            "rating": "优秀/良好/一般/较差",
            "trend": "上升/稳定/下降"
        }},
        "category_breakdown": [
            {{
                "name": "分类名称",
                "count": 数量,
                "original_value": 原值,
                "current_value": 现值,
                "usage_rate": 使用率%,
                "status": "健康/正常/预警",
                "insight": "该分类的核心发现和建议"
            }}
        ],
        "key_insights": [
            "洞察1：具体分类+数据+问题/亮点",
            "洞察2：价值变动+驱动因素",
            "洞察3：折旧合理性+优化空间"
        ]
    }},
    
    "virtual_asset_analysis": {{
        "summary": "虚拟资产总览：总投入¥XX，活跃XX项，过期XX项，利用率XX%，浪费率XX%",
        "efficiency_status": {{
            "utilization_rate": 利用率%,
            "waste_rate": 浪费率%,
            "rating": "优秀/良好/一般/较差"
        }},
        "category_breakdown": [
            {{
                "name": "分类名称",
                "total_amount": 总投入,
                "active_value": 活跃价值,
                "wasted_value": 浪费价值,
                "utilization": 利用率%,
                "status": "高效/正常/低效",
                "insight": "该分类的核心发现和建议"
            }}
        ],
        "expiring_alerts": [
            {{
                "project": "项目名",
                "days_left": 剩余天数,
                "value": 剩余价值,
                "urgency": "紧急/重要/一般"
            }}
        ],
        "key_insights": [
            "洞察1：TOP3高浪费分类+金额+原因",
            "洞察2：过期风险+应对方案",
            "洞察3：ROI分析+优化建议"
        ]
    }},
    
    "income_performance": {{
        "summary": "收入：总计¥XX，来源XX个分类，环比XX%",
        "income_structure": [
            {{"source": "来源分类", "amount": 金额, "percentage": 占比%}}
        ],
        "quality_assessment": {{
            "stability": "稳定性评分0-100",
            "diversity": "多元化评分0-100",
            "concentration_risk": "集中度风险：高/中/低"
        }},
        "key_insights": [
            "洞察1：收入结构+稳定性",
            "洞察2：增长潜力+瓶颈",
            "洞察3：多元化建议"
        ]
    }},
    
    "asset_allocation_review": {{
        "current_allocation": {{
            "fixed_percentage": 固定资产占比%,
            "virtual_percentage": 虚拟资产占比%,
            "balance_score": 配置平衡分0-100,
            "assessment": "配置评价：合理/偏重固定/偏重虚拟"
        }},
        "imbalances": [
            {{
                "issue": "失衡点描述",
                "current": "当前%",
                "target": "目标%",
                "impact": "影响分析",
                "action": "调整方案"
            }}
        ],
        "optimization_plan": {{
            "target_allocation": "目标配置：固定XX%、虚拟XX%",
            "increase_categories": ["需要增持的分类"],
            "decrease_categories": ["需要减持的分类"],
            "timeline": "调整时间表",
            "expected_benefit": "预期收益"
        }}
    }},
    
    "actionable_recommendations": [
        {{
            "priority": "高/中/低",
            "category": "固定资产/虚拟资产/配置/收入",
            "title": "建议标题",
            "problem": "当前问题+数据",
            "solution": "具体措施+步骤",
            "expected_result": "预期效果+时间",
            "investment": "所需投入（时间/金钱）"
        }}
    ],
    
    "risk_alerts": [
        {{
            "risk_type": "折旧贬值/虚拟浪费/配置失衡/收入集中",
            "severity": "高/中/低",
            "urgency": "紧急/重要/一般",
            "description": "风险描述+具体资产/项目+金额",
            "probability": "发生概率%",
            "impact": "潜在损失¥XX或影响",
            "mitigation": "缓解措施"
        }}
    ],
    
    "health_score": {{
        "overall_score": 75,
        "rating": "优秀(90-100)/良好(75-89)/一般(60-74)/较差(<60)",
        "trend": "较上期：上升+5/稳定/下降-3",
        "breakdown": {{
            "fixed_assets": {{"score": 20, "max": 25, "comment": "评价"}},
            "virtual_assets": {{"score": 18, "max": 25, "comment": "评价"}},
            "income_performance": {{"score": 20, "max": 25, "comment": "评价"}},
            "allocation_balance": {{"score": 17, "max": 25, "comment": "评价"}}
        }},
        "improvement_suggestions": [
            "提分措施1：具体行动+预期提升分数",
            "提分措施2：具体行动+预期提升分数"
        ]
    }},
    
    "next_period_focus": [
        {{
            "task": "任务描述",
            "target": "量化目标",
            "deadline": "完成期限",
            "expected_impact": "预期效果"
        }}
    ],
    
    "chart_data": {{
        "asset_allocation_pie": [
            {{"name": "固定资产", "value": {processed_data['fixed_assets']['total_current_value']}, "color": "#1890ff"}},
            {{"name": "虚拟资产", "value": {processed_data['virtual_assets']['total_amount']}, "color": "#52c41a"}}
        ],
        "fixed_asset_categories": [
            {{"category": "分类名", "count": 数量, "value": 现值, "status": "优秀/良好/一般/较差"}}
        ],
        "virtual_asset_utilization": [
            {{"category": "分类名", "utilization": 利用率%, "waste": 浪费率%, "status": "高效/正常/低效"}}
        ],
        "income_trend": [
            {{"period": "时间段", "amount": 金额}}
        ],
        "health_score_radar": [
            {{"dimension": "固定资产", "score": 得分, "fullScore": 25}},
            {{"dimension": "虚拟资产", "score": 得分, "fullScore": 25}},
            {{"dimension": "收入表现", "score": 得分, "fullScore": 25}},
            {{"dimension": "配置合理", "score": 得分, "fullScore": 25}}
        ],
        "waste_ranking": [
            {{"category": "高浪费分类", "amount": 浪费金额, "rate": 浪费率%}}
        ]
    }}
}}

===== 核心要求 =====
1. **数据真实性**：所有数字必须基于提供的数据，禁止编造
2. **结论清晰**：每个分析都要有明确结论，用🔴⚠️✅等emoji突出重点
3. **图表完整**：chart_data所有图表数据必须填充真实数值
4. **分类全覆盖**：逐一分析每个资产分类，不遗漏
5. **建议可执行**：建议包含具体步骤、时间、预期效果
6. **风险量化**：风险包含严重度、紧急度、概率、影响
7. **健康评分**：有明确的评分依据和计算逻辑
8. **JSON格式**：字符串值内不换行，一行完成
9. **纯JSON输出**：不要任何``json```标记或其他文字
10. **中文表达**：除ROI、emoji等，全部使用中文
11. **❗禁止数学表达式❗**：所有数值必须是计算好的具体数字，禁止使用 3500-3121.79 这种表达式，必须写378.21

===== 特别强调 =====
- 重点结论用**加粗**、🔴红色标记、或💰金额突出
- 每个分析模块都要有清晰的summary总结
- chart_data必须包含所有６类图表的完整数据
- key_conclusions必须提炼３个最重要的发现
- 每个category_breakdown都要包含真实的分类数据
- 所有建议都要有priority优先级和可执行方案

⚠️ **JSON格式质量控制** ⚠️
1. 严禁在字符串内使用换行符\n，全部内容必须写在一行内
2. 禁止使用不合法的Unicode字符或特殊控制字符
3. 所有逗号、冒号、括号必须成对出现，不能漏掉
4. 数组最后一个元素、对象最后一个字段后面不能有逗号
5. 字符串值内的引号必须转义：\" 而不是 "
6. 输出前自检JSON格式，确保可被解析器解析
7. 绝对不要输出 ```json``` 标记，直接输出纯JSON
"""
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
    
    def generate_weekly_report(self, user_id, start_date, end_date, 
                              qualitative_analysis=None, intelligent_insights=None):
        """
        生成周报（三阶段流程 - 纯文本中间格式）
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param qualitative_analysis: 【新增】AI定性分析结论
        :param intelligent_insights: 【新增】智能洞察指标
        :return: 报告内容（JSON格式）
        """
        print("\n" + "#"*80)
        print("# 周报生成三阶段流程开始")
        print("# 注意：中间阶段全部使用纯文本格式，最终输出JSON")
        print("#"*80 + "\n")
        
        # ===== 第一阶段：数据查询（当前期+上期） =====
        print("\n" + "="*80)
        print("[第一阶段] 数据查询开始")
        print("="*80)
        
        # 查询当前期数据
        current_data = self.prepare_asset_data(user_id, start_date, end_date)
        print(f"✓ 当前期数据查询完成: {start_date} 至 {end_date}")
        
        # 查询上期数据（同等时长）
        previous_data = self._get_previous_period_data(user_id, start_date, end_date)
        if previous_data:
            print(f"✓ 上期数据查询完成: {previous_data['period']['start_date']} 至 {previous_data['period']['end_date']}")
        else:
            print("⚠ 未找到上期数据，将仅分析当前期数据")
        
        print("="*80)
        print("[第一阶段] 数据查询完成")
        print("="*80 + "\n")
        
        # 立即将结构化数据转换为纯文本格式
        current_text = self._compress_data_to_text(current_data)
        print(f"\n[文本转换] 当前期数据转换完成: {len(current_text)} 字符")
        
        # 生成对比分析文本
        comparison_text = self._generate_comparison_text(current_data, previous_data) if previous_data else ""
        if comparison_text:
            print(f"[对比分析] 生成对比文本: {len(comparison_text)} 字符")
        
        # 合并为完整的数据文本
        compressed_text = current_text + "\n\n" + comparison_text
        print(f"\n[文本预览]\n{compressed_text[:500]}...\n")
        
        # ===== 第二阶段：AI数据预分析（可选，输入和输出都是纯文本） =====
        ai_insights_text = self._preprocess_data_with_ai(compressed_text, enable_ai_insights=False)
        
        # ===== 第三阶段：生成报告（输入纯文本，输出Markdown） =====
        print("\n" + "="*80)
        print("[第三阶段] 报告生成开始")
        print("="*80)
        
        # 【增强】显示定性分析信息
        if qualitative_analysis:
            print("\n🎯 [利用定性分析] AI已提供定性结论，将指导报告生成")
            print(f"  - 整体评估: {qualitative_analysis.get('overall_assessment')}")
            print(f"  - 紧急程度: {qualitative_analysis.get('severity_level')}")
            print(f"  - 关键问题: {len(qualitative_analysis.get('key_issues', []))}个")
            print(f"  - 重点关注: {', '.join(qualitative_analysis.get('focus_areas', [])[:2])}")
        
        if intelligent_insights:
            print("\n📊 [智能洞察] 已提供智能指标，将增强分析深度")
            print(f"  - 固定资产健康度: {intelligent_insights.get('fixed_asset_health', 0):.1f}/100")
            print(f"  - 虚拟资产效率: {intelligent_insights.get('virtual_asset_efficiency', 0):.1f}/100")
        
        # 构造报告生成Prompt（使用配置文件，传入对比数据 + 定性分析）
        prompt = get_weekly_report_prompt(
            compressed_text, ai_insights_text, current_data, previous_data,
            intelligent_insights=intelligent_insights,  # 【新增】
            qualitative_analysis=qualitative_analysis   # 【新增】
        )
        print(f"[Prompt版本] {PROMPT_VERSION}")
        
        print(f"\n[报告Prompt] Prompt长度: {len(prompt)} 字符")
        print(f"\n[Prompt完整内容]\n{prompt}")
        print("\n" + "-"*80)
        
        print("\n[调用API] 开始生成周报...")
        response_text = self._call_api(prompt)  # 不限制max_tokens，让模型自由输出
        
        print(f"\n[API响应] 周报原始响应长度: {len(response_text)} 字符")
        print(f"\n[周报Markdown内容预览]\n{response_text[:1000]}...")
        print("\n" + "-"*80)
        
        # 直接返回Markdown文本，不需要JSON解析
        markdown_report = response_text.strip()
        
        # 移除可能的markdown代码块标记
        if '```markdown' in markdown_report:
            markdown_report = markdown_report.split('```markdown')[1].split('```')[0].strip()
            print("[Markdown清理] 移除了```markdown```标记")
        elif markdown_report.startswith('```') and markdown_report.endswith('```'):
            markdown_report = markdown_report.strip('`').strip()
            print("[Markdown清理] 移除了代码块标记")
        
        # 生成图表数据
        chart_data = self._generate_chart_data(current_data, previous_data)
        print(f"[图表数据] 已生成{len(chart_data)}个图表")
        print(f"[图表数据详情]")
        for chart_name, chart_value in chart_data.items():
            print(f"  - {chart_name}: {len(chart_value) if isinstance(chart_value, list) else 'N/A'}项")
            if isinstance(chart_value, list) and len(chart_value) > 0:
                print(f"    示例: {chart_value[0]}")
        
        # 构造返回结果（保持兼容性，但主要内容是markdown + 图表数据）
        result = {
            "report_type": "markdown",
            "content": markdown_report,
            "chart_data": chart_data,  # 新增图表数据
            "intelligent_insights": intelligent_insights,  # 【新增】智能洞察
            "qualitative_analysis": qualitative_analysis,  # 【新增】定性分析
            "data_snapshot": current_data,
            "generated_at": current_data['period']['end_date']
        }
        
        print("\n" + "="*80)
        print("[第三阶段] 报告生成完成 - 文本格式")
        print("="*80)
        
        print("\n" + "#"*80)
        print("# 周报生成三阶段流程结束")
        print("#"*80 + "\n")
        
        return json.dumps(result, ensure_ascii=False)
    
    def generate_monthly_report(self, user_id, start_date, end_date,
                               qualitative_analysis=None, intelligent_insights=None):
        """
        生成月报（三阶段流程 - Markdown格式）
        :param qualitative_analysis: 【新增】AI定性分析结论
        :param intelligent_insights: 【新增】智能洞察指标
        """
        print("\n" + "#"*80)
        print("# 月报生成三阶段流程开始")
        print("# 注意：中间阶段全部使用纯文本格式，最终输出Markdown")
        print("#"*80 + "\n")
        
        # ===== 第一阶段：数据查询 + 立即转文本 =====
        print("\n" + "="*80)
        print("[第一阶段] 数据查询开始")
        print("="*80)
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        print("="*80)
        print("[第一阶段] 数据查询完成")
        print("="*80 + "\n")
        
        # 立即将结构化数据转换为纯文本格式
        compressed_text = self._compress_data_to_text(asset_data)
        print(f"\n[文本转换] 将结构化数据转换为纯文本: {len(compressed_text)} 字符")
        
        # ===== 第二阶段：AI数据预分析（可选，输入和输出都是纯文本） =====
        ai_insights_text = self._preprocess_data_with_ai(compressed_text, enable_ai_insights=False)
        
        # ===== 第三阶段：生成报告（输入纯文本，输出Markdown） =====
        print("\n" + "="*80)
        print("[第三阶段] 报告生成开始")
        print("="*80)
        
        # 构造报告生成Prompt（使用配置文件）
        prompt = get_monthly_report_prompt(compressed_text, ai_insights_text, asset_data)
        print(f"[Prompt版本] {PROMPT_VERSION}")
        print(f"\n[报告Prompt] Prompt长度: {len(prompt)} 字符")
        
        print("\n[调用API] 开始生成月报...")
        response_text = self._call_api(prompt)  # 不限制max_tokens，让模型自由输出
        
        print(f"\n[API响应] 月报原始响应长度: {len(response_text)} 字符")
        print(f"\n[月报Markdown内容预览]\n{response_text[:1000]}...")
        print("\n" + "-"*80)
        
        # 直接返回Markdown文本，不需要JSON解析
        markdown_report = response_text.strip()
        
        # 移除可能的markdown代码块标记
        if '```markdown' in markdown_report:
            markdown_report = markdown_report.split('```markdown')[1].split('```')[0].strip()
            print("[Markdown清理] 移除了```markdown```标记")
        elif markdown_report.startswith('```') and markdown_report.endswith('```'):
            markdown_report = markdown_report.strip('`').strip()
            print("[Markdown清理] 移除了代码块标记")
        
        # 构造返回结果（保持兼容性，但主要内容是markdown）
        result = {
            "report_type": "markdown",
            "content": markdown_report,
            "data_snapshot": asset_data,
            "generated_at": asset_data['period']['end_date']
        }
        
        print("\n" + "="*80)
        print("[第三阶段] 报告生成完成 - 文本格式")
        print("="*80)
        
        print("\n" + "#"*80)
        print("# 月报生成三阶段流程结束")
        print("#"*80 + "\n")
        
        return json.dumps(result, ensure_ascii=False)
    
    def generate_custom_report(self, user_id, start_date, end_date, focus_areas=None,
                              qualitative_analysis=None, intelligent_insights=None):
        """
        生成自定义报告（Markdown格式）
        :param user_id: 用户ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param focus_areas: 关注领域列表
        :param qualitative_analysis: 【新增】AI定性分析结论
        :param intelligent_insights: 【新增】智能洞察指标
        :return: 报告内容（Markdown格式）
        """
        print("\n" + "#"*80)
        print("# 自定义报告生成三阶段流程开始")
        print("# 注意：中间阶段全部使用纯文本格式，最终输出Markdown")
        print("#"*80 + "\n")
        
        # ===== 第一阶段：数据查询 + 立即转文本 =====
        print("\n" + "="*80)
        print("[第一阶段] 数据查询开始")
        print("="*80)
        asset_data = self.prepare_asset_data(user_id, start_date, end_date)
        print("="*80)
        print("[第一阶段] 数据查询完成")
        print("="*80 + "\n")
        
        # 立即将结构化数据转换为纯文本格式
        compressed_text = self._compress_data_to_text(asset_data)
        print(f"\n[文本转换] 将结构化数据转换为纯文本: {len(compressed_text)} 字符")
        
        # ===== 第二阶段：AI数据预分析（可选，输入和输出都是纯文本） =====
        ai_insights_text = self._preprocess_data_with_ai(compressed_text, enable_ai_insights=False)
        
        # ===== 第三阶段：生成报告（输入纯文本，输出Markdown） =====
        print("\n" + "="*80)
        print("[第三阶段] 报告生成开始")
        print("="*80)
        
        # 添加特别关注信息（如果有）
        focus_text = ""
        if focus_areas:
            focus_text = f"\n\n【特别关注】\n请在报告中重点分析以下方面：{', '.join(focus_areas)}\n"
            compressed_text += focus_text
        
        # 构造报告生成Prompt（使用配置文件）
        prompt = get_custom_report_prompt(compressed_text, ai_insights_text, asset_data)
        print(f"[Prompt版本] {PROMPT_VERSION}")
        print(f"\n[报告Prompt] Prompt长度: {len(prompt)} 字符")
        
        print("\n[调用API] 开始生成自定义报告...")
        response_text = self._call_api(prompt)  # 不限制max_tokens，让模型自由输出
        
        print(f"\n[API响应] 自定义报告原始响应长度: {len(response_text)} 字符")
        print(f"\n[自定义报告Markdown内容预览]\n{response_text[:1000]}...")
        print("\n" + "-"*80)
        
        # 直接返回Markdown文本，不需要JSON解析
        markdown_report = response_text.strip()
        
        # 移除可能的代码块标记
        if '```' in markdown_report:
            markdown_report = markdown_report.split('```')[1].split('```')[0].strip()
            print("[文本清理] 移除了``标记")
        elif markdown_report.startswith('``') and markdown_report.endswith('```'):
            markdown_report = markdown_report.strip('`').strip()
            print("[文本清理] 移除了代码块标记")
        
        # 构造返回结果（保持兼容性，但主要内容是文本）
        result = {
            "report_type": "text",
            "content": markdown_report,
            "data_snapshot": asset_data,
            "generated_at": asset_data['period']['end_date'],
            "focus_areas": focus_areas if focus_areas else []
        }
        
        print("\n" + "="*80)
        print("[第三阶段] 报告生成完成 - 文本格式")
        print("="*80)
        
        print("\n" + "#"*80)
        print("# 自定义报告生成三阶段流程结束")
        print("#"*80 + "\n")
        
        return json.dumps(result, ensure_ascii=False)
