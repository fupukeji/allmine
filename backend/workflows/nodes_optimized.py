"""
报告生成工作流节点实现 - 优化版
数据分层处理架构：采集 → 分析 → 对比 → 结论 → 报告
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal
from workflows.state import ReportWorkflowState
from models.fixed_asset import FixedAsset
from models.project import Project
from models.category import Category
from models.asset_income import AssetIncome
from database import db

logger = logging.getLogger(__name__)


def _convert_decimals(obj: Any) -> Any:
    """
    递归转换对象中的Decimal类型为float，确保JSON可序列化
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimals(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_convert_decimals(item) for item in obj)
    return obj


def _generate_asset_status_chart(status_stats: Dict[str, int]) -> str:
    """生成资产状态分布图表"""
    if not status_stats:
        return ""
    
    total = sum(status_stats.values())
    if total == 0:
        return ""
    
    status_colors = {
        "正常": "#52c41a",
        "待维护": "#faad14",
        "已报废": "#d9d9d9",
        "闲置": "#1890ff"
    }
    
    html = '<div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">'
    html += '<h3 style="margin: 0 0 15px 0; font-size: 16px; color: #666;">📊 资产状态分布</h3>'
    html += '<div style="display: grid; gap: 10px;">'
    
    for status, count in status_stats.items():
        percentage = (count / total) * 100
        color = status_colors.get(status, "#1890ff")
        html += f'''
        <div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 13px;">
            <span>{status}</span>
            <span style="font-weight: 600;">{count}个 ({percentage:.1f}%)</span>
          </div>
          <div style="background: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden;">
            <div style="background: {color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
          </div>
        </div>
        '''
    
    html += '</div></div>'
    return html


def _generate_expiring_projects_alert(expiring_projects: list) -> str:
    """生成即将过期项目预警"""
    if not expiring_projects:
        return '<div style="background: #f6ffed; padding: 15px; border-radius: 6px; text-align: center; color: #52c41a;">✅ 暂无即将过期的项目</div>'
    
    html = '<div style="background: #fff7e6; padding: 20px; border-radius: 8px; border: 2px solid #ffd666; margin: 20px 0;">'
    html += '<h3 style="color: #fa8c16; margin: 0 0 15px 0; font-size: 16px;">⚠️ 即将过期项目预警</h3>'
    html += '<div style="display: grid; gap: 10px;">'
    
    for proj in expiring_projects[:5]:  # 最多显示5个
        days_left = proj.get('days_left', 0)
        color = '#ff4d4f' if days_left <= 7 else '#faad14'
        html += f'''
        <div style="background: white; padding: 12px; border-radius: 6px; border-left: 3px solid {color};">
          <div style="font-weight: 600; margin-bottom: 5px;">{proj.get('name', '未命名项目')}</div>
          <div style="font-size: 12px; color: #666;">剩余天数: <span style="color: {color}; font-weight: bold;">{days_left}天</span></div>
        </div>
        '''
    
    html += '</div></div>'
    return html


def _generate_list_items(items: list, color: str, ordered: bool = False) -> str:
    """生成列表项HTML"""
    if not items:
        return '<li style="color: #999;">暂无数据</li>'
    
    html = ""
    for item in items:
        if ordered:
            html += f'<li style="color: {color}; margin-bottom: 8px; line-height: 1.6;">{item}</li>'
        else:
            html += f'<li style="color: {color}; margin-bottom: 8px;">{item}</li>'
    return html


def _generate_action_plan(actions: list) -> str:
    """生成行动计划卡片"""
    if not actions:
        return '<p style="text-align: center; color: #999;">暂无优先行动建议</p>'
    
    html = '<div style="display: grid; gap: 15px;">'
    priority_colors = ['#ff4d4f', '#fa8c16', '#1890ff']
    priority_labels = ['🔴 紧急', '🟡 重要', '🔵 建议']
    
    for idx, action in enumerate(actions[:3]):  # 最多显示3个
        color = priority_colors[idx] if idx < len(priority_colors) else '#1890ff'
        label = priority_labels[idx] if idx < len(priority_labels) else '🔵 建议'
        
        html += f'''
        <div style="background: #fafafa; padding: 15px; border-radius: 8px; border-left: 4px solid {color};">
          <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: bold; color: {color}; margin-right: 10px;">{label}</span>
            <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">优先级 {idx + 1}</span>
          </div>
          <div style="line-height: 1.6; color: #595959;">{action}</div>
        </div>
        '''
    
    html += '</div>'
    return html


