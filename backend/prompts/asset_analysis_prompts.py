"""
AI资产分析提示词配置
按照实际人们想要了解的内容设计,分析师角色明确,指令清晰
版本: 1.0.0
"""

PROMPT_VERSION = "1.0.0"


def get_system_prompt():
    """
    获取系统角色定义 - 明确分析师身份和职责
    """
    return """你是一位资深的个人财富管理顾问,专门帮助客户分析和优化资产配置。

你的核心能力:
1. 精准解读财务数据,发现深层次问题和机会
2. 提供基于数据的专业洞察和可执行建议
3. 用清晰简洁的语言解释复杂的财务概念
4. 关注客户真实需求,提供个性化的资产管理方案

你的工作原则:
- 基于真实数据分析,绝不编造数字
- 突出关键信息,标注风险点和机会点
- 建议具体可执行,包含时间表和预期效果
- 语言通俗易懂,避免过度专业术语"""


def get_asset_analysis_prompt(data_text, analysis_focus="综合分析"):
    """
    获取资产分析提示词
    
    Args:
        data_text: 格式化后的资产数据文本
        analysis_focus: 分析重点 (综合分析/固定资产/虚拟资产/收益分析)
    
    Returns:
        完整的分析提示词
    """
    return f"""请基于以下资产数据,进行{analysis_focus}。

===== 资产数据 =====
{data_text}

===== 分析要求 =====

**你需要关注的关键问题**:
1. 💰 资产健康度 - 固定资产是否在有效使用?折旧是否合理?
2. 📊 虚拟资产利用率 - 预付权益是否被充分使用?浪费率是否过高?
3. 💵 收益表现 - 资产产生的收入是否达到预期?哪些资产回报最好?
4. ⚠️ 风险预警 - 即将过期的项目?使用率低的资产?
5. 🎯 优化机会 - 哪些地方可以提升效率?如何减少浪费?

**输出格式要求**:
返回一个JSON对象,包含以下字段:

{{
    "summary": "核心发现总结(200字以内,突出最重要的3个发现)",
    
    "fixed_assets": {{
        "health_score": 健康评分(0-100),
        "key_findings": [
            "发现1:具体资产+数据+问题/亮点",
            "发现2:..."
        ],
        "recommendations": [
            "建议1:具体行动+预期效果",
            "建议2:..."
        ]
    }},
    
    "virtual_assets": {{
        "utilization_score": 利用率评分(0-100),
        "waste_analysis": "浪费分析:TOP3浪费分类+金额+原因",
        "expiring_alerts": [
            "项目名称 - 剩余X天 - ¥XX"
        ],
        "optimization_tips": [
            "优化建议1",
            "优化建议2"
        ]
    }},
    
    "income_analysis": {{
        "total_income": 总收入金额,
        "income_structure": [
            {{"source": "来源", "amount": 金额, "percentage": 占比}}
        ],
        "performance_review": "收入表现评价"
    }},
    
    "risk_alerts": [
        {{
            "level": "高/中/低",
            "type": "风险类型",
            "description": "风险描述",
            "solution": "应对方案"
        }}
    ],
    
    "action_plan": [
        {{
            "priority": "高/中/低",
            "action": "具体行动",
            "timeline": "时间表",
            "expected_result": "预期效果"
        }}
    ],
    
    "chart_insights": {{
        "asset_allocation": "资产配置分析",
        "trend_observation": "趋势观察",
        "comparison_note": "对比说明(如有上期数据)"
    }}
}}

**重要提示**:
1. 所有金额必须是具体数字,不要使用XX占位符
2. 百分比保留1位小数
3. 发现和建议要具体,包含数据支撑
4. 风险和机会都要明确指出
5. 确保JSON格式正确,所有引号、括号、逗号匹配
6. 不要输出```json```代码块标记,直接返回JSON对象

请开始分析:"""


