"""快速测试分类初始化"""
from services.category_service import initialize_user_categories, get_category_tree
from models.user import User
from app import create_app

app = create_app()

with app.app_context():
    user = User.query.first()
    if user:
        print(f'测试用户: {user.username} (ID: {user.id})')
        
        # 尝试初始化
        result = initialize_user_categories(user.id)
        print(f'初始化结果: {result}')
        
        # 获取分类树
        tree = get_category_tree(user.id)
        print(f'\n分类数量: {len(tree)}')
        
        for cat in tree:
            child_count = len(cat.get('children', []))
            print(f'- {cat["name"]}: {child_count} 个子分类')
    else:
        print('没有找到用户')
