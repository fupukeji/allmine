import sqlite3
conn = sqlite3.connect(r'e:\timevalue\data\timevalue.db')
c = conn.cursor()
c.execute("PRAGMA table_info(users)")
columns = [row[1] for row in c.fetchall()]
print("users表的字段:")
for col in columns:
    print(f"  - {col}")
    
if 'zhipu_api_key_encrypted' in columns and 'aliyun_api_key_encrypted' in columns:
    print("\n✓ 新字段已成功添加!")
else:
    print("\n✗ 新字段未找到")
    
conn.close()
