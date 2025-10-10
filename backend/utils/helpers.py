# 工具函数模块
from datetime import datetime
import re

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    if len(password) > 50:
        return False, "密码长度不能超过50位"
    return True, ""

def parse_datetime(datetime_str):
    """解析日期时间字符串"""
    if not datetime_str:
        return None
        
    try:
        # 支持多种日期格式
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d %H:%M',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"无法解析日期格式：{datetime_str}")
        
    except Exception as e:
        raise ValueError(f"日期格式错误：{str(e)}")

def format_currency(amount):
    """格式化货币显示"""
    return f"¥{amount:,.2f}"

def calculate_time_difference(start_time, end_time):
    """计算时间差（天数）"""
    if not start_time or not end_time:
        return 0
    return (end_time - start_time).total_seconds() / 86400

def get_status_text(status):
    """获取状态的中文描述"""
    status_map = {
        'not_started': '未开始',
        'active': '进行中',
        'expired': '已过期'
    }
    return status_map.get(status, '未知')

def truncate_text(text, max_length=50):
    """截断文本"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."