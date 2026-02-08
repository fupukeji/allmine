from flask import Blueprint, jsonify
from database import db
from datetime import datetime
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    用于Docker健康检查和负载均衡器探测
    """
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'timevalue-backend',
        'version': '1.0.0',
        'checks': {}
    }
    
    # 检查数据库连接
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['checks']['database'] = {
            'status': 'up',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'down',
            'message': f'Database connection failed: {str(e)}'
        }
    
    # 检查环境变量
    required_env_vars = ['DB_HOST', 'DB_NAME', 'SECRET_KEY']
    env_check = all(os.getenv(var) for var in required_env_vars)
    health_status['checks']['environment'] = {
        'status': 'up' if env_check else 'down',
        'message': 'Required environment variables present' if env_check else 'Missing required environment variables'
    }
    
    # 返回状态码
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return jsonify(health_status), status_code

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    就绪检查端点
    检查服务是否准备好接收流量
    """
    try:
        # 检查数据库连接
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@health_bp.route('/health/debug', methods=['GET'])
def health_debug():
    """临时调试端点 - 查看数据库连接信息"""
    info = {}
    try:
        result = db.session.execute(db.text('SELECT DATABASE()'))
        info['current_database'] = result.scalar()
        
        result = db.session.execute(db.text('SELECT COUNT(*) FROM users'))
        info['user_count'] = result.scalar()
        
        result = db.session.execute(db.text('SELECT id, username, email, role FROM users'))
        info['users'] = [{'id': r[0], 'username': r[1], 'email': r[2], 'role': r[3]} for r in result]
        
        info['env_db_host'] = os.getenv('DB_HOST', 'NOT SET')
        info['env_db_name'] = os.getenv('DB_NAME', 'NOT SET')
        info['env_mysql_address'] = os.getenv('MYSQL_ADDRESS', 'NOT SET')
    except Exception as e:
        info['error'] = str(e)
    
    return jsonify(info), 200

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    存活检查端点
    检查服务进程是否存活
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
