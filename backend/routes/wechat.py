"""
微信公众号相关接口
包括：微信登录、JSSDK配置、扫码登录等
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import requests
import time
import hashlib
import random
import string
import os
from datetime import datetime, timedelta
from database import db
from models.user import User
from utils.response import APIResponse

wechat_bp = Blueprint('wechat', __name__)

# 微信公众号配置（从环境变量获取）
WECHAT_APPID = os.getenv('WECHAT_APPID', '')
WECHAT_SECRET = os.getenv('WECHAT_SECRET', '')
WECHAT_TOKEN = os.getenv('WECHAT_TOKEN', '')  # 用于验证服务器配置

# 微信API地址
WECHAT_API_BASE = 'https://api.weixin.qq.com'
WECHAT_ACCESS_TOKEN_URL = f'{WECHAT_API_BASE}/cgi-bin/token'
WECHAT_OAUTH_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
WECHAT_USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'
WECHAT_JSAPI_TICKET_URL = f'{WECHAT_API_BASE}/cgi-bin/ticket/getticket'

# 扫码登录状态存储（简单实现，生产环境应使用Redis）
qrcode_sessions = {}

def generate_random_string(length=16):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_access_token():
    """
    获取微信access_token（普通接口调用凭证）
    注意：这个token应该缓存2小时，避免频繁请求
    """
    try:
        response = requests.get(WECHAT_ACCESS_TOKEN_URL, params={
            'grant_type': 'client_credential',
            'appid': WECHAT_APPID,
            'secret': WECHAT_SECRET
        }, timeout=10)
        
        data = response.json()
        if 'access_token' in data:
            return data['access_token']
        else:
            print(f"获取access_token失败: {data}")
            return None
    except Exception as e:
        print(f"获取access_token异常: {e}")
        return None


def get_jsapi_ticket(access_token):
    """
    获取jsapi_ticket（用于JS-SDK签名）
    注意：这个ticket应该缓存2小时
    """
    try:
        response = requests.get(WECHAT_JSAPI_TICKET_URL, params={
            'access_token': access_token,
            'type': 'jsapi'
        }, timeout=10)
        
        data = response.json()
        if data.get('errcode') == 0:
            return data['ticket']
        else:
            print(f"获取jsapi_ticket失败: {data}")
            return None
    except Exception as e:
        print(f"获取jsapi_ticket异常: {e}")
        return None


@wechat_bp.route('/wechat/jssdk-config', methods=['GET'])
def get_jssdk_config():
    """
    获取微信JSSDK配置信息
    前端调用此接口获取签名配置，用于初始化wx.config()
    """
    try:
        # 获取前端传来的URL（必须是当前页面URL，不含#及后面部分）
        url = request.args.get('url')
        if not url:
            return APIResponse.error('缺少url参数')
        
        # 1. 获取access_token（生产环境应该缓存）
        access_token = get_access_token()
        if not access_token:
            return APIResponse.error('获取access_token失败')
        
        # 2. 获取jsapi_ticket（生产环境应该缓存）
        jsapi_ticket = get_jsapi_ticket(access_token)
        if not jsapi_ticket:
            return APIResponse.error('获取jsapi_ticket失败')
        
        # 3. 生成签名
        timestamp = int(time.time())
        noncestr = generate_random_string()
        
        # 签名算法：按字典序排列参数，拼接后SHA1加密
        sign_string = f'jsapi_ticket={jsapi_ticket}&noncestr={noncestr}&timestamp={timestamp}&url={url}'
        signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
        
        return APIResponse.success({
            'appId': WECHAT_APPID,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        })
        
    except Exception as e:
        print(f"生成JSSDK配置失败: {e}")
        import traceback
        traceback.print_exc()
        return APIResponse.error(f'生成配置失败: {str(e)}')


@wechat_bp.route('/wechat/login', methods=['POST'])
def wechat_login():
    """
    微信登录接口
    前端通过微信授权获取code后，调用此接口换取token和用户信息
    """
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state', '')
        
        if not code:
            return APIResponse.error('缺少code参数')
        
        # 1. 用code换取网页授权access_token和openid
        print(f"[微信登录] 开始处理，code: {code}")
        
        oauth_response = requests.get(WECHAT_OAUTH_URL, params={
            'appid': WECHAT_APPID,
            'secret': WECHAT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }, timeout=10)
        
        oauth_data = oauth_response.json()
        print(f"[微信登录] OAuth响应: {oauth_data}")
        
        if 'errcode' in oauth_data:
            return APIResponse.error(f"微信授权失败: {oauth_data.get('errmsg', '未知错误')}")
        
        openid = oauth_data.get('openid')
        access_token = oauth_data.get('access_token')
        
        if not openid:
            return APIResponse.error('未获取到openid')
        
        # 2. 获取微信用户信息
        user_info_response = requests.get(WECHAT_USER_INFO_URL, params={
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }, timeout=10)
        
        user_info = user_info_response.json()
        print(f"[微信登录] 用户信息: {user_info}")
        
        if 'errcode' in user_info:
            return APIResponse.error(f"获取用户信息失败: {user_info.get('errmsg', '未知错误')}")
        
        nickname = user_info.get('nickname', '')
        headimgurl = user_info.get('headimgurl', '')
        sex = user_info.get('sex', 0)  # 1男2女0未知
        
        # 3. 查询或创建用户
        user = User.query.filter_by(wechat_openid=openid).first()
        
        if not user:
            # 创建新用户
            # 使用openid生成唯一用户名
            username = f"wx_{openid[:8]}"
            
            # 确保用户名唯一
            count = 1
            while User.query.filter_by(username=username).first():
                username = f"wx_{openid[:8]}_{count}"
                count += 1
            
            user = User(
                username=username,
                email=f"{openid}@wechat.user",  # 占位邮箱
                password='',  # 微信用户不需要密码
                wechat_openid=openid,
                wechat_nickname=nickname,
                wechat_avatar=headimgurl
            )
            user.role = 'user'  # 默认角色
            
            db.session.add(user)
            db.session.commit()
            
            print(f"[微信登录] 创建新用户: {username}")
            
            # 为新用户初始化默认分类
            from services.category_service import initialize_user_categories
            initialize_user_categories(user.id, skip_if_exists=False)
        else:
            # 更新现有用户的微信信息
            user.wechat_nickname = nickname
            user.wechat_avatar = headimgurl
            db.session.commit()
            print(f"[微信登录] 用户登录: {user.username}")
        
        # 4. 生成JWT token
        token = create_access_token(identity=str(user.id))
        
        # 5. 返回token和用户信息
        return APIResponse.success({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'wechat_nickname': user.wechat_nickname,
                'wechat_avatar': user.wechat_avatar
            }
        })
        
    except requests.RequestException as e:
        print(f"[微信登录] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return APIResponse.error('网络请求失败，请稍后重试')
    except Exception as e:
        print(f"[微信登录] 异常: {e}")
        import traceback
        traceback.print_exc()
        return APIResponse.error(f'登录失败: {str(e)}')


@wechat_bp.route('/wechat/verify', methods=['GET', 'POST'])
def wechat_verify():
    """
    微信服务器验证接口
    用于在微信公众号后台配置服务器地址时的验证
    """
    if request.method == 'GET':
        # 验证服务器配置
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        
        # 验证签名
        tmp_list = [WECHAT_TOKEN, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        tmp_signature = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        
        if tmp_signature == signature:
            return echostr
        else:
            return 'Invalid signature', 403
    else:
        # 接收微信服务器推送的消息（后续可扩展）
        return 'success'


@wechat_bp.route('/wechat/qrcode-status', methods=['GET'])
def get_qrcode_status():
    """
    查询扫码登录状态
    用于前端轮询检查用户是否已扫码登录
    """
    try:
        ticket = request.args.get('ticket')
        if not ticket:
            return APIResponse.error('缺少ticket参数', 400)
        
        # 检查扫码状态
        session = qrcode_sessions.get(ticket)
        if not session:
            return APIResponse.error('二维码不存在或已过期', 404)
        
        # 检查是否过期（5分钟）
        if datetime.now() > session['expire_time']:
            del qrcode_sessions[ticket]
            return APIResponse.error('二维码已过期', 410)
        
        # 返回状态
        return APIResponse.success({
            'status': session['status'],
            'token': session.get('token'),
            'user': session.get('user')
        })
        
    except Exception as e:
        print(f'查询扫码状态失败: {str(e)}')
        return APIResponse.error(f'查询失败: {str(e)}', 500)


@wechat_bp.route('/wechat/qrcode-confirm', methods=['POST'])
def confirm_qrcode():
    """
    确认扫码登录
    微信扫码后调用，通知后端扫码成功
    """
    try:
        ticket = request.args.get('ticket')
        token = request.args.get('token')
        
        if not ticket or not token:
            return APIResponse.error('缺少参数', 400)
        
        # 获取用户信息
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        user_id = decoded['sub']
        user = User.query.get(user_id)
        
        if not user:
            return APIResponse.error('用户不存在', 404)
        
        # 更新扫码状态
        if ticket in qrcode_sessions:
            qrcode_sessions[ticket]['status'] = 'scanned'
            qrcode_sessions[ticket]['token'] = token
            qrcode_sessions[ticket]['user'] = {
                'id': user.id,
                'username': user.username,
                'wechat_nickname': user.wechat_nickname,
                'wechat_avatar': user.wechat_avatar
            }
        
        return APIResponse.success({'message': '扫码成功'})
        
    except Exception as e:
        print(f'确认扫码失败: {str(e)}')
        return APIResponse.error(f'确认失败: {str(e)}', 500)
