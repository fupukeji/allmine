"""
报告生成LangGraph工作流图定义 - 优化版
数据分层处理架构
"""
import logging
from langgraph.graph import StateGraph, END
from workflows.state import ReportWorkflowState
from workflows.nodes_optimized import (
    init_task_node,
    collect_fixed_assets_node,
    collect_virtual_assets_node,
    ai_integrated_analysis_node,
    query_compare_previous_node,
    generate_qualitative_conclusion_node,
    generate_report_node,
    evaluate_quality_node,
    save_report_node,
    handle_retry_node,
    handle_failure_node
)
from workflows.routes_optimized import (
    route_after_evaluation,
    route_after_retry
)

logger = logging.getLogger(__name__)


def create_report_workflow():
    """
    创建报告生成工作流 - 优化版
    
    工作流节点：
    1. init_task - 初始化任务
    2. collect_fixed_assets - 采集固定资产 + 结构化分析
    3. collect_virtual_assets - 采集虚拟资产 + 结构化分析
    4. ai_integrated_analysis - AI综合分析（固定+虚拟）
    5. query_compare_previous - 查询上期数据 + 同比环比
    6. generate_qualitative_conclusion - 生成定性结论 + 结构化存储
    7. generate_report - 生成完整报告
    8. evaluate_quality - 质量评估
    9. save_report - 保存报告
    10. handle_retry - 重试处理
    11. handle_failure - 失败处理
    
    工作流路径（线性架构）：
    N1→N2→N3→N4→N5→N6→N7→N8→N9→END
    重试路径：N8→N10→N7→N8→N9→END
    失败路径：N8→N11→END
    """
    logger.info("🔧 创建优化版报告生成工作流")
    
    workflow = StateGraph(ReportWorkflowState)
    
    # 注册节点
    workflow.add_node("init_task", init_task_node)
    workflow.add_node("collect_fixed_assets", collect_fixed_assets_node)
    workflow.add_node("collect_virtual_assets", collect_virtual_assets_node)
    workflow.add_node("ai_integrated_analysis", ai_integrated_analysis_node)
    workflow.add_node("query_compare_previous", query_compare_previous_node)
    workflow.add_node("generate_qualitative_conclusion", generate_qualitative_conclusion_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("evaluate_quality", evaluate_quality_node)
    workflow.add_node("save_report", save_report_node)
    workflow.add_node("handle_retry", handle_retry_node)
    workflow.add_node("handle_failure", handle_failure_node)
    
    # 设置入口点
    workflow.set_entry_point("init_task")
    
    # 添加固定边（线性流程）
    workflow.add_edge("init_task", "collect_fixed_assets")
    workflow.add_edge("collect_fixed_assets", "collect_virtual_assets")
    workflow.add_edge("collect_virtual_assets", "ai_integrated_analysis")
    workflow.add_edge("ai_integrated_analysis", "query_compare_previous")
    workflow.add_edge("query_compare_previous", "generate_qualitative_conclusion")
    workflow.add_edge("generate_qualitative_conclusion", "generate_report")
    workflow.add_edge("generate_report", "evaluate_quality")
    workflow.add_edge("save_report", END)
    workflow.add_edge("handle_failure", END)
    
    # 添加条件边
    workflow.add_conditional_edges(
        "evaluate_quality",
        route_after_evaluation,
        {
            "save_report": "save_report",
            "handle_retry": "handle_retry",
            "handle_failure": "handle_failure"
        }
    )
    
    workflow.add_conditional_edges(
        "handle_retry",
        route_after_retry,
        {
            "generate_report": "generate_report"
        }
    )
    
    # 编译工作流
    app = workflow.compile()
    
    logger.info("✅ 优化版报告生成工作流创建完成")
    
    return app


# 全局工作流实例
report_workflow_app = None


def get_report_workflow():
    """获取报告工作流实例（单例模式）"""
    global report_workflow_app
    
    if report_workflow_app is None:
        report_workflow_app = create_report_workflow()
    
    return report_workflow_app
