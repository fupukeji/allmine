"""
验证用户密码
"""
from werkzeug.security import check_password_hash
import pymysql

conn = pymysql.connect(
    host='sh-cynosdbmysql-grp-gs9o93tm.sql.tencentcdb.com',
    port=28870,
    user='wangyongqing',
    password='Fpkj888~',
    database='allmine',
    charset='utf8mb4'
)
cursor = conn.cursor()
cursor.execute("SELECT password_hash FROM users WHERE username = 'wangyongqing'")
result = cursor.fetchone()
if result:
    password_hash = result[0]
    test_password = '15810507827'
    is_valid = check_password_hash(password_hash, test_password)
    print(f'密码验证结果: {is_valid}')
    print(f'密码哈希: {password_hash}')
else:
    print('用户不存在')
cursor.close()
conn.close()
