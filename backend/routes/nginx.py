from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.nginx_config import NginxConfig
from models.user import User
from database import db
from datetime import datetime
import os
import subprocess

nginx_bp = Blueprint('nginx', __name__)

def get_current_user():
    """获取当前用户"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def is_admin(user):
    """检查是否为管理员"""
    return user and user.is_admin

def reload_nginx():
    """重载Nginx配置"""
    try:
        # 测试配置是否有效（使用sudo）
        test_result = subprocess.run(
            ['sudo', 'nginx', '-t'],
            capture_output=True,
            text=True
        )
        
        if test_result.returncode != 0:
            return False, f"配置测试失败: {test_result.stderr}"
        
        # 重载Nginx（使用sudo）
        reload_result = subprocess.run(
            ['sudo', 'nginx', '-s', 'reload'],
            capture_output=True,
            text=True
        )
        
        if reload_result.returncode != 0:
            return False, f"重载失败: {reload_result.stderr}"
        
        return True, "Nginx配置已成功重载"
    except FileNotFoundError:
        return False, "Nginx未安装或不在系统PATH中"
    except Exception as e:
        return False, f"重载失败: {str(e)}"

@nginx_bp.route('/nginx/configs', methods=['GET'])
@jwt_required()
def get_nginx_configs():
    """获取所有Nginx配置"""
    try:
        current_user = get_current_user()
        
        if is_admin(current_user):
            # 管理员可以查看所有配置
            configs = NginxConfig.query.all()
        else:
            # 普通用户只能查看自己的配置
            configs = NginxConfig.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/configs', methods=['POST'])
@jwt_required()
def create_nginx_config():
    """创建Nginx配置"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # 创建配置
        config = NginxConfig(
            user_id=current_user.id,
            server_name=data.get('server_name', '_'),
            listen_port=data.get('listen_port', 80),
            ssl_enabled=data.get('ssl_enabled', False),
            ssl_port=data.get('ssl_port', 443),
            ssl_certificate=data.get('ssl_certificate'),
            ssl_certificate_key=data.get('ssl_certificate_key'),
            force_https=data.get('force_https', False),
            frontend_proxy_enabled=data.get('frontend_proxy_enabled', True),
            frontend_port=data.get('frontend_port', 3000),
            backend_port=data.get('backend_port', 5000),
            client_max_body_size=data.get('client_max_body_size', '20M'),
            gzip_enabled=data.get('gzip_enabled', True),
            access_log_enabled=data.get('access_log_enabled', True),
            custom_config=data.get('custom_config')
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置创建成功',
            'data': config.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/configs/<int:config_id>', methods=['GET'])
@jwt_required()
def get_nginx_config(config_id):
    """获取单个Nginx配置"""
    try:
        current_user = get_current_user()
        config = NginxConfig.query.get(config_id)
        
        if not config:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
        
        # 权限检查
        if not is_admin(current_user) and config.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': '无权访问此配置'
            }), 403
        
        return jsonify({
            'success': True,
            'data': config.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/configs/<int:config_id>', methods=['PUT'])
@jwt_required()
def update_nginx_config(config_id):
    """更新Nginx配置"""
    try:
        current_user = get_current_user()
        config = NginxConfig.query.get(config_id)
        
        if not config:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
        
        # 权限检查
        if not is_admin(current_user) and config.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': '无权修改此配置'
            }), 403
        
        data = request.get_json()
        
        # 更新字段
        config.server_name = data.get('server_name', config.server_name)
        config.listen_port = data.get('listen_port', config.listen_port)
        config.ssl_enabled = data.get('ssl_enabled', config.ssl_enabled)
        config.ssl_port = data.get('ssl_port', config.ssl_port)
        config.ssl_certificate = data.get('ssl_certificate', config.ssl_certificate)
        config.ssl_certificate_key = data.get('ssl_certificate_key', config.ssl_certificate_key)
        config.force_https = data.get('force_https', config.force_https)
        config.frontend_proxy_enabled = data.get('frontend_proxy_enabled', config.frontend_proxy_enabled)
        config.frontend_port = data.get('frontend_port', config.frontend_port)
        config.backend_port = data.get('backend_port', config.backend_port)
        config.client_max_body_size = data.get('client_max_body_size', config.client_max_body_size)
        config.gzip_enabled = data.get('gzip_enabled', config.gzip_enabled)
        config.access_log_enabled = data.get('access_log_enabled', config.access_log_enabled)
        config.custom_config = data.get('custom_config', config.custom_config)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置更新成功',
            'data': config.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/configs/<int:config_id>', methods=['DELETE'])
