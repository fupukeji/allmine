"""
数据库迁移脚本：为User模型添加微信字段
执行：python migrate_add_wechat_fields.py
"""
from app import create_app
from database import db

def migrate():
    app = create_app()
    
    with app.app_context():
        print("开始数据库迁移：添加微信字段...")
        
        try:
            # 执行SQL添加字段（如果不存在）
            with db.engine.connect() as conn:
                # 检查字段是否存在
                result = conn.execute(db.text("""
                    SELECT COUNT(*) as cnt 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'users' 
                    AND COLUMN_NAME = 'wechat_openid'
                """))
                exists = result.fetchone()[0] > 0
                
                if not exists:
                    print("添加字段：wechat_openid, wechat_unionid, wechat_nickname, wechat_avatar")
                    
                    # 添加微信字段
                    conn.execute(db.text("""
                        ALTER TABLE users 
                        ADD COLUMN wechat_openid VARCHAR(128) UNIQUE,
                        ADD COLUMN wechat_unionid VARCHAR(128),
                        ADD COLUMN wechat_nickname VARCHAR(100),
                        ADD COLUMN wechat_avatar VARCHAR(500)
                    """))
                    
                    # 添加索引
                    conn.execute(db.text("""
                        CREATE INDEX idx_wechat_openid ON users(wechat_openid)
                    """))
                    
                    conn.execute(db.text("""
                        CREATE INDEX idx_wechat_unionid ON users(wechat_unionid)
                    """))
                    
                    conn.commit()
                    print("✅ 迁移成功！微信字段已添加")
                else:
                    print("⚠️ 字段已存在，跳过迁移")
                    
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate()
