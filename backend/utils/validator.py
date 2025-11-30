"""
数据验证工具模块
提供通用的数据验证函数
"""
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


class Validator:
    """数据验证器"""
    
    @staticmethod
    def validate_email(email):
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if not email:
            return False, "邮箱不能为空"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "邮箱格式不正确"
        
        if len(email) > 100:
            return False, "邮箱长度不能超过100个字符"
        
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if not password:
            return False, "密码不能为空"
        
        if len(password) < 6:
            return False, "密码长度至少6位"
        
        if len(password) > 50:
            return False, "密码长度不能超过50位"
        
        return True, ""
    
    @staticmethod
    def validate_username(username):
        """
        验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if not username:
            return False, "用户名不能为空"
        
        if len(username) < 3:
            return False, "用户名长度至少3位"
        
        if len(username) > 50:
            return False, "用户名长度不能超过50位"
        
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            return False, "用户名只能包含字母、数字、下划线和中文"
        
        return True, ""
    
    @staticmethod
    def validate_amount(amount, min_value=0, max_value=None):
        """
        验证金额
        
        Args:
            amount: 金额
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        try:
            if amount is None:
                return False, "金额不能为空"
            
            decimal_amount = Decimal(str(amount))
            
            if decimal_amount < Decimal(str(min_value)):
                return False, f"金额不能小于{min_value}"
            
            if max_value is not None and decimal_amount > Decimal(str(max_value)):
                return False, f"金额不能大于{max_value}"
            
            # 检查小数位数
            exponent = decimal_amount.as_tuple().exponent
            if isinstance(exponent, int) and exponent < -2:
                return False, "金额最多保留2位小数"
            
            return True, ""
            
        except (InvalidOperation, ValueError, TypeError):
            return False, "金额格式不正确"
    
    @staticmethod
    def validate_date(date_str, date_format='%Y-%m-%d'):
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            date_format: 日期格式
            
        Returns:
            (bool, str, datetime): (是否有效, 错误消息, 日期对象)
        """
        if not date_str:
            return False, "日期不能为空", None
        
        try:
            date_obj = datetime.strptime(date_str, date_format)
            return True, "", date_obj
        except ValueError:
            return False, f"日期格式不正确，应为{date_format}", None
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """
        验证日期范围
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if not start_date or not end_date:
            return False, "开始日期和结束日期不能为空"
        
        if start_date > end_date:
            return False, "开始日期不能晚于结束日期"
        
        return True, ""
    
    @staticmethod
    def validate_required(value, field_name):
        """
        验证必填字段
        
        Args:
            value: 字段值
            field_name: 字段名称
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_name}不能为空"
        return True, ""
    
    @staticmethod
    def validate_length(value, field_name, min_length=None, max_length=None):
        """
        验证字符串长度
        
        Args:
            value: 字符串值
            field_name: 字段名称
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if not isinstance(value, str):
            return False, f"{field_name}必须是字符串"
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            return False, f"{field_name}长度不能少于{min_length}个字符"
        
        if max_length is not None and length > max_length:
            return False, f"{field_name}长度不能超过{max_length}个字符"
        
        return True, ""
    
    @staticmethod
    def validate_enum(value, field_name, allowed_values):
        """
        验证枚举值
        
        Args:
            value: 值
            field_name: 字段名称
            allowed_values: 允许的值列表
            
        Returns:
            (bool, str): (是否有效, 错误消息)
        """
        if value not in allowed_values:
            return False, f"{field_name}必须是以下值之一：{', '.join(map(str, allowed_values))}"
        return True, ""
