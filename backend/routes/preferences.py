"""
用户偏好设置API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.user import User

preferences_bp = Blueprint('preferences', __name__)

# 可选的AI模型列表
AI_MODELS = [
    {'value': 'glm-4-flash', 'label': 'GLM-4 Flash', 'description': '快速响应，适合日常使用'},
    {'value': 'glm-4', 'label': 'GLM-4', 'description': '高质量输出，适合复杂分析'},
    {'value': 'glm-4-plus', 'label': 'GLM-4 Plus', 'description': '最强性能，适合专业场景'},
    {'value': 'glm-4-0520', 'label': 'GLM-4-0520', 'description': '稳定版本'},
]

# 主题选项
THEMES = [
    {'value': 'light', 'label': '浅色模式', 'icon': '☀️'},
    {'value': 'dark', 'label': '深色模式', 'icon': '🌙'},
    {'value': 'auto', 'label': '跟随系统', 'icon': '🔄'},
]

# 语言选项
LANGUAGES = [
    {'value': 'zh-CN', 'label': '简体中文'},
    {'value': 'zh-TW', 'label': '繁體中文'},
    {'value': 'en-US', 'label': 'English'},
]


@preferences_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """获取用户偏好设置"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        # 检查是否配置了自定义API Key
        has_custom_api_key = bool(user.get_ai_api_key())
        
        return jsonify({
            'code': 200,
            'data': {
                'ai_settings': {
                    'model': user.zhipu_model or 'glm-4-flash',
                    'has_custom_api_key': has_custom_api_key,
                    'available_models': AI_MODELS,
                },
                'appearance': {
                    'theme': user.theme or 'light',
                    'language': user.language or 'zh-CN',
                    'available_themes': THEMES,
                    'available_languages': LANGUAGES,
                },
                'profile': {
                    'timezone': user.timezone or 'Asia/Shanghai',
                }
            }
        })
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取偏好设置失败: {str(e)}'}), 500


@preferences_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """更新用户偏好设置"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        # AI设置
        ai_settings = data.get('ai_settings', {})
        if 'model' in ai_settings:
            # 验证模型是否有效
            valid_models = [m['value'] for m in AI_MODELS]
            if ai_settings['model'] in valid_models:
                user.zhipu_model = ai_settings['model']
        
        if 'api_key' in ai_settings:
            # 更新自定义API Key
            user.set_ai_api_key(ai_settings['api_key'] if ai_settings['api_key'] else None)
        
        # 外观设置
        appearance = data.get('appearance', {})
        if 'theme' in appearance:
            user.theme = appearance['theme']
        if 'language' in appearance:
            user.language = appearance['language']
        
        # 其他设置
        profile = data.get('profile', {})
        if 'timezone' in profile:
            user.timezone = profile['timezone']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '偏好设置已更新'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新偏好设置失败: {str(e)}'}), 500


@preferences_bp.route('/preferences/ai-model', methods=['PUT'])
@jwt_required()
def update_ai_model():
    """快捷更新AI模型"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        model = data.get('model')
        
        valid_models = [m['value'] for m in AI_MODELS]
        if model not in valid_models:
            return jsonify({'code': 400, 'message': '无效的模型选择'}), 400
        
        user.zhipu_model = model
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '模型已更新',
            'data': {'model': model}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@preferences_bp.route('/preferences/api-key', methods=['PUT'])
@jwt_required()
def update_api_key():
    """更新自定义API Key"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if api_key:
            user.set_ai_api_key(api_key)
            message = 'API Key 已配置'
        else:
            user.set_ai_api_key(None)
            message = 'API Key 已清除，将使用系统默认'
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': message,
            'data': {'has_custom_api_key': bool(api_key)}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@preferences_bp.route('/preferences/api-key/test', methods=['POST'])
@jwt_required()
def test_api_key():
    """测试API Key是否有效"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            # 使用已保存的key
            api_key = user.get_ai_api_key()
        
        if not api_key:
            return jsonify({'code': 400, 'message': '未配置 API Key'}), 400
        
        # 尝试调用智谱AI进行测试
        import requests
        try:
            resp = requests.post(
                'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': user.zhipu_model or 'glm-4-flash',
                    'messages': [{'role': 'user', 'content': 'Hi'}],
                    'max_tokens': 10
                },
                timeout=10
            )
            
            if resp.status_code == 200:
                return jsonify({'code': 200, 'message': 'API Key 验证成功'})
            else:
                return jsonify({'code': 400, 'message': f'验证失败: {resp.json().get("error", {}).get("message", "未知错误")}'})
                
        except requests.exceptions.Timeout:
            return jsonify({'code': 400, 'message': '请求超时，请稍后重试'})
        except Exception as e:
            return jsonify({'code': 400, 'message': f'验证失败: {str(e)}'})
        
    except Exception as e:
        return jsonify({'code': 500, 'message': f'测试失败: {str(e)}'}), 500
