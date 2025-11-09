from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.ai_report import AIReport
from database import db
from datetime import datetime, timedelta, date
from services.alibabacloud_service import ZhipuAiService
import json

reports_bp = Blueprint('reports', __name__)

def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

@reports_bp.route('/reports/token', methods=['POST'])
@jwt_required()
def save_api_token():
    """保存用户的阿里云API Token"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        api_token = data.get('api_token', '').strip()
        
        if not api_token:
            return jsonify({
                'success': False,
                'message': 'API Token不能为空'
            }), 400
        
        # 加密保存Token
        user.set_aliyun_api_token(api_token)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API Token保存成功'
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
    """检查用户是否已配置API Token"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        has_token = user.aliyun_api_token_encrypted is not None
        
        return jsonify({
            'success': True,
            'data': {
                'has_token': has_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'检查失败：{str(e)}'
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
        
        # 检查是否配置了API Token
        api_token = user.get_aliyun_api_token()
        if not api_token:
            return jsonify({
                'success': False,
                'message': '请先配置阿里云API Token'
            }), 400
        
        data = request.get_json()
        report_type = data.get('report_type', 'custom')  # weekly, monthly, custom
        
        # 确定时间范围
        today = date.today()
        
        if report_type == 'weekly':
            # 本周：周一到今天
            start_date = today - timedelta(days=today.weekday())
            end_date = today
            title = f"资产周报 ({start_date.strftime('%Y年%m月%d日')} - {end_date.strftime('%m月%d日')})"
        elif report_type == 'monthly':
            # 本月：1号到今天
            start_date = date(today.year, today.month, 1)
            end_date = today
            title = f"资产月报 ({today.year}年{today.month}月)"
        else:
            # 自定义时间范围
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
        
        # 调用智谱AI生成报告
        try:
            service = ZhipuAiService(api_token)
            
            if report_type == 'weekly':
                content = service.generate_weekly_report(user.id, start_date, end_date)
            elif report_type == 'monthly':
                content = service.generate_monthly_report(user.id, start_date, end_date)
            else:
                focus_areas = data.get('focus_areas', [])
                content = service.generate_custom_report(user.id, start_date, end_date, focus_areas)
            
            # 解析内容提取摘要
            try:
                content_json = json.loads(content)
                if 'executive_summary' in content_json:
                    summary = content_json['executive_summary']
                elif 'period_summary' in content_json:
                    summary = content_json['period_summary']
                else:
                    summary = "报告已生成"
            except:
                summary = "报告已生成"
            
            # 更新报告状态
            report.content = content
            report.summary = summary
            report.status = 'completed'
            report.generated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '报告生成成功',
                'data': report.to_dict()
            }), 201
            
        except Exception as api_error:
            # API调用失败
            report.status = 'failed'
            report.error_message = str(api_error)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': f'报告生成失败：{str(api_error)}'
            }), 500
        
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
