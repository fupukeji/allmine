#!/usr/bin/env python3
"""
TimeValue 数据迁移工具
从SQLite迁移数据到MySQL
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pymysql

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from config.database import DatabaseConfig
from models.user import User
from models.category import Category
from models.project import Project
from models.asset import Asset

load_dotenv()


def get_sqlite_engine():
    """获取SQLite数据库引擎"""
    sqlite_uri = DatabaseConfig.get_sqlite_uri()
    return create_engine(sqlite_uri)


def get_mysql_engine():
    """获取MySQL数据库引擎"""
    mysql_uri = DatabaseConfig.get_mysql_uri(
        host=os.getenv('DB_HOST', '60.205.161.210'),
        port=int(os.getenv('DB_PORT', 3306)),
        database=os.getenv('DB_NAME', 'timevalue'),
        username=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    return create_engine(mysql_uri)


def test_mysql_connection():
    """测试MySQL连接"""
    try:
        engine = get_mysql_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ MySQL连接测试成功")
        return True
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        return False


def backup_sqlite():
    """备份SQLite数据库"""
    import shutil
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'timevalue.db')
    if not os.path.exists(db_path):
        print("⚠️  SQLite数据库不存在，跳过备份")
        return None
    
    backup_path = db_path.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    shutil.copy2(db_path, backup_path)
    print(f"✅ SQLite数据库已备份到: {backup_path}")
    return backup_path


def migrate_data():
    """迁移数据"""
    print("\n" + "="*60)
    print("🚀 TimeValue 数据迁移工具")
    print("="*60)
    
    # 1. 测试MySQL连接
    print("\n📋 步骤1: 测试MySQL连接...")
    if not test_mysql_connection():
        print("\n❌ 迁移失败: 无法连接到MySQL数据库")
        print("💡 请先运行 'python mysql_diagnostic.py' 检查MySQL配置")
        return False
    
    # 2. 备份SQLite数据库
    print("\n📋 步骤2: 备份SQLite数据库...")
    backup_path = backup_sqlite()
    
    # 3. 创建数据库会话
    print("\n📋 步骤3: 创建数据库连接...")
    sqlite_engine = get_sqlite_engine()
    mysql_engine = get_mysql_engine()
    
    SqliteSession = sessionmaker(bind=sqlite_engine)
    MysqlSession = sessionmaker(bind=mysql_engine)
    
    sqlite_session = SqliteSession()
    mysql_session = MysqlSession()
    
    try:
        # 4. 创建MySQL表结构
        print("\n📋 步骤4: 创建MySQL表结构...")
        from database import db
        from app import create_app
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = str(mysql_engine.url)
        
        with app.app_context():
            db.create_all()
            print("✅ MySQL表结构创建成功")
        
        # 5. 迁移用户数据
        print("\n📋 步骤5: 迁移用户数据...")
        users = sqlite_session.query(User).all()
        user_count = 0
        
        for user in users:
            # 检查MySQL中是否已存在
            existing = mysql_session.query(User).filter_by(username=user.username).first()
            if existing:
                print(f"   ⚠️  用户 '{user.username}' 已存在，跳过")
                continue
            
            new_user = User(
                id=user.id,
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                created_at=user.created_at
            )
            mysql_session.add(new_user)
            user_count += 1
        
        mysql_session.commit()
        print(f"   ✅ 迁移了 {user_count} 个用户")
        
        # 6. 迁移分类数据
        print("\n📋 步骤6: 迁移分类数据...")
        categories = sqlite_session.query(Category).all()
        category_count = 0
        
        for category in categories:
            new_category = Category(
                id=category.id,
                user_id=category.user_id,
                name=category.name,
                color=category.color,
                icon=category.icon,
                created_at=category.created_at
            )
            mysql_session.add(new_category)
            category_count += 1
        
        mysql_session.commit()
        print(f"   ✅ 迁移了 {category_count} 个分类")
        
        # 7. 迁移项目数据
        print("\n📋 步骤7: 迁移项目数据...")
        projects = sqlite_session.query(Project).all()
        project_count = 0
        
        for project in projects:
            new_project = Project(
                id=project.id,
                user_id=project.user_id,
                category_id=project.category_id,
                name=project.name,
                description=project.description,
                total_amount=project.total_amount,
                billing_type=project.billing_type,
                start_time=project.start_time,
                end_time=project.end_time,
                created_at=project.created_at,
                updated_at=project.updated_at
            )
            mysql_session.add(new_project)
            project_count += 1
        
        mysql_session.commit()
        print(f"   ✅ 迁移了 {project_count} 个项目")
        
        # 8. 迁移固定资产数据
        print("\n📋 步骤8: 迁移固定资产数据...")
        assets = sqlite_session.query(Asset).all()
        asset_count = 0
        
        for asset in assets:
            new_asset = Asset(
                id=asset.id,
                user_id=asset.user_id,
                category_id=asset.category_id,
                name=asset.name,
                description=asset.description,
                original_value=asset.original_value,
                purchase_date=asset.purchase_date,
                useful_life=asset.useful_life,
                salvage_value=asset.salvage_value,
                depreciation_method=asset.depreciation_method,
                status=asset.status,
                created_at=asset.created_at,
                updated_at=asset.updated_at
            )
            mysql_session.add(new_asset)
            asset_count += 1
        
        mysql_session.commit()
        print(f"   ✅ 迁移了 {asset_count} 个固定资产")
        
        # 9. 验证数据
        print("\n📋 步骤9: 验证迁移结果...")
        mysql_user_count = mysql_session.query(User).count()
        mysql_category_count = mysql_session.query(Category).count()
        mysql_project_count = mysql_session.query(Project).count()
        mysql_asset_count = mysql_session.query(Asset).count()
        
        print(f"   MySQL数据统计:")
        print(f"   - 用户: {mysql_user_count}")
        print(f"   - 分类: {mysql_category_count}")
        print(f"   - 项目: {mysql_project_count}")
        print(f"   - 固定资产: {mysql_asset_count}")
        
        # 10. 更新.env文件
        print("\n📋 步骤10: 更新配置文件...")
        response = input("\n是否切换到MySQL数据库? (y/n): ").strip().lower()
        if response == 'y':
            env_file = os.path.join(os.path.dirname(__file__), '.env')
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                if line.startswith('DB_TYPE='):
                    new_lines.append('DB_TYPE=mysql\n')
                else:
                    new_lines.append(line)
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("   ✅ 配置文件已更新为MySQL")
        
        print("\n" + "="*60)
        print("✅ 数据迁移完成！")
        print("="*60)
        print(f"\n📌 SQLite备份文件: {backup_path}")
        print("💡 提示: 请重启应用以使用MySQL数据库")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        mysql_session.rollback()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        sqlite_session.close()
        mysql_session.close()


if __name__ == '__main__':
    success = migrate_data()
    sys.exit(0 if success else 1)
