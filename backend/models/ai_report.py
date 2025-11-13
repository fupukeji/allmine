from database import db
from datetime import datetime

class AIReport(db.Model):
    """AI智能报告模型"""
    __tablename__ = 'ai_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 报告基本信息
    report_type = db.Column(db.String(20), nullable=False)  # weekly, monthly, yearly, custom
    title = db.Column(db.String(200), nullable=False)  # 报告标题
    
    # 时间范围
    start_date = db.Column(db.Date, nullable=False)  # 开始日期
    end_date = db.Column(db.Date, nullable=False)  # 结束日期
    
    # 报告内容
    summary = db.Column(db.Text)  # 摘要
    content = db.Column(db.Text)  # AI生成的详细内容（JSON格式），生成中时可为空
    
    # 数据快照（用于报告生成时的数据备份）
    data_snapshot = db.Column(db.Text)  # JSON格式的数据快照
    
    # 状态
    status = db.Column(db.String(20), default='generating')  # generating, completed, failed
    error_message = db.Column(db.Text)  # 错误信息（如果失败）
    
    # 时间戳
    generated_at = db.Column(db.DateTime)  # 生成完成时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('ai_reports', lazy=True))
    
    def get_type_text(self):
        """获取报告类型文字"""
        type_map = {
            'weekly': '周报',
            'monthly': '月报',
            'yearly': '年报',
            'custom': '自定义报告'
        }
        return type_map.get(self.report_type, '未知')
    
    def get_status_text(self):
        """获取状态文字"""
        status_map = {
            'generating': '生成中',
            'completed': '已完成',
            'failed': '失败'
        }
        return status_map.get(self.status, '未知')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'report_type_text': self.get_type_text(),
            'title': self.title,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'summary': self.summary,
            'content': self.content,
            'status': self.status,
            'status_text': self.get_status_text(),
            'error_message': self.error_message,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<AIReport {self.report_type}: {self.title}>'
