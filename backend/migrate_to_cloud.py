"""
数据库迁移脚本
从原数据库迁移到微信云托管新数据库
"""
import pymysql
import sys

# 原数据库配置（宝塔服务器 - 开发环境）
SOURCE_DB = {
    'host': '60.205.161.210',
    'port': 3306,
    'user': 'timevalue',
    'password': 'GX3sAXJzabZpCidp',
    'database': 'timevalue',
    'charset': 'utf8mb4'
}

# 目标数据库配置（微信云托管新实例）
TARGET_DB = {
    'host': 'sh-cynosdbmysql-grp-gs9o93tm.sql.tencentcdb.com',
    'port': 28870,
    'user': 'wangyongqing',
    'password': 'Fpkj888~',
    'charset': 'utf8mb4'
}

def create_database():
    """在目标数据库创建flask数据库"""
    print("=" * 60)
    print("1. 创建目标数据库...")
    print("=" * 60)
    
    conn = pymysql.connect(**{k: v for k, v in TARGET_DB.items() if k != 'database'})
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS allmine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ 数据库 allmine 创建成功")
    except Exception as e:
        print(f"⚠️ 创建数据库警告: {e}")
    finally:
        cursor.close()
        conn.close()

def get_tables(conn):
    """获取所有表"""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def get_create_table_sql(conn, table_name):
    """获取建表语句"""
    cursor = conn.cursor()
    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
    result = cursor.fetchone()
    cursor.close()
    return result[1] if result else None

def migrate_table(source_conn, target_conn, table_name):
    """迁移单个表"""
    print(f"\n   迁移表: {table_name}")
    
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    try:
        # 禁用外键检查
        target_cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        # 获取建表语句
        create_sql = get_create_table_sql(source_conn, table_name)
        if not create_sql:
            print(f"      ⚠️ 无法获取表结构")
            return False
        
        # 创建表
        try:
            target_cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            target_cursor.execute(create_sql)
            target_conn.commit()
            print(f"      ✅ 表结构创建成功")
        except Exception as e:
            print(f"      ⚠️ 创建表警告: {e}")
            return False
        
        # 获取数据
        source_cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = source_cursor.fetchall()
        
        if rows:
            # 获取列信息
            source_cursor.execute(f"DESCRIBE `{table_name}`")
            columns = [row[0] for row in source_cursor.fetchall()]
            
            # 构建INSERT语句
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f'`{col}`' for col in columns])
            insert_sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
            
            # 批量插入
            target_cursor.executemany(insert_sql, rows)
            target_conn.commit()
            print(f"      ✅ 数据迁移成功: {len(rows)} 条记录")
        else:
            print(f"      ℹ️ 表为空，无数据需要迁移")
        
        return True
        
    except Exception as e:
        print(f"      ❌ 迁移失败: {e}")
        return False
    finally:
        source_cursor.close()
        target_cursor.close()

def migrate():
    """执行迁移"""
    print("\n" + "=" * 60)
    print("TimeValue 数据库迁移工具")
    print("=" * 60)
    print(f"源数据库: {SOURCE_DB['host']}:{SOURCE_DB['port']}/{SOURCE_DB['database']}")
    print(f"目标数据库: {TARGET_DB['host']}:{TARGET_DB['port']}/allmine")
    
    # 创建目标数据库
    create_database()
    
    # 连接源数据库
    print("\n" + "=" * 60)
    print("2. 连接数据库...")
    print("=" * 60)
    
    try:
        source_conn = pymysql.connect(**SOURCE_DB)
        print(f"✅ 源数据库连接成功")
    except Exception as e:
        print(f"❌ 源数据库连接失败: {e}")
        return False
    
    try:
        target_conn = pymysql.connect(**{**TARGET_DB, 'database': 'allmine'})
        print(f"✅ 目标数据库连接成功")
    except Exception as e:
        print(f"❌ 目标数据库连接失败: {e}")
        source_conn.close()
        return False
    
    # 获取所有表
    print("\n" + "=" * 60)
    print("3. 迁移数据表...")
    print("=" * 60)
    
    tables = get_tables(source_conn)
    print(f"发现 {len(tables)} 个表: {', '.join(tables)}")
    
    success_count = 0
    for table in tables:
        if migrate_table(source_conn, target_conn, table):
            success_count += 1
    
    # 关闭连接
    source_conn.close()
    target_conn.close()
    
    # 打印结果
    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)
    print(f"成功: {success_count}/{len(tables)} 个表")
    
    return success_count == len(tables)

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
