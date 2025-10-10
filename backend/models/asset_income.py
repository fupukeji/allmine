from database import db
from datetime import datetime, date
from sqlalchemy import func

class AssetIncome(db.Model):
    """资产收入记录模型"""
    __tablename__ = 'asset_incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('fixed_assets.id'), nullable=False)
    income_type = db.Column(db.String(50), nullable=False)  # 收入类型：rent, license, dividend, sale, other
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # 收入金额
    expected_amount = db.Column(db.Numeric(15, 2))  # 预期收入金额
    cost = db.Column(db.Numeric(15, 2), default=0)  # 相关成本
    tax_rate = db.Column(db.Numeric(5, 2), default=0)  # 税率(%)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)  # 税费金额
    net_amount = db.Column(db.Numeric(15, 2))  # 净收入
    income_date = db.Column(db.Date, nullable=False)  # 收入日期
    expected_date = db.Column(db.Date)  # 预期收款日期
    actual_date = db.Column(db.Date)  # 实际收款日期
    description = db.Column(db.Text)  # 收入描述
    notes = db.Column(db.Text)  # 备注信息
    payer = db.Column(db.String(200))  # 付款方
    payment_method = db.Column(db.String(50), default='bank_transfer')  # 支付方式
    contract_reference = db.Column(db.String(100))  # 合同编号
    invoice_number = db.Column(db.String(100))  # 发票号码
    is_recurring = db.Column(db.Boolean, default=False)  # 是否循环收入
    recurring_frequency = db.Column(db.String(20))  # 循环频率：monthly, quarterly, yearly
    recurring_period = db.Column(db.String(20))  # 循环周期（兼容旧字段）
    recurring_end_date = db.Column(db.Date)  # 循环结束日期
    status = db.Column(db.String(20), default='pending')  # 状态：pending, received, overdue, cancelled, partial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    asset = db.relationship('FixedAsset', backref='incomes')
    
    def __init__(self, **kwargs):
        super(AssetIncome, self).__init__(**kwargs)
        # 自动计算净收入
        self.calculate_net_amount()
    
    def calculate_net_amount(self):
        """计算净收入"""
        if self.amount:
            cost = float(self.cost or 0)
            tax_rate = float(self.tax_rate or 0)
            amount = float(self.amount)
            
            # 计算税费
            self.tax_amount = amount * (tax_rate / 100)
            # 计算净收入 = 收入金额 - 成本 - 税费
            self.net_amount = amount - cost - float(self.tax_amount)
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'income_type': self.income_type,
            'income_type_text': self.get_income_type_text(),
            'amount': float(self.amount),
            'expected_amount': float(self.expected_amount) if self.expected_amount else None,
            'cost': float(self.cost) if self.cost else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'net_amount': float(self.net_amount) if self.net_amount else 0,
            'income_date': self.income_date.isoformat() if self.income_date else None,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'description': self.description,
            'notes': self.notes,
            'payer': self.payer,
            'payment_method': self.payment_method,
            'contract_reference': self.contract_reference,
            'invoice_number': self.invoice_number,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'recurring_period': self.recurring_period,  # 兼容旧字段
            'recurring_end_date': self.recurring_end_date.isoformat() if self.recurring_end_date else None,
            'status': self.status,
            'status_text': self.get_status_text(),
            'variance': self.calculate_variance(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_income_type_text(self):
        """获取收入类型中文描述"""
        return self.get_income_type_text_static(self.income_type)
    
    @staticmethod
    def get_income_type_text_static(income_type):
        """获取收入类型中文描述（静态方法）"""
        type_map = {
            'rent': '租金收入',
            'license': '授权费',
            'dividend': '分红',
            'sale': '销售收入',
            'appreciation': '增值收益',
            'interest': '利息收入',
            'royalty': '版权费',
            'service': '服务费',
            'other': '其他收入'
        }
        return type_map.get(income_type, '未知类型')
    
    def get_status_text(self):
        """获取状态中文描述"""
        status_map = {
            'pending': '待收',
            'received': '已收',
            'overdue': '逾期',
            'cancelled': '已取消',
            'partial': '部分收取'
        }
        return status_map.get(self.status, '未知状态')
    
    def calculate_variance(self):
        """计算预期与实际的差异"""
        if self.expected_amount and self.amount:
            variance = float(self.amount) - float(self.expected_amount)
            variance_rate = (variance / float(self.expected_amount)) * 100
            return {
                'absolute': variance,
                'rate': round(variance_rate, 2)
            }
        return None
    
    @classmethod
    def get_asset_total_income(cls, asset_id):
        """获取资产总收入"""
        result = db.session.query(
            func.sum(cls.net_amount).label('total_income'),
            func.count(cls.id).label('income_count')
        ).filter_by(asset_id=asset_id, status='received').first()
        
        return {
            'total_income': float(result.total_income) if result and result.total_income else 0,
            'income_count': result.income_count if result else 0
        }
    
    @classmethod
    def get_income_by_type(cls, asset_id):
        """按类型获取收入统计"""
        results = db.session.query(
            cls.income_type,
            func.sum(cls.net_amount).label('total_amount'),
            func.count(cls.id).label('count')
        ).filter_by(asset_id=asset_id, status='received').group_by(cls.income_type).all()
        
        return [
            {
                'income_type': result.income_type,
                'income_type_text': AssetIncome().get_income_type_text_static(result.income_type),
                'total_amount': float(result.total_amount) if result.total_amount else 0,
                'count': result.count or 0
            }
            for result in results
        ]
    
    @classmethod
    def get_monthly_income_trend(cls, asset_id, months=12):
        """获取月度收入趋势"""
        from sqlalchemy import extract
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=months*30)
        
        results = db.session.query(
            extract('year', cls.income_date).label('year'),
            extract('month', cls.income_date).label('month'),
            func.sum(cls.net_amount).label('total_amount')
        ).filter(
            cls.asset_id == asset_id,
            cls.status == 'received',
            cls.income_date >= start_date.date()
        ).group_by(
            extract('year', cls.income_date),
            extract('month', cls.income_date)
        ).order_by('year', 'month').all()
        
        return [
            {
                'period': f"{int(result.year)}-{int(result.month):02d}",
                'amount': float(result.total_amount) if result.total_amount else 0
            }
            for result in results
        ]