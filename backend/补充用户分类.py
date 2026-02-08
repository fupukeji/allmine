"""
为现有用户补充缺失的分类
确保所有用户都有固定资产和虚拟资产的完整分类
"""

from app import create_app
from database import db
from models.user import User
from services.category_service import initialize_user_categories

def fix_user_categories():
    app = create_app()
    with app.app_context():
        try:
            # 获取所有用户
            users = User.query.all()
            print(f"找到 {len(users)} 个用户\n")
            
            for user in users:
                print(f"处理用户: {user.username} (ID: {user.id})")
                
                # 为用户初始化分类（不跳过已有分类）
                result = initialize_user_categories(user.id, skip_if_exists=False)
                
                if result:
                    print(f"  ✅ 分类已更新")
                else:
                    print(f"  ℹ️  分类已存在或更新失败")
                print()
            
            print("\n✅ 所有用户分类已补充完成！")
            
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_user_categories()
