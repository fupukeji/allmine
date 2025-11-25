from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.ai_report import AIReport
from database import db
from datetime import datetime, timedelta, date
from services.zhipu_service import ZhipuAiService
import json
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from workflows.service import get_workflow_service

reports_bp = Blueprint('reports', __name__)

# 创建线程池用于并发生成报告（最多5个并发任务）
executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix='report_gen')

def _generate_report_async(report_id, user_id, api_key, model, report_type, start_date, end_date, focus_areas=None):
    """异步生成报告的后台任务（使用LangGraph工作流）"""
    # 使用Flask应用上下文
    from flask import current_app
    from app import create_app
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            print(f"\n{'='*80}")
            print(f"[LangGraph工作流] 开始处理 - 报告ID: {report_id}")
            print(f"- 用户ID: {user_id}")
            print(f"- 报告类型: {report_type}")
            print(f"- 时间范围: {start_date} 至 {end_date}")
            print(f"- 模型: {model}")
            print(f"- 线程: {threading.current_thread().name}")
            print(f"{'='*80}\n")
            
            # 构建工作流任务上下文
            task_context = {
                "report_id": report_id,
                "user_id": user_id,
                "api_key": api_key,
                "model": model,
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "focus_areas": focus_areas or [],
                "enable_ai_insights": False  # 禁用AI预分析以节省API调用
            }
            
            # 获取工作流服务并执行
            workflow_service = get_workflow_service()
            
            # 在新的事件循环中执行异步工作流
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                final_state = loop.run_until_complete(
                    workflow_service.execute_workflow(task_context)
                )
            finally:
                loop.close()
            
            # 从final_state中提取报告内容
            content = final_state.get('report_content')
            
            # 检查执行路径最后一个节点是否是失败节点
            execution_path = final_state.get('execution_path', [])
            last_node = execution_path[-1]['node'] if execution_path else None
            
            # 如果最后一个节点是handle_failure，说明工作流失败了
            if last_node == 'handle_failure':
                # 确保error_message存在
                if not final_state.get('error_message'):
                    final_state['error_message'] = '报告生成失败，已达最大重试次数'
                
                error_msg = final_state['error_message']
                print(f"\n[LangGraph工作流] ❌ 失败 - 报告ID: {report_id}")
                print(f"- 错误: {error_msg}\n")
                
                # 注意：handle_failure_node已经保存了状态和工作流轨迹，不需要重复保存
                return
            
            # 检查是否有错误或内容为空
            if final_state.get('error_message') or not content:
                error_msg = final_state.get('error_message', '报告生成失败')
                print(f"\n[LangGraph工作流] ❌ 失败 - 报告ID: {report_id}")
                print(f"- 错误: {error_msg}\n")
                
                # 更新报告状态为失败
                report = AIReport.query.get(report_id)
                if report:
                    report.status = 'failed'
                    report.error_message = error_msg
                    # 保存工作流轨迹（即使失败也保存）
                    if final_state.get('execution_path'):
                        report.execution_path = json.dumps(final_state['execution_path'], ensure_ascii=False)
                    if final_state.get('agent_decisions') or final_state.get('quality_score'):
                        report.workflow_metadata = json.dumps({
                            "agent_decisions": final_state.get('agent_decisions', []),
                            "quality_score": final_state.get('quality_score'),
                            "retry_count": final_state.get('retry_count', 0),
                            "start_time": final_state.get('start_time'),
                            "end_time": final_state.get('end_time'),
                            "error_message": error_msg
                        }, ensure_ascii=False)
                    db.session.commit()
                return
            
            # 解析内容提取摘要
            try:
                content_json = json.loads(content)
                # 新格式：executive_summary 是对象
                if 'executive_summary' in content_json:
                    exec_summary = content_json['executive_summary']
                    if isinstance(exec_summary, dict):
                        # 提取content字段作为摘要
                        summary = exec_summary.get('content', exec_summary.get('title', '报告已生成'))
                    else:
                        summary = str(exec_summary)
                # 旧格式：period_summary 是字符串
                elif 'period_summary' in content_json:
                    summary = str(content_json['period_summary'])
                else:
                    summary = "报告已生成"
                
                # 确保summary是字符串，限制长度
                summary = str(summary)[:500] if summary else "报告已生成"
            except Exception as e:
                print(f"[摘要提取失败] {e}")
                summary = "报告已生成"
            
            # 更新报告状态
            report = AIReport.query.get(report_id)
            if report:
                report.content = content
                report.summary = summary
                report.status = 'completed'
                report.generated_at = datetime.utcnow()
                
                # 保存工作流轨迹数据（这部分应该已经在save_report_node中保存了，但为了确保兼容性再保存一次）
                if final_state.get('execution_path'):
                    report.execution_path = json.dumps(final_state['execution_path'], ensure_ascii=False)
                if final_state.get('agent_decisions') or final_state.get('quality_score'):
                    report.workflow_metadata = json.dumps({
                        "agent_decisions": final_state.get('agent_decisions', []),
                        "quality_score": final_state.get('quality_score'),
                        "retry_count": final_state.get('retry_count', 0),
                        "start_time": final_state.get('start_time'),
                        "end_time": final_state.get('end_time')
                    }, ensure_ascii=False)
                
                db.session.commit()
                
                print(f"\n[LangGraph工作流] ✅ 成功 - 报告ID: {report_id}")
                print(f"- 摘要: {summary[:50]}...")
                print(f"- 生成时间: {report.generated_at}")
                print(f"- 工作流节点数: {len(final_state.get('execution_path', []))}\n")
            else:
                print(f"\n[LangGraph工作流] ⚠️ 报告不存在 - 报告ID: {report_id}\n")
                
        except Exception as e:
            # 处理错误
            import traceback
            error_details = traceback.format_exc()
            
            print(f"\n[LangGraph工作流] ❌ 失败 - 报告ID: {report_id}")
            print(f"- 错误类型: {type(e).__name__}")
            print(f"- 错误信息: {str(e)}")
            print(f"- 详细堆栈:\n{error_details}")
            print("=" * 50 + "\n")
            
            try:
                report = AIReport.query.get(report_id)
                if report:
                    report.status = 'failed'
                    report.error_message = str(e)
                    db.session.commit()
            except Exception as db_error:
                print(f"[LangGraph工作流] 数据库更新失败: {str(db_error)}")

