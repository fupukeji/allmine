"""
报告生成工作流状态定义 - 优化版
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class ReportWorkflowState(TypedDict):
    """报告生成工作流状态 - 数据分层处理架构"""
    
    # ==================== 任务上下文 ====================
    task_context: Dict[str, Any]  # 包含：report_id, user_id, report_type, start_date, end_date等
    
    # ==================== 数据采集层 ====================
    fixed_assets_data: Optional[Dict[str, Any]]  # 固定资产结构化数据
    fixed_assets_analysis: Optional[Dict[str, Any]]  # 固定资产分析结果
    
    virtual_assets_data: Optional[Dict[str, Any]]  # 虚拟资产结构化数据
    virtual_assets_analysis: Optional[Dict[str, Any]]  # 虚拟资产分析结果
    
    # ==================== AI分析层 ====================
    integrated_analysis: Optional[Dict[str, Any]]  # AI综合分析结果（固定+虚拟）
    
    # ==================== 对比分析层 ====================
    previous_period_data: Optional[Dict[str, Any]]  # 上期数据（固定+虚拟）
    comparison_analysis: Optional[Dict[str, Any]]  # 同比环比分析结果
    
    # ==================== 定性结论层 ====================
    qualitative_conclusion: Optional[Dict[str, Any]]  # 定性结论（文本+结构化指标）
    structured_indicators: Optional[Dict[str, Any]]  # 结构化指标存储
    
    # ==================== 报告生成层 ====================
    report_content: Optional[str]  # 生成的报告内容（JSON格式）
    
    # ==================== 质量评估层 ====================
    quality_score: Optional[Dict[str, Any]]  # 质量评分（准确性+完整性+结构性）
    evaluation_result: Optional[str]  # 评估结果：pass/retry/fail
    
    # ==================== 执行控制 ====================
    execution_path: List[Dict[str, Any]]  # 执行路径追踪
    retry_count: int  # 当前重试次数
    max_retries: int  # 最大重试次数（默认3次）
    error_message: Optional[str]  # 错误信息
    
    # ==================== 时间戳 ====================
    start_time: str  # 工作流开始时间
    end_time: Optional[str]  # 工作流结束时间
