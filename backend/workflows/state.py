"""
报告生成工作流状态定义
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class ReportWorkflowState(TypedDict):
    """报告生成工作流状态"""
    
    # 任务上下文
    task_context: Dict[str, Any]  # 包含：report_id, user_id, report_type, start_date, end_date等
    
    # 数据层
    raw_data: Optional[Dict[str, Any]]  # 原始数据（固定资产、虚拟资产等）
    compressed_text: Optional[str]  # 压缩后的文本数据
    previous_data: Optional[Dict[str, Any]]  # 上期数据（用于对比）
    comparison_text: Optional[str]  # 对比分析文本
    
    # 智能洞察层（新增）
    intelligent_insights: Optional[Dict[str, Any]]  # 智能洞察指标（健康度、效率、ROI等）
    
    # AI分析层
    ai_insights: Optional[str]  # AI预分析洞察
    report_content: Optional[str]  # 生成的报告内容（JSON格式）
    
    # 质量评估层
    quality_score: Optional[Dict[str, Any]]  # 质量评分
    evaluation_result: Optional[str]  # 评估结果：pass/retry/fail
    
    # 决策与执行路径
    agent_decisions: List[Dict[str, Any]]  # Agent决策历史
    execution_path: List[Dict[str, Any]]  # 执行路径追踪
    
    # 重试控制
    retry_count: int  # 当前重试次数
    max_retries: int  # 最大重试次数（默认3次）
    
    # 错误处理
    error_message: Optional[str]  # 错误信息
    
    # 时间戳
    start_time: str  # 工作流开始时间
    end_time: Optional[str]  # 工作流结束时间
