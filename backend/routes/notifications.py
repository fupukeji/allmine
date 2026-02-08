"""
通知设置API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.notification_settings import UserNotificationSettings

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notification-settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """获取用户通知设置"""
    try:
        user_id = int(get_jwt_identity())
        settings = UserNotificationSettings.get_or_create(user_id)
        
        return jsonify({
            'code': 200,
            'data': settings.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取通知设置失败: {str(e)}'
        }), 500


@notifications_bp.route('/notification-settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """更新用户通知设置"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        settings = UserNotificationSettings.get_or_create(user_id)
        
        # 更新通知方式
        channels = data.get('notification_channels', {})
        if 'push_enabled' in channels:
            settings.push_enabled = channels['push_enabled']
        if 'email_enabled' in channels:
            settings.email_enabled = channels['email_enabled']
        if 'sms_enabled' in channels:
            settings.sms_enabled = channels['sms_enabled']
        if 'wechat_enabled' in channels:
            settings.wechat_enabled = channels['wechat_enabled']
        
        # 更新业务通知
        business = data.get('business_notifications', {})
        
        # 收租提醒
        if 'rent_reminder' in business:
            rent = business['rent_reminder']
            if 'enabled' in rent:
                settings.rent_reminder_enabled = rent['enabled']
            if 'days' in rent:
                settings.rent_reminder_days = rent['days']
        
        # 资产到期
        if 'asset_expiry' in business:
            asset = business['asset_expiry']
            if 'enabled' in asset:
                settings.asset_expiry_enabled = asset['enabled']
            if 'days' in asset:
                settings.asset_expiry_days = asset['days']
        
        # 费用提醒
        if 'expense_reminder' in business:
            expense = business['expense_reminder']
            if 'enabled' in expense:
                settings.expense_reminder_enabled = expense['enabled']
            if 'days' in expense:
                settings.expense_reminder_days = expense['days']
        
        # 折旧提醒
        if 'depreciation' in business:
            dep = business['depreciation']
            if 'enabled' in dep:
                settings.depreciation_enabled = dep['enabled']
        
        # 价值变动
        if 'value_change' in business:
            vc = business['value_change']
            if 'enabled' in vc:
                settings.value_change_enabled = vc['enabled']
            if 'threshold' in vc:
                settings.value_change_threshold = vc['threshold']
        
        # 周报
        if 'weekly_report' in business:
            wr = business['weekly_report']
            if 'enabled' in wr:
                settings.weekly_report_enabled = wr['enabled']
        
        # 月报
        if 'monthly_report' in business:
            mr = business['monthly_report']
            if 'enabled' in mr:
                settings.monthly_report_enabled = mr['enabled']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '通知设置已更新',
            'data': settings.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新通知设置失败: {str(e)}'
        }), 500


@notifications_bp.route('/notification-settings/toggle', methods=['POST'])
@jwt_required()
def toggle_notification():
    """快捷切换单个通知开关"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        key = data.get('key')  # 如 'push_enabled', 'rent_reminder_enabled'
        value = data.get('value')
        
        if not key:
            return jsonify({
                'code': 400,
                'message': '缺少参数 key'
            }), 400
        
        settings = UserNotificationSettings.get_or_create(user_id)
        
        # 验证字段是否存在
        if not hasattr(settings, key):
            return jsonify({
                'code': 400,
                'message': f'无效的设置项: {key}'
            }), 400
        
        # 切换值
        if value is None:
            current = getattr(settings, key)
            value = not current
        
        setattr(settings, key, value)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设置已更新',
            'data': {
                'key': key,
                'value': value
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500
