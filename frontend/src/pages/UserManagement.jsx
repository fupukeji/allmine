import React, { useState, useEffect } from 'react'
import {
  Table,
  Card,
  Button,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Popconfirm,
  Row,
  Col,
  Statistic,
  Typography,
  Tooltip,
  Alert
} from 'antd'
import {
  UserOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TeamOutlined,
  CrownOutlined
} from '@ant-design/icons'
import { getUsers, createUser, updateUser, deleteUser, toggleUserStatus, getAdminStats } from '../services/admin'

const { Title } = Typography
const { Option } = Select

const UserManagement = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [deleteModalVisible, setDeleteModalVisible] = useState(false)
  const [deletingUser, setDeletingUser] = useState(null)
  const [stats, setStats] = useState({})
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  })
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    role: ''
  })
  const [form] = Form.useForm()
  const [deleteForm] = Form.useForm()

  useEffect(() => {
    fetchUsers()
    fetchStats()
  }, [pagination.current, pagination.pageSize, filters])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await getUsers({
        page: pagination.current,
        per_page: pagination.pageSize,
        ...filters
      })

      if (response.code === 200) {
        setUsers(response.data)
        setPagination({
          ...pagination,
          total: response.pagination.total
        })
      }
    } catch (error) {
      console.error('获取用户列表失败:', error)
      message.error('获取用户列表失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await getAdminStats()
      if (response.code === 200) {
        setStats(response.data)
      }
    } catch (error) {
      console.error('获取统计数据失败:', error)
    }
  }

  const handleTableChange = (paginationInfo) => {
    setPagination(paginationInfo)
  }

  const handleSearch = (value) => {
    setFilters({ ...filters, search: value })
    setPagination({ ...pagination, current: 1 })
  }

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value })
    setPagination({ ...pagination, current: 1 })
  }

  const handleCreateUser = () => {
    setEditingUser(null)
    setModalVisible(true)
    form.resetFields()
  }

  const handleEditUser = (user) => {
    setEditingUser(user)
    setModalVisible(true)
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active
    })
  }

  const handleDeleteUser = async (user) => {
    setDeletingUser(user)
    setDeleteModalVisible(true)
    deleteForm.resetFields()
  }

  const confirmDeleteUser = async () => {
    try {
      const values = await deleteForm.validateFields()
      const response = await deleteUser(deletingUser.id, {
        username: values.username,
        password: values.password
      })
      if (response.code === 200) {
        message.success(response.message)
        setDeleteModalVisible(false)
        setDeletingUser(null)
        deleteForm.resetFields()
        fetchUsers()
        fetchStats()
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      if (error.response?.data?.message) {
        message.error(error.response.data.message)
      } else if (error.errorFields) {
        // 表单验证失败
        message.error('请填写完整信息')
      } else {
        message.error('删除用户失败')
      }
    }
  }

  const handleToggleStatus = async (userId) => {
    try {
      const response = await toggleUserStatus(userId)
      if (response.code === 200) {
        message.success(response.message)
        fetchUsers()
        fetchStats()
      }
    } catch (error) {
      console.error('切换用户状态失败:', error)
      message.error('操作失败')
    }
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingUser) {
        const response = await updateUser(editingUser.id, values)
        if (response.code === 200) {
          message.success('用户更新成功')
          setModalVisible(false)
          fetchUsers()
        }
      } else {
        const response = await createUser(values)
        if (response.code === 200) {
          message.success('用户创建成功')
          setModalVisible(false)
          fetchUsers()
          fetchStats()
        }
      }
    } catch (error) {
      console.error('操作失败:', error)
      if (error.response?.data?.message) {
        message.error(error.response.data.message)
      } else {
        message.error('操作失败')
      }
    }
  }

  const handleModalCancel = () => {
    setModalVisible(false)
    setEditingUser(null)
    form.resetFields()
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      render: (text, record) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <UserOutlined style={{ marginRight: 8 }} />
          {text}
          {record.role === 'admin' && (
            <CrownOutlined style={{ marginLeft: 8, color: '#faad14' }} />
          )}
        </div>
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role) => (
        <Tag color={role === 'admin' ? 'gold' : 'blue'}>
          {role === 'admin' ? '管理员' : '普通用户'}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '项目数',
      dataIndex: 'project_count',
      key: 'project_count',
    },
    {
      title: '分类数',
      dataIndex: 'category_count',
      key: 'category_count',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="编辑用户">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEditUser(record)}
            />
          </Tooltip>
          
          <Tooltip title={record.is_active ? '禁用用户' : '启用用户'}>
            <Button
              type="link"
              onClick={() => handleToggleStatus(record.id)}
              style={{ color: record.is_active ? '#faad14' : '#52c41a' }}
            >
              {record.is_active ? '禁用' : '启用'}
            </Button>
          </Tooltip>
          
          <Popconfirm
            title="确定要删除这个用户吗？"
            description="此操作将清除该用户的所有数据且不可恢复"
            onConfirm={() => handleDeleteUser(record)}
            okText="下一步"
            cancelText="取消"
          >
            <Tooltip title="删除用户">
              <Button
                type="link"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Title level={2}><TeamOutlined /> 用户管理</Title>
      
      {/* 统计卡片 */}
      {stats.user_stats && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={stats.user_stats.total}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="活跃用户"
                value={stats.user_stats.active}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="禁用用户"
                value={stats.user_stats.inactive}
                valueStyle={{ color: '#f5222d' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={6}>
            <Card>
              <Statistic
                title="管理员"
                value={stats.user_stats.admins}
                prefix={<CrownOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} justify="space-between" align="middle">
          <Col>
            <Space>
              <Input.Search
                placeholder="搜索用户名或邮箱"
                allowClear
                style={{ width: 250 }}
                onSearch={handleSearch}
              />
              
              <Select
                placeholder="状态"
                allowClear
                style={{ width: 120 }}
                onChange={(value) => handleFilterChange('status', value)}
              >
                <Option value="active">启用</Option>
                <Option value="inactive">禁用</Option>
              </Select>
              
              <Select
                placeholder="角色"
                allowClear
                style={{ width: 120 }}
                onChange={(value) => handleFilterChange('role', value)}
              >
                <Option value="admin">管理员</Option>
                <Option value="user">普通用户</Option>
              </Select>
            </Space>
          </Col>
          
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreateUser}
            >
              添加用户
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 用户表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
          }}
          onChange={handleTableChange}
        />
      </Card>

      {/* 用户编辑/创建弹窗 */}
      <Modal
        title={editingUser ? '编辑用户' : '创建用户'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            role: 'user',
            is_active: true
          }}
        >
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
              disabled={!!editingUser}
            />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              label="密码"
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码长度至少6位' }
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}

          <Form.Item
            label="角色"
            name="role"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select>
              <Option value="user">普通用户</Option>
              <Option value="admin">管理员</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="状态"
            name="is_active"
            valuePropName="checked"
          >
            <Switch
              checkedChildren="启用"
              unCheckedChildren="禁用"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 删除用户确认弹窗 */}
      <Modal
        title="删除用户确认"
        open={deleteModalVisible}
        onOk={confirmDeleteUser}
        onCancel={() => {
          setDeleteModalVisible(false)
          setDeletingUser(null)
          deleteForm.resetFields()
        }}
        okText="确认删除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
        width={500}
      >
        {deletingUser && (
          <>
            <Alert
              message="警告：此操作不可恢复！"
              description={
                <div>
                  <p>删除用户 <strong>{deletingUser.username}</strong> 将清除以下所有数据：</p>
                  <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                    <li>所有虚拟资产（项目）</li>
                    <li>所有固定资产</li>
                    <li>所有分类</li>
                    <li>所有资产收入记录</li>
                    <li>所有维护记录</li>
                    <li>所有AI报告</li>
                  </ul>
                  <p style={{ marginTop: 8, color: '#ff4d4f', fontWeight: 'bold' }}>
                    请谨慎操作，此操作无法撤销！
                  </p>
                </div>
              }
              type="warning"
              showIcon
              style={{ marginBottom: 24 }}
            />
            
            <Form
              form={deleteForm}
              layout="vertical"
            >
              <Form.Item
                label="请输入要删除的用户名进行确认"
                name="username"
                rules={[
                  { required: true, message: '请输入用户名' },
                  {
                    validator: (_, value) => {
                      if (value && value !== deletingUser.username) {
                        return Promise.reject('用户名不匹配')
                      }
                      return Promise.resolve()
                    }
                  }
                ]}
              >
                <Input
                  placeholder={`请输入: ${deletingUser.username}`}
                  prefix={<UserOutlined />}
                />
              </Form.Item>

              <Form.Item
                label="请输入您的管理员密码"
                name="password"
                rules={[
                  { required: true, message: '请输入您的密码' }
                ]}
              >
                <Input.Password
                  placeholder="请输入您的管理员密码"
                  prefix={<DeleteOutlined />}
                />
              </Form.Item>
            </Form>
          </>
        )}
      </Modal>
    </div>
  )
}

export default UserManagement