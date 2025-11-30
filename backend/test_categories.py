"""
分类系统测试和迁移脚本
用于测试新的层级分类系统，并为现有用户初始化默认分类
"""

from database import db
from models.user import User
from models.category import Category
from services.category_service import initialize_user_categories, get_category_tree
from app import app

def test_category_structure():
    """测试分类结构"""
    print("\n" + "="*60)
    print("测试分类结构")
    print("="*60)
    
    with app.app_context():
        # 获取第一个用户
        user = User.query.first()
        if not user:
            print("❌ 没有找到用户")
            return False
        
        print(f"✓ 测试用户: {user.username} (ID: {user.id})")
        
        # 获取用户的分类树
        category_tree = get_category_tree(user.id)
        
        if not category_tree:
            print("❌ 该用户没有分类")
            return False
        
        print(f"\n✓ 找到 {len(category_tree)} 个一级分类\n")
        
        # 显示分类树
        for top_cat in category_tree:
            print(f"📁 {top_cat['name']} ({top_cat['color']}) - {top_cat['project_count']} 个项目")
            
            if top_cat.get('children'):
                for child_cat in top_cat['children']:
                    print(f"   └─ {child_cat['name']} ({child_cat['color']}) - {child_cat['project_count']} 个项目")
            print()
        
        return True

def initialize_existing_users():
    """为现有用户初始化默认分类"""
    print("\n" + "="*60)
    print("为现有用户初始化默认分类")
    print("="*60)
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ 没有找到用户")
            return
        
        print(f"找到 {len(users)} 个用户\n")
        
        for user in users:
            # 检查用户是否已有分类
            existing_count = Category.query.filter_by(user_id=user.id).count()
            
            if existing_count > 0:
                print(f"⊙ {user.username} (ID: {user.id}) - 已有 {existing_count} 个分类，跳过")
            else:
                print(f"→ {user.username} (ID: {user.id}) - 正在初始化...", end="")
                success = initialize_user_categories(user.id)
                if success:
                    new_count = Category.query.filter_by(user_id=user.id).count()
                    print(f" ✓ 成功创建 {new_count} 个分类")
                else:
                    print(" ✗ 初始化失败")

def show_category_statistics():
    """显示分类统计信息"""
    print("\n" + "="*60)
    print("分类统计信息")
    print("="*60)
    
    with app.app_context():
        total_users = User.query.count()
        total_categories = Category.query.count()
        top_level_categories = Category.query.filter_by(parent_id=None).count()
        
        print(f"\n总用户数: {total_users}")
        print(f"总分类数: {total_categories}")
        print(f"一级分类数: {top_level_categories}")
        print(f"二级分类数: {total_categories - top_level_categories}")
        
        # 按用户分组统计
        print("\n用户分类分布:")
        users = User.query.all()
        for user in users:
            user_cats = Category.query.filter_by(user_id=user.id).count()
            user_top_cats = Category.query.filter_by(user_id=user.id, parent_id=None).count()
            print(f"  {user.username}: {user_cats} 个分类 ({user_top_cats} 个一级分类)")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("TimeValue 分类系统管理工具")
    print("="*60)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看分类结构")
        print("2. 为现有用户初始化默认分类")
        print("3. 显示分类统计信息")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            test_category_structure()
        elif choice == '2':
            confirm = input("\n⚠️  确定要为现有用户初始化分类吗? (yes/no): ").strip().lower()
            if confirm == 'yes':
                initialize_existing_users()
            else:
                print("已取消")
        elif choice == '3':
            show_category_statistics()
        elif choice == '4':
            print("\n再见!")
            break
        else:
            print("无效的选项，请重新选择")

if __name__ == '__main__':
    main()
