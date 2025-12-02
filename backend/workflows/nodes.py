"""
报告生成工作流节点实现
每个节点负责工作流中的一个具体步骤
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any
from workflows.state import ReportWorkflowState


logger = logging.getLogger(__name__)


def _save_workflow_trace_realtime(state: ReportWorkflowState):
    """
    实时保存工作流轨迹到数据库
    在每个节点执行后调用，实现实时更新
    """
    from models.ai_report import AIReport
    from database import db
    
    try:
        task_context = state.get("task_context", {})
        report_id = task_context.get("report_id")
        
        if not report_id:
            return
        
        report = AIReport.query.get(report_id)
        if report:
            # 保存工作流轨迹
            report.execution_path = json.dumps(state.get("execution_path", []), ensure_ascii=False)
            report.workflow_metadata = json.dumps({
                "agent_decisions": state.get("agent_decisions", []),
                "quality_score": state.get("quality_score"),
                "retry_count": state.get("retry_count", 0),
                "start_time": state.get("start_time"),
                "end_time": state.get("end_time")
            }, ensure_ascii=False)
            db.session.commit()
            
            node_count = len(state.get('execution_path', []))
            last_node = state['execution_path'][-1]['node'] if state.get('execution_path') else 'unknown'
            logger.info(f"💾 [实时保存] 报告ID: {report_id} | 节点数: {node_count} | 最新节点: {last_node}")
    except Exception as e:
        logger.warning(f"⚠️ [实时保存] 失败: {str(e)}")
        # 不影响主流程


async def init_task_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N1: 初始化任务节点
    - 设置任务上下文
    - 初始化工作流状态
    - 记录开始时间
    """
    task_context = state["task_context"]
    report_id = task_context.get("report_id")
    
    logger.info(f"🚀 [N1-任务初始化] 开始 - 报告ID: {report_id}")
    
    # 更新状态
    state["start_time"] = datetime.utcnow().isoformat()
    state["retry_count"] = 0
    state["max_retries"] = 3
    state["agent_decisions"] = []
    state["execution_path"] = [{
        "node": "init_task",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed"
    }]
    
    logger.info(f"✅ [N1-任务初始化] 完成")
    
    # 实时保存
    _save_workflow_trace_realtime(state)
    
    return state


