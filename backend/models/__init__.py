# 导入所有模型以便app.py可以找到它们
from .user import User
from .category import Category
from .project import Project
from .fixed_asset import FixedAsset
from .asset_expense import AssetExpense
from .notification_settings import UserNotificationSettings

__all__ = ['User', 'Category', 'Project', 'FixedAsset', 'AssetExpense', 'UserNotificationSettings']