@jwt_required()
def delete_nginx_config(config_id):
    """删除Nginx配置"""
    try:
        current_user = get_current_user()
        config = NginxConfig.query.get(config_id)
        
        if not config:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
        
        # 权限检查
        if not is_admin(current_user) and config.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': '无权删除此配置'
            }), 403
        
        # 如果是激活的配置，不允许删除
        if config.is_active:
            return jsonify({
                'success': False,
                'message': '无法删除激活的配置，请先停用'
            }), 400
        
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置删除成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/configs/<int:config_id>/preview', methods=['GET'])
@jwt_required()
def preview_nginx_config(config_id):
    """预览Nginx配置"""
    try:
        current_user = get_current_user()
        config = NginxConfig.query.get(config_id)
        
        if not config:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
        
        # 权限检查
        if not is_admin(current_user) and config.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': '无权预览此配置'
            }), 403
        
        # 生成配置内容
        config_content = config.generate_nginx_config()
        
        return jsonify({
            'success': True,
            'data': {
                'content': config_content
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'预览配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/configs/<int:config_id>/apply', methods=['POST'])
@jwt_required()
def apply_nginx_config(config_id):
    """应用Nginx配置"""
    try:
        current_user = get_current_user()
        
        # 只有管理员可以应用配置
        if not is_admin(current_user):
            return jsonify({
                'success': False,
                'message': '只有管理员可以应用配置'
            }), 403
        
        config = NginxConfig.query.get(config_id)
        
        if not config:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
        
        # 生成配置内容
        config_content = config.generate_nginx_config()
        
        # 确定Nginx配置文件路径
        nginx_config_path = '/etc/nginx/sites-available/timevalue.conf'
        nginx_enabled_path = '/etc/nginx/sites-enabled/timevalue.conf'
        
        # 检查配置目录是否存在
        config_dir = os.path.dirname(nginx_config_path)
        if not os.path.exists(config_dir):
            return jsonify({
                'success': False,
                'message': f'Nginx配置目录不存在: {config_dir}'
            }), 500
        
        # 写入配置文件
        try:
            with open(nginx_config_path, 'w') as f:
                f.write(config_content)
            
            # 创建软链接（如果不存在）
            if not os.path.exists(nginx_enabled_path):
                os.symlink(nginx_config_path, nginx_enabled_path)
        except PermissionError:
            return jsonify({
                'success': False,
                'message': '没有权限写入Nginx配置文件，请确保应用以适当的权限运行'
            }), 500
        
        # 重载Nginx
        success, message = reload_nginx()
        
        if success:
            # 停用其他配置
            NginxConfig.query.update({'is_active': False})
            
            # 激活当前配置
            config.is_active = True
            config.last_applied = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'应用配置失败: {str(e)}'
        }), 500

@nginx_bp.route('/nginx/status', methods=['GET'])
@jwt_required()
def nginx_status():
    """获取Nginx状态"""
    try:
        # 检查Nginx是否运行（使用sudo）
        result = subprocess.run(
            ['sudo', 'systemctl', 'is-active', 'nginx'],
            capture_output=True,
            text=True
        )
        
        is_running = result.returncode == 0 and result.stdout.strip() == 'active'
        
        # 获取激活的配置
        active_config = NginxConfig.query.filter_by(is_active=True).first()
        
        return jsonify({
            'success': True,
            'data': {
                'is_running': is_running,
                'active_config': active_config.to_dict() if active_config else None
            }
        }), 200
    except FileNotFoundError:
        return jsonify({
            'success': True,
            'data': {
                'is_running': False,
                'active_config': None,
                'message': 'systemctl命令不可用'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取状态失败: {str(e)}'
        }), 500
