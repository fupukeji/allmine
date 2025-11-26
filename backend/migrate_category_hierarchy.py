"""
数据库迁移脚本：添加分类层级支持
为categories表添加parent_id、description、sort_order字段
"""

from app import create_app
from database import db
from sqlalchemy import text

def migrate():
    """执行迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n" + "="*60)
            print("开始数据库迁移：添加分类层级字段")
            print("="*60 + "\n")
            
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('categories')]
            
            # 添加parent_id字段
            if 'parent_id' not in columns:
                print("➕ 添加字段: parent_id (INTEGER, nullable)")
                db.session.execute(text(
                    "ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id)"
                ))
                print("✅ parent_id 字段添加成功")
            else:
                print("⏭️  parent_id 字段已存在，跳过")
            
            # 添加description字段
            if 'description' not in columns:
                print("➕ 添加字段: description (VARCHAR(200), nullable)")
                db.session.execute(text(
                    "ALTER TABLE categories ADD COLUMN description VARCHAR(200)"
                ))
                print("✅ description 字段添加成功")
            else:
                print("⏭️  description 字段已存在，跳过")
            
            # 添加sort_order字段
            if 'sort_order' not in columns:
                print("➕ 添加字段: sort_order (INTEGER, default 0)")
                db.session.execute(text(
                    "ALTER TABLE categories ADD COLUMN sort_order INTEGER DEFAULT 0"
                ))
                print("✅ sort_order 字段添加成功")
            else:
                print("⏭️  sort_order 字段已存在，跳过")
            
            db.session.commit()
            
            # 删除旧的唯一约束
            print("\n更新唯一约束...")
            try:
                db.session.execute(text(
                    "DROP INDEX IF EXISTS unique_user_category"
                ))
                print("✅ 已删除旧的唯一约束")
            except Exception as e:
                print(f"⚠️  删除旧约束时出错（可能不存在）: {e}")
            
            # 创建新的唯一约束
            try:
                db.session.execute(text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS unique_user_parent_category "
                    "ON categories(user_id, COALESCE(parent_id, 0), name)"
                ))
                print("✅ 已创建新的唯一约束（同一用户下同一父级的分类名不能重复）")
            except Exception as e:
                print(f"⚠️  创建新约束时出错: {e}")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("✅ 数据库迁移完成！")
            print("="*60 + "\n")
            print("现在分类支持：")
            print("  • 最多3级层级结构")
            print("  • 分类描述字段")
            print("  • 自定义排序顺序")
            print("  • 同一父级下的分类名称唯一性校验")
            print()
            
        except Exception as e:
            print(f"\n❌ 迁移失败: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate()
