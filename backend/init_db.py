"""
数据库初始化脚本
用于创建数据库表和初始化基础数据
"""
from app import create_app
from database import db
from models.user import User
from services.category_service import initialize_user_categories

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("开始初始化数据库...")
        print("="*60)
        
        # 创建所有表
        print("\n1. 创建数据表...")
        db.create_all()
        print("✓ 数据表创建成功")
        
        # 检查管理员用户
        print("\n2. 检查管理员用户...")
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("   创建管理员用户...")
            admin = User(
                username='admin',
                email='admin@timevalue.com',
                password='admin123'
            )
            admin.role = 'admin'
            db.session.add(admin)
            db.session.commit()
            print("   ✓ 管理员用户创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
            
            # 初始化默认分类
            print("\n3. 初始化默认分类...")
            success = initialize_user_categories(admin.id, skip_if_exists=False)
            if success:
                print("   ✓ 默认分类初始化成功")
            else:
                print("   ✗ 默认分类初始化失败")
        else:
            print("   ✓ 管理员用户已存在")
        
        print("\n" + "="*60)
        print("数据库初始化完成！")
        print("="*60)
        print(f"\n数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\n提示:")
        print("  - 默认管理员: admin / admin123")
        print("  - 首次登录后请修改密码")
        print("  - 已为admin用户初始化默认分类")

if __name__ == '__main__':
    init_database()