def get_weekly_report_prompt(data_text, previous_data_text=""):
    """
    获取周报生成提示词
    
    Args:
        data_text: 本周数据文本
        previous_data_text: 上周数据文本(可选)
    """
    comparison_hint = ""
    if previous_data_text:
        comparison_hint = f"""
**上周数据对比**:
{previous_data_text}

请在分析中标注周环比变化(用📈📉➡️表示趋势),重点关注:
- 资产价值变化及原因
- 收入增减趋势
- 利用率和浪费率的变化
- 新出现的问题或改善点
"""
    
    # 获取当前时间(作为报告生成时间)
    from datetime import datetime
    generate_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    
    return f"""请生成一份清晰易读的资产周报。

===== 本周数据 =====
{data_text}
{comparison_hint}

===== 报告结构 =====

# 📊 资产周报

## 一、核心摘要
- 本周整体情况(3-5句话)
- 最重要的发现(用🔴标注)
- 需要立即关注的问题(用⚠️标注)

## 二、固定资产分析
- 总体状况:数量、价值、使用率
- 重点关注:哪些资产表现好/差
- 收入情况:本周收入及来源分布

## 三、虚拟资产分析
- 利用情况:利用率、浪费率
- 即将过期预警(7天内)
- TOP3浪费分类及原因

## 四、本周亮点与问题
**亮点** ✅:
1. ...
2. ...

**问题** ⚠️:
1. ...
2. ...

## 五、下周行动计划
1. **高优先级**:
2. **中优先级**:

## 六、数据可视化说明
简要说明资产配置、利用率等关键指标的图表含义

---

**报告生成时间**: {generate_time}  
**分析系统**: TimeValue AI 资产管理系统  
**技术支持**: 智谱AI GLM-4 大模型

**输出要求**:
1. 使用Markdown格式
2. 数据必须真实,来自上述提供的数据
3. 用emoji增强可读性(💰💵📊📈📉⚠️✅🔴等)
4. 重要数字用**加粗**
5. 不要输出```markdown```代码块标记
6. 直接返回Markdown文本
7. 落款信息必须包含报告生成时间(不是周期结束时间)

请生成周报:"""


def get_monthly_report_prompt(data_text):
    """获取月报生成提示词"""
    weekly_prompt = get_weekly_report_prompt(data_text)
    return weekly_prompt.replace("周报", "月报").replace("本周", "本月").replace("上周", "上月").replace("下周", "下月")


def get_yearly_report_prompt(data_text):
    """获取年报生成提示词"""
    weekly_prompt = get_weekly_report_prompt(data_text)
    return weekly_prompt.replace("周报", "年报").replace("本周", "本年").replace("上周", "上年").replace("下周", "明年")


def get_chart_data_prompt(ai_analysis_result):
    """
    根据AI分析结果,生成图表数据的提示词
    
    Args:
        ai_analysis_result: AI分析的JSON结果
    """
    return f"""基于以下分析结果,生成前端图表所需的数据配置。

===== AI分析结果 =====
{ai_analysis_result}

===== 需要生成的图表 =====

请返回一个JSON对象,包含以下图表的数据配置:

{{
    "asset_allocation_pie": [
        {{"name": "固定资产", "value": 数值}},
        {{"name": "虚拟资产", "value": 数值}}
    ],
    
    "fixed_asset_categories_bar": [
        {{"category": "分类名", "value": 价值, "count": 数量}}
    ],
    
    "virtual_asset_utilization_gauge": {{
        "utilization_rate": 利用率百分比,
        "waste_rate": 浪费率百分比
    }},
    
    "income_structure_pie": [
        {{"source": "来源", "amount": 金额}}
    ],
    
    "health_score_radar": [
        {{"dimension": "固定资产", "score": 得分, "maxScore": 100}},
        {{"dimension": "虚拟资产", "score": 得分, "maxScore": 100}},
        {{"dimension": "收入表现", "score": 得分, "maxScore": 100}},
        {{"dimension": "风险控制", "score": 得分, "maxScore": 100}}
    ]
}}

**要求**:
1. 所有数值必须是数字类型,不是字符串
2. 百分比不要带%符号,直接数字(如 75 不是 "75%")
3. 确保JSON格式正确
4. 不要输出代码块标记

请生成图表数据配置:"""
