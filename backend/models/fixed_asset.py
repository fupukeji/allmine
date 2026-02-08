from database import db
from datetime import datetime, timedelta
from decimal import Decimal

class FixedAsset(db.Model):
    __tablename__ = 'fixed_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True, nullable=False)  # 资产编号
    name = db.Column(db.String(100), nullable=False)  # 资产名称
    description = db.Column(db.Text)  # 资产描述
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # 分类
    
    # 财务信息
    original_value = db.Column(db.Numeric(15, 2), nullable=False)  # 原值
    current_value = db.Column(db.Numeric(15, 2), nullable=False)  # 当前价值
    accumulated_depreciation = db.Column(db.Numeric(15, 2), default=0)  # 累计折旧
    residual_rate = db.Column(db.Numeric(5, 2), default=5.00)  # 残值率(%)
    
    # 时间信息
    purchase_date = db.Column(db.Date, nullable=False)  # 购买日期
    useful_life_years = db.Column(db.Integer, nullable=False)  # 预计使用年限
    depreciation_start_date = db.Column(db.Date, nullable=False)  # 折旧开始日期
    
    # 折旧信息
    depreciation_method = db.Column(db.String(20), default='straight_line')  # 折旧方法
    annual_depreciation_rate = db.Column(db.Numeric(5, 2))  # 年折旧率(%)
    monthly_depreciation = db.Column(db.Numeric(12, 2))  # 月折旧额
    
    # 状态和位置信息
    status = db.Column(db.String(20), default='in_use')  # 使用状态: in_use, rent, sell, idle, maintenance, disposed
    location = db.Column(db.String(100))  # 所在位置
    responsible_person = db.Column(db.String(50))  # 责任人
    
    # 处置信息
    rent_price = db.Column(db.Numeric(12, 2))  # 月租金
    rent_deposit = db.Column(db.Numeric(12, 2))  # 押金
    rent_start_date = db.Column(db.Date)  # 租期开始日期
    rent_end_date = db.Column(db.Date)  # 租期结束日期
    rent_due_day = db.Column(db.Integer, default=1)  # 收租日(每月几号)
    tenant_name = db.Column(db.String(50))  # 租客姓名
    tenant_phone = db.Column(db.String(20))  # 租客电话
    sell_price = db.Column(db.Numeric(15, 2))  # 售出价格
    dispose_date = db.Column(db.Date)  # 处置日期
    dispose_note = db.Column(db.Text)  # 处置备注
    
    # 系统字段
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = db.relationship('Category', backref=db.backref('fixed_assets', lazy=True))
    user = db.relationship('User', backref=db.backref('fixed_assets', lazy=True))
    
    def __init__(self, **kwargs):
        super(FixedAsset, self).__init__(**kwargs)
        # 自动计算折旧相关数据
        if self.original_value and self.useful_life_years and self.residual_rate:
            self.calculate_depreciation_data()
    
    def calculate_depreciation_data(self):
        """计算折旧相关数据"""
        if self.depreciation_method == 'straight_line':
            # 直线法折旧
            residual_value = self.original_value * (self.residual_rate / 100)
            depreciable_amount = self.original_value - residual_value
            
            # 年折旧率 = (1 - 残值率) / 使用年限
            self.annual_depreciation_rate = (100 - self.residual_rate) / self.useful_life_years
            
            # 月折旧额 = 可折旧金额 / (使用年限 * 12)
            self.monthly_depreciation = depreciable_amount / (self.useful_life_years * 12)
    
    def get_status_text(self):
        """获取状态文字"""
        status_map = {
            'in_use': '使用中',
            'rent': '出租中',
            'sell': '待出售',
            'idle': '闲置',
            'maintenance': '维修中',
            'disposed': '已处置'
        }
        return status_map.get(self.status, '未知')
    
    def calculate_current_depreciation(self, base_date=None):
        """计算当前折旧情况"""
        if base_date is None:
            base_date = datetime.now().date()
        
        if base_date < self.depreciation_start_date:
            return {
                'months_depreciated': 0,
                'accumulated_depreciation': 0,
                'current_value': float(self.original_value),
                'depreciation_rate': 0,
                'remaining_life_months': self.useful_life_years * 12,
                'is_fully_depreciated': False
            }
        
        # 计算已折旧月数
        months_diff = (base_date.year - self.depreciation_start_date.year) * 12 + \
                     (base_date.month - self.depreciation_start_date.month)
        
        # 如果基准日期的日数小于开始日期的日数，减少一个月
        if base_date.day < self.depreciation_start_date.day:
            months_diff -= 1
        
        months_depreciated = max(0, months_diff)
        total_useful_months = self.useful_life_years * 12
        
        # 不能超过总使用月数
        months_depreciated = min(months_depreciated, total_useful_months)
        
        # 计算累计折旧
        accumulated_depreciation = float(self.monthly_depreciation) * months_depreciated
        residual_value = float(self.original_value) * (float(self.residual_rate) / 100)
        max_depreciation = float(self.original_value) - residual_value
        accumulated_depreciation = min(accumulated_depreciation, max_depreciation)
        
        # 计算当前价值
        current_value = float(self.original_value) - accumulated_depreciation
        current_value = max(current_value, residual_value)
        
        # 计算折旧率
        depreciation_rate = (accumulated_depreciation / float(self.original_value)) * 100
        
        # 剩余使用月数
        remaining_life_months = max(0, total_useful_months - months_depreciated)
        
        return {
            'months_depreciated': months_depreciated,
            'accumulated_depreciation': round(accumulated_depreciation, 2),
            'current_value': round(current_value, 2),
            'depreciation_rate': round(depreciation_rate, 2),
            'remaining_life_months': remaining_life_months,
            'is_fully_depreciated': months_depreciated >= total_useful_months
        }
    
    def to_dict(self, include_calculations=True, base_date=None):
        """转换为字典"""
        data = {
            'id': self.id,
            'asset_code': self.asset_code,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            
            # 财务信息
            'original_value': float(self.original_value),
            'current_value': float(self.current_value),
            'accumulated_depreciation': float(self.accumulated_depreciation),
            'residual_rate': float(self.residual_rate),
            
            # 时间信息
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'useful_life_years': self.useful_life_years,
            'depreciation_start_date': self.depreciation_start_date.isoformat() if self.depreciation_start_date else None,
            
            # 折旧信息
            'depreciation_method': self.depreciation_method,
            'annual_depreciation_rate': float(self.annual_depreciation_rate) if self.annual_depreciation_rate else 0,
            'monthly_depreciation': float(self.monthly_depreciation) if self.monthly_depreciation else 0,
            
            # 状态信息
            'status': self.status,
            'status_text': self.get_status_text(),
            'location': self.location,
            'responsible_person': self.responsible_person,
            
            # 处置信息
            'rent_price': float(self.rent_price) if self.rent_price else None,
            'rent_deposit': float(self.rent_deposit) if self.rent_deposit else None,
            'rent_start_date': self.rent_start_date.isoformat() if self.rent_start_date else None,
            'rent_end_date': self.rent_end_date.isoformat() if self.rent_end_date else None,
            'rent_due_day': self.rent_due_day or 1,
            'tenant_name': self.tenant_name,
            'tenant_phone': self.tenant_phone,
            'sell_price': float(self.sell_price) if self.sell_price else None,
            'dispose_date': self.dispose_date.isoformat() if self.dispose_date else None,
            'dispose_note': self.dispose_note,
            
            # 系统信息
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_calculations:
            depreciation_data = self.calculate_current_depreciation(base_date)
            data.update(depreciation_data)
        
        return data
    
    def __repr__(self):
        return f'<FixedAsset {self.asset_code}: {self.name}>'