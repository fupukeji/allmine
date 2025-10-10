from database import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

class AssetMaintenance(db.Model):
    """资产维护记录模型"""
    __tablename__ = 'asset_maintenances'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('fixed_assets.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # 维护类型：routine, repair, upgrade, inspection
    title = db.Column(db.String(200), nullable=False)  # 维护标题
    description = db.Column(db.Text)  # 维护描述
    maintenance_date = db.Column(db.Date, nullable=False)  # 维护日期
    cost = db.Column(db.Numeric(15, 2), default=0)  # 维护成本
    next_maintenance_date = db.Column(db.Date)  # 下次维护日期
    maintenance_interval = db.Column(db.Integer)  # 维护间隔（天）
    provider = db.Column(db.String(200))  # 维护供应商
    warranty_end_date = db.Column(db.Date)  # 保修结束日期
    priority = db.Column(db.String(20), default='medium')  # 优先级：low, medium, high, urgent
    status = db.Column(db.String(20), default='planned')  # 状态：planned, in_progress, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    asset = db.relationship('FixedAsset', backref='maintenances')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'maintenance_type': self.maintenance_type,
            'maintenance_type_text': self.get_maintenance_type_text(),
            'title': self.title,
            'description': self.description,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'cost': float(self.cost) if self.cost else 0,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'maintenance_interval': self.maintenance_interval,
            'provider': self.provider,
            'warranty_end_date': self.warranty_end_date.isoformat() if self.warranty_end_date else None,
            'priority': self.priority,
            'priority_text': self.get_priority_text(),
            'status': self.status,
            'status_text': self.get_status_text(),
            'is_overdue': self.is_overdue(),
            'days_until_next': self.days_until_next_maintenance(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_maintenance_type_text(self):
        """获取维护类型中文描述"""
        type_map = {
            'routine': '例行保养',
            'repair': '故障维修',
            'upgrade': '升级改造',
            'inspection': '检查检测',
            'cleaning': '清洁保养',
            'calibration': '校准调试',
            'other': '其他维护'
        }
        return type_map.get(self.maintenance_type, '未知类型')
    
    def get_priority_text(self):
        """获取优先级中文描述"""
        priority_map = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'urgent': '紧急'
        }
        return priority_map.get(self.priority, '未知')
    
    def get_status_text(self):
        """获取状态中文描述"""
        status_map = {
            'planned': '计划中',
            'in_progress': '进行中',
            'completed': '已完成',
            'cancelled': '已取消'
        }
        return status_map.get(self.status, '未知状态')
    
    def is_overdue(self):
        """检查是否过期"""
        if self.next_maintenance_date and self.status in ['planned', 'in_progress']:
            return self.next_maintenance_date < date.today()
        return False
    
    def days_until_next_maintenance(self):
        """距离下次维护的天数"""
        if self.next_maintenance_date:
            delta = self.next_maintenance_date - date.today()
            return delta.days
        return None
    
    @classmethod
    def get_asset_maintenance_stats(cls, asset_id):
        """获取资产维护统计"""
        # 总维护次数和费用
        total_stats = db.session.query(
            func.count(cls.id).label('total_count'),
            func.sum(cls.cost).label('total_cost')
        ).filter_by(asset_id=asset_id, status='completed').first()
        
        # 按类型统计
        type_stats = db.session.query(
            cls.maintenance_type,
            func.count(cls.id).label('count'),
            func.sum(cls.cost).label('total_cost')
        ).filter_by(asset_id=asset_id, status='completed').group_by(cls.maintenance_type).all()
        
        # 即将到期的维护
        upcoming = cls.query.filter(
            cls.asset_id == asset_id,
            cls.status.in_(['planned', 'in_progress']),
            cls.next_maintenance_date.isnot(None),
            cls.next_maintenance_date <= date.today() + timedelta(days=30)
        ).order_by(cls.next_maintenance_date).all()
        
        return {
            'total_maintenance_count': total_stats.total_count or 0 if total_stats else 0,
            'total_maintenance_cost': float(total_stats.total_cost) if total_stats and total_stats.total_cost else 0,
            'type_distribution': [
                {
                    'maintenance_type': stat.maintenance_type,
                    'maintenance_type_text': cls().get_maintenance_type_text() if hasattr(cls(), 'get_maintenance_type_text') else stat.maintenance_type,
                    'count': stat.count,
                    'total_cost': float(stat.total_cost) if stat.total_cost else 0
                }
                for stat in type_stats
            ],
            'upcoming_maintenances': [maintenance.to_dict() for maintenance in upcoming]
        }
    
    @classmethod
    def get_overdue_maintenances(cls, user_assets_ids):
        """获取用户所有资产的过期维护"""
        return cls.query.filter(
            cls.asset_id.in_(user_assets_ids),
            cls.status.in_(['planned', 'in_progress']),
            cls.next_maintenance_date.isnot(None),
            cls.next_maintenance_date < date.today()
        ).order_by(cls.next_maintenance_date).all()
    
    @classmethod
    def get_maintenance_calendar(cls, user_assets_ids, start_date, end_date):
        """获取维护日历"""
        maintenances = cls.query.filter(
            cls.asset_id.in_(user_assets_ids),
            cls.next_maintenance_date.between(start_date, end_date)
        ).order_by(cls.next_maintenance_date).all()
        
        calendar_data = {}
        for maintenance in maintenances:
            date_str = maintenance.next_maintenance_date.isoformat()
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            calendar_data[date_str].append(maintenance.to_dict())
        
        return calendar_data


class MaintenanceReminder(db.Model):
    """维护提醒设置模型"""
    __tablename__ = 'maintenance_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('fixed_assets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reminder_type = db.Column(db.String(50), nullable=False)  # 提醒类型：routine, warranty, custom
    name = db.Column(db.String(200), nullable=False)  # 提醒名称
    description = db.Column(db.Text)  # 提醒描述
    interval_days = db.Column(db.Integer, nullable=False)  # 提醒间隔（天）
    advance_days = db.Column(db.Integer, default=7)  # 提前提醒天数
    next_reminder_date = db.Column(db.Date, nullable=False)  # 下次提醒日期
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    last_reminded = db.Column(db.DateTime)  # 最后提醒时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    asset = db.relationship('FixedAsset', backref='reminders')
    user = db.relationship('User', backref='maintenance_reminders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'user_id': self.user_id,
            'reminder_type': self.reminder_type,
            'name': self.name,
            'description': self.description,
            'interval_days': self.interval_days,
            'advance_days': self.advance_days,
            'next_reminder_date': self.next_reminder_date.isoformat() if self.next_reminder_date else None,
            'is_active': self.is_active,
            'last_reminded': self.last_reminded.isoformat() if self.last_reminded else None,
            'days_until_reminder': self.days_until_reminder(),
            'is_due': self.is_due(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def days_until_reminder(self):
        """距离提醒的天数"""
        if self.next_reminder_date:
            delta = self.next_reminder_date - date.today()
            return delta.days
        return None
    
    def is_due(self):
        """是否到期需要提醒"""
        if self.is_active and self.next_reminder_date:
            return self.next_reminder_date <= date.today()
        return False
    
    def update_next_reminder(self):
        """更新下次提醒日期"""
        if self.next_reminder_date:
            self.next_reminder_date = self.next_reminder_date + timedelta(days=self.interval_days)
            self.last_reminded = datetime.utcnow()
    
    @classmethod
    def get_due_reminders(cls, user_id):
        """获取到期的提醒"""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.is_active == True,
            cls.next_reminder_date <= date.today()
        ).order_by(cls.next_reminder_date).all()