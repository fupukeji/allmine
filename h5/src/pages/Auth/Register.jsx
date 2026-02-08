/**
 * 注册页面 - 晶莹剔透现代风格
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Form, Input, Button, Toast } from 'antd-mobile'
import { EyeInvisibleOutline, EyeOutline } from 'antd-mobile-icons'
import { register } from '../../services/auth'
import './Login.css'

export default function Register() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  
  const handleRegister = async (values) => {
    const { username, email, password, confirmPassword } = values
    
    // 验证
    if (!username || !email || !password) {
      Toast.show({ icon: 'fail', content: '请填写完整信息' })
      return
    }
    
    if (password !== confirmPassword) {
      Toast.show({ icon: 'fail', content: '两次密码输入不一致' })
      return
    }
    
    if (password.length < 6) {
      Toast.show({ icon: 'fail', content: '密码长度至少6位' })
      return
    }
    
    // 邮箱格式验证
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (!emailRegex.test(email)) {
      Toast.show({ icon: 'fail', content: '邮箱格式不正确' })
      return
    }
    
    setLoading(true)
    try {
      const res = await register(username, email, password)
      
      if (res.code === 200 || res.code === 201) {
        Toast.show({ icon: 'success', content: '注册成功，请登录' })
        navigate('/login', { replace: true })
      } else {
        Toast.show({ icon: 'fail', content: res.message || '注册失败' })
      }
    } catch (error) {
      console.error('注册错误:', error)
      Toast.show({ icon: 'fail', content: error.message || '注册失败' })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="login-page register-page">
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
          <h1 className="app-name">创建账号</h1>
          <p className="app-slogan">加入 TimeValue，开启智能资产管理</p>
        </div>
        
        {/* 注册表单 */}
        <div className="login-form-card glass-card">
          <Form
            layout="vertical"
            onFinish={handleRegister}
            footer={
              <Button
                block
                type="submit"
                color="primary"
                size="large"
                loading={loading}
                className="login-btn"
              >
                注册
              </Button>
            }
          >
            <Form.Item
              name="username"
              label="用户名"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input
                placeholder="3-20个字符"
                clearable
                autoComplete="username"
              />
            </Form.Item>
            
            <Form.Item
              name="email"
              label="邮箱"
              rules={[{ required: true, message: '请输入邮箱' }]}
            >
              <Input
                placeholder="用于找回密码"
                clearable
                type="email"
                autoComplete="email"
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
                placeholder="至少6位字符"
                autoComplete="new-password"
              />
            </Form.Item>
            
            <Form.Item
              name="confirmPassword"
              label="确认密码"
              rules={[{ required: true, message: '请再次输入密码' }]}
              extra={
                <div className="password-toggle" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                  {showConfirmPassword ? <EyeOutline /> : <EyeInvisibleOutline />}
                </div>
              }
            >
              <Input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="再次输入密码"
                autoComplete="new-password"
              />
            </Form.Item>
          </Form>
          
          {/* 登录入口 */}
          <div className="login-link">
            已有账号？<Link to="/login">立即登录</Link>
          </div>
        </div>
        
        {/* 注册须知 */}
        <div className="wechat-tip" style={{ marginTop: '24px' }}>
          注册即表示您同意我们的服务条款和隐私政策
        </div>
        
        {/* 版权信息 */}
        <div className="login-footer">
          <p>© 2024 孚普科技（北京）有限公司</p>
        </div>
      </div>
    </div>
  )
}
