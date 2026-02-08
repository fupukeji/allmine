"""
测试数据库连接
快速验证宝塔服务器数据库配置是否正确
"""
import os
from dotenv import load_dotenv
import pymysql

# 加载环境变量
load_dotenv()

def test_connection():
    print("=" * 60)
    print("  TimeValue 数据库连接测试")
    print("=" * 60)
    print()
    
    # 读取配置
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    print("📋 配置信息:")
    print(f"   主机: {db_host}")
    print(f"   端口: {db_port}")
    print(f"   数据库: {db_name}")
    print(f"   用户: {db_user}")
    print(f"   密码: {'*' * len(db_password) if db_password else '未设置'}")
    print()
    
    try:
        print("🔌 正在连接数据库...")
        
        # 尝试连接
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ 连接成功！")
        print()
        
        # 获取数据库版本
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"📊 MySQL版本: {version}")
            
            # 获取当前数据库
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"📁 当前数据库: {current_db}")
            
            # 检查users表是否存在
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users'
            """, (db_name,))
            users_table_exists = cursor.fetchone()[0] > 0
            
            if users_table_exists:
                print("✅ users表已存在")
                
                # 检查微信字段是否存在
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'users' 
                    AND COLUMN_NAME = 'wechat_openid'
                """, (db_name,))
                wechat_field_exists = cursor.fetchone()[0] > 0
                
                if wechat_field_exists:
                    print("✅ 微信字段已添加")
                else:
                    print("⚠️  微信字段未添加，需要执行迁移脚本")
                    print("   运行: python migrate_add_wechat_fields.py")
            else:
                print("⚠️  users表不存在，需要初始化数据库")
                print("   运行: python init_db.py")
        
        connection.close()
        print()
        print("=" * 60)
        print("  ✅ 数据库配置正确，可以正常使用！")
        print("=" * 60)
        
    except pymysql.err.OperationalError as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("可能的原因：")
        print("  1. 数据库服务器未启动")
        print("  2. IP地址或端口错误")
        print("  3. 用户名或密码错误")
        print("  4. 防火墙阻止连接")
        print("  5. 数据库不存在")
        print()
        print("请检查宝塔面板的数据库配置")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_connection()
