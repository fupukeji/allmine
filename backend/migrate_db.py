"""
数据库迁移脚本 - 添加用户个人信息字段
Powered by 孚普科技（北京）有限公司
"""
import sqlite3
import os

def migrate_database():
    """迁移数据库，添加新字段"""
    db_path = 'timevalue.db'
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，将在启动时自动创建")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否已经有phone字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 需要添加的字段
        new_fields = [
            ('phone', 'VARCHAR(20)'),
            ('location', 'VARCHAR(100)'),
            ('bio', 'TEXT'),
            ('website', 'VARCHAR(200)'),
            ('company', 'VARCHAR(100)'),
            ('avatar', 'TEXT'),
            ('language', 'VARCHAR(10) DEFAULT "zh-CN"'),
            ('timezone', 'VARCHAR(50) DEFAULT "Asia/Shanghai"'),
            ('theme', 'VARCHAR(20) DEFAULT "light"'),
            ('email_notifications', 'BOOLEAN DEFAULT 1'),
            ('sms_notifications', 'BOOLEAN DEFAULT 0')
        ]
        
        # 添加缺失的字段
        for field_name, field_type in new_fields:
            if field_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {field_name} {field_type}')
                    print(f"✅ 添加字段: {field_name}")
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' not in str(e):
                        print(f"❌ 添加字段 {field_name} 失败: {e}")
        
        conn.commit()
        conn.close()
        
        print("🎉 数据库迁移完成！")
        print("🚀 Powered by 孚普科技（北京）有限公司")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")

if __name__ == "__main__":
    migrate_database()