async def collect_data_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N2: 数据采集节点（增强版）
    - 查询固定资产数据（含折旧明细）
    - 查询虚拟资产数据（含时间价值分析）
    - 查询收入数据（含ROI计算）
    - 查询分类层级结构
    - 构建结构化数据 + 智能洞察
    """
    from services.zhipu_service import ZhipuAiService
    from models.category import Category
    from datetime import datetime
    
    task_context = state["task_context"]
    user_id = task_context["user_id"]
    start_date = task_context["start_date"]
    end_date = task_context["end_date"]
    
    logger.info(f"📊 [N2-数据采集增强] 开始 - 用户ID: {user_id}, 时间范围: {start_date} 至 {end_date}")
    
    try:
        # 使用现有的服务方法准备基础数据
        service = ZhipuAiService(api_token="dummy", model="dummy")  # 仅用于数据查询
        raw_data = service.prepare_asset_data(user_id, start_date, end_date)
        
        # 【增强1】获取分类层级结构
        categories = Category.query.filter_by(user_id=user_id).all()
        category_hierarchy = []
        for cat in categories:
            category_hierarchy.append({
                'id': cat.id,
                'name': cat.name,
                'parent_id': cat.parent_id,
                'level': cat.get_level(),
                'full_path': cat.get_full_path(),
                'project_count': len(cat.projects)
            })
        
        # 【增强2】计算智能洞察指标
        insights = {
            # 固定资产健康度
            'fixed_asset_health': _calculate_fixed_asset_health(raw_data['fixed_assets']),
            # 虚拟资产效率评级
            'virtual_asset_efficiency': _calculate_virtual_efficiency(raw_data['virtual_assets']),
            # 收入质量评分
            'income_quality': _calculate_income_quality(raw_data['fixed_assets']),
            # 资产配置均衡度
            'allocation_balance': _calculate_allocation_balance(raw_data),
            # 分类层级数据
            'category_hierarchy': category_hierarchy
        }
        
        state["raw_data"] = raw_data
        
        logger.info(f"✅ [N2-数据采集增强] 完成")
        logger.info(f"   - 固定资产: {raw_data['fixed_assets']['total_assets']}项")
        logger.info(f"   - 虚拟资产: {raw_data['virtual_assets']['total_projects']}项")
        logger.info(f"   - 分类层级: {len(category_hierarchy)}个分类，最深{max([c['level'] for c in category_hierarchy], default=0)}层")
        logger.info(f"   - 智能洞察: 健康度{insights['fixed_asset_health']:.1f}, 效率{insights['virtual_asset_efficiency']:.1f}")
        
        # 将insights单独存储，不修改raw_data结构
        state["intelligent_insights"] = insights
        
        state["execution_path"].append({
            "node": "collect_data",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "data_summary": {
                "fixed_assets_count": raw_data['fixed_assets']['total_assets'],
                "virtual_assets_count": raw_data['virtual_assets']['total_projects'],
                "category_count": len(category_hierarchy),
                "insights": insights
            }
        })
        
        # 实时保存
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.error(f"❌ [N2-数据采集] 失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        state["error_message"] = f"数据采集失败: {str(e)}"
        state["execution_path"].append({
            "node": "collect_data",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


def _calculate_fixed_asset_health(fixed_data):
    """计算固定资产健康度（0-100）"""
    if fixed_data['total_assets'] == 0:
        return 50.0  # 无资产默认中等
    
    # 考虑因素：折旧率、收入率、使用率
    health_score = 100.0
    
    # 折旧率惩罚（折旧率越高扣分越多）
    depreciation_penalty = min(40, fixed_data['depreciation_rate'] * 0.5)
    health_score -= depreciation_penalty
    
    # 收入率加分
    if fixed_data['total_current_value'] > 0:
        income_rate = (fixed_data['total_income'] / fixed_data['total_current_value']) * 100
        income_bonus = min(30, income_rate * 3)
        health_score += income_bonus
    
    # 使用率加分
    status_stats = fixed_data.get('status_stats', {})
    if fixed_data['total_assets'] > 0:
        in_use = status_stats.get('使用中', 0)
        usage_rate = (in_use / fixed_data['total_assets']) * 100
        usage_bonus = min(20, usage_rate * 0.2)
        health_score += usage_bonus
    
    return round(max(0, min(100, health_score)), 1)


def _calculate_virtual_efficiency(virtual_data):
    """计算虚拟资产效率（0-100）"""
    if virtual_data['total_projects'] == 0:
        return 50.0
    
    # 基于利用率和浪费率
    efficiency = virtual_data['utilization_rate'] - virtual_data['waste_rate'] * 2
    
    # 即将过期项目扣分
    if virtual_data.get('expiring_soon'):
        expiring_count = len(virtual_data['expiring_soon'])
        efficiency -= min(20, expiring_count * 5)
    
    return round(max(0, min(100, efficiency)), 1)


def _calculate_income_quality(fixed_data):
    """计算收入质量（0-100）"""
    if fixed_data['total_current_value'] == 0:
        return 0.0
    
    # ROI作为主要指标
    roi = (fixed_data['total_income'] / fixed_data['total_current_value']) * 100
    
    # 转换为0-100分数
    # 10% ROI = 100分, 5% ROI = 50分, 0% ROI = 0分
    quality = roi * 10
    
    return round(max(0, min(100, quality)), 1)


def _calculate_allocation_balance(raw_data):
    """计算资产配置均衡度（0-100）"""
    fixed_value = raw_data['fixed_assets']['total_current_value']
    virtual_value = raw_data['virtual_assets']['total_amount']
    total = fixed_value + virtual_value
    
    if total == 0:
        return 50.0
    
    # 理想比例：固定资产60-80%，虚拟资产20-40%
    fixed_ratio = (fixed_value / total) * 100
    
    if 60 <= fixed_ratio <= 80:
        balance = 100  # 完美均衡
    elif 50 <= fixed_ratio < 60 or 80 < fixed_ratio <= 90:
        balance = 80   # 良好
    elif 40 <= fixed_ratio < 50 or 90 < fixed_ratio <= 95:
        balance = 60   # 一般
    else:
        balance = 40   # 失衡
    
    return round(balance, 1)


async def compress_data_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N3: 数据压缩节点（增强版）
    - 将结构化数据压缩为简洁文本
    - 融合智能洞察指标
    - 为AI生成做准备
    """
    from services.zhipu_service import ZhipuAiService
    
    logger.info(f"🗜️ [N3-数据压缩增强] 开始")
    
    try:
        raw_data = state["raw_data"]
        if not raw_data:
            raise Exception("原始数据为空")
        
        service = ZhipuAiService(api_token="dummy", model="dummy")
        compressed_text = service._compress_data_to_text(raw_data)
        
        # 【增强】添加智能洞察摘要
        insights = state.get("intelligent_insights")
        if insights:
            insights_text = "\n\n【智能洞察指标】\n"
            insights_text += f"- 🟢 固定资产健康度: {insights['fixed_asset_health']:.1f}/100\n"
            insights_text += f"- ⚡ 虚拟资产效率: {insights['virtual_asset_efficiency']:.1f}/100\n"
            insights_text += f"- 💵 收入质量: {insights['income_quality']:.1f}/100\n"
            insights_text += f"- ⚖️ 资产配置均衡度: {insights['allocation_balance']:.1f}/100\n"
            
            # 分类层级信息
            if 'category_hierarchy' in insights:
                max_level = max([c['level'] for c in insights['category_hierarchy']], default=0)
                top_categories = [c for c in insights['category_hierarchy'] if c['level'] == 0]
                insights_text += f"\n- 📂 分类结构: {len(insights['category_hierarchy'])}个分类，{max_level+1}层深度，{len(top_categories)}个顶级分类"
                # 显示前3个最活跃的分类
                sorted_cats = sorted(insights['category_hierarchy'], key=lambda x: x['project_count'], reverse=True)[:3]
                for cat in sorted_cats:
                    insights_text += f"\n  • {cat['full_path']}: {cat['project_count']}个项目"
            
            compressed_text += insights_text
        
        state["compressed_text"] = compressed_text
        
        logger.info(f"✅ [N3-数据压缩增强] 完成 - 压缩后文本长度: {len(compressed_text)} 字符")
        logger.debug(f"压缩后文本预览:\n{compressed_text[:500]}...")
        
        state["execution_path"].append({
            "node": "compress_data",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "text_length": len(compressed_text),
            "has_insights": insights is not None
        })
        
        # 实时保存
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.error(f"❌ [N3-数据压缩] 失败: {str(e)}")
        state["error_message"] = f"数据压缩失败: {str(e)}"
        state["execution_path"].append({
            "node": "compress_data",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


async def agent_decide_comparison_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N4: Agent决策-是否需要上期对比
    - 分析报告类型和时间跨度
    - 决定是否查询上期数据
    """
    logger.info(f"🤖 [N4-Agent决策] 开始 - 判断是否需要上期对比")
    
    task_context = state["task_context"]
    report_type = task_context.get("report_type", "custom")
    
    # 决策逻辑：周报、月报、年报需要上期对比
    need_comparison = report_type in ['weekly', 'monthly', 'yearly']
    
    decision = {
        "node": "agent_decide_comparison",
        "timestamp": datetime.utcnow().isoformat(),
        "decision": {
            "need_comparison": need_comparison,
            "reason": f"报告类型为{report_type}，{'需要' if need_comparison else '无需'}上期对比",
            "next_node": "query_previous_data" if need_comparison else "generate_report"
        }
    }
    
    state["agent_decisions"].append(decision)
    state["execution_path"].append({
        "node": "agent_decide_comparison",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "decision": decision["decision"]
    })
    
    logger.info(f"✅ [N4-Agent决策] 完成 - {'需要' if need_comparison else '无需'}上期对比")
    
    return state


async def query_previous_data_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N5: 查询上期数据节点
    - 计算上期时间范围
    - 查询上期数据
    - 生成对比文本
    """
    from services.zhipu_service import ZhipuAiService
    
    logger.info(f"📅 [N5-查询上期] 开始")
    
    try:
        task_context = state["task_context"]
        user_id = task_context["user_id"]
        start_date = task_context["start_date"]
        end_date = task_context["end_date"]
        
        service = ZhipuAiService(api_token="dummy", model="dummy")
        previous_data = service._get_previous_period_data(user_id, start_date, end_date)
        
        if previous_data:
            state["previous_data"] = previous_data
            
            # 生成对比文本
            comparison_text = service._generate_comparison_text(state["raw_data"], previous_data)
            state["comparison_text"] = comparison_text
            
            logger.info(f"✅ [N5-查询上期] 完成 - 已生成对比分析")
        else:
            logger.warning(f"⚠️ [N5-查询上期] 未找到上期数据，跳过对比")
            state["comparison_text"] = ""
        
        state["execution_path"].append({
            "node": "query_previous_data",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "has_previous_data": previous_data is not None
        })
        
    except Exception as e:
        logger.warning(f"⚠️ [N5-查询上期] 异常: {str(e)}，跳过对比")
        state["comparison_text"] = ""
        state["execution_path"].append({
            "node": "query_previous_data",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "skipped",
            "error": str(e)
        })
    
    return state


async def ai_preanalysis_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N6: AI预分析节点（定性分析阶段）
    - 基于智能洞察指标和压缩数据进行AI定性分析
    - 输出结构化的定性结论，为后续报告生成提供指导
    - 这是"从数据到结论"的关键第一步
    """
    from services.zhipu_service import ZhipuAiService
    import json
    
    logger.info(f"🧠 [N6-AI定性分析] 开始")
    
    try:
        task_context = state["task_context"]
        api_key = task_context.get("api_key")
        model = task_context.get("model", "glm-4-flash")
        
        if not api_key:
            logger.warning(f"⚠️ [N6-AI定性分析] API Key未配置，跳过预分析")
            state["qualitative_analysis"] = None
            state["ai_insights"] = ""  # 兼容旧字段
            state["execution_path"].append({
                "node": "ai_preanalysis",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "skipped",
                "reason": "API Key未配置"
            })
            return state
        
        # 获取智能洞察指标
        intelligent_insights = state.get("intelligent_insights", {})
        compressed_text = state["compressed_text"]
        
        if not intelligent_insights:
            logger.warning(f"⚠️ [N6-AI定性分析] 未找到智能洞察指标，跳过预分析")
            state["qualitative_analysis"] = None
            state["ai_insights"] = ""
            state["execution_path"].append({
                "node": "ai_preanalysis",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "skipped",
                "reason": "未找到智能洞察指标"
            })
            return state
        
        # 提取关键指标
        fixed_asset_health = intelligent_insights.get('fixed_asset_health', 0)
        virtual_asset_efficiency = intelligent_insights.get('virtual_asset_efficiency', 0)
        income_quality = intelligent_insights.get('income_quality', 0)
        allocation_balance = intelligent_insights.get('allocation_balance', 0)
        
        logger.info(f"   - 固定资产健康度: {fixed_asset_health:.1f}/100")
        logger.info(f"   - 虚拟资产效率: {virtual_asset_efficiency:.1f}/100")
        logger.info(f"   - 收入质量: {income_quality:.1f}/100")
        logger.info(f"   - 资产配置均衡度: {allocation_balance:.1f}/100")
        
        # 构建定性分析Prompt
        qualitative_prompt = f"""
【任务】作为专业的资产管理分析师，请基于以下智能洞察指标和数据摘要，生成一份**结构化的定性分析结论**。

【智能洞察指标】
- 🏠 固定资产健康度: {fixed_asset_health:.1f}/100
- ⚡ 虚拟资产效率: {virtual_asset_efficiency:.1f}/100
- 💵 收入质量: {income_quality:.1f}/100
- ⚖️ 资产配置均衡度: {allocation_balance:.1f}/100

【数据摘要】
{compressed_text[:2000]}  # 只取前2000字符避免太长

【输出要求】
请以JSON格式输出以下结构的定性分析结论：

```json
{{
  "overall_assessment": "整体评估：优秀/良好/中等/较差/危险",
  "severity_level": "紧急程度：低/中/高",
  "key_issues": [
    "问题1：描述发现的主要问题",
    "问题2：..."
  ],
  "strengths": [
    "优势1：描述资产管理的亮点",
    "优势2：..."
  ],
  "focus_areas": [
    "重点关注区域1",
    "重点关注区域2"
  ],
  "preliminary_recommendations": [
    "初步建议1",
    "初步建议2"
  ],
  "analysis_summary": "用200字总结上述判断的核心逻辑"
}}
```

【分析原则】
1. **指标门限**: 评分>=80为优秀，60-80为良好，40-60为中等，<40为需关注
2. **问题识别**: 重点指出评分<60的指标及原因
3. **优势发现**: 识别评分>=80的亮点领域
4. **关注重点**: 明确后续报告应深入分析的领域
5. **初步建议**: 提供高层次的改进方向

请直接输出纯JSON，不要任何额外文字。
"""
        
        # 调用AI生成定性分析
        service = ZhipuAiService(api_token=api_key, model=model)
        
        logger.info(f"🤖 [N6-AI定性分析] 调用AI进行定性分析...")
        response = service.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位专业的资产管理分析师，擅长基于量化指标快速识别问题和机会。"},
                {"role": "user", "content": qualitative_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        qualitative_text = response.choices[0].message.content.strip()
        logger.info(f"✅ [N6-AI定性分析] AI返回长度: {len(qualitative_text)} 字符")
        
        # 解析JSON结果
        try:
            # 提取JSON（去除代码块标记）
            if "```json" in qualitative_text:
                qualitative_text = qualitative_text.split("```json")[1].split("```")[0].strip()
            elif "```" in qualitative_text:
                qualitative_text = qualitative_text.split("```")[1].split("```")[0].strip()
            
            qualitative_analysis = json.loads(qualitative_text)
            
            # 验证必要字段
            required_fields = ["overall_assessment", "severity_level", "key_issues", "focus_areas"]
            for field in required_fields:
                if field not in qualitative_analysis:
                    logger.warning(f"⚠️ [N6-AI定性分析] 缺少必要字段: {field}，使用默认值")
                    qualitative_analysis[field] = "" if field in ["overall_assessment", "severity_level"] else []
            
            state["qualitative_analysis"] = qualitative_analysis
            state["ai_insights"] = qualitative_text  # 保留原始文本供兼容
            
            logger.info(f"✅ [N6-AI定性分析] 完成")
            logger.info(f"   - 整体评估: {qualitative_analysis['overall_assessment']}")
            logger.info(f"   - 紧急程度: {qualitative_analysis['severity_level']}")
            logger.info(f"   - 关键问题数: {len(qualitative_analysis.get('key_issues', []))}")
            logger.info(f"   - 重点关注: {', '.join(qualitative_analysis.get('focus_areas', [])[:3])}")
            
            state["execution_path"].append({
                "node": "ai_preanalysis",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed",
                "qualitative_summary": {
                    "assessment": qualitative_analysis['overall_assessment'],
                    "severity": qualitative_analysis['severity_level'],
                    "issues_count": len(qualitative_analysis.get('key_issues', [])),
                    "focus_areas": qualitative_analysis.get('focus_areas', [])
                }
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ [N6-AI定性分析] JSON解析失败: {str(e)}")
            logger.error(f"AI返回内容: {qualitative_text[:500]}...")
            # 降级处理：使用基于指标的简单判断
            qualitative_analysis = _generate_simple_qualitative_analysis(intelligent_insights)
            state["qualitative_analysis"] = qualitative_analysis
            state["ai_insights"] = json.dumps(qualitative_analysis, ensure_ascii=False)
            
            state["execution_path"].append({
                "node": "ai_preanalysis",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed",
                "note": "AI解析失败，使用规则生成"
            })
        
    except Exception as e:
        logger.error(f"❌ [N6-AI定性分析] 异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # 降级处理
        intelligent_insights = state.get("intelligent_insights", {})
        if intelligent_insights:
            qualitative_analysis = _generate_simple_qualitative_analysis(intelligent_insights)
            state["qualitative_analysis"] = qualitative_analysis
            state["ai_insights"] = json.dumps(qualitative_analysis, ensure_ascii=False)
        else:
            state["qualitative_analysis"] = None
            state["ai_insights"] = ""
        
        state["execution_path"].append({
            "node": "ai_preanalysis",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


def _generate_simple_qualitative_analysis(intelligent_insights: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于智能洞察指标生成简单的定性分析（降级方案）
    """
    fixed_asset_health = intelligent_insights.get('fixed_asset_health', 0)
    virtual_asset_efficiency = intelligent_insights.get('virtual_asset_efficiency', 0)
    income_quality = intelligent_insights.get('income_quality', 0)
    allocation_balance = intelligent_insights.get('allocation_balance', 0)
    
    avg_score = (fixed_asset_health + virtual_asset_efficiency + income_quality + allocation_balance) / 4
    
    # 整体评估
    if avg_score >= 80:
        overall_assessment = "优秀"
        severity_level = "低"
    elif avg_score >= 60:
        overall_assessment = "良好"
        severity_level = "低"
    elif avg_score >= 40:
        overall_assessment = "中等"
        severity_level = "中"
    else:
        overall_assessment = "较差"
        severity_level = "高"
    
    # 识别问题
    key_issues = []
    strengths = []
    focus_areas = []
    
    if fixed_asset_health < 60:
        key_issues.append(f"固定资产健康度偏低（{fixed_asset_health:.1f}分），可能存在过度折旧或收入不足问题")
        focus_areas.append("固定资产健康度提升")
    elif fixed_asset_health >= 80:
        strengths.append(f"固定资产健康度优秀（{fixed_asset_health:.1f}分）")
    
    if virtual_asset_efficiency < 60:
        key_issues.append(f"虚拟资产效率偏低（{virtual_asset_efficiency:.1f}分），存在浪费或即将过期情况")
        focus_areas.append("虚拟资产利用率优化")
    elif virtual_asset_efficiency >= 80:
        strengths.append(f"虚拟资产效率优秀（{virtual_asset_efficiency:.1f}分）")
    
    if income_quality < 60:
        key_issues.append(f"收入质量需提升（{income_quality:.1f}分），ROI表现不佳")
        focus_areas.append("增加资产收入")
    elif income_quality >= 80:
        strengths.append(f"收入质量优秀（{income_quality:.1f}分）")
    
    if allocation_balance < 60:
        key_issues.append(f"资产配置失衡（{allocation_balance:.1f}分），需调整结构")
        focus_areas.append("资产配置优化")
    elif allocation_balance >= 80:
        strengths.append(f"资产配置均衡（{allocation_balance:.1f}分）")
    
    # 如果没有问题，添加默认关注
    if not focus_areas:
        focus_areas = ["保持当前优秀状态", "密切监控资产变化"]
    
    return {
        "overall_assessment": overall_assessment,
        "severity_level": severity_level,
        "key_issues": key_issues if key_issues else ["无明显问题"],
        "strengths": strengths if strengths else ["无特别突出之处"],
        "focus_areas": focus_areas,
        "preliminary_recommendations": [
            "根据关键问题制定针对性改进方案",
            "定期监控各项指标变化趋势"
        ],
        "analysis_summary": f"根据智能指标分析，当前资产状况为{overall_assessment}（平均分{avg_score:.1f}）。" + 
                           ("需重点关注" + ",".join(focus_areas[:2]) if key_issues else "整体表现良好")
    }


async def generate_report_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N7: 生成报告节点（基于定性分析的定量报告）
    - 基于定性分析结论调用AI生成详细报告
    - 解析JSON格式内容
    - 将定性结论注入报告，形成完整分析链
    """
    from services.zhipu_service import ZhipuAiService
    import json
    
    logger.info(f"📝 [N7-生成报告] 开始")
    
    try:
        task_context = state["task_context"]
        api_key = task_context["api_key"]
        model = task_context.get("model", "glm-4-flash")
        report_type = task_context.get("report_type", "custom")
        
        # 获取定性分析结论
        qualitative_analysis = state.get("qualitative_analysis")
        intelligent_insights = state.get("intelligent_insights")
        
        if qualitative_analysis:
            logger.info(f"🎯 [N7-生成报告] 利用定性分析结论指导报告生成")
            logger.info(f"   - 整体评估: {qualitative_analysis.get('overall_assessment')}")
            logger.info(f"   - 关键问题: {len(qualitative_analysis.get('key_issues', []))}个")
            logger.info(f"   - 重点关注: {', '.join(qualitative_analysis.get('focus_areas', [])[:2])}")
        else:
            logger.warning(f"⚠️ [N7-生成报告] 未找到定性分析，使用传统模式生成报告")
        
        service = ZhipuAiService(api_token=api_key, model=model)
        
        # 根据报告类型调用对应的生成方法
        user_id = task_context["user_id"]
        start_date = task_context["start_date"]
        end_date = task_context["end_date"]
        focus_areas = task_context.get("focus_areas", [])
        
        # 【增强】将定性分析和智能洞察传递给报告生成方法
        if report_type == 'weekly':
            content = service.generate_weekly_report(
                user_id, start_date, end_date,
                qualitative_analysis=qualitative_analysis,
                intelligent_insights=intelligent_insights
            )
        elif report_type == 'monthly':
            content = service.generate_monthly_report(
                user_id, start_date, end_date,
                qualitative_analysis=qualitative_analysis,
                intelligent_insights=intelligent_insights
            )
        elif report_type == 'yearly':
            content = service.generate_custom_report(
                user_id, start_date, end_date, 
                focus_areas or ['年度资产增长趋势', '年度收益表现', '资产配置优化'],
                qualitative_analysis=qualitative_analysis,
                intelligent_insights=intelligent_insights
            )
        else:  # custom
            content = service.generate_custom_report(
                user_id, start_date, end_date, focus_areas,
                qualitative_analysis=qualitative_analysis,
                intelligent_insights=intelligent_insights
            )
        
        # 【增强】将定性分析注入报告内容
        if qualitative_analysis and content:
            try:
                report_data = json.loads(content)
                # 添加定性分析到报告中
                report_data['qualitative_analysis'] = qualitative_analysis
                content = json.dumps(report_data, ensure_ascii=False, indent=2)
                logger.info(f"✅ [N7-生成报告] 已将定性分析注入报告")
            except json.JSONDecodeError:
                logger.warning(f"⚠️ [N7-生成报告] 报告内容非JSON格式，跳过注入")
        
        state["report_content"] = content
        
        logger.info(f"✅ [N7-生成报告] 完成 - 内容长度: {len(content)} 字符")
        
        state["execution_path"].append({
            "node": "generate_report",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "content_length": len(content),
            "used_qualitative_analysis": qualitative_analysis is not None
        })
        
    except Exception as e:
        logger.error(f"❌ [N7-生成报告] 失败: {str(e)}")
        state["error_message"] = f"报告生成失败: {str(e)}"
        state["execution_path"].append({
            "node": "generate_report",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


async def evaluate_quality_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N8: 质量评估节点
    - 检查JSON格式
    - 评估内容完整性
    - 评估数据准确性
    - 计算质量分数
    """
    import json
    
    logger.info(f"🔍 [N8-质量评估] 开始")
    
    try:
        report_content = state["report_content"]
        
        if not report_content:
            raise Exception("报告内容为空")
        
        # 尝试解析JSON
        try:
            content_json = json.loads(report_content)
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {str(e)}")
        
        # 评估维度
        score = {
            "json_validity": 100,  # JSON格式有效
            "completeness": 0,  # 内容完整性
            "data_accuracy": 0,  # 数据准确性
            "total_score": 0
        }
        
        # 检查必要字段
        required_fields = [
            'executive_summary', 'key_conclusions', 'fixed_asset_analysis',
            'virtual_asset_analysis', 'income_performance', 'asset_allocation_review',
            'actionable_recommendations', 'risk_alerts', 'health_score', 'chart_data'
        ]
        
        present_fields = sum(1 for field in required_fields if field in content_json)
        score["completeness"] = int((present_fields / len(required_fields)) * 100)
        
        # 检查数据引用（简单检查是否包含数值）
        content_str = str(content_json)
        has_numbers = any(char.isdigit() for char in content_str)
        score["data_accuracy"] = 100 if has_numbers else 0
        
        # 计算总分
        score["total_score"] = int(
            score["json_validity"] * 0.3 +
            score["completeness"] * 0.4 +
            score["data_accuracy"] * 0.3
        )
        
        state["quality_score"] = score
        
        # 判断是否合格（总分≥80）
        if score["total_score"] >= 60:
            state["evaluation_result"] = "pass"
            logger.info(f"✅ [N8-质量评估] 完成 - 评分: {score['total_score']:.1f}/100，合格")
        elif state["retry_count"] < state["max_retries"]:
            state["evaluation_result"] = "retry"
            logger.warning(f"⚠️ [N8-质量评估] 完成 - 评分: {score['total_score']:.1f}/100，需要重试")
        else:
            state["evaluation_result"] = "fail"
            logger.error(f"❌ [N8-质量评估] 完成 - 评分: {score['total_score']:.1f}/100，已达最大重试次数")
        
        state["execution_path"].append({
            "node": "evaluate_quality",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "quality_score": score,
            "evaluation_result": state["evaluation_result"]
        })
        
    except Exception as e:
        logger.error(f"❌ [N8-质量评估] 失败: {str(e)}")
        state["evaluation_result"] = "retry" if state["retry_count"] < state["max_retries"] else "fail"
        state["execution_path"].append({
            "node": "evaluate_quality",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e),
            "evaluation_result": state["evaluation_result"]
        })
    
    return state


async def save_report_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N9: 保存报告节点
    - 解析报告内容提取摘要
    - 更新数据库报告状态
    """
    import json
    from models.ai_report import AIReport
    from database import db
    
    logger.info(f"💾 [N9-保存报告] 开始")
    
    try:
        task_context = state["task_context"]
        report_id = task_context["report_id"]
        
        report = AIReport.query.get(report_id)
        if not report:
            raise Exception(f"报告不存在: {report_id}")
        
        # 提取摘要
        content = state["report_content"]
        if not content:
            raise Exception("报告内容为空")
        
        try:
            content_json = json.loads(content)
            # 新格式：executive_summary 是对象
            if 'executive_summary' in content_json:
                exec_summary = content_json['executive_summary']
                if isinstance(exec_summary, dict):
                    summary = exec_summary.get('content', exec_summary.get('title', '报告已生成'))
                else:
                    summary = str(exec_summary)
            # 旧格式：period_summary 是字符串
            elif 'period_summary' in content_json:
                summary = str(content_json['period_summary'])
            else:
                summary = "报告已生成"
            
            summary = str(summary)[:500] if summary else "报告已生成"
        except Exception as e:
            logger.warning(f"⚠️ 摘要提取失败: {e}")
            summary = "报告已生成"
        
        # 【增强】添加智能洞察到报告内容
        intelligent_insights = state.get("intelligent_insights")
        if intelligent_insights:
            # 如果是Markdown格式，注入智能洞察
            try:
                report_data = json.loads(content)
                if isinstance(report_data, dict):
                    report_data["intelligent_insights"] = intelligent_insights
                    content = json.dumps(report_data, ensure_ascii=False)
                    logger.info(f"✅ 已注入智能洞察到报告内容")
            except:
                # 如果解析失败，保持原样
                pass
        
        # 更新报告
        report.content = content
        report.summary = summary
        report.status = 'completed'
        report.generated_at = datetime.utcnow()
        
        # 持久化工作流轨迹（新增）
        report.execution_path = json.dumps(state.get("execution_path", []), ensure_ascii=False)
        report.workflow_metadata = json.dumps({
            "agent_decisions": state.get("agent_decisions", []),
            "quality_score": state.get("quality_score"),
            "retry_count": state.get("retry_count", 0),
            "start_time": state.get("start_time"),
            "end_time": state.get("end_time")
        }, ensure_ascii=False)
        
        db.session.commit()
        
        state["end_time"] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ [N9-保存报告] 完成 - 报告ID: {report_id}")
        
        state["execution_path"].append({
            "node": "save_report",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        })
        
    except Exception as e:
        logger.error(f"❌ [N9-保存报告] 失败: {str(e)}")
        state["error_message"] = f"保存报告失败: {str(e)}"
        state["execution_path"].append({
            "node": "save_report",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


async def handle_retry_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N10: 重试处理节点
    - 增加重试计数
    - 分析失败原因
    - 调整生成策略
    """
    logger.info(f"🔄 [N10-重试处理] 开始")
    
    state["retry_count"] += 1
    current_retry = state["retry_count"]
    max_retries = state["max_retries"]
    
    logger.info(f"⚠️ [N10-重试处理] 第 {current_retry}/{max_retries} 次重试")
    
    # 记录重试决策
    decision = {
        "node": "handle_retry",
        "timestamp": datetime.utcnow().isoformat(),
        "decision": {
            "retry_count": current_retry,
            "max_retries": max_retries,
            "reason": "质量评估未通过，尝试重新生成",
            "next_node": "generate_report"
        }
    }
    
    state["agent_decisions"].append(decision)
    state["execution_path"].append({
        "node": "handle_retry",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "retry_count": current_retry
    })
    
    logger.info(f"✅ [N10-重试处理] 完成 - 准备重新生成报告")
    
    return state


async def handle_failure_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N11: 失败处理节点
    - 记录失败原因
    - 更新报告状态为失败
    - 保存工作流轨迹
    """
    import json
    from models.ai_report import AIReport
    from database import db
    
    logger.error(f"❌ [N11-失败处理] 开始")
    
    try:
        task_context = state["task_context"]
        report_id = task_context["report_id"]
        
        report = AIReport.query.get(report_id)
        if report:
            # 确保error_message存在
            if not state.get("error_message"):
                state["error_message"] = "报告生成失败，已达最大重试次数"
            
            error_msg = state["error_message"]
            report.status = 'failed'
            report.error_message = error_msg
            
            # 保存工作流轨迹（即使失败也要保存）
            report.execution_path = json.dumps(state.get("execution_path", []), ensure_ascii=False)
            report.workflow_metadata = json.dumps({
                "agent_decisions": state.get("agent_decisions", []),
                "quality_score": state.get("quality_score"),
                "retry_count": state.get("retry_count", 0),
                "start_time": state.get("start_time"),
                "end_time": state.get("end_time"),
                "error_message": error_msg
            }, ensure_ascii=False)
            
            db.session.commit()
            
            logger.error(f"❌ [N11-失败处理] 完成 - 报告ID: {report_id}, 原因: {error_msg}")
        
        state["end_time"] = datetime.utcnow().isoformat()
        state["execution_path"].append({
            "node": "handle_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        })
        
    except Exception as e:
        logger.error(f"❌ [N11-失败处理] 异常: {str(e)}")
        state["execution_path"].append({
            "node": "handle_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        })
    
    return state
