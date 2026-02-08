"""
为fixed_assets表添加出租相关字段
- rent_deposit: 押金
- rent_start_date: 租期开始日期
- rent_end_date: 租期结束日期
- rent_due_day: 收租日(每月几号)
- tenant_name: 租客姓名
- tenant_phone: 租客电话
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'timevalue'),
    'charset': 'utf8mb4'
}

def check_column_exists(cursor, table, column):
    """检查字段是否存在"""
    cursor.execute(f"""
        SELECT COUNT(*) FROM information_schema.columns 
        WHERE table_schema = '{DB_CONFIG['database']}' 
        AND table_name = '{table}' 
        AND column_name = '{column}'
    """)
    return cursor.fetchone()[0] > 0

def add_rent_fields():
    """添加出租相关字段"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 需要添加的字段
        fields = [
            ('rent_deposit', 'DECIMAL(12,2) DEFAULT NULL COMMENT "押金"'),
            ('rent_start_date', 'DATE DEFAULT NULL COMMENT "租期开始日期"'),
            ('rent_end_date', 'DATE DEFAULT NULL COMMENT "租期结束日期"'),
            ('rent_due_day', 'INT DEFAULT 1 COMMENT "收租日(每月几号)"'),
            ('tenant_name', 'VARCHAR(50) DEFAULT NULL COMMENT "租客姓名"'),
            ('tenant_phone', 'VARCHAR(20) DEFAULT NULL COMMENT "租客电话"')
        ]
        
        for field_name, field_def in fields:
            if check_column_exists(cursor, 'fixed_assets', field_name):
                print(f'字段 {field_name} 已存在，跳过')
            else:
                sql = f'ALTER TABLE fixed_assets ADD COLUMN {field_name} {field_def}'
                cursor.execute(sql)
                print(f'成功添加字段: {field_name}')
        
        conn.commit()
        print('\n出租字段迁移完成!')
        
    except Exception as e:
        conn.rollback()
        print(f'迁移失败: {e}')
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    add_rent_fields()
