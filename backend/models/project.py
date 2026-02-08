from database import db
from datetime import datetime
from utils.crypto import encrypt_credential, decrypt_credential

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)  # 总支付金额
    purchase_time = db.Column(db.DateTime)  # 购买时间（可选）
    start_time = db.Column(db.DateTime, nullable=False)  # 开始计算时间
    end_time = db.Column(db.DateTime, nullable=False)  # 结束时间
    purpose = db.Column(db.Text)  # 购买目的（可选）
    account_username = db.Column(db.String(100))  # 账号用户名（可选）
    _account_password = db.Column('account_password', db.String(500))  # 账号密码（加密存储）
    
    @property
    def account_password(self):
        """解密获取密码"""
        return decrypt_credential(self._account_password)
    
    @account_password.setter
    def account_password(self, value):
        """加密存储密码"""
        self._account_password = encrypt_credential(value) if value else None
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    def get_status(self):
        """获取项目状态"""
        now = datetime.utcnow()
        if now < self.start_time:
            return 'not_started'  # 未开始
        elif now > self.end_time:
            return 'expired'  # 已过期
        else:
            return 'active'  # 消耗中
    
    def calculate_values(self, base_time=None):
        """计算价值数据"""
        if base_time is None:
            base_time = datetime.utcnow()
        
        # 总时长（天）
        total_days = (self.end_time - self.start_time).total_seconds() / 86400
        
        # 已使用时长（天）
        if base_time <= self.start_time:
            used_days = 0
        elif base_time >= self.end_time:
            used_days = total_days
        else:
            used_days = (base_time - self.start_time).total_seconds() / 86400
        
        # 单位时间成本（元/天）
        unit_cost = float(self.total_amount) / total_days if total_days > 0 else 0
        
        # 已消耗成本
        used_cost = unit_cost * used_days
        
        # 剩余价值
        remaining_value = float(self.total_amount) - used_cost
        if remaining_value < 0:
            remaining_value = 0
        
        # 消耗进度
        progress = (used_days / total_days * 100) if total_days > 0 else 0
        if progress > 100:
            progress = 100
        
        return {
            'unit_cost': round(unit_cost, 2),
            'used_cost': round(used_cost, 2),
            'remaining_value': round(remaining_value, 2),
            'progress': round(progress, 2),
            'total_days': round(total_days, 1),
            'used_days': round(used_days, 1),
            'status': self.get_status()
        }
    
    def to_dict(self, include_calculations=True, base_time=None):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'total_amount': float(self.total_amount),
            'purchase_time': self.purchase_time.isoformat() if self.purchase_time else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'account_username': self.account_username,  # 账号用户名
            'account_password': self.account_password,  # 账号密码（解密后返回）
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None
        }
        
        if include_calculations:
            data.update(self.calculate_values(base_time))
        
        return data
    
    def __repr__(self):
        return f'<Project {self.name}>'