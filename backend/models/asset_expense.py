from database import db
from datetime import datetime

class AssetExpense(db.Model):
    """资产费用记录"""
    __tablename__ = 'asset_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('fixed_assets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 费用信息
    expense_type = db.Column(db.String(50), nullable=False)  # 费用类型: maintenance/insurance/tax/utility/other
    expense_name = db.Column(db.String(100), nullable=False)  # 费用名称
    amount = db.Column(db.Numeric(12, 2), nullable=False)  # 金额
    expense_date = db.Column(db.Date, nullable=False)  # 费用日期
    
    # 周期性费用
    is_recurring = db.Column(db.Boolean, default=False)  # 是否周期性费用
    recurring_period = db.Column(db.String(20))  # 周期: monthly/quarterly/yearly
    next_due_date = db.Column(db.Date)  # 下次到期日
    
    # 附加信息
    description = db.Column(db.Text)  # 描述/备注
    receipt_image = db.Column(db.String(255))  # 收据图片URL
    
    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    asset = db.relationship('FixedAsset', backref=db.backref('expenses', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('asset_expenses', lazy=True))
    
    # 费用类型配置（按资产类别）
    EXPENSE_TYPES = {
        'house': [  # 房产
            {'value': 'property_fee', 'label': '物业费'},
            {'value': 'maintenance', 'label': '维修费'},
            {'value': 'renovation', 'label': '装修费'},
            {'value': 'utility', 'label': '水电燃气'},
            {'value': 'tax', 'label': '房产税'},
            {'value': 'insurance', 'label': '保险费'},
            {'value': 'other', 'label': '其他'}
        ],
        'car': [  # 车辆
            {'value': 'insurance', 'label': '保险费'},
            {'value': 'maintenance', 'label': '保养费'},
            {'value': 'repair', 'label': '维修费'},
            {'value': 'fuel', 'label': '油费'},
            {'value': 'parking', 'label': '停车费'},
            {'value': 'toll', 'label': '过路费'},
            {'value': 'tax', 'label': '车船税'},
            {'value': 'inspection', 'label': '年检费'},
            {'value': 'other', 'label': '其他'}
        ],
        'electronics': [  # 电子设备
            {'value': 'repair', 'label': '维修费'},
            {'value': 'accessory', 'label': '配件费'},
            {'value': 'warranty', 'label': '延保费'},
            {'value': 'software', 'label': '软件/服务'},
            {'value': 'other', 'label': '其他'}
        ],
        'default': [  # 默认
            {'value': 'maintenance', 'label': '维护费'},
            {'value': 'repair', 'label': '维修费'},
            {'value': 'insurance', 'label': '保险费'},
            {'value': 'tax', 'label': '税费'},
            {'value': 'other', 'label': '其他'}
        ]
    }
    
    @classmethod
    def get_expense_types(cls, category_name=None):
        """根据资产分类获取费用类型列表"""
        if not category_name:
            return cls.EXPENSE_TYPES['default']
        
        category_lower = category_name.lower()
        if '房' in category_name or 'house' in category_lower or '产' in category_name:
            return cls.EXPENSE_TYPES['house']
        elif '车' in category_name or 'car' in category_lower:
            return cls.EXPENSE_TYPES['car']
        elif '电' in category_name or 'electronic' in category_lower or '设备' in category_name:
            return cls.EXPENSE_TYPES['electronics']
        else:
            return cls.EXPENSE_TYPES['default']
    
    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'expense_type': self.expense_type,
            'expense_name': self.expense_name,
            'amount': float(self.amount) if self.amount else 0,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'is_recurring': self.is_recurring,
            'recurring_period': self.recurring_period,
            'next_due_date': self.next_due_date.isoformat() if self.next_due_date else None,
            'description': self.description,
            'receipt_image': self.receipt_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
