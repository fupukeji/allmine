"""
智谱AI服务 - 重构版本
使用官方 zai-sdk,关闭流式输出,移除 max_tokens 限制
"""

import json
import re
from zai import ZhipuAiClient
from prompts.asset_analysis_prompts import (
    get_system_prompt,
    get_asset_analysis_prompt,
    get_weekly_report_prompt,
    get_monthly_report_prompt,
    get_yearly_report_prompt
)
from services.data_service import AssetDataService
from services.data_formatter import DataFormatter


class ZhipuAIService:
    """智谱AI服务类 - 使用官方SDK"""
    
    def __init__(self, api_key, model="glm-4-flash"):
        """
        初始化服务
        
        Args:
            api_key: 智谱AI API Key
            model: 模型名称,默认 glm-4-flash (免费且高速)
        """
        self.client = ZhipuAiClient(api_key=api_key)
        self.model = model
        print(f"✓ 智谱AI服务初始化成功 - 模型: {model}")
    
    def call_ai(self, prompt, system_prompt=None):
        """
        调用AI模型 - 非流式模式,无token限制
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词(可选)
        
        Returns:
            str: AI响应内容
        """
        try:
            print(f"\n=== 调用AI模型 ===")
            print(f"模型: {self.model}")
            print(f"Prompt长度: {len(prompt)} 字符")
            print(f"流式输出: 关闭")
            print(f"Token限制: 无")
            
            # 构建消息
            messages = []
            
            # 添加系统提示词
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                # 使用默认系统提示词
                messages.append({
                    "role": "system",
                    "content": get_system_prompt()
                })
            
            # 添加用户提示词
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用API - 关闭流式,无token限制
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                # 不设置 max_tokens,让模型自由输出
                # 不设置 stream=True,使用非流式模式
            )
            
            # 获取响应内容
            result = response.choices[0].message.content
            
            print(f"✓ AI响应成功")
            print(f"响应长度: {len(result)} 字符")
            print(f"Finish reason: {response.choices[0].finish_reason}")
            
            return result
            
        except Exception as e:
            print(f"✗ AI调用失败: {str(e)}")
            import traceback
            print(f"错误详情:\n{traceback.format_exc()}")
            raise Exception(f"AI调用失败: {str(e)}")
    
    def clean_ai_response(self, response_text, expected_format="json"):
        """
        清理AI响应,处理标点符号和特殊字符
        
        Args:
            response_text: AI原始响应
            expected_format: 期望格式 json/markdown/text
        
        Returns:
            清理后的文本
        """
        cleaned = response_text.strip()
        
        if expected_format == "json":
            # 移除可能的代码块标记
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif cleaned.startswith("```") and cleaned.endswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1]).strip()
            
            # 尝试解析JSON,确保格式正确
            try:
                json_obj = json.loads(cleaned)
                # 重新序列化,确保格式规范
                cleaned = json.dumps(json_obj, ensure_ascii=False, indent=2)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败: {str(e)}")
                print(f"原始内容: {cleaned[:500]}...")
                # 尝试修复常见JSON错误
                cleaned = self._fix_json_errors(cleaned)
        
        elif expected_format == "markdown":
            # 移除markdown代码块标记
            if "```markdown" in cleaned:
                cleaned = cleaned.split("```markdown")[1].split("```")[0].strip()
            elif cleaned.startswith("```") and cleaned.endswith("```"):
                cleaned = cleaned.strip("`").strip()
        
        return cleaned
    
    def _fix_json_errors(self, json_text):
        """尝试修复常见的JSON错误"""
        # 1. 移除尾部多余的逗号
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        # 2. 确保所有键都有引号
        json_text = re.sub(r'(\w+):', r'"\1":', json_text)
        
        try:
            json.loads(json_text)
            return json_text
        except:
            # 如果还是失败,返回原文
            return json_text
    
    def analyze_assets(self, user_id, start_date, end_date, focus="综合分析"):
        """
        分析资产数据并返回结构化结果
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            focus: 分析重点
        
        Returns:
            dict: 分析结果JSON
        """
        print("\n" + "="*80)
        print("🎯 资产分析流程开始")
        print("="*80)
        
        # 第一步: 查询数据
        print("\n[步骤1] 查询数据...")
        asset_data = AssetDataService.query_asset_data(user_id, start_date, end_date)
        
        # 第二步: 格式化数据
        print("\n[步骤2] 格式化数据...")
        data_text = DataFormatter.format_asset_data(asset_data)
        print(f"格式化完成,文本长度: {len(data_text)} 字符")
        print(f"\n[数据预览]\n{data_text[:500]}...\n")
        
        # 第三步: 生成提示词
        print("\n[步骤3] 生成提示词...")
        prompt = get_asset_analysis_prompt(data_text, focus)
        
        # 第四步: 调用AI
        print("\n[步骤4] 调用AI分析...")
        ai_response = self.call_ai(prompt)
        
        # 第五步: 清理和解析响应
        print("\n[步骤5] 处理AI响应...")
        cleaned_response = self.clean_ai_response(ai_response, "json")
        
        try:
            result = json.loads(cleaned_response)
            print("✓ AI分析完成")
            print("="*80 + "\n")
            return result
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {str(e)}")
            print(f"响应内容: {cleaned_response[:1000]}...")
            raise Exception(f"AI响应解析失败: {str(e)}")
    
    def generate_weekly_report(self, user_id, start_date, end_date):
        """
        生成周报 - Markdown格式
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 包含报告内容和图表数据的字典
        """
        print("\n" + "="*80)
        print("📊 周报生成流程开始")
        print("="*80)
        
        # 查询当前期数据
        print("\n[步骤1] 查询本周数据...")
        current_data = AssetDataService.query_asset_data(user_id, start_date, end_date)
        
        # 查询上期数据
        print("\n[步骤2] 查询上周数据(用于对比)...")
        previous_data = AssetDataService.query_previous_period_data(user_id, start_date, end_date)
        
        # 格式化当前期数据
        print("\n[步骤3] 格式化数据...")
        current_text = DataFormatter.format_asset_data(current_data)
        
        # 格式化对比数据
        comparison_text = ""
        if previous_data:
            comparison_text = DataFormatter.format_comparison_data(current_data, previous_data)
        
        # 生成提示词
        print("\n[步骤4] 生成报告提示词...")
        prompt = get_weekly_report_prompt(current_text, comparison_text)
        
        # 调用AI生成报告
        print("\n[步骤5] AI生成周报...")
        ai_response = self.call_ai(prompt)
        
        # 清理响应
        print("\n[步骤6] 清理报告内容...")
        report_markdown = self.clean_ai_response(ai_response, "markdown")
        
        # 生成图表数据
        print("\n[步骤7] 生成图表数据...")
        chart_data = self._generate_chart_data(current_data, previous_data)
        
        result = {
            "report_type": "markdown",
            "content": report_markdown,
            "chart_data": chart_data,
            "data_snapshot": current_data,
            "period": current_data['period']
        }
        
        print("✓ 周报生成完成")
        print("="*80 + "\n")
        
        return result
    
    def generate_monthly_report(self, user_id, start_date, end_date):
        """生成月报"""
        print("\n" + "="*80)
        print("📊 月报生成流程开始")
        print("="*80)
        
        # 查询数据
        print("\n[步骤1] 查询本月数据...")
        current_data = AssetDataService.query_asset_data(user_id, start_date, end_date)
        
        # 格式化
        print("\n[步骤2] 格式化数据...")
        data_text = DataFormatter.format_asset_data(current_data)
        
        # 生成提示词
        print("\n[步骤3] 生成报告提示词...")
        prompt = get_monthly_report_prompt(data_text)
        
        # 调用AI
        print("\n[步骤4] AI生成月报...")
        ai_response = self.call_ai(prompt)
        
        # 清理
        print("\n[步骤5] 清理报告内容...")
        report_markdown = self.clean_ai_response(ai_response, "markdown")
        
        # 图表
        print("\n[步骤6] 生成图表数据...")
        chart_data = self._generate_chart_data(current_data, None)
        
        result = {
            "report_type": "markdown",
            "content": report_markdown,
            "chart_data": chart_data,
            "data_snapshot": current_data,
            "period": current_data['period']
        }
        
        print("✓ 月报生成完成")
        print("="*80 + "\n")
        
        return result
    
    def generate_yearly_report(self, user_id, start_date, end_date):
        """生成年报"""
        print("\n" + "="*80)
        print("📊 年报生成流程开始")
        print("="*80)
        
        # 查询数据
        print("\n[步骤1] 查询本年数据...")
        current_data = AssetDataService.query_asset_data(user_id, start_date, end_date)
        
        # 格式化
        print("\n[步骤2] 格式化数据...")
        data_text = DataFormatter.format_asset_data(current_data)
        
        # 生成提示词
        print("\n[步骤3] 生成报告提示词...")
        prompt = get_yearly_report_prompt(data_text)
        
        # 调用AI
        print("\n[步骤4] AI生成年报...")
        ai_response = self.call_ai(prompt)
        
        # 清理
        print("\n[步骤5] 清理报告内容...")
        report_markdown = self.clean_ai_response(ai_response, "markdown")
        
        # 图表
        print("\n[步骤6] 生成图表数据...")
        chart_data = self._generate_chart_data(current_data, None)
        
        result = {
            "report_type": "markdown",
            "content": report_markdown,
            "chart_data": chart_data,
            "data_snapshot": current_data,
            "period": current_data['period']
        }
        
        print("✓ 年报生成完成")
        print("="*80 + "\n")
        
        return result
    
    def generate_custom_report(self, user_id, start_date, end_date, focus_areas=None):
        """
        生成自定义报告
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            focus_areas: 关注领域列表(可选)
        
        Returns:
            dict: 报告数据
        """
        print("\n" + "="*80)
        print("📊 自定义报告生成流程开始")
        print("="*80)
        
        # 查询数据
        print("\n[步骤1] 查询数据...")
        current_data = AssetDataService.query_asset_data(user_id, start_date, end_date)
        
        # 格式化
        print("\n[步骤2] 格式化数据...")
        data_text = DataFormatter.format_asset_data(current_data)
        
        # 添加特别关注信息
        if focus_areas:
            focus_text = f"\n\n【特别关注】\n请在报告中重点分析以下方面：{', '.join(focus_areas)}\n"
            data_text += focus_text
        
        # 生成提示词
        print("\n[步骤3] 生成报告提示词...")
        prompt = get_yearly_report_prompt(data_text)  # 使用年报格式
        
        # 调用AI
        print("\n[步骤4] AI生成报告...")
        ai_response = self.call_ai(prompt)
        
        # 清理
        print("\n[步骤5] 清理报告内容...")
        report_markdown = self.clean_ai_response(ai_response, "markdown")
        
        # 图表
        print("\n[步骤6] 生成图表数据...")
        chart_data = self._generate_chart_data(current_data, None)
        
        result = {
            "report_type": "markdown",
            "content": report_markdown,
            "chart_data": chart_data,
            "data_snapshot": current_data,
            "period": current_data['period'],
            "focus_areas": focus_areas if focus_areas else []
        }
        
        print("✓ 自定义报告生成完成")
        print("="*80 + "\n")
        
        return result
    
    def _generate_chart_data(self, current_data, previous_data=None):
        """
        生成图表数据
        
        Args:
            current_data: 当前期数据
            previous_data: 上期数据(可选)
        
        Returns:
            dict: ECharts配置数据
        """
        chart_data = {}
        fa = current_data['fixed_assets']
        va = current_data['virtual_assets']
        
        # 1. 资产配置饼图
        chart_data['asset_allocation_pie'] = [
            {
                'name': '固定资产',
                'value': float(fa['total_current_value'])
            },
            {
                'name': '虚拟资产',
                'value': float(va['total_amount'])
            }
        ]
        
        # 2. 固定资产分类柱状图
        if fa['category_stats']:
            chart_data['fixed_asset_categories'] = [
                {
                    'category': cat_name,
                    'value': float(cat_data['total_value']),
                    'count': cat_data['count'],
                    'original_value': float(cat_data.get('original_value', cat_data['total_value']))
                }
                for cat_name, cat_data in fa['category_stats'].items()
            ]
        else:
            chart_data['fixed_asset_categories'] = []
        
        # 3. 固定资产状态分布饼图
        if fa.get('status_stats'):
            chart_data['fixed_asset_status_pie'] = [
                {'name': status, 'value': count}
                for status, count in fa['status_stats'].items()
            ]
        else:
            chart_data['fixed_asset_status_pie'] = []
        
        # 4. 虚拟资产利用率仪表盘
        chart_data['virtual_asset_utilization_gauge'] = {
            'utilization_rate': round(va['utilization_rate'], 1),
            'waste_rate': round(va['waste_rate'], 1),
            'total_amount': float(va['total_amount']),
            'used_value': float(va['total_used_value']),
            'remaining_value': float(va['total_remaining_value']),
            'wasted_value': float(va['total_wasted_value'])
        }
        
        # 5. 虚拟资产分类利用率表格/柱状图
        if va.get('category_stats'):
            virtual_categories = []
            for cat_name, cat_data in va['category_stats'].items():
                total = cat_data['total_amount']
                wasted = cat_data.get('wasted_value', 0)
                utilization = ((total - wasted) / total * 100) if total > 0 else 0
                waste_rate = (wasted / total * 100) if total > 0 else 0
                
                virtual_categories.append({
                    'category': cat_name,
                    'count': cat_data['count'],
                    'total_amount': float(total),
                    'wasted_value': float(wasted),
                    'utilization': round(utilization, 1),
                    'waste': round(waste_rate, 1)
                })
            chart_data['virtual_asset_utilization'] = virtual_categories
        else:
            chart_data['virtual_asset_utilization'] = []
        
        # 6. 收入结构饼图
        if fa.get('income_by_category'):
            chart_data['income_structure_pie'] = [
                {
                    'source': cat_name,
                    'amount': float(amount)
                }
                for cat_name, amount in fa['income_by_category'].items()
                if amount > 0
            ]
        else:
            chart_data['income_structure_pie'] = []
        
        # 7. 健康评分雷达图
        fa_health = min(100, (fa['total_current_value'] / max(1, fa['total_original_value']) * 100))
        va_health = 100 - va['waste_rate']
        income_health = min(100, fa['total_income'] / 100) if fa['total_income'] > 0 else 50
        usage_health = min(100, (fa.get('status_stats', {}).get('在用', 0) / max(1, fa['total_assets']) * 100))
        
        chart_data['health_score_radar'] = [
            {'dimension': '固定资产', 'score': round(fa_health, 1), 'maxScore': 100},
            {'dimension': '虚拟资产', 'score': round(va_health, 1), 'maxScore': 100},
            {'dimension': '收益表现', 'score': round(income_health, 1), 'maxScore': 100},
            {'dimension': '使用效率', 'score': round(usage_health, 1), 'maxScore': 100},
            {'dimension': '风险控制', 'score': 75, 'maxScore': 100}
        ]
        
        # 8. 如果有上期数据,添加对比图表
        if previous_data:
            prev_fa = previous_data['fixed_assets']
            prev_va = previous_data['virtual_assets']
            
            # 8.1 资产价值趋势线图
            chart_data['asset_value_trend'] = [
                {
                    'period': '上期',
                    '固定资产': float(prev_fa['total_current_value']),
                    '虚拟资产': float(prev_va['total_amount']),
                    '总资产': float(prev_fa['total_current_value'] + prev_va['total_amount'])
                },
                {
                    'period': '本期',
                    '固定资产': float(fa['total_current_value']),
                    '虚拟资产': float(va['total_amount']),
                    '总资产': float(fa['total_current_value'] + va['total_amount'])
                }
            ]
            
            # 8.2 收入对比柱状图
            chart_data['income_comparison'] = [
                {'period': '上期', 'income': float(prev_fa['total_income'])},
                {'period': '本期', 'income': float(fa['total_income'])}
            ]
            
            # 8.3 利用率对比折线图
            chart_data['utilization_comparison'] = [
                {
                    'period': '上期',
                    '利用率': round(prev_va['utilization_rate'], 1),
                    '浪费率': round(prev_va['waste_rate'], 1)
                },
                {
                    'period': '本期',
                    '利用率': round(va['utilization_rate'], 1),
                    '浪费率': round(va['waste_rate'], 1)
                }
            ]
            
            # 8.4 环比变化指标
            chart_data['change_indicators'] = {
                'asset_change': {
                    'value': float(fa['total_current_value'] + va['total_amount'] - prev_fa['total_current_value'] - prev_va['total_amount']),
                    'percent': round(((fa['total_current_value'] + va['total_amount']) / max(1, prev_fa['total_current_value'] + prev_va['total_amount']) - 1) * 100, 2)
                },
                'income_change': {
                    'value': float(fa['total_income'] - prev_fa['total_income']),
                    'percent': round((fa['total_income'] / max(1, prev_fa['total_income']) - 1) * 100, 2) if prev_fa['total_income'] > 0 else 0
                },
                'utilization_change': {
                    'value': round(va['utilization_rate'] - prev_va['utilization_rate'], 2),
                    'percent': round(va['utilization_rate'] - prev_va['utilization_rate'], 2)
                }
            }
        
        # 9. 虚拟资产状态分布堆叠柱状图
        chart_data['virtual_asset_status'] = [
            {'name': '活跃', 'value': va.get('active_count', 0)},
            {'name': '已过期', 'value': va.get('expired_count', 0)},
            {'name': '未开始', 'value': va.get('not_started_count', 0)}
        ]
        
        # 10. 综合资产价值堆叠面积图（如果有历史数据）
        if previous_data:
            prev_fa = previous_data['fixed_assets']
            prev_va = previous_data['virtual_assets']
            chart_data['comprehensive_asset_area'] = [
                {
                    'period': '上期',
                    '有形资产': float(prev_fa['total_current_value']),
                    '活跃权益': float(prev_va['total_amount'] - prev_va['total_wasted_value']),
                    '浪费权益': float(prev_va['total_wasted_value'])
                },
                {
                    'period': '本期',
                    '有形资产': float(fa['total_current_value']),
                    '活跃权益': float(va['total_amount'] - va['total_wasted_value']),
                    '浪费权益': float(va['total_wasted_value'])
                }
            ]
        
        print(f"[DEBUG] 生成了 {len(chart_data)} 个图表数据集")
        for key in chart_data.keys():
            print(f"  - {key}")
        
        return chart_data
