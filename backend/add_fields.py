# 简单的数据库字段添加脚本
import sqlite3
import os
import sys

db_file = r'e:\timevalue\data\timevalue.db'

if not os.path.exists(db_file):
    print(f"数据库文件不存在: {db_file}")
    sys.exit(1)

print(f"连接数据库: {db_file}")
conn = sqlite3.connect(db_file)
c = conn.cursor()

# 添加第一个字段
try:
    print("添加 zhipu_api_key_encrypted...")
    c.execute("ALTER TABLE users ADD COLUMN zhipu_api_key_encrypted TEXT")
    conn.commit()
    print("成功!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("字段已存在，跳过")
    else:
        print(f"错误: {e}")

# 添加第二个字段  
try:
    print("添加 aliyun_api_key_encrypted...")
    c.execute("ALTER TABLE users ADD COLUMN aliyun_api_key_encrypted TEXT")
    conn.commit()
    print("成功!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("字段已存在，跳过")
    else:
        print(f"错误: {e}")

# 创建system_config表
try:
    print("创建 system_config 表...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value TEXT,
            description VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("成功!")
except Exception as e:
    print(f"错误: {e}")

# 初始化默认配置
try:
    c.execute("SELECT * FROM system_config WHERE config_key='ai_provider'")
    if not c.fetchone():
        print("插入默认AI服务商配置...")
        c.execute("INSERT INTO system_config (config_key, config_value, description) VALUES ('ai_provider', 'zhipu', '当前AI服务商')")
        conn.commit()
        print("成功!")
    else:
        print("配置已存在")
except Exception as e:
    print(f"错误: {e}")

conn.close()
print("\n所有操作完成!")
