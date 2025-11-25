"""
报告生成工作流路由函数
定义节点间的条件跳转逻辑
"""
from workflows.state import ReportWorkflowState


def route_after_decide_comparison(state: ReportWorkflowState) -> str:
    """
    决策节点后的路由：判断是否需要查询上期数据
    """
    if not state.get("agent_decisions"):
        return "generate_report"
    
    last_decision = state["agent_decisions"][-1]
    decision = last_decision.get("decision", {})
    need_comparison = decision.get("need_comparison", False)
    
    if need_comparison:
        return "query_previous_data"
    else:
        return "ai_preanalysis"


def route_after_query_previous(state: ReportWorkflowState) -> str:
    """
    查询上期数据后的路由：直接进入AI预分析
    """
    return "ai_preanalysis"


def route_after_evaluation(state: ReportWorkflowState) -> str:
    """
    质量评估后的路由：根据评估结果决定下一步
    - pass: 保存报告
    - retry: 重试生成
    - fail: 失败处理
    """
    evaluation_result = state.get("evaluation_result") or "fail"
    
    route_mapping = {
        "pass": "save_report",
        "retry": "handle_retry",
        "fail": "handle_failure"
    }
    
    return route_mapping.get(evaluation_result, "handle_failure")


def route_after_retry(state: ReportWorkflowState) -> str:
    """
    重试处理后的路由：返回生成报告节点
    """
    return "generate_report"
