"""
报告生成LangGraph工作流图定义
"""
import logging
from langgraph.graph import StateGraph, END
from workflows.state import ReportWorkflowState
from workflows.nodes import (
    init_task_node,
    collect_data_node,
    compress_data_node,
    agent_decide_comparison_node,
    query_previous_data_node,
    ai_preanalysis_node,
    generate_report_node,
    evaluate_quality_node,
    save_report_node,
    handle_retry_node,
    handle_failure_node
)
from workflows.routes import (
    route_after_decide_comparison,
    route_after_query_previous,
    route_after_evaluation,
    route_after_retry
)

logger = logging.getLogger(__name__)


def create_report_workflow():
    """
    创建报告生成工作流
    
    工作流节点：
    1. init_task - 初始化任务
    2. collect_data - 数据采集
    3. compress_data - 数据压缩
    4. agent_decide_comparison - Agent决策是否需要上期对比
    5. query_previous_data - 查询上期数据（条件）
    6. ai_preanalysis - AI预分析（可选）
    7. generate_report - 生成报告
    8. evaluate_quality - 质量评估
    9. save_report - 保存报告
    10. handle_retry - 重试处理
    11. handle_failure - 失败处理
    
    工作流路径：
    - 正常路径：1→2→3→4→6→7→8→9→END
    - 需要对比：1→2→3→4→5→6→7→8→9→END
    - 需要重试：1→2→3→4→6→7→8→10→7→8→9→END
    - 失败路径：1→2→3→4→6→7→8→11→END
    """
    logger.info("🔧 开始创建报告生成工作流")
    
    # 创建状态图
    workflow = StateGraph(ReportWorkflowState)
    
    # 注册节点
    workflow.add_node("init_task", init_task_node)
    workflow.add_node("collect_data", collect_data_node)
    workflow.add_node("compress_data", compress_data_node)
    workflow.add_node("agent_decide_comparison", agent_decide_comparison_node)
    workflow.add_node("query_previous_data", query_previous_data_node)
    workflow.add_node("ai_preanalysis", ai_preanalysis_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("evaluate_quality", evaluate_quality_node)
    workflow.add_node("save_report", save_report_node)
    workflow.add_node("handle_retry", handle_retry_node)
    workflow.add_node("handle_failure", handle_failure_node)
    
    # 设置入口点
    workflow.set_entry_point("init_task")
    
    # 添加固定边
    workflow.add_edge("init_task", "collect_data")
    workflow.add_edge("collect_data", "compress_data")
    workflow.add_edge("compress_data", "agent_decide_comparison")
    workflow.add_edge("ai_preanalysis", "generate_report")
    workflow.add_edge("generate_report", "evaluate_quality")
    workflow.add_edge("save_report", END)
    workflow.add_edge("handle_failure", END)
    
    # 添加条件边
    workflow.add_conditional_edges(
        "agent_decide_comparison",
        route_after_decide_comparison,
        {
            "query_previous_data": "query_previous_data",
            "ai_preanalysis": "ai_preanalysis"
        }
    )
    
    workflow.add_conditional_edges(
        "query_previous_data",
        route_after_query_previous,
        {
            "ai_preanalysis": "ai_preanalysis"
        }
    )
    
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
    
    logger.info("✅ 报告生成工作流创建完成 (LangGraph驱动)")
    
    return app


# 全局工作流实例（延迟初始化）
report_workflow_app = None


def get_report_workflow():
    """获取报告工作流实例（单例模式）"""
    global report_workflow_app
    
    if report_workflow_app is None:
        report_workflow_app = create_report_workflow()
    
    return report_workflow_app
