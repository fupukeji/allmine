"""
数据库迁移脚本：添加多模型API Key字段
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始执行迁移...")

try:
    from app import create_app
    from database import db
    from sqlalchemy import text
    
    print("模块导入成功")
except Exception as e:
    print(f"导入错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def migrate():
    """执行迁移"""
    app = create_app()
    
    with app.app_context():
        print("\n开始数据库迁移...")
        
        try:
            # 检查字段是否已存在
            result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
            columns = [row[1] for row in result]
            
            print(f"当前users表字段: {columns}")
            
            # 添加zhipu_api_key_encrypted字段
            if 'zhipu_api_key_encrypted' not in columns:
                print("添加字段: zhipu_api_key_encrypted")
                db.session.execute(text("ALTER TABLE users ADD COLUMN zhipu_api_key_encrypted TEXT"))
                db.session.commit()
                print("✓ zhipu_api_key_encrypted 字段添加成功")
            else:
                print("✓ zhipu_api_key_encrypted 字段已存在")
            
            # 添加aliyun_api_key_encrypted字段
            if 'aliyun_api_key_encrypted' not in columns:
                print("添加字段: aliyun_api_key_encrypted")
                db.session.execute(text("ALTER TABLE users ADD COLUMN aliyun_api_key_encrypted TEXT"))
                db.session.commit()
                print("✓ aliyun_api_key_encrypted 字段添加成功")
            else:
                print("✓ aliyun_api_key_encrypted 字段已存在")
            
            # 迁移旧数据：将aliyun_api_token_encrypted的数据复制到zhipu_api_key_encrypted
            if 'aliyun_api_token_encrypted' in columns:
                print("\n迁移旧数据...")
                result = db.session.execute(text(
                    "UPDATE users SET zhipu_api_key_encrypted = aliyun_api_token_encrypted "
                    "WHERE aliyun_api_token_encrypted IS NOT NULL AND zhipu_api_key_encrypted IS NULL"
                ))
                db.session.commit()
                print(f"✓ 已迁移 {result.rowcount} 条旧数据")
            
            # 创建system_config表（如果不存在）
            print("\n创建system_config表...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key VARCHAR(100) NOT NULL UNIQUE,
                    config_value TEXT,
                    description VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("✓ system_config 表已创建")
            
            # 初始化默认AI服务商配置
            print("\n初始化默认配置...")
            result = db.session.execute(text(
                "SELECT * FROM system_config WHERE config_key = 'ai_provider'"
            )).fetchone()
            
            if not result:
                db.session.execute(text(
                    "INSERT INTO system_config (config_key, config_value, description) "
                    "VALUES ('ai_provider', 'zhipu', '当前使用的AI服务商: zhipu')"
                ))
                db.session.commit()
                print("✓ 已设置默认AI服务商为智谱AI")
            else:
                print("✓ AI服务商配置已存在")
            
            print("\n✅ 数据库迁移完成！")
            print("现在可以正常登录和使用多模型功能了。")
            
        except Exception as e:
            import traceback
            print(f"\n❌ 迁移失败: {e}")
            print(traceback.format_exc())
            db.session.rollback()

if __name__ == '__main__':
    migrate()
