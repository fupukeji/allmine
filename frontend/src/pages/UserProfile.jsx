import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  message,
  Avatar,
  Upload,
  Row,
  Col,
  Divider,
  Typography,
  Space,
  Tag,
  Switch,
  Select,
  TimePicker,
  Radio,
  Modal,
  Alert
} from 'antd'
import {
  UserOutlined,
  MailOutlined,
  LockOutlined,
  PhoneOutlined,
  HomeOutlined,
  SettingOutlined,
  CameraOutlined,
  SaveOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  ExclamationCircleOutlined,
  DeleteOutlined
} from '@ant-design/icons'
import { getUserProfile, updateUserProfile, changePassword } from '../services/profile'
import request from '../utils/request'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { Option } = Select

const UserProfile = () => {
  const [profileForm] = Form.useForm()
  const [preferencesForm] = Form.useForm()
  const [passwordForm] = Form.useForm()
  const [resetForm] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [resetLoading, setResetLoading] = useState(false)
  const [userInfo, setUserInfo] = useState({})
  const [avatar, setAvatar] = useState('')
  const [resetModalVisible, setResetModalVisible] = useState(false)

  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      const response = await getUserProfile()
      if (response.code === 200) {
        const userData = response.data
        setUserInfo(userData)
        setAvatar(userData.avatar || '')
        
        // 填充表单数据
        profileForm.setFieldsValue({
          username: userData.username,
          email: userData.email,
          phone: userData.phone || '',
          location: userData.location || '',
          bio: userData.bio || '',
          website: userData.website || '',
          company: userData.company || ''
        })
        
        preferencesForm.setFieldsValue({
          language: userData.language || 'zh-CN',
          timezone: userData.timezone || 'Asia/Shanghai',
          theme: userData.theme || 'light',
          email_notifications: userData.email_notifications !== false,
          sms_notifications: userData.sms_notifications !== false
        })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      message.error('获取用户信息失败')
    }
  }

  const handleProfileUpdate = async () => {
    try {
      setLoading(true)
      const values = await profileForm.validateFields()
      
      const response = await updateUserProfile({
        ...values,
        avatar: avatar
      })
      
      if (response.code === 200) {
        message.success('个人信息更新成功')
        // 更新本地用户信息
        const updatedUserInfo = { ...userInfo, ...values, avatar }
        setUserInfo(updatedUserInfo)
        
        // 重新获取最新的用户信息以保证数据同步
        await fetchUserProfile()
        
        // 触发父组件刷新（如果需要）
        window.dispatchEvent(new CustomEvent('userProfileUpdated', { 
          detail: response.data 
        }))
      }
    } catch (error) {
      console.error('更新个人信息失败:', error)
      if (error.response?.data?.message) {
        message.error(error.response.data.message)
      } else {
        message.error('更新失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePreferencesUpdate = async () => {
    try {
      setLoading(true)
      const values = await preferencesForm.validateFields()
      
      const response = await updateUserProfile({
        ...values
      })
      
      if (response.code === 200) {
        message.success('偏好设置更新成功')
        // 更新本地用户信息
        const updatedUserInfo = { ...userInfo, ...values }
        setUserInfo(updatedUserInfo)
        
        // 重新获取最新的用户信息以保证数据同步
        await fetchUserProfile()
        
        // 触发父组件刷新（如果需要）
        window.dispatchEvent(new CustomEvent('userProfileUpdated', { 
          detail: response.data 
        }))
      }
    } catch (error) {
      console.error('更新偏好设置失败:', error)
      if (error.response?.data?.message) {
        message.error(error.response.data.message)
      } else {
        message.error('更新失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordUpdate = async () => {
    try {
      setPasswordLoading(true)
      const values = await passwordForm.validateFields()
      
      const response = await changePassword({
        oldPassword: values.oldPassword,
        newPassword: values.newPassword
      })
      
      if (response.code === 200) {
        message.success('密码修改成功')
        passwordForm.resetFields()
      }
    } catch (error) {
      console.error('修改密码失败:', error)
      if (error.response?.data?.message) {
        message.error(error.response.data.message)
      } else {
        message.error('修改密码失败')
      }
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleResetDatabase = async () => {
    try {
      setResetLoading(true)
      const values = await resetForm.validateFields()
      
      const response = await request.post('/auth/reset-database', {
        password: values.password
      })
      
      if (response.success) {
        message.success('数据库清空成功，页面将刷新')
        resetForm.resetFields()
        setResetModalVisible(false)
        // 1秒后刷新页面
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      } else {
        message.error(response.message || '清空失败')
      }
    } catch (error) {
      console.error('清空数据库失败:', error)
      message.error(error.response?.data?.message || '清空失败')
    } finally {
      setResetLoading(false)
    }
  }

  const showResetConfirm = () => {
    setResetModalVisible(true)
  }

  const beforeUpload = (file) => {
    const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
    if (!isJpgOrPng) {
      message.error('只能上传 JPG/PNG 格式的图片!')
      return false
    }
    const isLt2M = file.size / 1024 / 1024 < 2
    if (!isLt2M) {
      message.error('图片大小不能超过 2MB!')
      return false
    }
    
    // 这里可以添加上传到服务器的逻辑
    const reader = new FileReader()
    reader.onload = (e) => {
      setAvatar(e.target.result)
    }
    reader.readAsDataURL(file)
    
    return false // 阻止默认上传
  }

  const formatDate = (date) => {
    return date ? dayjs(date).format('YYYY-MM-DD') : '-'
  }

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'red'
      case 'user': return 'blue'
      default: return 'default'
    }
  }

  const getRoleText = (role) => {
    switch (role) {
      case 'admin': return '管理员'
      case 'user': return '普通用户'
      default: return '未知'
    }
  }

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>
          <SettingOutlined /> 个人设置
        </Title>
        
        <Row gutter={24}>
          {/* 左侧：个人信息预览 */}
          <Col xs={24} lg={8}>
            <Card title="个人信息" style={{ marginBottom: '24px' }}>
              <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <div style={{ position: 'relative', display: 'inline-block' }}>
                  <Avatar
                    size={120}
                    src={avatar}
                    icon={<UserOutlined />}
                    style={{ border: '3px solid #f0f0f0' }}
                  />
                  <Upload
                    showUploadList={false}
                    beforeUpload={beforeUpload}
                    accept="image/*"
                  >
                    <Button
                      type="primary"
                      shape="circle"
                      icon={<CameraOutlined />}
                      size="small"
                      style={{
                        position: 'absolute',
                        bottom: 0,
                        right: 0,
                        border: '2px solid white'
                      }}
                    />
                  </Upload>
                </div>
                <div style={{ marginTop: '16px' }}>
                  <Title level={4}>{userInfo.username}</Title>
                  <Text type="secondary">{userInfo.email}</Text>
                  <div style={{ marginTop: '8px' }}>
                    <Tag color={getRoleColor(userInfo.role)}>
                      {getRoleText(userInfo.role)}
                    </Tag>
                    <Tag color={userInfo.is_active ? 'green' : 'red'}>
                      {userInfo.is_active ? '正常' : '已禁用'}
                    </Tag>
                  </div>
                </div>
              </div>
              
              <Divider />
              
              <div>
                <Text strong>账户信息</Text>
                <div style={{ marginTop: '12px' }}>
                  <div style={{ marginBottom: '8px' }}>
                    <Text type="secondary">注册时间：</Text>
                    <Text>{formatDate(userInfo.created_at)}</Text>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <Text type="secondary">最后登录：</Text>
                    <Text>{formatDate(userInfo.last_login)}</Text>
                  </div>
                  <div>
                    <Text type="secondary">用户ID：</Text>
                    <Text>#{userInfo.id}</Text>
                  </div>
                </div>
              </div>
            </Card>
          </Col>

          {/* 右侧：设置表单 */}
          <Col xs={24} lg={16}>
            {/* 基本信息 */}
            <Card title="基本信息" style={{ marginBottom: '24px' }}>
              <Form
                form={profileForm}
                layout="vertical"
                onFinish={handleProfileUpdate}
              >
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="用户名"
                      name="username"
                      rules={[
                        { required: true, message: '请输入用户名' },
                        { min: 3, max: 20, message: '用户名长度应在3-20个字符之间' }
                      ]}
                    >
                      <Input
                        prefix={<UserOutlined />}
                        placeholder="请输入用户名"
                      />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="邮箱地址"
                      name="email"
                      rules={[
                        { required: true, message: '请输入邮箱地址' },
                        { type: 'email', message: '请输入有效的邮箱地址' }
                      ]}
                    >
                      <Input
                        prefix={<MailOutlined />}
                        placeholder="请输入邮箱地址"
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="手机号码"
                      name="phone"
                    >
                      <Input
                        prefix={<PhoneOutlined />}
                        placeholder="请输入手机号码"
                      />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="所在地区"
                      name="location"
                    >
                      <Input
                        prefix={<HomeOutlined />}
                        placeholder="请输入所在地区"
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="公司/组织"
                      name="company"
                    >
                      <Input placeholder="请输入公司或组织名称" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="个人网站"
                      name="website"
                    >
                      <Input placeholder="请输入个人网站地址" />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  label="个人简介"
                  name="bio"
                >
                  <Input.TextArea
                    rows={3}
                    placeholder="介绍一下自己..."
                    maxLength={200}
                    showCount
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                  >
                    保存基本信息
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            {/* 偏好设置 */}
            <Card title="偏好设置" style={{ marginBottom: '24px' }}>
              <Form
                form={preferencesForm}
                layout="vertical"
                onFinish={handlePreferencesUpdate}
              >
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item
                      label="语言"
                      name="language"
                    >
                      <Select placeholder="选择语言">
                        <Option value="zh-CN">简体中文</Option>
                        <Option value="en-US">English</Option>
                        <Option value="ja-JP">日本語</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      label="时区"
                      name="timezone"
                    >
                      <Select placeholder="选择时区">
                        <Option value="Asia/Shanghai">上海 (UTC+8)</Option>
                        <Option value="Asia/Tokyo">东京 (UTC+9)</Option>
                        <Option value="America/New_York">纽约 (UTC-5)</Option>
                        <Option value="Europe/London">伦敦 (UTC+0)</Option>
                      </Select>
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      label="主题"
                      name="theme"
                    >
                      <Radio.Group>
                        <Radio value="light">浅色</Radio>
                        <Radio value="dark">深色</Radio>
                      </Radio.Group>
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item
                      label="邮件通知"
                      name="email_notifications"
                      valuePropName="checked"
                    >
                      <Switch />
                      <Text type="secondary" style={{ marginLeft: '8px' }}>
                        接收重要事件的邮件通知
                      </Text>
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="短信通知"
                      name="sms_notifications"
                      valuePropName="checked"
                    >
                      <Switch />
                      <Text type="secondary" style={{ marginLeft: '8px' }}>
                        接收重要事件的短信通知
                      </Text>
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    icon={<SaveOutlined />}
                  >
                    保存偏好设置
                  </Button>
                </Form.Item>
              </Form>
            </Card>

            {/* 安全设置 */}
            <Card title="安全设置">
              <Form
                form={passwordForm}
                layout="vertical"
                onFinish={handlePasswordUpdate}
              >
                <Form.Item
                  label="当前密码"
                  name="oldPassword"
                  rules={[{ required: true, message: '请输入当前密码' }]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请输入当前密码"
                    iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                  />
                </Form.Item>

                <Form.Item
                  label="新密码"
                  name="newPassword"
                  rules={[
                    { required: true, message: '请输入新密码' },
                    { min: 6, message: '密码长度至少6位' }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请输入新密码"
                    iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                  />
                </Form.Item>

                <Form.Item
                  label="确认新密码"
                  name="confirmPassword"
                  dependencies={['newPassword']}
                  rules={[
                    { required: true, message: '请确认新密码' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('newPassword') === value) {
                          return Promise.resolve()
                        }
                        return Promise.reject(new Error('两次输入的密码不一致'))
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="请再次输入新密码"
                    iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
                  />
                </Form.Item>

                <Form.Item>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={passwordLoading}
                    danger
                  >
                    修改密码
                  </Button>
                </Form.Item>
              </Form>

              <Divider />

              {/* 清空数据库 */}
              <div style={{ marginTop: 24 }}>
                <Alert
                  message="危险操作"
                  description="清空数据库将删除所有资产、项目、分类等数据，仅保留用户信息。此操作不可恢复，请谨慎操作！"
                  type="error"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Button
                  danger
                  icon={<DeleteOutlined />}
                  onClick={showResetConfirm}
                >
                  清空数据库
                </Button>
              </div>
            </Card>
          </Col>
        </Row>

        {/* 清空数据库确认弹窗 */}
        <Modal
          title={
            <Space>
              <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
              确认清空数据库
            </Space>
          }
          open={resetModalVisible}
          onCancel={() => {
            setResetModalVisible(false)
            resetForm.resetFields()
          }}
          footer={null}
          width={500}
        >
          <Alert
            message="警告：此操作将永久删除以下数据"
            description={
              <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                <li>所有固定资产记录</li>
                <li>所有项目记录（随风而逝）</li>
                <li>所有资产分类</li>
                <li>所有收入记录</li>
                <li>所有维护记录</li>
                <li>所有AI报告</li>
                <li>智谱AI API Key配置</li>
              </ul>
            }
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
          />

          <Form
            form={resetForm}
            layout="vertical"
            onFinish={handleResetDatabase}
          >
            <Form.Item
              label="请输入您的登录密码以确认此操作"
              name="password"
              rules={[
                { required: true, message: '请输入登录密码' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="请输入当前登录密码"
                size="large"
                iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                <Button 
                  onClick={() => {
                    setResetModalVisible(false)
                    resetForm.resetFields()
                  }}
                >
                  取消
                </Button>
                <Button
                  type="primary"
                  danger
                  htmlType="submit"
                  loading={resetLoading}
                  icon={<DeleteOutlined />}
                >
                  确认清空
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  )
}

export default UserProfile