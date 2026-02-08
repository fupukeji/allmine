"""
更新用户账号密码
"""
import pymysql
from werkzeug.security import generate_password_hash

# 目标数据库配置
TARGET_DB = {
    'host': 'sh-cynosdbmysql-grp-gs9o93tm.sql.tencentcdb.com',
    'port': 28870,
    'user': 'wangyongqing',
    'password': 'Fpkj888~',
    'database': 'allmine',
    'charset': 'utf8mb4'
}

# 新用户信息
NEW_USERNAME = 'wangyongqing'
NEW_PASSWORD = '15810507827'
NEW_EMAIL = 'wangyongqing@fupukeji.com'

def update_user():
    """更新或创建用户"""
    print("=" * 60)
    print("更新用户账号")
    print("=" * 60)
    
    conn = pymysql.connect(**TARGET_DB)
    cursor = conn.cursor()
    
    try:
        # 生成密码哈希
        password_hash = generate_password_hash(NEW_PASSWORD)
        
        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (NEW_USERNAME,))
        user = cursor.fetchone()
        
        if user:
            # 更新现有用户
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, email = %s, role = 'admin'
                WHERE username = %s
            """, (password_hash, NEW_EMAIL, NEW_USERNAME))
            print(f"✅ 用户 {NEW_USERNAME} 密码已更新")
        else:
            # 创建新用户
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, created_at)
                VALUES (%s, %s, %s, 'admin', NOW())
            """, (NEW_USERNAME, NEW_EMAIL, password_hash))
            print(f"✅ 用户 {NEW_USERNAME} 已创建")
        
        conn.commit()
        
        print(f"\n用户名: {NEW_USERNAME}")
        print(f"密码: {NEW_PASSWORD}")
        print(f"邮箱: {NEW_EMAIL}")
        print(f"角色: admin")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_user()
