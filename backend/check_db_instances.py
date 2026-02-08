"""
检查两个数据库实例中的用户数据
"""
import pymysql

# 实例1: 之前迁移数据用的CynosDB（外网）
DB1 = {
    'host': 'sh-cynosdbmysql-grp-gs9o93tm.sql.tencentcdb.com',
    'port': 28870,
    'user': 'wangyongqing',
    'password': 'Fpkj888~',
    'charset': 'utf8mb4'
}

# 实例2: 云托管默认MySQL（外网入口未知，尝试用root）
# 内网地址 10.33.112.28:3306 从本地无法访问

print("=" * 60)
print("检查 CynosDB 实例 (28870端口)")
print("=" * 60)
try:
    conn = pymysql.connect(**DB1)
    cursor = conn.cursor()
    
    # 列出所有数据库
    cursor.execute("SHOW DATABASES")
    dbs = cursor.fetchall()
    print(f"数据库列表: {[d[0] for d in dbs]}")
    
    # 检查allmine数据库中的用户
    cursor.execute("USE allmine")
    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()
    print(f"\nallmine数据库用户 ({len(users)}个):")
    for u in users:
        print(f"  ID:{u[0]} 用户名:{u[1]} 邮箱:{u[2]} 角色:{u[3]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"连接失败: {e}")

print("\n" + "=" * 60)
print("结论：云托管用的 10.33.112.28:3306 可能是不同实例")
print("需要在云托管后端数据库中重新创建用户")
print("=" * 60)
