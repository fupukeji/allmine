#!/usr/bin/env python3
"""
MySQL数据库验证脚本
验证表结构和初始数据
"""

import pymysql
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

def verify_mysql():
    """验证MySQL数据库"""
    print("\n" + "="*60)
    print("🔍 TimeValue MySQL 数据库验证")
    print("="*60)
    
    config = {
        'host': os.getenv('DB_HOST', '60.205.161.210'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'timevalue'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'timevalue'),
        'charset': 'utf8mb4'
    }
    
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # 1. 显示配置信息
        print(f"\n📋 数据库配置:")
        print(f"   主机: {config['host']}:{config['port']}")
        print(f"   数据库: {config['database']}")
        print(f"   用户: {config['user']}")
        
        # 2. 显示表列表
        print(f"\n📊 数据表列表:")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table}")
        
        # 3. 显示每个表的记录数
        print(f"\n📈 表记录统计:")
        table_stats = []
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_stats.append([table, count])
        
        print(tabulate(table_stats, headers=['表名', '记录数'], tablefmt='grid'))
        
        # 4. 显示用户信息
        print(f"\n👤 用户信息:")
        cursor.execute("SELECT id, username, email, is_active, created_at FROM users")
        users = cursor.fetchall()
        
        if users:
            user_data = []
            for user in users:
                user_data.append([
                    user[0],  # id
                    user[1],  # username
                    user[2],  # email
                    '✅' if user[3] else '❌',  # is_active
                    user[4].strftime('%Y-%m-%d %H:%M:%S') if user[4] else 'N/A'  # created_at
                ])
            print(tabulate(user_data, headers=['ID', '用户名', '邮箱', '状态', '创建时间'], tablefmt='grid'))
        else:
            print("   ⚠️  暂无用户数据")
        
        # 5. 显示分类信息
        print(f"\n📁 分类信息:")
        cursor.execute("SELECT id, user_id, name, color, icon FROM categories LIMIT 10")
        categories = cursor.fetchall()
        
        if categories:
            cat_data = []
            for cat in categories:
                cat_data.append([
                    cat[0],  # id
                    cat[1],  # user_id
                    cat[2],  # name
                    cat[3],  # color
                    cat[4] or 'N/A'  # icon
                ])
            print(tabulate(cat_data, headers=['ID', '用户ID', '分类名', '颜色', '图标'], tablefmt='grid'))
        else:
            print("   ⚠️  暂无分类数据")
        
        # 6. 显示MySQL版本和字符集
        print(f"\n⚙️  数据库信息:")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   MySQL版本: {version}")
        
        cursor.execute("SHOW VARIABLES LIKE 'character_set_database'")
        charset = cursor.fetchone()[1]
        print(f"   数据库字符集: {charset}")
        
        cursor.execute("SHOW VARIABLES LIKE 'collation_database'")
        collation = cursor.fetchone()[1]
        print(f"   数据库排序规则: {collation}")
        
        print("\n" + "="*60)
        print("✅ MySQL数据库验证完成！")
        print("="*60)
        print(f"\n💡 提示:")
        print(f"   - 数据库连接正常")
        print(f"   - 共有 {len(tables)} 个数据表")
        print(f"   - 用户数: {len(users)}")
        print(f"   - 分类数: {len(categories)}")
        print(f"   - 可以开始使用系统了！")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    verify_mysql()
