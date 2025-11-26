from database import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#1890ff')  # 默认蓝色
    icon = db.Column(db.String(50), default='folder')  # 默认文件夹图标
    description = db.Column(db.String(200))  # 分类描述
    sort_order = db.Column(db.Integer, default=0)  # 排序顺序
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)  # 父分类ID
    
    # 自关联：子分类
    children = db.relationship('Category', 
                              backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic',
                              cascade='all, delete-orphan')
    
    # 关联关系
    projects = db.relationship('Project', backref='category', lazy=True)
    
    # 唯一约束：同一用户下同一父级的分类名不能重复
    __table_args__ = (db.UniqueConstraint('user_id', 'parent_id', 'name', name='unique_user_parent_category'),)
    
    def to_dict(self, include_children=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'icon': self.icon,
            'description': self.description,
            'sort_order': self.sort_order,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'project_count': len(self.projects)
        }
        
        # 包含子分类
        if include_children:
            data['children'] = [child.to_dict(include_children=True) 
                              for child in self.children.order_by(Category.sort_order, Category.name).all()]
        
        return data
    
    def get_full_path(self):
        """获取完整路径（如：一级分类 > 二级分类 > 三级分类）"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_level(self):
        """获取分类层级（0为顶级）"""
        if self.parent:
            return self.parent.get_level() + 1
        return 0
    
    def __repr__(self):
        return f'<Category {self.name}>'