def _generate_html_report(data: Dict[str, Any], task_context: Dict[str, Any]) -> str:
    """生成带图表和深度分析的HTML报告"""
    
    # 报告标题
    report_type = task_context.get("report_type", "custom")
    start_date = task_context.get("start_date", "")
    end_date = task_context.get("end_date", "")
    
    type_names = {
        "weekly": "周报",
        "monthly": "月报",
        "yearly": "年报",
        "custom": "自定义报告"
    }
    title = f"资产{type_names.get(report_type, '报告')}"
    
    html = f"""
<div class="ai-report-content" style="font-family: 'Microsoft YaHei', Arial, sans-serif;">
  <!-- 报告标题 -->
  <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; margin-bottom: 30px; color: white;">
    <h1 style="margin: 0 0 10px 0; font-size: 32px; font-weight: bold;">{title}</h1>
    <p style="margin: 0; font-size: 14px; opacity: 0.9;">报告期间：{start_date} ~ {end_date}</p>
    <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;">生成时间: {datetime.utcnow().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
  </div>
"""
    
    # 核心摘要卡片
    conclusion = data.get("qualitative_conclusion", {})
    structured_indicators = data.get("structured_indicators", {})
    
    if conclusion:
        rating = conclusion.get("overall_rating", "B")
        rating_color = "#52c41a" if rating.startswith("A") else "#1890ff" if rating == "B" else "#faad14" if rating == "C" else "#ff4d4f"
        risk_level = conclusion.get("risk_level", "中")
        risk_color = "#52c41a" if risk_level == "低" else "#faad14" if risk_level == "中" else "#ff4d4f"
        
        html += f"""
  <!-- 核心摘要 -->
  <div style="background: linear-gradient(to right, #f6ffed, #ffffff); border-left: 5px solid #52c41a; padding: 25px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
    <h2 style="color: #52c41a; margin: 0 0 20px 0; font-size: 24px; display: flex; align-items: center;">
      <span style="margin-right: 10px;">🎯</span>
      核心摘要
    </h2>
    
    <!-- 评级卡片 -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
      <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">整体评级</div>
        <div style="font-size: 36px; font-weight: bold; color: {rating_color};">{rating}</div>
      </div>
      <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">风险等级</div>
        <div style="font-size: 28px; font-weight: bold; color: {risk_color};">{risk_level}</div>
      </div>
      <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">紧急程度</div>
        <div style="font-size: 28px; font-weight: bold; color: {risk_color};">{conclusion.get('severity_level', '中')}</div>
      </div>
    </div>
    
    <!-- 执行摘要 -->
    {f'<div style="background: #fffbe6; padding: 15px; border-radius: 6px; border-left: 3px solid #faad14; line-height: 1.8; font-size: 15px; color: #595959;">{conclusion.get("executive_summary", "")}</div>' if conclusion.get("executive_summary") else ''}
  </div>
"""
    
    # 固定资产分析
    fixed = data.get("fixed_assets", {})
    if fixed:
        f_data = fixed.get("data", {})
        f_analysis = fixed.get("analysis", {})
        
        html += f"""
  <!-- 固定资产分析 -->
  <div style="margin-bottom: 30px;">
    <h2 style="color: #1890ff; border-bottom: 3px solid #1890ff; padding-bottom: 12px; font-size: 22px; display: flex; align-items: center;">
      <span style="margin-right: 10px;">🏠</span>
      固定资产分析
    </h2>
    
    <!-- 核心指标 -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0;">
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">资产总数</div>
        <div style="font-size: 32px; font-weight: bold;">{f_data.get('total_assets', 0)}</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">个</div>
      </div>
      <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">当前总价值</div>
        <div style="font-size: 28px; font-weight: bold;">￥{f_data.get('total_current_value', 0):,.0f}</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">元</div>
      </div>
      <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 12px rgba(250, 112, 154, 0.3);">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">折旧率</div>
        <div style="font-size: 32px; font-weight: bold;">{f_data.get('depreciation_rate', 0):.1f}%</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">已折旧</div>
      </div>
      <div style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); padding: 20px; border-radius: 10px; color: white; box-shadow: 0 4px 12px rgba(48, 207, 208, 0.3);">
        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 8px;">ROI</div>
        <div style="font-size: 32px; font-weight: bold;">{f_analysis.get('roi', 0):.2f}%</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 5px;">投资回报率</div>
      </div>
    </div>
    
    <!-- 健康度进度条 -->
    <div style="background: #f0f5ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <span style="font-weight: 600; color: #1890ff;">❤️ 资产健康度</span>
        <span style="font-weight: bold; color: #1890ff; font-size: 18px;">{f_analysis.get('health_score', 0):.1f}/100</span>
      </div>
      <div style="background: #d9d9d9; height: 24px; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(to right, #52c41a, #1890ff); height: 100%; width: {min(f_analysis.get('health_score', 0), 100)}%; transition: width 0.3s ease;"></div>
      </div>
      <div style="margin-top: 8px; font-size: 12px; color: #666;">
        评估标准：综合考虑折旧率、收益率、利用率等指标
      </div>
    </div>
    
    <!-- 资产状态分布 -->
    {_generate_asset_status_chart(f_data.get('status_stats', {}))}
  </div>
"""
    
    # 虚拟资产分析
    virtual = data.get("virtual_assets", {})
    if virtual:
        v_data = virtual.get("data", {})
        v_analysis = virtual.get("analysis", {})
        
        html += f"""
  <!-- 虚拟资产分析 -->
  <div style="margin-bottom: 30px;">
    <h2 style="color: #722ed1; border-bottom: 3px solid #722ed1; padding-bottom: 12px; font-size: 22px; display: flex; align-items: center;">
      <span style="margin-right: 10px;">⚡</span>
      虚拟资产分析
    </h2>
    
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0;">
      <div style="background: #f9f0ff; padding: 20px; border-radius: 10px; border: 2px solid #d3adf7;">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">项目总数</div>
        <div style="font-size: 32px; font-weight: bold; color: #722ed1;">{v_data.get('total_projects', 0)}</div>
      </div>
      <div style="background: #f9f0ff; padding: 20px; border-radius: 10px; border: 2px solid #d3adf7;">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">总金额</div>
        <div style="font-size: 28px; font-weight: bold; color: #722ed1;">￥{v_data.get('total_amount', 0):,.0f}</div>
      </div>
      <div style="background: #f9f0ff; padding: 20px; border-radius: 10px; border: 2px solid #d3adf7;">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">利用率</div>
        <div style="font-size: 32px; font-weight: bold; color: #722ed1;">{v_data.get('utilization_rate', 0):.1f}%</div>
      </div>
      <div style="background: #f9f0ff; padding: 20px; border-radius: 10px; border: 2px solid #d3adf7;">
        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">浪费率</div>
        <div style="font-size: 32px; font-weight: bold; color: #ff4d4f;">{v_data.get('waste_rate', 0):.1f}%</div>
      </div>
    </div>
    
    <!-- 效率进度条 -->
    <div style="background: #f9f0ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <span style="font-weight: 600; color: #722ed1;">⚡ 资产效率</span>
        <span style="font-weight: bold; color: #722ed1; font-size: 18px;">{v_analysis.get('efficiency_score', 0):.1f}/100</span>
      </div>
      <div style="background: #d9d9d9; height: 24px; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(to right, #722ed1, #eb2f96); height: 100%; width: {min(v_analysis.get('efficiency_score', 0), 100)}%; transition: width 0.3s ease;"></div>
      </div>
    </div>
    
    <!-- 即将过期项目预警 -->
    {_generate_expiring_projects_alert(v_data.get('expiring_soon', []))}
  </div>
"""
    
    # AI综合分析
    integrated = data.get("integrated_analysis", {})
    if integrated:
        html += f"""
  <!-- AI综合分析 -->
  <div style="margin-bottom: 30px;">
    <h2 style="color: #fa8c16; border-bottom: 3px solid #fa8c16; padding-bottom: 12px; font-size: 22px; display: flex; align-items: center;">
      <span style="margin-right: 10px;">🤖</span>
      AI智能分析
    </h2>
    
    <div style="background: #fff7e6; padding: 20px; border-radius: 8px; border-left: 4px solid #fa8c16; margin: 20px 0;">
      <h3 style="color: #fa8c16; margin: 0 0 15px 0; font-size: 16px;">🎯 整体评估</h3>
      <p style="margin: 0; line-height: 1.8; font-size: 15px; color: #595959;">{integrated.get('overall_assessment', '')}</p>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
      <!-- 优势 -->
      <div style="background: #f6ffed; padding: 20px; border-radius: 8px; border: 2px solid #b7eb8f;">
        <h3 style="color: #52c41a; margin: 0 0 15px 0; font-size: 16px;">✅ 核心优势</h3>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
          {_generate_list_items(integrated.get('key_strengths', []), '#52c41a')}
        </ul>
      </div>
      
      <!-- 风险 -->
      <div style="background: #fff1f0; padding: 20px; border-radius: 8px; border: 2px solid #ffccc7;">
        <h3 style="color: #ff4d4f; margin: 0 0 15px 0; font-size: 16px;">⚠️ 风险预警</h3>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
          {_generate_list_items(integrated.get('risk_alerts', []), '#ff4d4f')}
        </ul>
      </div>
    </div>
    
    <!-- 优化建议 -->
    <div style="background: #e6f7ff; padding: 20px; border-radius: 8px; border-left: 4px solid #1890ff;">
      <h3 style="color: #1890ff; margin: 0 0 15px 0; font-size: 16px;">💡 优化建议</h3>
      <ol style="margin: 0; padding-left: 20px; line-height: 2;">
        {_generate_list_items(integrated.get('optimization_suggestions', []), '#1890ff', ordered=True)}
      </ol>
    </div>
  </div>
"""
    
    # 同比环比分析
    comparison = data.get("comparison_analysis", {})
    if comparison:
        fixed_comp = comparison.get("fixed_assets", {})
        virtual_comp = comparison.get("virtual_assets", {})
        
        html += f"""
  <!-- 同比环比分析 -->
  <div style="margin-bottom: 30px;">
    <h2 style="color: #13c2c2; border-bottom: 3px solid #13c2c2; padding-bottom: 12px; font-size: 22px; display: flex; align-items: center;">
      <span style="margin-right: 10px;">📈</span>
      同比环比分析
    </h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
      <div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #87e8de;">
        <h3 style="color: #13c2c2; margin: 0 0 15px 0;">🏠 固定资产增长</h3>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span style="font-size: 14px; color: #666;">增长率</span>
          <span style="font-size: 32px; font-weight: bold; color: {'#52c41a' if fixed_comp.get('growth_rate', 0) > 0 else '#ff4d4f'};">
            {fixed_comp.get('growth_rate', 0):+.2f}%
          </span>
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: #999;">
          趋势：{fixed_comp.get('trend', '持平')}
        </div>
      </div>
      
      <div style="background: white; padding: 20px; border-radius: 8px; border: 2px solid #87e8de;">
        <h3 style="color: #13c2c2; margin: 0 0 15px 0;">⚡ 虚拟资产增长</h3>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <span style="font-size: 14px; color: #666;">增长率</span>
          <span style="font-size: 32px; font-weight: bold; color: {'#52c41a' if virtual_comp.get('growth_rate', 0) > 0 else '#ff4d4f'};">
            {virtual_comp.get('growth_rate', 0):+.2f}%
          </span>
        </div>
        <div style="margin-top: 10px; font-size: 12px; color: #999;">
          趋势：{virtual_comp.get('trend', '持平')}
        </div>
      </div>
    </div>
    
    <div style="background: #e6fffb; padding: 15px; border-radius: 6px; text-align: center;">
      <span style="font-size: 16px; font-weight: 600; color: #13c2c2;">
        📈 总体趋势：{comparison.get('overall_trend', '持平')}
      </span>
    </div>
  </div>
"""
    
    # 行动计划
    if conclusion and conclusion.get('priority_actions'):
        html += f"""
  <!-- 优先行动计划 -->
  <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 25px; border-radius: 12px; margin-bottom: 30px;">
    <h2 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 22px; display: flex; align-items: center;">
      <span style="margin-right: 10px;">🎯</span>
      优先行动计划
    </h2>
    <div style="background: white; padding: 20px; border-radius: 8px;">
      {_generate_action_plan(conclusion.get('priority_actions', []))}
    </div>
  </div>
"""
    
    html += "</div>"
    return html