def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

@reports_bp.route('/reports/token', methods=['POST'])
@jwt_required()
def save_api_token():
    """保存用户的AI API Key和模型配置（仅支持智谱AI）"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        model = data.get('model', 'glm-4-flash').strip()  # 获取模型配置
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': 'API Key不能为空'
            }), 400
        
        # 加密保存API Key
        user.set_ai_api_key(api_key)
        # 保存模型配置
        user.zhipu_model = model
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'智谱AI API Key和模型配置保存成功（{model}）'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'保存失败：{str(e)}'
        }), 500

@reports_bp.route('/reports/token', methods=['GET'])
@jwt_required()
def check_api_token():
    """检查用户是否已配置API Key（仅支持智谱AI）"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 检查智谱AI的Key配置情况
        has_token = user.get_ai_api_key() is not None
        
        # 获取加密后的Key显示（前4+后4位）
        masked_key = None
        if has_token:
            full_key = user.get_ai_api_key()
            if len(full_key) > 8:
                masked_key = f"{full_key[:4]}{'*' * (len(full_key) - 8)}{full_key[-4:]}"
            else:
                masked_key = '*' * len(full_key)
        
        return jsonify({
            'success': True,
            'data': {
                'has_token': has_token,
                'provider': 'zhipu',
                'provider_name': '智谱AI',
                'masked_key': masked_key,
                'model': user.zhipu_model or 'glm-4-flash'  # 返回模型配置
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'检查失败：{str(e)}'
        }), 500

@reports_bp.route('/reports/token/reveal', methods=['POST'])
@jwt_required()
def reveal_api_token():
    """显示完整的API Key（需要密码验证）"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        password = data.get('password', '').strip()
        
        if not password:
            return jsonify({
                'success': False,
                'message': '请输入密码'
            }), 400
        
        # 验证密码
        if not user.check_password(password):
            return jsonify({
                'success': False,
                'message': '密码错误'
            }), 401
        
        # 获取完整的API Key
        api_key = user.get_ai_api_key()
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': '未配置API Key'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'api_key': api_key
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取失败：{str(e)}'
        }), 500

@reports_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_report():
    """生成智能报告"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 检查是否配置了API Key
        api_key = user.get_ai_api_key()
        
        if not api_key:
            return jsonify({
                'success': False,
                'message': '请先配置智谱AI的API Key'
            }), 400
        
        data = request.get_json()
        report_type = data.get('report_type', 'custom')  # weekly, monthly, yearly, custom
        
        # 确定时间范围
        today = date.today()
        
        if report_type == 'weekly':
            # 周报：支持选择具体某一周
            year = data.get('year', today.year)
            week = data.get('week', today.isocalendar()[1])  # ISO周数
            
            # 计算该周的开始和结束日期
            # ISO 8601: 周一为一周的第一天
            jan_4 = date(year, 1, 4)  # 第一周总是包含1月4日
            week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
            start_date = week_1_monday + timedelta(weeks=week-1)
            end_date = start_date + timedelta(days=6)
            
            title = f"资产周报 ({year}年第{week}周: {start_date.strftime('%Y年%m月%d日')} - {end_date.strftime('%m月%d日')})"
            
        elif report_type == 'monthly':
            # 月报：支持选择具体某个月
            year = data.get('year', today.year)
            month = data.get('month', today.month)
            
            # 计算该月的开始和结束日期
            start_date = date(year, month, 1)
            # 下个月的1号再减1天
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            title = f"资产月报 ({year}年{month}月)"
            
        elif report_type == 'yearly':
            # 年报：支持选择具体某一年
            year = data.get('year', today.year)
            
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            title = f"资产年报 ({year}年)"
            
        else:
            # 自定义时间范围：支持任意时间段
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            if not start_date_str or not end_date_str:
                return jsonify({
                    'success': False,
                    'message': '自定义报告需要提供开始和结束日期'
                }), 400
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            title = f"资产分析报告 ({start_date.strftime('%Y年%m月%d日')} - {end_date.strftime('%m月%d日')})"
        
        # 创建报告记录
        report = AIReport(
            user_id=user.id,
            report_type=report_type,
            title=title,
            start_date=start_date,
            end_date=end_date,
            status='generating'
        )
        db.session.add(report)
        db.session.commit()
        
        # 获取focus_areas（如果有）
        focus_areas = data.get('focus_areas', None)
        
        # 提交异步任务到线程池
        executor.submit(
            _generate_report_async,
            report.id,
            user.id,
            api_key,
            user.zhipu_model or 'glm-4-flash',
            report_type,
            start_date,
            end_date,
            focus_areas
        )
        
        print(f"\n[并发报告] 报告任务已提交 - 报告ID: {report.id}, 类型: {report_type}")
        
        # 立即返回201，不等待生成完成
        return jsonify({
            'success': True,
            'message': '报告生成任务已提交，正在后台处理',
            'data': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'生成报告失败：{str(e)}'
        }), 500

@reports_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """获取用户的报告列表"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 获取查询参数
        report_type = request.args.get('type')  # weekly, monthly, custom
        status = request.args.get('status')  # generating, completed, failed
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # 构建查询
        query = AIReport.query.filter_by(user_id=user.id)
        
        if report_type:
            query = query.filter_by(report_type=report_type)
        if status:
            query = query.filter_by(status=status)
        
        # 按创建时间倒序
        query = query.order_by(AIReport.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'reports': [report.to_dict() for report in pagination.items],
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取报告列表失败：{str(e)}'
        }), 500

@reports_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """获取单个报告详情"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        report = AIReport.query.get(report_id)
        
        if not report:
            return jsonify({
                'success': False,
                'message': '报告不存在'
            }), 404
        
        # 权限检查
        if report.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权访问此报告'
            }), 403
        
        return jsonify({
            'success': True,
            'data': report.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取报告失败：{str(e)}'
        }), 500

