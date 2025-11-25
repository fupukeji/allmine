"""
添加工作流轨迹字段到AIReport模型
执行方式：python backend/migrate_add_workflow_fields.py
"""

from app import create_app
from database import db
from sqlalchemy import text

def migrate():
    """添加工作流相关字段"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("开始数据库迁移：添加工作流轨迹字段")
            print("="*60 + "\n")
            
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('ai_reports')]
            
            # 添加execution_path字段
            if 'execution_path' not in columns:
                print("➕ 添加字段: execution_path (TEXT)")
                db.session.execute(text(
                    "ALTER TABLE ai_reports ADD COLUMN execution_path TEXT"
                ))
                print("✅ execution_path 字段添加成功")
            else:
                print("⏭️  execution_path 字段已存在，跳过")
            
            # 添加workflow_metadata字段
            if 'workflow_metadata' not in columns:
                print("➕ 添加字段: workflow_metadata (TEXT)")
                db.session.execute(text(
                    "ALTER TABLE ai_reports ADD COLUMN workflow_metadata TEXT"
                ))
                print("✅ workflow_metadata 字段添加成功")
            else:
                print("⏭️  workflow_metadata 字段已存在，跳过")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ 数据库迁移完成！")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ 迁移失败: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate()
