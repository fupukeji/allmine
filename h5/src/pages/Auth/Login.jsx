/**
 * 登录页面 - 晶莹剔透现代风格
 * 支持账号密码登录和微信登录
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Form, Input, Button, Toast } from 'antd-mobile'
import { EyeInvisibleOutline, EyeOutline } from 'antd-mobile-icons'
import { login } from '../../services/auth'
import wechatSDK from '../../utils/wechat'
import './Login.css'

export default function Login() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  
  const handleLogin = async (values) => {
    const { username, password } = values
    
    if (!username || !password) {
      Toast.show({ icon: 'fail', content: '请输入用户名和密码' })
      return
    }
    
    setLoading(true)
    try {
      const res = await login(username, password)
      
      if (res.code === 200 && res.data.token) {
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('userInfo', JSON.stringify(res.data.user))
        
        Toast.show({ icon: 'success', content: '登录成功' })
        
        // 刷新页面以更新App组件状态
        setTimeout(() => {
          window.location.href = '/'
        }, 500)
      } else {
        Toast.show({ icon: 'fail', content: res.message || '登录失败' })
      }
    } catch (error) {
      console.error('登录错误:', error)
      Toast.show({ icon: 'fail', content: error.message || '登录失败' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleWeChatLogin = () => {
    try {
      Toast.show({
        icon: 'loading',
        content: '正在跳转微信授权...',
        duration: 0
      })
      
      const appId = import.meta.env.VITE_WECHAT_APPID
      const redirectUri = encodeURIComponent(window.location.origin + '/wechat-callback')
      const state = Math.random().toString(36).substring(7)
      
      const authUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo&state=${state}#wechat_redirect`
      
      window.location.href = authUrl
    } catch (error) {
      Toast.show({ icon: 'fail', content: '微信登录失败' })
    }
  }
  
  return (
    <div className="login-page">
      {/* 背景装饰 */}
      <div className="login-bg">
        <div className="bg-circle circle-1"></div>
        <div className="bg-circle circle-2"></div>
        <div className="bg-circle circle-3"></div>
      </div>
      
      <div className="login-container">
        {/* Logo区域 */}
        <div className="login-header">
          <div className="logo-wrapper">
            <img src="/logo.jpg" alt="TimeValue" className="logo-img" />
          </div>
          <h1 className="app-name">TimeValue</h1>
          <p className="app-slogan">智能资产管理，让财富可视化</p>
        </div>
        
        {/* 登录表单 */}
        <div className="login-form-card glass-card">
          <Form
            layout="vertical"
            onFinish={handleLogin}
            footer={
              <Button
                block
                type="submit"
                color="primary"
                size="large"
                loading={loading}
                className="login-btn"
              >
                登录
              </Button>
            }
          >
            <Form.Item
              name="username"
              label="账号"
              rules={[{ required: true, message: '请输入用户名或邮箱' }]}
            >
              <Input
                placeholder="用户名或邮箱"
                clearable
                autoComplete="username"
              />
            </Form.Item>
            
            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }]}
              extra={
                <div className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOutline /> : <EyeInvisibleOutline />}
                </div>
              }
            >
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="请输入密码"
                autoComplete="current-password"
              />
            </Form.Item>
          </Form>
          
          {/* 注册入口 */}
          <div className="register-link">
            还没有账号？<Link to="/register">立即注册</Link>
          </div>
        </div>
        
        {/* 分隔线 */}
        <div className="login-divider">
          <span>其他登录方式</span>
        </div>
        
        {/* 微信登录 */}
        {wechatSDK.isWeChatBrowser && (
          <Button
            block
            color="success"
            size="large"
            className="wechat-btn"
            onClick={handleWeChatLogin}
          >
            <span className="wechat-icon">💬</span>
            微信快捷登录
          </Button>
        )}
        
        {!wechatSDK.isWeChatBrowser && (
          <div className="wechat-tip">
            在微信中打开可使用微信快捷登录
          </div>
        )}
        
        {/* 版权信息 */}
        <div className="login-footer">
          <p>© 2024 孚普科技（北京）有限公司</p>
        </div>
      </div>
    </div>
  )
}