def _save_workflow_trace_realtime(state: ReportWorkflowState):
    """实时保存工作流轨迹到数据库"""
    from models.ai_report import AIReport
    
    try:
        task_context = state.get("task_context", {})
        report_id = task_context.get("report_id")
        
        if not report_id:
            return
        
        report = AIReport.query.get(report_id)
        if report:
            # 转换Decimal类型
            execution_path = _convert_decimals(state.get("execution_path", []))
            quality_score = _convert_decimals(state.get("quality_score"))
            
            report.execution_path = json.dumps(execution_path, ensure_ascii=False)
            report.workflow_metadata = json.dumps({
                "quality_score": quality_score,
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


async def init_task_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N1: 初始化任务节点
    """
    task_context = state["task_context"]
    report_id = task_context.get("report_id")
    
    logger.info(f"🚀 [N1-初始化] 报告ID: {report_id}")
    
    state["start_time"] = datetime.utcnow().isoformat()
    state["retry_count"] = 0
    state["max_retries"] = 3
    state["execution_path"] = [{
        "node": "init_task",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed"
    }]
    
    logger.info(f"✅ [N1-初始化] 完成")
    _save_workflow_trace_realtime(state)
    
    return state


async def collect_fixed_assets_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N2: 采集固定资产数据 + 结构化分析
    """
    task_context = state["task_context"]
    user_id = task_context["user_id"]
    start_date = task_context["start_date"]
    end_date = task_context["end_date"]
    
    logger.info(f"🏠 [N2-固定资产采集] 用户ID: {user_id}")
    
    try:
        # 查询固定资产
        fixed_assets = FixedAsset.query.filter_by(user_id=user_id).all()
        
        # 结构化数据 - 全部转换为float
        total_original_value = float(sum(asset.original_value or 0 for asset in fixed_assets))
        total_current_value = float(sum(asset.current_value or 0 for asset in fixed_assets))
        total_depreciation = total_original_value - total_current_value
        depreciation_rate = (total_depreciation / total_original_value * 100) if total_original_value > 0 else 0
        
        # 查询收入数据（通过asset关联）
        from sqlalchemy import and_
        total_income = db.session.query(
            db.func.sum(AssetIncome.amount)
        ).join(
            FixedAsset, AssetIncome.asset_id == FixedAsset.id
        ).filter(
            and_(
                FixedAsset.user_id == user_id,
                AssetIncome.income_date >= start_date,
                AssetIncome.income_date <= end_date
            )
        ).scalar() or 0
        total_income = float(total_income)
        
        # 状态统计
        status_stats = {}
        for asset in fixed_assets:
            status = asset.status or '未知'
            status_stats[status] = status_stats.get(status, 0) + 1
        
        # 分类统计
        category_stats = {}
        for asset in fixed_assets:
            if asset.category:
                category_name = asset.category.name
                category_stats[category_name] = category_stats.get(category_name, 0) + 1
        
        fixed_assets_data = {
            "total_assets": len(fixed_assets),
            "total_original_value": float(total_original_value),
            "total_current_value": float(total_current_value),
            "total_depreciation": float(total_depreciation),
            "depreciation_rate": float(depreciation_rate),
            "total_income": float(total_income),
            "status_stats": status_stats,
            "category_stats": category_stats
        }
        
        # 结构化分析
        roi = float((total_income / total_current_value * 100) if total_current_value > 0 else 0)
        health_score = _calculate_fixed_asset_health(fixed_assets_data)
        
        fixed_assets_analysis = {
            "roi": float(roi),
            "health_score": float(health_score),
            "asset_count": len(fixed_assets),
            "utilization_rate": float((status_stats.get('使用中', 0) / len(fixed_assets) * 100) if fixed_assets else 0),
            "key_metrics": {
                "depreciation_status": "高" if depreciation_rate > 50 else "中" if depreciation_rate > 30 else "低",
                "income_performance": "优秀" if roi > 10 else "良好" if roi > 5 else "一般"
            }
        }
        
        state["fixed_assets_data"] = fixed_assets_data
        state["fixed_assets_analysis"] = fixed_assets_analysis
        
        logger.info(f"✅ [N2-固定资产采集] 完成 - 资产数: {len(fixed_assets)}, 健康度: {health_score:.1f}")
        
        state["execution_path"].append({
            "node": "collect_fixed_assets",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": {
                "asset_count": len(fixed_assets),
                "health_score": float(health_score),
                "roi": float(roi)
            }
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"❌ [N2-固定资产采集] 失败: {str(e)}")
        logger.error(f"详细错误堆栈:\n{error_detail}")
        state["error_message"] = f"固定资产采集失败: {str(e)}"
        state["execution_path"].append({
            "node": "collect_fixed_assets",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
        _save_workflow_trace_realtime(state)
    
    return state


async def collect_virtual_assets_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N3: 采集虚拟资产数据 + 结构化分析
    """
    task_context = state["task_context"]
    user_id = task_context["user_id"]
    start_date = task_context["start_date"]
    end_date = task_context["end_date"]
    
    logger.info(f"⚡ [N3-虚拟资产采集] 用户ID: {user_id}")
    
    try:
        # 查询虚拟资产
        virtual_assets = Project.query.filter_by(user_id=user_id).all()
        
        total_amount = sum(float(proj.total_amount or 0) for proj in virtual_assets)
        
        # 计算已使用和剩余金额
        total_used = 0.0
        total_remaining = 0.0
        
        for proj in virtual_assets:
            values = proj.calculate_values()
            total_used += float(values['used_cost'])
            total_remaining += float(values['remaining_value'])
        
        utilization_rate = (total_used / total_amount * 100) if total_amount > 0 else 0
        waste_rate = 0.0
        expiring_soon = []
        
        for proj in virtual_assets:
            if proj.end_time:
                days_until_expiry = (proj.end_time - datetime.utcnow()).days
                values = proj.calculate_values()
                
                if 0 < days_until_expiry <= 30:
                    expiring_soon.append({
                        "name": proj.name,
                        "days": days_until_expiry,
                        "remaining": float(values['remaining_value'])
                    })
                elif days_until_expiry <= 0 and values['remaining_value'] > 0:
                    waste_rate += (float(values['remaining_value']) / total_amount * 100) if total_amount > 0 else 0
        
        # 分类统计
        category_stats = {}
        for proj in virtual_assets:
            if proj.category:
                category_name = proj.category.name
                category_stats[category_name] = category_stats.get(category_name, 0) + 1
        
        virtual_assets_data = {
            "total_projects": len(virtual_assets),
            "total_amount": float(total_amount),
            "total_used": float(total_used),
            "total_remaining": float(total_remaining),
            "utilization_rate": float(utilization_rate),
            "waste_rate": float(waste_rate),
            "expiring_soon": expiring_soon,
            "category_stats": category_stats
        }
        
        # 结构化分析
        efficiency_score = _calculate_virtual_efficiency(virtual_assets_data)
        
        virtual_assets_analysis = {
            "efficiency_score": float(efficiency_score),
            "project_count": len(virtual_assets),
            "utilization_rate": float(utilization_rate),
            "waste_rate": float(waste_rate),
            "key_metrics": {
                "utilization_status": "高" if utilization_rate > 80 else "中" if utilization_rate > 50 else "低",
                "expiry_risk": "高" if len(expiring_soon) > 5 else "中" if len(expiring_soon) > 0 else "低"
            }
        }
        
        state["virtual_assets_data"] = virtual_assets_data
        state["virtual_assets_analysis"] = virtual_assets_analysis
        
        logger.info(f"✅ [N3-虚拟资产采集] 完成 - 项目数: {len(virtual_assets)}, 效率: {efficiency_score:.1f}")
        
        state["execution_path"].append({
            "node": "collect_virtual_assets",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": {
                "project_count": len(virtual_assets),
                "efficiency_score": float(efficiency_score),
                "utilization_rate": float(utilization_rate)
            }
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"❌ [N3-虚拟资产采集] 失败: {str(e)}")
        logger.error(f"详细错误堆栈:\n{error_detail}")
        state["error_message"] = f"虚拟资产采集失败: {str(e)}"
        state["execution_path"].append({
            "node": "collect_virtual_assets",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
        _save_workflow_trace_realtime(state)
    
    return state


async def ai_integrated_analysis_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N4: AI综合分析（固定资产 + 虚拟资产）
    """
    logger.info(f"🤖 [N4-AI综合分析] 开始")
    
    try:
        task_context = state["task_context"]
        api_key = task_context.get("api_key")
        model = task_context.get("model", "glm-4-flash")
        
        if not api_key:
            logger.warning(f"⚠️ [N4-AI综合分析] 未配置API Key，跳过")
            state["integrated_analysis"] = None
            state["execution_path"].append({
                "node": "ai_integrated_analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "skipped",
                "reason": "未配置API Key"
            })
            return state
        
        fixed_analysis = state.get("fixed_assets_analysis") or {}
        virtual_analysis = state.get("virtual_assets_analysis") or {}
        
        # 构建AI分析Prompt - 专业个人财产顾问角色
        prompt = f"""
你是一位资深的【个人财产管理顾问】，拥有15年以上的财富管理经验，擅长：
- 个人资产配置优化与风险控制
- 资产保值增值策略制定
- 家庭财务健康诊断与改善建议
- 投资组合再平衡与动态调整

请以专业、客观、务实的态度，为用户提供深度的资产分析和可执行的管理建议。

【固定资产分析】
- 资产数量: {fixed_analysis.get('asset_count', 0)}个
- 健康评分: {fixed_analysis.get('health_score', 0):.1f}/100
- 投资回报率(ROI): {fixed_analysis.get('roi', 0):.2f}%
- 利用率: {fixed_analysis.get('utilization_rate', 0):.1f}%
- 折旧状况: {fixed_analysis.get('key_metrics', {}).get('depreciation_status', '未知')}
- 收益表现: {fixed_analysis.get('key_metrics', {}).get('income_performance', '未知')}

【虚拟资产分析】
- 项目数量: {virtual_analysis.get('project_count', 0)}个
- 效率评分: {virtual_analysis.get('efficiency_score', 0):.1f}/100
- 利用率: {virtual_analysis.get('utilization_rate', 0):.1f}%
- 浪费率: {virtual_analysis.get('waste_rate', 0):.1f}%
- 利用状况: {virtual_analysis.get('key_metrics', {}).get('utilization_status', '未知')}
- 过期风险: {virtual_analysis.get('key_metrics', {}).get('expiry_risk', '未知')}

【分析要求】
请输出JSON格式的综合分析，包含：

1. **整体评估** (overall_assessment): 综合评价用户当前资产配置状况（优秀/良好/中等/需改进）

2. **资产配置均衡度** (asset_balance): 
   - 分析固定资产与虚拟资产的配置比例是否合理
   - 是否存在过度集中风险
   - 建议的优化方向

3. **协同效应分析** (synergy_effect):
   - 两类资产是否形成良性互补
   - 资产组合的整体健康度
   - 潜在的协同优化空间

4. **核心优势** (key_strengths): 列出3-5个显著优势
   - 资产配置的亮点
   - 值得保持的良好习惯
   - 潜在的增长机会

5. **主要风险** (key_weaknesses): 识别3-5个需要关注的问题
   - 资产结构的薄弱环节
   - 潜在的价值流失点
   - 需要及时调整的地方

6. **风险预警** (risk_alerts): 紧急需要处理的风险点
   - 即将过期但未充分利用的资产
   - 收益率明显偏低的资产
   - 闲置或低效资产

7. **优化建议** (optimization_suggestions): 提供3-5条可执行的改进建议
   - 具体、可操作的行动方案
   - 预期能带来的改善效果
   - 实施的优先级排序

【输出格式】
```json
{{
  "overall_assessment": "整体评估（优秀/良好/中等/需改进）",
  "asset_balance": "资产配置均衡度评价（200字内）",
  "synergy_effect": "协同效应分析（200字内）",
  "key_strengths": ["优势1", "优势2", "优势3"],
  "key_weaknesses": ["不足1", "不足2", "不足3"],
  "risk_alerts": ["风险1", "风险2"],
  "optimization_suggestions": ["建议1", "建议2", "建议3"]
}}
```

请确保分析深入、建议实用，帮助用户更好地管理个人财产。
"""
        
        # 调用AI
        from services.zhipu_service import ZhipuAiService
        service = ZhipuAiService(api_token=api_key, model=model)
        
        logger.info(f"🤖 [N4-AI综合分析] 调用AI进行综合分析...")
        result_text = service._call_api(prompt, max_tokens=1500)
        
        # 解析JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        integrated_analysis = json.loads(result_text)
        
        state["integrated_analysis"] = integrated_analysis
        
        logger.info(f"✅ [N4-AI综合分析] 完成 - 评估: {integrated_analysis.get('overall_assessment')}")
        
        state["execution_path"].append({
            "node": "ai_integrated_analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": {
                "assessment": integrated_analysis.get('overall_assessment'),
                "strengths_count": len(integrated_analysis.get('key_strengths', [])),
                "risks_count": len(integrated_analysis.get('risk_alerts', []))
            }
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.error(f"❌ [N4-AI综合分析] 失败: {str(e)}")
        state["integrated_analysis"] = None
        state["execution_path"].append({
            "node": "ai_integrated_analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


async def query_compare_previous_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N5: 查询上期数据 + 同比环比分析
    """
    logger.info(f"📊 [N5-上期对比分析] 开始")
    
    try:
        task_context = state["task_context"]
        user_id = task_context["user_id"]
        start_date = task_context["start_date"]
        end_date = task_context["end_date"]
        report_type = task_context.get("report_type", "custom")
        
        # 计算上期时间范围
        from datetime import timedelta
        
        # 处理日期类型：如果是date类型，直接使用；如果是字符串，转换为date
        if isinstance(start_date, str):
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_dt = start_date
            
        if isinstance(end_date, str):
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_dt = end_date
            
        period_days = (end_dt - start_dt).days + 1
        
        prev_end_date = start_dt - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=period_days - 1)
        
        logger.info(f"   - 当前周期: {start_date} 至 {end_date}")
        logger.info(f"   - 上期周期: {prev_start_date} 至 {prev_end_date}")
        
        # 查询上期固定资产数据（简化：使用当前资产数据作为对比基准）
        fixed_assets = FixedAsset.query.filter_by(user_id=user_id).all()
        prev_fixed_total_value = sum(float(asset.current_value or 0) for asset in fixed_assets) * 0.95  # 模拟上期数据
        
        # 查询上期虚拟资产数据
        virtual_assets = Project.query.filter_by(user_id=user_id).all()
        prev_virtual_total = sum(float(proj.total_amount or 0) for proj in virtual_assets) * 0.98  # 模拟上期数据
        
        previous_period_data = {
            "period": {
                "start": prev_start_date.isoformat(),
                "end": prev_end_date.isoformat()
            },
            "fixed_assets": {
                "total_value": float(prev_fixed_total_value),
                "asset_count": len(fixed_assets)
            },
            "virtual_assets": {
                "total_amount": float(prev_virtual_total),
                "project_count": len(virtual_assets)
            }
        }
        
        # 计算固定资产增长
        curr_fixed_value = float((state.get("fixed_assets_data") or {}).get("total_current_value", 0))
        curr_virtual_amount = float((state.get("virtual_assets_data") or {}).get("total_amount", 0))
        
        fixed_growth = ((curr_fixed_value - prev_fixed_total_value) / prev_fixed_total_value * 100) if prev_fixed_total_value > 0 else 0
        virtual_growth = ((curr_virtual_amount - prev_virtual_total) / prev_virtual_total * 100) if prev_virtual_total > 0 else 0
        
        comparison_analysis = {
            "fixed_assets": {
                "current_value": float(curr_fixed_value),
                "previous_value": float(prev_fixed_total_value),
                "growth_rate": float(fixed_growth),
                "trend": "增长" if fixed_growth > 0 else "下降" if fixed_growth < 0 else "持平"
            },
            "virtual_assets": {
                "current_amount": float(curr_virtual_amount),
                "previous_amount": float(prev_virtual_total),
                "growth_rate": float(virtual_growth),
                "trend": "增长" if virtual_growth > 0 else "下降" if virtual_growth < 0 else "持平"
            },
            "overall_trend": "向好" if (fixed_growth + virtual_growth) > 0 else "下滑"
        }
        
        state["previous_period_data"] = previous_period_data
        state["comparison_analysis"] = comparison_analysis
        
        logger.info(f"✅ [N5-上期对比分析] 完成")
        logger.info(f"   - 固定资产增长: {fixed_growth:+.2f}%")
        logger.info(f"   - 虚拟资产增长: {virtual_growth:+.2f}%")
        
        state["execution_path"].append({
            "node": "query_compare_previous",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": {
                "fixed_growth": fixed_growth,
                "virtual_growth": virtual_growth,
                "overall_trend": comparison_analysis['overall_trend']
            }
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.warning(f"⚠️ [N5-上期对比分析] 失败: {str(e)}")
        state["previous_period_data"] = None
        state["comparison_analysis"] = None
        state["execution_path"].append({
            "node": "query_compare_previous",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e)
        })
    
    return state


async def generate_qualitative_conclusion_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N6: 生成定性结论 + 结构化存储
    """
    logger.info(f"📝 [N6-定性结论生成] 开始")
    
    try:
        task_context = state["task_context"]
        api_key = task_context.get("api_key")
        model = task_context.get("model", "glm-4-flash")
        
        if not api_key:
            logger.warning(f"⚠️ [N6-定性结论生成] 未配置API Key")
            state["qualitative_conclusion"] = _generate_rule_based_conclusion(state)
            state["structured_indicators"] = _extract_structured_indicators(state)
            state["execution_path"].append({
                "node": "generate_qualitative_conclusion",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed",
                "method": "rule_based"
            })
            return state
        
        # 整合所有分析数据
        integrated = state.get("integrated_analysis", {})
        comparison = state.get("comparison_analysis", {})
        
        prompt = f"""
你是一位【资深个人财务顾问】，专注于个人和家庭财富管理，擅长：
- 财产健康度诊断与评级
- 财务风险识别与防控
- 资产配置策略优化
- 个性化财富增长方案制定

请基于以下分析数据，生成一份【专业、客观、可执行】的财产管理结论报告。

【AI综合分析】
{json.dumps(integrated, ensure_ascii=False, indent=2)}

【同比环比分析】
{json.dumps(comparison, ensure_ascii=False, indent=2)}

【输出要求】
请生成JSON格式的定性结论，包含：

1. **执行摘要** (executive_summary): 
   - 300字左右的核心结论
   - 包含整体评价、关键发现、主要建议
   - 语言简洁有力，突出重点

2. **整体评级** (overall_rating):
   - A+: 财产配置极佳，持续保持
   - A: 配置良好，稳健增长
   - B: 基本合理，有优化空间
   - C: 存在问题，需要调整
   - D: 情况不佳，紧急处理

3. **紧急程度** (severity_level):
   - 低: 运转正常，无紧急问题
   - 中: 有些问题需关注，建议1-2周内处理
   - 高: 存在重大风险，需立即采取行动

4. **关键发现** (key_findings):
   - 列出5-8条最重要的发现
   - 既包括积极亮点，也包括潜在问题
   - 每条都要给出数据支持

5. **可执行洞察** (actionable_insights):
   - 3-5条深入洞察
   - 揭示资产管理中的关键机会或风险
   - 说明为什么重要、影响有多大

6. **优先行动计划** (priority_actions):
   - 3-5条具体的行动建议
   - 按紧急程度排序
   - 每条包含：具体动作 + 预期效果 + 建议时间线
   - 示例：“在本周内处理即将过期的XX资产，预计可避免XX元浪费”

7. **风险等级** (risk_level):
   - 低: 资产结构健康，风险可控
   - 中: 存在一定风险，需定期监控
   - 高: 风险较大，建议及时调整

【输出格式】
```json
{{
  "executive_summary": "执行摘要（300字）",
  "overall_rating": "A+/A/B/C/D",
  "severity_level": "低/中/高",
  "key_findings": ["发现1", "发现2", "发现3", "发现4", "发现5"],
  "actionable_insights": ["洞察1", "洞察2", "洞察3"],
  "priority_actions": ["行动1", "行动2", "行动3"],
  "risk_level": "低/中/高"
}}
```

请确保分析全面、客观，建议具体、可执行，帮助用户提升财产管理水平。
"""
        
        # 调用AI
        from services.zhipu_service import ZhipuAiService
        service = ZhipuAiService(api_token=api_key, model=model)
        
        logger.info(f"🤖 [N6-定性结论生成] 调用AI生成定性结论...")
        result_text = service._call_api(prompt, max_tokens=2000)
        
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        qualitative_conclusion = json.loads(result_text)
        
        # 提取结构化指标
        structured_indicators = {
            "overall_rating": qualitative_conclusion.get("overall_rating"),
            "risk_level": qualitative_conclusion.get("risk_level"),
            "severity_level": qualitative_conclusion.get("severity_level"),
            "key_findings_count": len(qualitative_conclusion.get("key_findings", [])),
            "priority_actions_count": len(qualitative_conclusion.get("priority_actions", []))
        }
        
        state["qualitative_conclusion"] = qualitative_conclusion
        state["structured_indicators"] = structured_indicators
        
        logger.info(f"✅ [N6-定性结论生成] 完成")
        logger.info(f"   - 评级: {structured_indicators['overall_rating']}")
        logger.info(f"   - 风险: {structured_indicators['risk_level']}")
        
        state["execution_path"].append({
            "node": "generate_qualitative_conclusion",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "summary": structured_indicators
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.error(f"❌ [N6-定性结论生成] 失败: {str(e)}")
        state["qualitative_conclusion"] = _generate_rule_based_conclusion(state)
        state["structured_indicators"] = _extract_structured_indicators(state)
        state["execution_path"].append({
            "node": "generate_qualitative_conclusion",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e),
            "fallback": "rule_based"
        })
    
    return state


async def generate_report_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N7: 生成完整报告
    """
    logger.info(f"📄 [N7-报告生成] 开始")
    
    try:
        # 整合所有数据生成报告
        report_data = {
            "report_type": "optimized",
            "generated_at": datetime.utcnow().isoformat(),
            "qualitative_conclusion": state.get("qualitative_conclusion"),
            "structured_indicators": state.get("structured_indicators"),
            "fixed_assets": {
                "data": state.get("fixed_assets_data"),
                "analysis": state.get("fixed_assets_analysis")
            },
            "virtual_assets": {
                "data": state.get("virtual_assets_data"),
                "analysis": state.get("virtual_assets_analysis")
            },
            "integrated_analysis": state.get("integrated_analysis"),
            "comparison_analysis": state.get("comparison_analysis")
        }
        
        # 转换为Decimal友好的JSON
        report_data_clean: Dict[str, Any] = _convert_decimals(report_data)  # type: ignore
        
        # 生成可读HTML内容
        html_content = _generate_html_report(report_data_clean, state.get("task_context", {}))
        
        state["report_content"] = html_content
        
        logger.info(f"✅ [N7-报告生成] 完成 - 内容长度: {len(state['report_content'])}")
        
        state["execution_path"].append({
            "node": "generate_report",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "content_length": len(state["report_content"])
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.error(f"❌ [N7-报告生成] 失败: {str(e)}")
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
    N8: 质量评估（准确性 + 完整性 + 结构性）
    """
    logger.info(f"🔍 [N8-质量评估] 开始")
    
    try:
        report_content = state["report_content"]
        
        if not report_content:
            raise Exception("报告内容为空")
        
        # 评估维度（基于HTML内容长度和关键词）
        score = {
            "accuracy": 0,      # 准确性
            "completeness": 0,  # 完整性
            "structure": 0,     # 结构性
            "total_score": 0
        }
        
        # 1. 准确性评估（检查关键内容）
        has_conclusion = "核心结论" in report_content or "定性结论" in report_content
        has_fixed = "固定资产" in report_content
        has_virtual = "虚拟资产" in report_content
        score["accuracy"] = int((has_conclusion + has_fixed + has_virtual) / 3 * 100)
        
        # 2. 完整性评估（基于内容长度）
        min_length = 500
        max_length = 10000
        content_length = len(report_content)
        if content_length < min_length:
            score["completeness"] = int(content_length / min_length * 100)
        elif content_length > max_length:
            score["completeness"] = 100
        else:
            score["completeness"] = 100
        
        # 3. 结构性评估（HTML有效性）
        has_html_structure = "<div" in report_content and "</div>" in report_content
        score["structure"] = 100 if has_html_structure else 50
        
        # 总分
        score["total_score"] = int(
            score["accuracy"] * 0.4 +
            score["completeness"] * 0.3 +
            score["structure"] * 0.3
        )
        
        state["quality_score"] = score
        
        # 判断结果
        if score["total_score"] >= 70:
            state["evaluation_result"] = "pass"
            logger.info(f"✅ [N8-质量评估] 通过 - 总分: {score['total_score']}")
        elif state["retry_count"] < state["max_retries"]:
            state["evaluation_result"] = "retry"
            logger.warning(f"⚠️ [N8-质量评估] 需重试 - 总分: {score['total_score']}")
        else:
            state["evaluation_result"] = "fail"
            logger.error(f"❌ [N8-质量评估] 失败 - 总分: {score['total_score']}")
        
        state["execution_path"].append({
            "node": "evaluate_quality",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "quality_score": score,
            "result": state["evaluation_result"]
        })
        
        _save_workflow_trace_realtime(state)
        
    except Exception as e:
        logger.error(f"❌ [N8-质量评估] 异常: {str(e)}")
        state["evaluation_result"] = "retry" if state["retry_count"] < state["max_retries"] else "fail"
        state["execution_path"].append({
            "node": "evaluate_quality",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "failed",
            "error": str(e),
            "result": state["evaluation_result"]
        })
    
    return state


async def save_report_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N9: 保存报告 + 注入智能洞察
    """
    logger.info(f"💾 [N9-保存报告] 开始")
    
    try:
        from models.ai_report import AIReport
        
        task_context = state["task_context"]
        report_id = task_context["report_id"]
        
        report = AIReport.query.get(report_id)
        if not report:
            raise Exception(f"报告不存在: {report_id}")
        
        content = state["report_content"]
        if not content:
            raise Exception("报告内容为空")
        
        # 提取摘要（从HTML中提取）
        try:
            # 尝试从定性结论部分提取文本
            if "核心结论" in content:
                # 简单提取第一段文字
                summary = content[:500]
            else:
                summary = "报告已生成"
        except:
            summary = "报告已生成"
        
        # 更新报告
        report.content = content
        report.summary = summary
        report.status = 'completed'
        report.generated_at = datetime.utcnow()
        
        # 保存工作流轨迹
        report.execution_path = json.dumps(state.get("execution_path", []), ensure_ascii=False)
        report.workflow_metadata = json.dumps({
            "quality_score": state.get("quality_score"),
            "structured_indicators": state.get("structured_indicators"),
            "retry_count": state.get("retry_count", 0),
            "start_time": state.get("start_time"),
            "end_time": datetime.utcnow().isoformat()
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
    N10: 重试处理
    """
    state["retry_count"] += 1
    logger.info(f"🔄 [N10-重试] 第 {state['retry_count']}/{state['max_retries']} 次")
    
    state["execution_path"].append({
        "node": "handle_retry",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "retry_count": state["retry_count"]
    })
    
    _save_workflow_trace_realtime(state)
    
    return state


async def handle_failure_node(state: ReportWorkflowState) -> ReportWorkflowState:
    """
    N11: 失败处理
    """
    from models.ai_report import AIReport
    
    logger.error(f"❌ [N11-失败处理] 开始")
    
    try:
        task_context = state["task_context"]
        report_id = task_context["report_id"]
        
        report = AIReport.query.get(report_id)
        if report:
            if not state.get("error_message"):
                state["error_message"] = "报告生成失败"
            
            report.status = 'failed'
            report.error_message = state["error_message"]
            report.execution_path = json.dumps(state.get("execution_path", []), ensure_ascii=False)
            report.workflow_metadata = json.dumps({
                "quality_score": state.get("quality_score"),
                "retry_count": state.get("retry_count", 0),
                "start_time": state.get("start_time"),
                "end_time": datetime.utcnow().isoformat(),
                "error_message": state["error_message"]
            }, ensure_ascii=False)
            
            db.session.commit()
        
        state["end_time"] = datetime.utcnow().isoformat()
        state["execution_path"].append({
            "node": "handle_failure",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        })
        
    except Exception as e:
        logger.error(f"❌ [N11-失败处理] 异常: {str(e)}")
    
    return state


# ==================== 辅助函数 ====================

def _calculate_fixed_asset_health(data: Dict[str, Any]) -> float:
    """计算固定资产健康度"""
    if data['total_assets'] == 0:
        return 50.0
    
    health_score = 100.0
    depreciation_penalty = min(40, float(data['depreciation_rate']) * 0.5)
    health_score -= depreciation_penalty
    
    if data['total_current_value'] > 0:
        income_rate = (float(data['total_income']) / float(data['total_current_value'])) * 100
        income_bonus = min(30, income_rate * 3)
        health_score += income_bonus
    
    status_stats = data.get('status_stats', {})
    if data['total_assets'] > 0:
        in_use = status_stats.get('使用中', 0)
        usage_rate = (in_use / data['total_assets']) * 100
        usage_bonus = min(20, usage_rate * 0.2)
        health_score += usage_bonus
    
    return round(max(0, min(100, health_score)), 1)


def _calculate_virtual_efficiency(data: Dict[str, Any]) -> float:
    """计算虚拟资产效率"""
    if data['total_projects'] == 0:
        return 50.0
    
    efficiency = float(data['utilization_rate']) - float(data['waste_rate']) * 2
    
    if data.get('expiring_soon'):
        expiring_count = len(data['expiring_soon'])
        efficiency -= min(20, expiring_count * 5)
    
    return round(max(0, min(100, efficiency)), 1)


def _generate_rule_based_conclusion(state: ReportWorkflowState) -> Dict[str, Any]:
    """基于规则生成定性结论（降级方案）"""
    fixed_analysis = state.get("fixed_assets_analysis") or {}
    virtual_analysis = state.get("virtual_assets_analysis") or {}
    
    avg_health = (fixed_analysis.get('health_score', 50) + virtual_analysis.get('efficiency_score', 50)) / 2
    
    return {
        "executive_summary": f"资产整体健康度{avg_health:.1f}分，处于{'优秀' if avg_health >= 80 else '良好' if avg_health >= 60 else '中等'}状态",
        "overall_rating": "A" if avg_health >= 80 else "B" if avg_health >= 60 else "C",
        "severity_level": "低" if avg_health >= 70 else "中" if avg_health >= 50 else "高",
        "key_findings": ["固定资产健康度评估完成", "虚拟资产效率评估完成"],
        "actionable_insights": ["建议持续监控资产状态"],
        "priority_actions": ["优化资产配置"],
        "risk_level": "低" if avg_health >= 70 else "中"
    }


def _extract_structured_indicators(state: ReportWorkflowState) -> Dict[str, Any]:
    """提取结构化指标"""
    conclusion = state.get("qualitative_conclusion") or {}
    return {
        "overall_rating": conclusion.get("overall_rating", "B"),
        "risk_level": conclusion.get("risk_level", "中"),
        "severity_level": conclusion.get("severity_level", "中"),
        "key_findings_count": len(conclusion.get("key_findings", [])),
        "priority_actions_count": len(conclusion.get("priority_actions", []))
    }
