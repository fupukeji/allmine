#!/usr/bin/env python3
"""
TimeValue MySQL连接诊断工具
用于测试和诊断MySQL数据库连接问题
"""

import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_mysql_connection():
    """测试MySQL连接"""
    print("\n" + "="*60)
    print("🔍 TimeValue MySQL 连接诊断")
    print("="*60)
    
    # 配置信息
    config = {
        'host': os.getenv('DB_HOST', '60.205.161.210'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'timevalue'),
        'charset': 'utf8mb4'
    }
    
    print(f"\n📋 连接配置:")
    print(f"   主机: {config['host']}")
    print(f"   端口: {config['port']}")
    print(f"   用户: {config['user']}")
    print(f"   密码: {'*' * len(config['password'])}")
    print(f"   数据库: {config['database']}")
    
    # 测试1: 不指定数据库的连接
    print(f"\n🔧 测试1: 连接到MySQL服务器（不指定数据库）...")
    try:
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            charset=config['charset']
        )
        print("   ✅ 成功连接到MySQL服务器！")
        
        # 获取服务器信息
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   📌 MySQL版本: {version}")
        
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        print(f"   📌 可用数据库: {', '.join(databases)}")
        
        if config['database'] in databases:
            print(f"   ✅ 数据库 '{config['database']}' 存在")
        else:
            print(f"   ⚠️  数据库 '{config['database']}' 不存在，需要创建")
            
        cursor.close()
        conn.close()
        
        # 测试2: 连接到指定数据库
        print(f"\n🔧 测试2: 连接到数据库 '{config['database']}'...")
        try:
            conn = pymysql.connect(**config)
            print("   ✅ 成功连接到数据库！")
            
            # 检查表
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            if tables:
                print(f"   📌 现有表: {', '.join(tables)}")
            else:
                print(f"   ⚠️  数据库为空，需要初始化表结构")
            
            cursor.close()
            conn.close()
            
            print("\n" + "="*60)
            print("✅ 诊断完成：数据库连接正常！")
            print("="*60)
            return True
            
        except pymysql.err.OperationalError as e:
            error_code, error_msg = e.args
            print(f"   ❌ 连接失败: [{error_code}] {error_msg}")
            
            if error_code == 1049:
                print(f"\n   💡 解决方案: 数据库不存在，创建数据库...")
                try:
                    conn = pymysql.connect(
                        host=config['host'],
                        port=config['port'],
                        user=config['user'],
                        password=config['password'],
                        charset=config['charset']
                    )
                    cursor = conn.cursor()
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    print(f"   ✅ 数据库 '{config['database']}' 创建成功！")
                    cursor.close()
                    conn.close()
                    return True
                except Exception as create_error:
                    print(f"   ❌ 创建数据库失败: {create_error}")
                    return False
            
            return False
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        print(f"   ❌ 连接失败: [{error_code}] {error_msg}")
        
        print("\n" + "="*60)
        print("❌ 诊断失败：无法连接到MySQL服务器")
        print("="*60)
        
        # 提供解决方案
        if error_code == 1130:
            print("\n🔧 问题原因: 主机IP未被授权访问MySQL服务器")
            print("\n💡 解决方案:")
            print("   1. 登录到MySQL服务器 (60.205.161.210)")
            print("   2. 执行以下SQL命令授权:")
            print(f"      GRANT ALL PRIVILEGES ON {config['database']}.* TO '{config['user']}'@'%' IDENTIFIED BY '{config['password']}';")
            print(f"      FLUSH PRIVILEGES;")
            print("\n   或者使用mysql_native_password插件 (MySQL 8.0+):")
            print(f"      ALTER USER '{config['user']}'@'%' IDENTIFIED WITH mysql_native_password BY '{config['password']}';")
            print(f"      GRANT ALL PRIVILEGES ON {config['database']}.* TO '{config['user']}'@'%';")
            print(f"      FLUSH PRIVILEGES;")
            print("\n   3. 检查MySQL配置文件 bind-address 是否为 0.0.0.0")
            print("   4. 检查防火墙是否开放3306端口")
            print("   5. 检查云服务器安全组是否开放3306端口")
            
        elif error_code == 2003:
            print("\n🔧 问题原因: 无法连接到MySQL服务器")
            print("\n💡 解决方案:")
            print("   1. 检查MySQL服务是否运行")
            print("   2. 检查服务器地址是否正确")
            print("   3. 检查网络连接")
            print("   4. 检查防火墙设置")
            
        elif error_code == 1045:
            print("\n🔧 问题原因: 用户名或密码错误")
            print("\n💡 解决方案:")
            print("   1. 检查.env文件中的DB_USER和DB_PASSWORD")
            print("   2. 确认MySQL用户凭据是否正确")
        
        return False
    
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")
        print("\n" + "="*60)
        print("❌ 诊断失败：发生未知错误")
        print("="*60)
        return False


def switch_to_sqlite():
    """切换到SQLite数据库"""
    print("\n" + "="*60)
    print("🔄 切换到SQLite数据库")
    print("="*60)
    
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith('DB_TYPE='):
                new_lines.append('DB_TYPE=sqlite\n')
                print("   ✅ DB_TYPE 已设置为 sqlite")
            else:
                new_lines.append(line)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("   ✅ 配置文件已更新")
        print("\n💡 提示: 现在可以使用 'python init_db.py' 初始化SQLite数据库")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"   ❌ 切换失败: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    # 测试连接
    success = test_mysql_connection()
    
    # 如果失败，询问是否切换到SQLite
    if not success:
        print("\n" + "="*60)
        response = input("\n是否切换到SQLite数据库? (y/n): ").strip().lower()
        if response == 'y':
            switch_to_sqlite()
        else:
            print("\n💡 提示: 请按照上述解决方案修复MySQL连接问题后重试")
            print("   或运行 'python mysql_diagnostic.py' 并选择切换到SQLite")
    
    print("\n")
