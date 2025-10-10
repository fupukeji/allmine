from database import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#1890ff')  # 默认蓝色
    icon = db.Column(db.String(50), default='folder')  # 默认文件夹图标
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关联关系
    projects = db.relationship('Project', backref='category', lazy=True)
    
    # 唯一约束：同一用户下分类名不能重复
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_user_category'),)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'project_count': len(self.projects)
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'