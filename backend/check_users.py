"""
检查用户数据
"""
import pymysql

# 目标数据库配置
TARGET_DB = {
    'host': 'sh-cynosdbmysql-grp-gs9o93tm.sql.tencentcdb.com',
    'port': 28870,
    'user': 'wangyongqing',
    'password': 'Fpkj888~',
    'database': 'allmine',
    'charset': 'utf8mb4'
}

def check_users():
    """检查用户数据"""
    print("=" * 60)
    print("检查用户数据")
    print("=" * 60)
    
    conn = pymysql.connect(**TARGET_DB)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, username, email, role, password_hash FROM users")
        users = cursor.fetchall()
        
        print(f"共 {len(users)} 个用户:")
        for user in users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}")
            print(f"    密码哈希: {user[4][:50]}..." if user[4] else "    密码哈希: None")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check_users()
