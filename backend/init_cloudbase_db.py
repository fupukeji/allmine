"""
初始化腾讯云CloudBase数据库
创建timevalue数据库和表结构
"""
import os
from dotenv import load_dotenv
import pymysql

# 加载环境变量
load_dotenv()

def init_database():
    print("=" * 60)
    print("  TimeValue 云数据库初始化")
    print("=" * 60)
    print()
    
    # 读取配置
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    print("📋 数据库信息:")
    print(f"   主机: {db_host}")
    print(f"   端口: {db_port}")
    print(f"   数据库: {db_name}")
    print(f"   用户: {db_user}")
    print()
    
    try:
        # 1. 连接到MySQL服务器（不指定数据库）
        print("🔌 [1/4] 连接到MySQL服务器...")
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset='utf8mb4',
            connect_timeout=10
        )
        print("✅ 连接成功")
        print()
        
        # 2. 创建数据库
        print(f"📦 [2/4] 创建数据库 {db_name}...")
        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            if cursor.fetchone():
                print(f"⚠️  数据库 {db_name} 已存在，跳过创建")
            else:
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✅ 数据库 {db_name} 创建成功")
        
        connection.commit()
        connection.close()
        print()
        
        # 3. 连接到新创建的数据库
        print(f"🔌 [3/4] 连接到数据库 {db_name}...")
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            connect_timeout=10
        )
        print("✅ 连接成功")
        print()
        
        # 4. 创建表结构
        print("🏗️  [4/4] 创建表结构...")
        
        # 导入app来创建表
        from app import create_app
        from database import db
        
        app = create_app()
        with app.app_context():
            # 创建所有表
            db.create_all()
            print("✅ 表结构创建成功")
            
            # 显示创建的表
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print()
                print("📊 已创建的表:")
                for table in tables:
                    print(f"   - {table[0]}")
        
        connection.close()
        print()
        print("=" * 60)
        print("  🎉 数据库初始化完成！")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 执行数据库迁移添加微信字段")
        print("     python migrate_add_wechat_fields.py")
        print()
        print("  2. 启动应用测试")
        print("     python app.py")
        print()
        
    except pymysql.err.OperationalError as e:
        print(f"❌ 操作失败: {e}")
        print()
        print("可能的原因：")
        print("  1. 数据库连接信息错误")
        print("  2. 用户权限不足")
        print("  3. 网络连接问题")
        print()
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_database()
