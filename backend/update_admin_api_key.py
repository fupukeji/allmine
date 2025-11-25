"""
更新管理员用户的智谱AI API Key
"""

from app import create_app
from database import db
from models.user import User

def update_api_key():
    app = create_app()
    
    with app.app_context():
        # 查找管理员用户
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("未找到管理员用户")
            return
        
        # 设置API Key
        api_key = "14151791ef28494ab6b30f0964675334.ttwJa0Wtep6Q1Hx7"
        admin.set_ai_api_key(api_key)
        admin.zhipu_model = "glm-4-flash"
        
        db.session.commit()
        
        print(f"成功更新管理员用户的API配置")
        print(f"  - 用户名: {admin.username}")
        print(f"  - 模型: {admin.zhipu_model}")
        print(f"  - API Key (前4后4): {api_key[:4]}...{api_key[-4:]}")
        
        # 验证
        decrypted = admin.get_ai_api_key()
        if decrypted == api_key:
            print(f"  - 验证: 通过")
        else:
            print(f"  - 验证: 失败")

if __name__ == '__main__':
    update_api_key()
