"""
数据库迁移脚本：为categories表添加asset_type字段
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否已存在
            result = db.session.execute(text("SHOW COLUMNS FROM categories LIKE 'asset_type'"))
            if result.fetchone():
                print("asset_type 字段已存在，无需迁移")
                return
            
            # 添加asset_type字段
            db.session.execute(text("""
                ALTER TABLE categories 
                ADD COLUMN asset_type VARCHAR(20) DEFAULT 'virtual' 
                COMMENT '资产类型: virtual(虚拟资产), fixed(固定资产)'
            """))
            db.session.commit()
            print("✅ 成功添加 asset_type 字段")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 迁移失败: {e}")
            raise

if __name__ == '__main__':
    migrate()
