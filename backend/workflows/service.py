"""
报告生成工作流服务层 - 优化版
封装工作流调用、状态追踪、错误处理
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
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


class ReportWorkflowService:
    """报告生成工作流服务"""
    
    def __init__(self):
        self.logger = logger
    
    async def execute_workflow(self, task_context: Dict[str, Any]) -> ReportWorkflowState:
        """
        执行完整的报告生成工作流 - 优化版
        
        Args:
            task_context: 任务上下文，包含report_id, user_id, api_key, model等
        
        Returns:
            最终的工作流状态
        """
        self.logger.info(f"🚀 执行优化版工作流 - 报告ID: {task_context.get('report_id')}")
        
        # 初始化状态
        state: ReportWorkflowState = {
            "task_context": task_context,
            "fixed_assets_data": None,
            "fixed_assets_analysis": None,
            "virtual_assets_data": None,
            "virtual_assets_analysis": None,
            "integrated_analysis": None,
            "previous_period_data": None,
            "comparison_analysis": None,
            "qualitative_conclusion": None,
            "structured_indicators": None,
            "report_content": None,
            "quality_score": None,
            "evaluation_result": None,
            "execution_path": [],
            "retry_count": 0,
            "max_retries": 3,
            "error_message": None,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None
        }
        
        try:
            # 获取工作流应用
            from workflows.graph_optimized import get_report_workflow
            workflow_app = get_report_workflow()
            
            if workflow_app is None:
                self.logger.warning("⚠️ LangGraph不可用，使用手动执行模式")
                state = await self._execute_node_sequence(state)
            else:
                self.logger.info("✅ 使用LangGraph图驱动执行")
                final_state = await workflow_app.ainvoke(state)
                # 类型转换：LangGraph返回的是dict，需要更新到state中
                for key, value in final_state.items():
                    state[key] = value
            
            self.logger.info(f"✅ 工作流执行完成 - 报告ID: {task_context.get('report_id')}")
            
        except Exception as e:
            self.logger.error(f"❌ 工作流执行失败: {str(e)}")
            import traceback
            self.logger.error(f"堆栈信息:\n{traceback.format_exc()}")
            state["error_message"] = str(e)
            state["end_time"] = datetime.utcnow().isoformat()
        
        return state
    
    async def _execute_node_sequence(self, state: ReportWorkflowState) -> ReportWorkflowState:
        """
        执行节点序列（手动实现工作流逻辑）- 优化版
        """
        # N1: 初始化
        state = await init_task_node(state)
        if state.get("error_message"):
            return await handle_failure_node(state)
        
        # N2: 采集固定资产
        state = await collect_fixed_assets_node(state)
        if state.get("error_message"):
            return await handle_failure_node(state)
        
        # N3: 采集虚拟资产
        state = await collect_virtual_assets_node(state)
        if state.get("error_message"):
            return await handle_failure_node(state)
        
        # N4: AI综合分析
        state = await ai_integrated_analysis_node(state)
        
        # N5: 查询上期对比
        state = await query_compare_previous_node(state)
        
        # N6: 生成定性结论
        state = await generate_qualitative_conclusion_node(state)
        
        # 进入生成-评估-重试循环
        while True:
            # N7: 生成报告
            state = await generate_report_node(state)
            if state.get("error_message"):
                return await handle_failure_node(state)
            
            # N8: 质量评估
            state = await evaluate_quality_node(state)
            
            # 根据评估结果路由
            next_action = route_after_evaluation(state)
            
            if next_action == "save_report":
                # N9: 保存报告
                state = await save_report_node(state)
                break
            
            elif next_action == "handle_retry":
                # N10: 重试处理
                state = await handle_retry_node(state)
                continue
            
            else:  # handle_failure
                # N11: 失败处理
                state = await handle_failure_node(state)
                break
        
        return state
    
    def get_workflow_visualization(self) -> Dict[str, Any]:
        """
        获取工作流可视化数据（Mermaid格式）- 优化版
        """
        mermaid_graph = """
graph TD
    A[初始化任务] --> B[采集固定资产]
    B --> C[采集虚拟资产]
    C --> D[AI综合分析]
    D --> E[上期对比分析]
    E --> F[生成定性结论]
    F --> G[生成报告]
    G --> H[质量评估]
    H --> I{评估结果}
    I -->|合格| J[保存报告]
    I -->|重试| K[重试处理]
    I -->|失败| L[失败处理]
    K --> G
    J --> M((结束))
    L --> M
"""
        
        return {
            "format": "mermaid",
            "graph": mermaid_graph,
            "nodes": [
                {"id": "init_task", "name": "初始化任务", "type": "start"},
                {"id": "collect_fixed_assets", "name": "采集固定资产", "type": "process"},
                {"id": "collect_virtual_assets", "name": "采集虚拟资产", "type": "process"},
                {"id": "ai_integrated_analysis", "name": "AI综合分析", "type": "process"},
                {"id": "query_compare_previous", "name": "上期对比分析", "type": "process"},
                {"id": "generate_qualitative_conclusion", "name": "生成定性结论", "type": "process"},
                {"id": "generate_report", "name": "生成报告", "type": "process"},
                {"id": "evaluate_quality", "name": "质量评估", "type": "process"},
                {"id": "save_report", "name": "保存报告", "type": "end"},
                {"id": "handle_retry", "name": "重试处理", "type": "process"},
                {"id": "handle_failure", "name": "失败处理", "type": "end"}
            ]
        }


# 全局服务实例
_workflow_service: Optional[ReportWorkflowService] = None


def get_workflow_service() -> ReportWorkflowService:
    """获取工作流服务实例（单例）"""
    global _workflow_service
    
    if _workflow_service is None:
        _workflow_service = ReportWorkflowService()
    
    return _workflow_service
