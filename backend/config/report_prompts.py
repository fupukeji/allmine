"""
AI报告生成Prompt配置模块
版本：6.0.0 - 全新设计，支持上期对比和增强可视化
"""

PROMPT_VERSION = "6.0.0"

def get_weekly_report_prompt(compressed_text, ai_insights_text, current_data, previous_data=None, 
                            intelligent_insights=None, qualitative_analysis=None):
    """
    获取周报生成Prompt（增强版 - 利用智能洞察 + 定性分析）
    
    Args:
        compressed_text: 压缩后的数据文本（已包含当前期和对比信息）
        ai_insights_text: AI洞察文本（可选）
        current_data: 当前期数据字典
        previous_data: 上期数据字典（可选，用于对比）
        intelligent_insights: 智能洞察指标字典（新增）
        qualitative_analysis: AI定性分析结论（【新增】核心！）
    
    Returns:
        str: 完整的Prompt
    """
    
    # 判断是否有上期对比数据
    has_comparison = previous_data is not None
    
    # 提取关键数据
    curr_fa = current_data['fixed_assets']
    curr_va = current_data['virtual_assets']
    period = current_data['period']
    
    # 【新增】提取智能洞察指标
    insights_context = ""
    if intelligent_insights:
        health = intelligent_insights.get('fixed_asset_health', 0)
        efficiency = intelligent_insights.get('virtual_asset_efficiency', 0)
        income_quality = intelligent_insights.get('income_quality', 0)
        balance = intelligent_insights.get('allocation_balance', 0)
        
        # 健康度评级
        health_rating = "🟢优秀" if health >= 80 else "🟡良好" if health >= 60 else "🔴需关注" if health >= 40 else "⚫紧急"
        efficiency_rating = "🟢高效" if efficiency >= 80 else "🟡正常" if efficiency >= 60 else "🔴低效" if efficiency >= 40 else "⚫严重浪费"
        income_rating = "🟢优秀" if income_quality >= 80 else "🟡良好" if income_quality >= 60 else "🔴偏低" if income_quality >= 40 else "⚫极低"
        balance_rating = "🟢均衡" if balance >= 80 else "🟡可接受" if balance >= 60 else "🔴失衡" if balance >= 40 else "⚫严重失衡"
        
        insights_context = f"""\n\n【重要】智能诊断指标（请在报告中重点分析）：
✦ 固定资产健康度：{health:.1f}/100 {health_rating}
✦ 虚拟资产效率：{efficiency:.1f}/100 {efficiency_rating}
✦ 收入质量：{income_quality:.1f}/100 {income_rating}
✦ 资产配置均衡度：{balance:.1f}/100 {balance_rating}

分析要求：
1. 如健康度<60，诊断原因（折旧过快？收入不足？闲置过多？）并给出改善方案
2. 如效率<60，分析浪费根源（哪个分类？什么类型？）并提出优化建议
3. 如收入质量<60，评估ROI合理性，建议调整资产结构
4. 如均衡度<60，建议理想配置比例（固定60-80%，虚拟20-40%）"""
    
    # 【新增】定性分析结论注入
    qualitative_context = ""
    if qualitative_analysis:
        qa = qualitative_analysis
        key_issues_text = '\n'.join(f'- {issue}' for issue in qa.get('key_issues', []))
        strengths_text = '\n'.join(f'- {strength}' for strength in qa.get('strengths', []))
        focus_areas_text = '\n'.join(f'- {area}' for area in qa.get('focus_areas', []))
        recommendations_text = '\n'.join(f'- {rec}' for rec in qa.get('preliminary_recommendations', []))
        
        qualitative_context = f"""

【核心】AI定性分析结论（请基于此结论深入分析数据）：

🎯 整体评估：{qa.get('overall_assessment', '未知')}
⚠️ 紧急程度：{qa.get('severity_level', '未知')}

💔 关键问题（必须重点分析）：
{key_issues_text if key_issues_text else '- 无明显问题'}

✨ 优势亮点：
{strengths_text if strengths_text else '- 无特别突出之处'}

🎯 重点关注领域（必须深入讨论）：
{focus_areas_text if focus_areas_text else '- 保持现状'}

💡 初步建议：
{recommendations_text if recommendations_text else '- 持续监控'}

📝 分析总结：
{qa.get('analysis_summary', '')}

⚡ 重要指示：
1. 必须针对上述关键问题，从数据中找出证据和根本原因
2. 必须针对重点关注领域，提供具体的数据分析和改进建议
3. 优势亮点要表扬，问题要深入剖析，建议要可执行
4. 不要重复定性结论的原话，而是基于它进行定量分析
"""
    
    # 构建简洁对比说明
    if has_comparison:
        prev_fa = previous_data['fixed_assets']
        prev_va = previous_data['virtual_assets']
        context = f"""对比分析：上期({previous_data['period']['start_date']}~{previous_data['period']['end_date']}) vs 本期({period['start_date']}~{period['end_date']})
固定资产：¥{curr_fa['total_current_value']:,.0f}(上期¥{prev_fa['total_current_value']:,.0f}) 收入：¥{curr_fa['total_income']:,.0f}(上期¥{prev_fa['total_income']:,.0f})
虚拟资产：利用率{curr_va['utilization_rate']:.1f}%(上期{prev_va['utilization_rate']:.1f}%) 浪费率{curr_va['waste_rate']:.1f}%(上期{prev_va['waste_rate']:.1f}%)
要求：用📈📉➡️标记趋势，用🟢🟡🔴标记状态，计算变化%，分析原因和预测"""
    else:
        context = f"""本期数据({period['start_date']}~{period['end_date']})：固定资产¥{curr_fa['total_current_value']:,.0f} 收入¥{curr_fa['total_income']:,.0f} 利用率{curr_va['utilization_rate']:.1f}% 浪费率{curr_va['waste_rate']:.1f}%
首次报告无对比，全面分析现状，建立基准"""
    
    # 构建核心指标表格
    if has_comparison:
        metrics_table = ( "| 指标 | 本期 | 上期 | 变化 | 趋势 |\n"
                         "|------|------|------|------|------|\n"
                         "| 💰固定资产 | [实际数值] | [实际数值] | [计算%] | 📈📉➡️ |\n"
                         "| 💵收入 | [实际数值] | [实际数值] | [计算%] | 📈📉➡️ |\n"
                         "| 📊利用率 | [实际数值] | [实际数值] | [计算%] | �︢�︡🔴 |\n"
                         "| 🔴浪费率 | [实际数值] | [实际数值] | [计算%] | �︢�︡🔴 |" )
    else:
        metrics_table = ( "| 指标 | 数值 | 状态 |\n"
                         "|------|------|------|\n"
                         "| 💰固定资产 | [实际数值] | �︢�︡🔴 |\n"
                         "| 💵收入 | [实际数值] | �︢�︡🔴 |\n"
                         "| 📊利用率 | [实际数值] | �︢�︡🔴 |\n"
                         "| 🔴浪费率 | [实际数值] | �︢�︡🔴 |" )
    
    return f"""你是资深财富分析师。基于真实数据生成Markdown周报。

{context}

数据：
{compressed_text}{insights_context}{qualitative_context}

核心要求：
1. 用真实数据，禁止XX占位符
2. 用emoji📊表格进度条
3. {'对比分析，标记变化趋势' if has_comparison else '分析现状建立基准'}
4. 给出可执行建议
5. 表格格式：每个|前后必须有空格，表格前后必须有空行

报告结构

# 📈 资产周报({period['start_date']}~{period['end_date']})

## 📋 执行摘要

核心发现：[最重要发现+数字]

本周概览：
💰固定资产{curr_fa['total_assets']}项¥{curr_fa['total_current_value']:,.0f} 💵收入¥{curr_fa['total_income']:,.0f}
💳虚拟资产{curr_va['total_projects']}项 利用率{curr_va['utilization_rate']:.1f}% 浪费率{curr_va['waste_rate']:.1f}% 浪费¥{curr_va['total_wasted_value']:,.0f}

{'关键变化：[2-3个变化+emoji+数字+趋势]' if has_comparison else '关键发现：[2-3个发现]'}

---

## 🎯 核心指标

{metrics_table}

[分析2个关键发现]

## 🏠 固定资产

{curr_fa['total_assets']}项 ¥{curr_fa['total_current_value']:,.0f} 折旧¥{curr_fa['total_depreciation']:,.0f} 收入¥{curr_fa['total_income']:,.0f}

[分析使用状况和收益{'变化' if has_comparison else ''}]

---

## 💳 虚拟资产

投入¥{curr_va['total_amount']:,.0f} 活跃{curr_va['active_count']}项 过期{curr_va['expired_count']}项浪费¥{curr_va['total_wasted_value']:,.0f}
利用率{curr_va['utilization_rate']:.1f}% 浪费率{curr_va['waste_rate']:.1f}%

**利用率可视化**：
```
已消耗 ██████░░░░ 60%
浪费  ██░░░░░░░░ 20% 🔴
```
(用█表示填充，░表示空白，根据实际数值调整数量)

[分析利用情况和浪费原因{'变化' if has_comparison else ''}]

---

## 💡 建议

🔴高优先级：[1-2条，含问题+目标+行动计划+预期]
🟡中优先级：[1-2条]

---

## 📈 趋势预测

{'基于趋势下周预测：[给出2-3个关键指标预测值]' if has_comparison else '建立基准，下周对比分析'}

## 📌 下周关注

1. [关注点1]
2. [关注点2]

---

📅{period['start_date']}~{period['end_date']}({period['days']}天) 📊固定{curr_fa['total_assets']}项虚拟{curr_va['total_projects']}项

⚠️重要：用真实数据，禁止XX占位符，基于实际数据分析，直接输出Markdown不要``标记
"""


def get_monthly_report_prompt(compressed_text, ai_insights_text, current_data, previous_data=None, 
                             intelligent_insights=None, qualitative_analysis=None):
    """
    获取月报生成Prompt（复用周报逻辑）
    """
    return get_weekly_report_prompt(compressed_text, ai_insights_text, current_data, previous_data, 
                                    intelligent_insights, qualitative_analysis).replace('周报', '月报').replace('本周', '本月')


def get_yearly_report_prompt(compressed_text, ai_insights_text, current_data, 
                            intelligent_insights=None, qualitative_analysis=None):
    """
    获取年报生成Prompt
    """
    return get_monthly_report_prompt(compressed_text, ai_insights_text, current_data, None, 
                                    intelligent_insights, qualitative_analysis).replace('月报', '年报').replace('本月', '本年')


def get_custom_report_prompt(compressed_text, ai_insights_text, current_data, previous_data=None, 
                            intelligent_insights=None, qualitative_analysis=None):
    """
    获取自定义报告Prom pt
    """
    return get_weekly_report_prompt(compressed_text, ai_insights_text, current_data, previous_data, 
                                   intelligent_insights, qualitative_analysis).replace('周报', '分析报告').replace('本周', '本期')
