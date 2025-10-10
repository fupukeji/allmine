import React, { useState, useEffect } from 'react'
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  DatePicker, 
  InputNumber,
  message, 
  Popconfirm, 
  Typography, 
  Space,
  Tag,
  Row,
  Col,
  Progress,
  Card,
  Statistic
} from 'antd'
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  EyeOutlined,
  FilterOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { 
  getProjects, 
  createProject, 
  updateProject, 
  deleteProject,
  batchDeleteProjects
} from '../services/projects'
import { getCategories } from '../services/categories'

const { Title } = Typography
const { TextArea } = Input
const { Option } = Select

const Projects = () => {
  const [projects, setProjects] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [filters, setFilters] = useState({})
  const [form] = Form.useForm()

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    fetchProjects()
  }, [filters])

  const fetchData = async () => {
    await Promise.all([
      fetchProjects(),
      fetchCategories()
    ])
  }

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await getProjects(filters)
      if (response.code === 200) {
        setProjects(response.data)
      }
    } catch (error) {
      console.error('获取项目列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await getCategories()
      if (response.code === 200) {
        setCategories(response.data)
      }
    } catch (error) {
      console.error('获取分类列表失败:', error)
    }
  }

  const handleAdd = () => {
    setEditingProject(null)
    setModalVisible(true)
    form.resetFields()
    form.setFieldsValue({
      start_time: dayjs(),
      end_time: dayjs().add(1, 'year')
    })
  }

  const handleEdit = (project) => {
    setEditingProject(project)
    setModalVisible(true)
    form.setFieldsValue({
      ...project,
      start_time: project.start_time ? dayjs(project.start_time) : null,
      end_time: project.end_time ? dayjs(project.end_time) : null,
      purchase_time: project.purchase_time ? dayjs(project.purchase_time) : null,
    })
  }

  const handleView = (project) => {
    setSelectedProject(project)
    setDetailModalVisible(true)
  }

  const handleDelete = async (projectId) => {
    try {
      const response = await deleteProject(projectId)
      if (response.code === 200) {
        message.success('删除成功')
        fetchProjects()
      }
    } catch (error) {
      console.error('删除项目失败:', error)
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的项目')
      return
    }

    try {
      const response = await batchDeleteProjects(selectedRowKeys)
      if (response.code === 200) {
        message.success(response.message)
        setSelectedRowKeys([])
        fetchProjects()
      }
    } catch (error) {
      console.error('批量删除失败:', error)
    }
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()
      
      // 格式化时间
      const projectData = {
        ...values,
        start_time: values.start_time ? values.start_time.format('YYYY-MM-DD HH:mm:ss') : null,
        end_time: values.end_time ? values.end_time.format('YYYY-MM-DD HH:mm:ss') : null,
        purchase_time: values.purchase_time ? values.purchase_time.format('YYYY-MM-DD HH:mm:ss') : null,
      }
      
      if (editingProject) {
        // 更新项目
        const response = await updateProject(editingProject.id, projectData)
        if (response.code === 200) {
          message.success('更新成功')
          setModalVisible(false)
          fetchProjects()
        }
      } else {
        // 创建项目
        const response = await createProject(projectData)
        if (response.code === 200) {
          message.success('创建成功')
          setModalVisible(false)
          fetchProjects()
        }
      }
    } catch (error) {
      console.error('操作失败:', error)
    }
  }

  const handleModalCancel = () => {
    setModalVisible(false)
    setEditingProject(null)
    form.resetFields()
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'not_started': return 'blue'
      case 'active': return 'green'
      case 'expired': return 'red'
      default: return 'default'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'not_started': return '未开始'
      case 'active': return '消耗中'
      case 'expired': return '已过期'
      default: return '未知'
    }
  }

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      width: 150,
    },
    {
      title: '分类',
      dataIndex: 'category_name',
      key: 'category_name',
      width: 100,
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value) => `¥${value.toFixed(2)}`,
      width: 120,
    },
    {
      title: '已消耗',
      dataIndex: 'used_cost',
      key: 'used_cost',
      render: (value) => `¥${value.toFixed(2)}`,
      width: 120,
    },
    {
      title: '剩余价值',
      dataIndex: 'remaining_value',
      key: 'remaining_value',
      render: (value) => `¥${value.toFixed(2)}`,
      width: 120,
    },
    {
      title: '消耗进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (value) => <Progress percent={value} size="small" />,
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
      width: 80,
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD') : '-',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
            size="small"
          >
            详情
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个项目吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
  }

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
        <Col>
          <Title level={2}>项目管理</Title>
        </Col>
        <Col>
          <Space>
            <Select
              placeholder="筛选分类"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => setFilters({ ...filters, category_id: value })}
            >
              {categories.map(cat => (
                <Option key={cat.id} value={cat.id}>{cat.name}</Option>
              ))}
            </Select>
            <Select
              placeholder="筛选状态"
              style={{ width: 120 }}
              allowClear
              onChange={(value) => setFilters({ ...filters, status: value })}
            >
              <Option value="not_started">未开始</Option>
              <Option value="active">消耗中</Option>
              <Option value="expired">已过期</Option>
            </Select>
            {selectedRowKeys.length > 0 && (
              <Popconfirm
                title={`确定删除选中的${selectedRowKeys.length}个项目吗？`}
                onConfirm={handleBatchDelete}
                okText="确定"
                cancelText="取消"
              >
                <Button danger>
                  批量删除 ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
            )}
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={handleAdd}
            >
              添加项目
            </Button>
          </Space>
        </Col>
      </Row>

      <Table
        dataSource={projects}
        columns={columns}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        scroll={{ x: 1200 }}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      {/* 添加/编辑项目模态框 */}
      <Modal
        title={editingProject ? '编辑项目' : '添加项目'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        destroyOnClose
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            label="项目名称"
            name="name"
            rules={[
              { required: true, message: '请输入项目名称!' },
              { max: 100, message: '项目名称不能超过100个字符!' }
            ]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="所属分类"
                name="category_id"
                rules={[{ required: true, message: '请选择分类!' }]}
              >
                <Select placeholder="请选择分类">
                  {categories.map(cat => (
                    <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="总支付金额"
                name="total_amount"
                rules={[
                  { required: true, message: '请输入总金额!' },
                  { type: 'number', min: 0.01, message: '金额必须大于0!' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入总金额"
                  precision={2}
                  min={0.01}
                  addonAfter="元"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="开始计算时间"
                name="start_time"
                rules={[{ required: true, message: '请选择开始时间!' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  showTime
                  format="YYYY-MM-DD HH:mm:ss"
                  placeholder="选择开始时间"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="结束时间"
                name="end_time"
                rules={[{ required: true, message: '请选择结束时间!' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  showTime
                  format="YYYY-MM-DD HH:mm:ss"
                  placeholder="选择结束时间"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="购买时间（可选）"
            name="purchase_time"
          >
            <DatePicker
              style={{ width: '100%' }}
              showTime
              format="YYYY-MM-DD HH:mm:ss"
              placeholder="选择购买时间"
            />
          </Form.Item>

          <Form.Item
            label="购买目的（可选）"
            name="purpose"
          >
            <TextArea
              rows={3}
              placeholder="请输入购买目的或备注信息"
              maxLength={500}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 项目详情模态框 */}
      <Modal
        title="项目详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedProject && (
          <div>
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="总金额"
                    value={selectedProject.total_amount}
                    precision={2}
                    suffix="元"
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="已消耗成本"
                    value={selectedProject.used_cost}
                    precision={2}
                    suffix="元"
                    valueStyle={{ color: '#faad14' }}
                  />
                </Card>
              </Col>
              <Col span={8}>
                <Card size="small">
                  <Statistic
                    title="剩余价值"
                    value={selectedProject.remaining_value}
                    precision={2}
                    suffix="元"
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col span={12}>
                <Card size="small">
                  <Statistic
                    title="单位时间成本"
                    value={selectedProject.unit_cost}
                    precision={2}
                    suffix="元/天"
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small">
                  <Statistic
                    title="消耗进度"
                    value={selectedProject.progress}
                    precision={1}
                    suffix="%"
                  />
                </Card>
              </Col>
            </Row>

            <Card size="small" title="项目信息">
              <Row gutter={16}>
                <Col span={12}>
                  <p><strong>项目名称：</strong>{selectedProject.name}</p>
                  <p><strong>所属分类：</strong>{selectedProject.category_name}</p>
                  <p><strong>项目状态：</strong>
                    <Tag color={getStatusColor(selectedProject.status)}>
                      {getStatusText(selectedProject.status)}
                    </Tag>
                  </p>
                </Col>
                <Col span={12}>
                  <p><strong>购买时间：</strong>
                    {selectedProject.purchase_time ? dayjs(selectedProject.purchase_time).format('YYYY-MM-DD HH:mm') : '未设置'}
                  </p>
                  <p><strong>开始时间：</strong>
                    {dayjs(selectedProject.start_time).format('YYYY-MM-DD HH:mm')}
                  </p>
                  <p><strong>结束时间：</strong>
                    {dayjs(selectedProject.end_time).format('YYYY-MM-DD HH:mm')}
                  </p>
                </Col>
              </Row>
              
              {selectedProject.purpose && (
                <div style={{ marginTop: '16px' }}>
                  <p><strong>购买目的：</strong></p>
                  <p style={{ background: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
                    {selectedProject.purpose}
                  </p>
                </div>
              )}
            </Card>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Projects