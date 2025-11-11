import sqlite3
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'timevalue.db')
print(f"数据库路径: {db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 检查字段是否已存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\n当前字段: {columns}")
    
    # 添加zhipu_api_key_encrypted字段
    if 'zhipu_api_key_encrypted' not in columns:
        print("\n添加字段: zhipu_api_key_encrypted")
        cursor.execute("ALTER TABLE users ADD COLUMN zhipu_api_key_encrypted TEXT")
        conn.commit()
        print("✓ 成功")
    else:
        print("\n✓ zhipu_api_key_encrypted 已存在")
    
    # 添加aliyun_api_key_encrypted字段
    if 'aliyun_api_key_encrypted' not in columns:
        print("\n添加字段: aliyun_api_key_encrypted")
        cursor.execute("ALTER TABLE users ADD COLUMN aliyun_api_key_encrypted TEXT")
        conn.commit()
        print("✓ 成功")
    else:
        print("\n✓ aliyun_api_key_encrypted 已存在")
    
    # 迁移旧数据
    if 'aliyun_api_token_encrypted' in columns:
        print("\n迁移旧数据...")
        cursor.execute("""
            UPDATE users 
            SET zhipu_api_key_encrypted = aliyun_api_token_encrypted 
            WHERE aliyun_api_token_encrypted IS NOT NULL 
            AND zhipu_api_key_encrypted IS NULL
        """)
        conn.commit()
        print(f"✓ 迁移了 {cursor.rowcount} 条数据")
    
    # 创建system_config表
    print("\n创建system_config表...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key VARCHAR(100) NOT NULL UNIQUE,
            config_value TEXT,
            description VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("✓ 成功")
    
    # 初始化配置
    cursor.execute("SELECT * FROM system_config WHERE config_key = 'ai_provider'")
    if not cursor.fetchone():
        print("\n初始化AI服务商配置...")
        cursor.execute("""
            INSERT INTO system_config (config_key, config_value, description) 
            VALUES ('ai_provider', 'zhipu', '当前使用的AI服务商')
        """)
        conn.commit()
        print("✓ 成功")
    else:
        print("\n✓ AI服务商配置已存在")
    
    print("\n✅ 数据库迁移完成！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