@reports_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """删除报告"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        report = AIReport.query.get(report_id)
        
        if not report:
            return jsonify({
                'success': False,
                'message': '报告不存在'
            }), 404
        
        # 权限检查
        if report.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权删除此报告'
            }), 403
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '报告删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除报告失败：{str(e)}'
        }), 500

@reports_bp.route('/reports/stats', methods=['GET'])
@jwt_required()
def get_report_stats():
    """获取报告统计信息"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 统计各类型报告数量
        total = AIReport.query.filter_by(user_id=user.id).count()
        weekly = AIReport.query.filter_by(user_id=user.id, report_type='weekly').count()
        monthly = AIReport.query.filter_by(user_id=user.id, report_type='monthly').count()
        custom = AIReport.query.filter_by(user_id=user.id, report_type='custom').count()
        
        # 统计各状态报告数量
        completed = AIReport.query.filter_by(user_id=user.id, status='completed').count()
        failed = AIReport.query.filter_by(user_id=user.id, status='failed').count()
        
        # 最新报告
        latest_report = AIReport.query.filter_by(
            user_id=user.id, 
            status='completed'
        ).order_by(AIReport.created_at.desc()).first()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'by_type': {
                    'weekly': weekly,
                    'monthly': monthly,
                    'custom': custom
                },
                'by_status': {
                    'completed': completed,
                    'failed': failed
                },
                'latest_report': latest_report.to_dict() if latest_report else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败：{str(e)}'
        }), 500


@reports_bp.route('/reports/workflow/visualization', methods=['GET'])
@jwt_required()
def get_workflow_visualization():
    """获取工作流可视化数据"""
    try:
        workflow_service = get_workflow_service()
        visualization_data = workflow_service.get_workflow_visualization()
        
        return jsonify({
            'success': True,
            'data': visualization_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取工作流可视化失败：{str(e)}'
        }), 500


@reports_bp.route('/reports/<int:report_id>/workflow-trace', methods=['GET'])
@jwt_required()
def get_report_workflow_trace(report_id):
    """获取报告的工作流执行轨迹"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        report = AIReport.query.get(report_id)
        
        if not report:
            return jsonify({
                'success': False,
                'message': '报告不存在'
            }), 404
        
        # 权限检查
        if report.user_id != user.id:
            return jsonify({
                'success': False,
                'message': '无权访问此报告'
            }), 403
        
        # 从报告中提取工作流执行轨迹
        report_dict = report.to_dict()
        
        trace_data = {
            'report_id': report_id,
            'status': report.status,
            'execution_path': report_dict.get('execution_path', []),
            'workflow_metadata': report_dict.get('workflow_metadata', {}),
            'created_at': report.created_at.isoformat() if report.created_at else None,
            'completed_at': report.generated_at.isoformat() if report.generated_at else None
        }
        
        return jsonify({
            'success': True,
            'data': trace_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取工作流轨迹失败：{str(e)}'
        }), 500
