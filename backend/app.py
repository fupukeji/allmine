from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从独立模块导入数据库实例
from database import db
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # 启用调试模式和详细错误日志
    app.config['DEBUG'] = True
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///timevalue.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Token不过期，生产环境需要调整
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # 在初始化扩展后立即导入所有模型
    from models.user import User
    from models.category import Category  
    from models.project import Project
    from models.fixed_asset import FixedAsset
    from models.asset_income import AssetIncome
    from models.asset_maintenance import AssetMaintenance, MaintenanceReminder
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.categories import categories_bp
    from routes.projects import projects_bp
    from routes.analytics import analytics_bp
    from routes.admin import admin_bp
    from routes.assets import assets_bp
    from routes.asset_income import asset_income_bp
    from routes.maintenance import maintenance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(assets_bp, url_prefix='/api')
    app.register_blueprint(asset_income_bp, url_prefix='/api')
    app.register_blueprint(maintenance_bp, url_prefix='/api')
    
    # 创建数据表
    with app.app_context():
        print("Debug: Creating database tables...")
        try:
            # 先删除所有表，然后重新创建（开发环境）
            db.drop_all()
            db.create_all()
            print("Debug: Tables created successfully")
            
            # 创建默认管理员用户
            admin = User(
                username='admin',
                email='admin@timevalue.com',
                password='admin123'  # 默认密码，首次登录需修改
            )
            admin.role = 'admin'  # 设置为管理员角色
            db.session.add(admin)
            db.session.commit()
            
            # 为admin用户创建默认分类
            from models.category import Category
            default_categories = [
                {'name': '运动健身', 'color': '#52c41a', 'icon': 'trophy'},
                {'name': '技术工具', 'color': '#1890ff', 'icon': 'code'},
                {'name': '生活服务', 'color': '#faad14', 'icon': 'home'},
                {'name': '娱乐休闲', 'color': '#eb2f96', 'icon': 'smile'},
                {'name': '固定资产', 'color': '#722ed1', 'icon': 'bank'}
            ]
            
            for cat_data in default_categories:
                category = Category(
                    name=cat_data['name'],
                    color=cat_data['color'],
                    icon=cat_data['icon'],
                    user_id=admin.id
                )
                db.session.add(category)
            
            db.session.commit()
            print("默认管理员用户已创建：admin/admin123")
            
        except Exception as e:
            print(f"Debug: Database initialization error: {e}")
            print("Attempting to create tables without dropping...")
            try:
                db.create_all()
                print("Tables created successfully on retry")
            except Exception as retry_error:
                print(f"Retry failed: {retry_error}")
    
    return app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 TimeValue 个人资产管理系统")
    print("💰 恒产生金 - 让每一份资产都创造价值")
    print("")
    print("🏢 Powered by 孚普科技（北京）有限公司")
    print("🤖 AI驱动的MVP快速迭代解决方案")
    print("🌐 https://fupukeji.com")
    print("📚 GitHub: https://github.com/fupukeji")
    print("="*60 + "\n")
    
    app = create_app()
    print("✅ 后端服务启动成功 - http://localhost:5000")
    print("📖 API文档: http://localhost:5000/api")
    print("⚠️  请确保前端服务也已启动")
    print("\n💡 提示: 使用 python start_timevalue.py 可一键启动完整系统\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)