"""
为fixed_assets表添加处置相关字段
- rent_price: 月租金
- sell_price: 售出价格
- dispose_date: 处置日期
- dispose_note: 处置备注
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

def add_dispose_fields():
    """添加处置相关字段"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # 需要添加的字段
        fields = [
            ('rent_price', 'DECIMAL(12,2) DEFAULT NULL COMMENT "月租金"'),
            ('sell_price', 'DECIMAL(15,2) DEFAULT NULL COMMENT "售出价格"'),
            ('dispose_date', 'DATE DEFAULT NULL COMMENT "处置日期"'),
            ('dispose_note', 'TEXT DEFAULT NULL COMMENT "处置备注"')
        ]
        
        for field_name, field_def in fields:
            if check_column_exists(cursor, 'fixed_assets', field_name):
                print(f'字段 {field_name} 已存在，跳过')
            else:
                sql = f'ALTER TABLE fixed_assets ADD COLUMN {field_name} {field_def}'
                cursor.execute(sql)
                print(f'成功添加字段: {field_name}')
        
        conn.commit()
        print('\n数据库迁移完成!')
        
    except Exception as e:
        conn.rollback()
        print(f'迁移失败: {e}')
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    add_dispose_fields()
