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
      padding: '20px'
    }}>
      <Row justify="center" style={{ width: '100%', maxWidth: '400px' }}>
        <Col span={24}>
          <Card style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
                时间价值计算器
              </Title>
              <Text type="secondary">管理您的预付费资产价值</Text>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
                Powered by 孚普科技（北京）有限公司
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
                  prefix={<UserOutlined />} 
                  placeholder="用户名或邮箱" 
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[
                  { required: true, message: '请输入密码!' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="密码"
                />
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  style={{ width: '100%' }}
                >
                  登录
                </Button>
              </Form.Item>
            </Form>
            
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                还没有账号？ <Link to="/register">立即注册</Link>
              </Text>
              <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
                <Text style={{ fontSize: '11px', color: '#666' }}>
                  🚀 孚普科技（北京）有限公司 - AI驱动的MVP快速迭代解决方案<br/>
                  🌐 了解更多AI产品: https://fupukeji.com
                </Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Login