from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 角色：admin, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 个人信息字段
    phone = db.Column(db.String(20))  # 手机号
    location = db.Column(db.String(100))  # 所在地址
    bio = db.Column(db.Text)  # 个人简介
    website = db.Column(db.String(200))  # 个人网站
    company = db.Column(db.String(100))  # 公司/组织
    avatar = db.Column(db.Text)  # 头像（base64或URL）
    
    # 偏好设置
    language = db.Column(db.String(10), default='zh-CN')  # 语言
    timezone = db.Column(db.String(50), default='Asia/Shanghai')  # 时区
    theme = db.Column(db.String(20), default='light')  # 主题
    email_notifications = db.Column(db.Boolean, default=True)  # 邮件通知
    sms_notifications = db.Column(db.Boolean, default=False)  # 短信通知
    
    # 关联关系
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == 'admin'
    
    def can_manage_users(self):
        """检查是否可以管理用户"""
        return self.is_admin()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            # 个人信息
            'phone': self.phone,
            'location': self.location,
            'bio': self.bio,
            'website': self.website,
            'company': self.company,
            'avatar': self.avatar,
            # 偏好设置
            'language': self.language,
            'timezone': self.timezone,
            'theme': self.theme,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications
        }
    
    def __repr__(self):
        return f'<User {self.username}>'