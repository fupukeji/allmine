import React, { useState } from 'react'
import { Form, Input, Button, Card, message, Row, Col, Typography } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../services/auth'

const { Title, Text } = Typography

const Login = ({ onLogin }) => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const response = await login(values)
      if (response.code === 200) {
        message.success('登录成功')
        // 传递用户信息给父组件
        onLogin(response.data.user)
        navigate('/')
      }
    } catch (error) {
      console.error('登录失败:', error)
      // 处理登录错误
      if (error.response && error.response.data && error.response.data.message) {
        message.error(error.response.data.message)
      } else {
        message.error('登录失败，请检查用户名和密码')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* 顶部装饰横幅 */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '6px',
        background: 'linear-gradient(90deg, #ffd700 0%, #ffed4e 25%, #00f2fe 50%, #764ba2 75%, #ffd700 100%)',
        backgroundSize: '200% 100%',
        animation: 'gradientFlow 3s ease infinite'
      }} />
      
      <style>
        {`
          @keyframes gradientFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
        `}
      </style>
      {/* 背景装饰圆圈 */}
      <div style={{
        position: 'absolute',
        top: '-100px',
        right: '-100px',
        width: '400px',
        height: '400px',
        borderRadius: '50%',
        background: 'rgba(255,255,255,0.1)',
        animation: 'float 6s ease-in-out infinite'
      }} />
      <div style={{
        position: 'absolute',
        bottom: '-150px',
        left: '-150px',
        width: '500px',
        height: '500px',
        borderRadius: '50%',
        background: 'rgba(255,255,255,0.08)',
        animation: 'float 8s ease-in-out infinite reverse'
      }} />
      
      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(20px); }
          }
          @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .login-card {
            animation: slideUp 0.6s ease-out;
          }
        `}
      </style>
      
      <Row justify="center" style={{ width: '100%', maxWidth: '450px', position: 'relative', zIndex: 1 }}>
        <Col span={24}>
          <Card 
            className="login-card"
            style={{ 
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
              borderRadius: '20px',
              border: 'none',
              overflow: 'hidden'
            }}
          >
            {/* 头部装饰 */}
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              margin: '-24px -24px 24px -24px',
              padding: '40px 24px',
              textAlign: 'center',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{
                position: 'absolute',
                top: '-50px',
                right: '-50px',
                width: '150px',
                height: '150px',
                borderRadius: '50%',
                background: 'rgba(255,255,255,0.1)'
              }} />
              <div style={{ position: 'relative', zIndex: 1 }}>
                <img 
                  src="/logo.jpg" 
                  alt="TimeValue Logo" 
                  style={{
                    width: '100px',
                    height: '100px',
                    borderRadius: '24px',
                    margin: '0 auto 20px',
                    display: 'block',
                    backdropFilter: 'blur(10px)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                    border: '3px solid rgba(255,255,255,0.3)',
                    objectFit: 'cover'
                  }}
                />
                <Title level={2} style={{ color: 'white', marginBottom: '8px', fontWeight: 'bold', textAlign: 'center' }}>
                  TimeValue
                </Title>
                <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: '16px', display: 'block', textAlign: 'center' }}>
                  恒产生金 · 资产管理系统
                </Text>
              </div>
            </div>
            
            <Form
              name="login"
              onFinish={onFinish}
              autoComplete="off"
              size="large"
            >
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: '请输入用户名或邮箱!' }
                ]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: '#667eea' }} />} 
                  placeholder="用户名或邮箱"
                  style={{
                    borderRadius: '10px',
                    padding: '12px 15px',
                    fontSize: '15px'
                  }}
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[
                  { required: true, message: '请输入密码!' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#667eea' }} />}
                  placeholder="密码"
                  style={{
                    borderRadius: '10px',
                    padding: '12px 15px',
                    fontSize: '15px'
                  }}
                />
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  style={{ 
                    width: '100%',
                    height: '50px',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)'
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)'
                  }}
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
            
            <div style={{ textAlign: 'center', marginTop: '24px' }}>
              <Text type="secondary" style={{ fontSize: '14px' }}>
                还没有账号？ 
                <Link 
                  to="/register" 
                  style={{ 
                    color: '#667eea', 
                    fontWeight: 'bold',
                    marginLeft: '4px'
                  }}
                >
                  立即注册
                </Link>
              </Text>
            </div>
            
            <div style={{ 
              marginTop: '24px', 
              padding: '16px', 
              background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <Text style={{ fontSize: '12px', color: '#666', display: 'block', marginBottom: '4px' }}>
                🚀 Powered by 孚普科技（北京）有限公司
              </Text>
              <Text style={{ fontSize: '11px', color: '#999' }}>
                AI驱动的MVP快速迭代解决方案
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Login