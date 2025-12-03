"""
报告生成工作流路由函数 - 优化版
"""
from workflows.state import ReportWorkflowState


def route_after_evaluation(state: ReportWorkflowState) -> str:
    """
    质量评估后的路由
    - pass: 保存报告
    - retry: 重试生成
    - fail: 失败处理
    """
    evaluation_result = state.get("evaluation_result", "fail")
    
    route_mapping = {
        "pass": "save_report",
        "retry": "handle_retry",
        "fail": "handle_failure"
    }
    
    return route_mapping.get(evaluation_result, "handle_failure")


def route_after_retry(state: ReportWorkflowState) -> str:
    """
    重试处理后的路由：返回报告生成节点
    """
    return "generate_report"
