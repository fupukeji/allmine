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
      padding: '20px'
    }}>
      <Row justify="center" style={{ width: '100%', maxWidth: '400px' }}>
        <Col span={24}>
          <Card style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
                用户注册
              </Title>
              <Text type="secondary">创建您的账号</Text>
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
                  prefix={<UserOutlined />} 
                  placeholder="用户名（3-20个字符）" 
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
                  prefix={<MailOutlined />} 
                  placeholder="邮箱地址" 
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
                  prefix={<LockOutlined />}
                  placeholder="密码（至少6位）"
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
                  prefix={<LockOutlined />}
                  placeholder="确认密码"
                />
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  style={{ width: '100%' }}
                >
                  注册
                </Button>
              </Form.Item>
            </Form>
            
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                已有账号？ <Link to="/login">立即登录</Link>
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Register