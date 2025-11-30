"""
报告生成工作流服务层
封装工作流调用、状态跟踪、错误处理
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
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
        执行完整的报告生成工作流 (LangGraph驱动)
        
        Args:
            task_context: 任务上下文，包含report_id, user_id, api_key, model等
        
        Returns:
            最终的工作流状态
        """
        self.logger.info(f"🚀 开始执行LangGraph工作流 - 报告ID: {task_context.get('report_id')}")
        
        # 初始化状态
        state: ReportWorkflowState = {
            "task_context": task_context,
            "raw_data": None,
            "compressed_text": None,
            "previous_data": None,
            "comparison_text": None,
            "intelligent_insights": None,  # 新增
            "ai_insights": None,
            "report_content": None,
            "quality_score": None,
            "evaluation_result": None,
            "agent_decisions": [],
            "execution_path": [],
            "retry_count": 0,
            "max_retries": 3,
            "error_message": None,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None
        }
        
        try:
            # 获取工作流应用
            from workflows.graph import get_report_workflow
            workflow_app = get_report_workflow()
            
            if workflow_app is None:
                # 降级到手动执行模式
                self.logger.warning("⚠️ LangGraph不可用，使用手动执行模式")
                state = await self._execute_node_sequence(state)
            else:
                # 使用LangGraph执行
                self.logger.info("✅ 使用LangGraph图驱动执行")
                final_state = await workflow_app.ainvoke(state)
                state = final_state
            
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
        执行节点序列（手动实现工作流逻辑）
        由于LangGraph尚未安装，这里用传统方式实现工作流
        """
        # N1: 初始化
        state = await init_task_node(state)
        if state.get("error_message"):
            return await handle_failure_node(state)
        
        # N2: 数据采集
        state = await collect_data_node(state)
        if state.get("error_message"):
            return await handle_failure_node(state)
        
        # N3: 数据压缩
        state = await compress_data_node(state)
        if state.get("error_message"):
            return await handle_failure_node(state)
        
        # N4: Agent决策是否需要上期对比
        state = await agent_decide_comparison_node(state)
        next_node = route_after_decide_comparison(state)
        
        # N5: 查询上期数据（条件）
        if next_node == "query_previous_data":
            state = await query_previous_data_node(state)
        
        # N6: AI预分析
        state = await ai_preanalysis_node(state)
        
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
                # 继续循环，重新生成
                continue
            
            else:  # handle_failure
                # N11: 失败处理
                state = await handle_failure_node(state)
                break
        
        return state
    
    def get_workflow_visualization(self) -> Dict[str, Any]:
        """
        获取工作流可视化数据（Mermaid格式）
        """
        mermaid_graph = """
graph TD
    A[初始化任务] --> B[数据采集]
    B --> C[数据压缩]
    C --> D{Agent决策<br/>需要对比?}
    D -->|是| E[查询上期数据]
    D -->|否| F[AI预分析]
    E --> F
    F --> G[生成报告]
    G --> H[质量评估]
    H --> I{评估结果}
    I -->|合格| J[保存报告]
    I -->|重试| K[重试处理]
    I -->|失败| L[失败处理]
    K --> G
    J --> M((结束))
    L --> M
    
    style A fill:#e1f5e1
    style J fill:#c8e6c9
    style L fill:#ffcdd2
    style D fill:#fff9c4
    style I fill:#fff9c4
"""
        
        return {
            "format": "mermaid",
            "graph": mermaid_graph,
            "nodes": [
                {"id": "init_task", "name": "初始化任务", "type": "start"},
                {"id": "collect_data", "name": "数据采集", "type": "process"},
                {"id": "compress_data", "name": "数据压缩", "type": "process"},
                {"id": "agent_decide_comparison", "name": "Agent决策", "type": "decision"},
                {"id": "query_previous_data", "name": "查询上期数据", "type": "process"},
                {"id": "ai_preanalysis", "name": "AI预分析", "type": "process"},
                {"id": "generate_report", "name": "生成报告", "type": "process"},
                {"id": "evaluate_quality", "name": "质量评估", "type": "process"},
                {"id": "save_report", "name": "保存报告", "type": "end"},
                {"id": "handle_retry", "name": "重试处理", "type": "process"},
                {"id": "handle_failure", "name": "失败处理", "type": "end"}
            ],
            "edges": [
                {"from": "init_task", "to": "collect_data", "type": "fixed"},
                {"from": "collect_data", "to": "compress_data", "type": "fixed"},
                {"from": "compress_data", "to": "agent_decide_comparison", "type": "fixed"},
                {"from": "agent_decide_comparison", "to": "query_previous_data", "type": "conditional", "condition": "需要对比"},
                {"from": "agent_decide_comparison", "to": "ai_preanalysis", "type": "conditional", "condition": "无需对比"},
                {"from": "query_previous_data", "to": "ai_preanalysis", "type": "fixed"},
                {"from": "ai_preanalysis", "to": "generate_report", "type": "fixed"},
                {"from": "generate_report", "to": "evaluate_quality", "type": "fixed"},
                {"from": "evaluate_quality", "to": "save_report", "type": "conditional", "condition": "合格"},
                {"from": "evaluate_quality", "to": "handle_retry", "type": "conditional", "condition": "重试"},
                {"from": "evaluate_quality", "to": "handle_failure", "type": "conditional", "condition": "失败"},
                {"from": "handle_retry", "to": "generate_report", "type": "fixed"}
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
