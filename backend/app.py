from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

from database import db
from config.database import DatabaseConfig, DatabaseSettings
from utils.response import APIResponse

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    app.config['DEBUG'] = True
    
    # 配置秘钥
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    
    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.get_database_uri_from_env()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = DatabaseSettings.get_engine_options()
    
    db.init_app(app)
    jwt.init_app(app)
    
    # CORS配置 - 允许所有来源访问
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 在初始化扩展后立即导入所有模型
    from models.user import User
    from models.category import Category  
    from models.project import Project
    from models.fixed_asset import FixedAsset
    from models.asset_income import AssetIncome
    from models.asset_maintenance import AssetMaintenance, MaintenanceReminder
    from models.nginx_config import NginxConfig
    from models.ai_report import AIReport
    from models.asset_expense import AssetExpense
    from models.notification_settings import UserNotificationSettings
    
    # 注册蓝图
    from routes.auth import auth_bp
    from routes.categories import categories_bp
    from routes.projects import projects_bp
    from routes.analytics import analytics_bp
    from routes.admin import admin_bp
    from routes.assets import assets_bp
    from routes.asset_income import asset_income_bp
    from routes.maintenance import maintenance_bp
    from routes.nginx import nginx_bp
    from routes.reports import reports_bp
    from routes.health import health_bp  # 健康检查
    from routes.wechat import wechat_bp  # 微信相关
    from routes.expenses import expenses_bp  # 资产费用
    from routes.notifications import notifications_bp  # 通知设置
    from routes.preferences import preferences_bp  # 偏好设置
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(assets_bp, url_prefix='/api')
    app.register_blueprint(asset_income_bp, url_prefix='/api')
    app.register_blueprint(maintenance_bp, url_prefix='/api')
    app.register_blueprint(nginx_bp, url_prefix='/api')
    app.register_blueprint(reports_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')  # 健康检查
    app.register_blueprint(wechat_bp, url_prefix='/api')  # 微信相关
    app.register_blueprint(expenses_bp, url_prefix='/api')  # 资产费用
    app.register_blueprint(notifications_bp, url_prefix='/api')  # 通知设置
    app.register_blueprint(preferences_bp, url_prefix='/api')  # 偏好设置
    
    # 创建数据表
    with app.app_context():
        print("正在初始化数据库...")
        try:
            db.create_all()
            print("数据表创建成功")
            
            # 检查管理员用户
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@timevalue.com',
                    password='admin123'
                )
                admin.role = 'admin'
                db.session.add(admin)
                db.session.commit()
                
                # 初始化默认分类
                from services.category_service import initialize_user_categories
                initialize_user_categories(admin.id, skip_if_exists=False)
                
                print("默认管理员已创建: admin/admin123")
            else:
                print("管理员用户已存在")
            
        except Exception as e:
            print(f"数据库初始化错误: {e}")
            import traceback
            traceback.print_exc()
    
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