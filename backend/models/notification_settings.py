"""
用户通知设置模型
"""
from database import db
from datetime import datetime

class UserNotificationSettings(db.Model):
    """用户通知设置"""
    __tablename__ = 'user_notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # ==================== 通知方式开关 ====================
    # 系统推送通知
    push_enabled = db.Column(db.Boolean, default=True)
    # 邮件通知
    email_enabled = db.Column(db.Boolean, default=True)
    # 短信通知
    sms_enabled = db.Column(db.Boolean, default=False)
    # 微信通知（服务号模板消息）
    wechat_enabled = db.Column(db.Boolean, default=True)
    
    # ==================== 业务通知开关 ====================
    # 收租提醒（租金到期前N天提醒）
    rent_reminder_enabled = db.Column(db.Boolean, default=True)
    rent_reminder_days = db.Column(db.Integer, default=3)  # 提前天数
    
    # 资产到期提醒（虚拟资产到期前N天提醒）
    asset_expiry_enabled = db.Column(db.Boolean, default=True)
    asset_expiry_days = db.Column(db.Integer, default=7)  # 提前天数
    
    # 费用提醒（周期性费用到期前N天提醒）
    expense_reminder_enabled = db.Column(db.Boolean, default=True)
    expense_reminder_days = db.Column(db.Integer, default=3)  # 提前天数
    
    # 折旧提醒（资产完全折旧时提醒）
    depreciation_enabled = db.Column(db.Boolean, default=True)
    
    # 价值变动提醒（资产价值大幅变动时提醒）
    value_change_enabled = db.Column(db.Boolean, default=False)
    value_change_threshold = db.Column(db.Integer, default=10)  # 变动阈值百分比
    
    # 周报/月报（定期汇总报告）
    weekly_report_enabled = db.Column(db.Boolean, default=False)
    monthly_report_enabled = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = db.relationship('User', backref=db.backref('notification_settings', uselist=False))
    
    @staticmethod
    def get_or_create(user_id):
        """获取或创建用户通知设置"""
        settings = UserNotificationSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = UserNotificationSettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            # 通知方式
            'notification_channels': {
                'push_enabled': self.push_enabled,
                'email_enabled': self.email_enabled,
                'sms_enabled': self.sms_enabled,
                'wechat_enabled': self.wechat_enabled,
            },
            # 业务通知
            'business_notifications': {
                'rent_reminder': {
                    'enabled': self.rent_reminder_enabled,
                    'days': self.rent_reminder_days,
                    'label': '收租提醒',
                    'description': '租金到期前提醒收租'
                },
                'asset_expiry': {
                    'enabled': self.asset_expiry_enabled,
                    'days': self.asset_expiry_days,
                    'label': '资产到期',
                    'description': '虚拟资产到期前提醒'
                },
                'expense_reminder': {
                    'enabled': self.expense_reminder_enabled,
                    'days': self.expense_reminder_days,
                    'label': '费用提醒',
                    'description': '周期性费用到期前提醒'
                },
                'depreciation': {
                    'enabled': self.depreciation_enabled,
                    'label': '折旧提醒',
                    'description': '资产完全折旧时提醒'
                },
                'value_change': {
                    'enabled': self.value_change_enabled,
                    'threshold': self.value_change_threshold,
                    'label': '价值变动',
                    'description': '资产价值大幅变动时提醒'
                },
                'weekly_report': {
                    'enabled': self.weekly_report_enabled,
                    'label': '周报',
                    'description': '每周资产汇总报告'
                },
                'monthly_report': {
                    'enabled': self.monthly_report_enabled,
                    'label': '月报',
                    'description': '每月资产汇总报告'
                }
            },
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserNotificationSettings user_id={self.user_id}>'
