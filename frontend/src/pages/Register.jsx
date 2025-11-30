import React, { useState } from 'react'
import { Form, Input, Button, Card, message, Row, Col, Typography } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../services/auth'

const { Title, Text } = Typography

const Register = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const response = await register(values)
      if (response.code === 200) {
        message.success('注册成功，请登录')
        navigate('/login')
      }
    } catch (error) {
      console.error('注册失败:', error)
      // 处理注册错误
      if (error.response && error.response.data && error.response.data.message) {
        message.error(error.response.data.message)
      } else {
        message.error('注册失败，请重试')
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
          .register-card {
            animation: slideUp 0.6s ease-out;
          }
        `}
      </style>
      
      <Row justify="center" style={{ width: '100%', maxWidth: '450px', position: 'relative', zIndex: 1 }}>
        <Col span={24}>
          <Card 
            className="register-card"
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
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'rgba(255,255,255,0.2)',
                  borderRadius: '20px',
                  margin: '0 auto 16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '40px',
                  backdropFilter: 'blur(10px)'
                }}>
                  👤
                </div>
                <Title level={2} style={{ color: 'white', marginBottom: '8px', fontWeight: 'bold' }}>
                  用户注册
                </Title>
                <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: '15px' }}>
                  创建您的TimeValue账号
                </Text>
              </div>
            </div>
            
            <Form
              name="register"
              onFinish={onFinish}
              autoComplete="off"
              size="large"
            >
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: '请输入用户名!' },
                  { min: 3, max: 20, message: '用户名长度应在3-20个字符之间!' }
                ]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: '#667eea' }} />} 
                  placeholder="用户名（3-20个字符）"
                  style={{
                    borderRadius: '10px',
                    padding: '12px 15px',
                    fontSize: '15px'
                  }}
                />
              </Form.Item>

              <Form.Item
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱!' },
                  { type: 'email', message: '请输入正确的邮箱格式!' }
                ]}
              >
                <Input 
                  prefix={<MailOutlined style={{ color: '#667eea' }} />} 
                  placeholder="邮箱地址"
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
                  { required: true, message: '请输入密码!' },
                  { min: 6, message: '密码长度至少6位!' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#667eea' }} />}
                  placeholder="密码（至少6位）"
                  style={{
                    borderRadius: '10px',
                    padding: '12px 15px',
                    fontSize: '15px'
                  }}
                />
              </Form.Item>

              <Form.Item
                name="confirmPassword"
                dependencies={['password']}
                rules={[
                  { required: true, message: '请确认密码!' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve()
                      }
                      return Promise.reject(new Error('两次输入的密码不一致!'))
                    },
                  })
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#667eea' }} />}
                  placeholder="确认密码"
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
                  注册
                </Button>
              </Form.Item>
            </Form>
            
            <div style={{ textAlign: 'center', marginTop: '24px' }}>
              <Text type="secondary" style={{ fontSize: '14px' }}>
                已有账号？ 
                <Link 
                  to="/login" 
                  style={{ 
                    color: '#667eea', 
                    fontWeight: 'bold',
                    marginLeft: '4px'
                  }}
                >
                  立即登录
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

export default Register