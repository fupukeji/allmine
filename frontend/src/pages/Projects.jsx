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
  Statistic,
  TreeSelect,
  Tabs
} from 'antd'
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  EyeOutlined,
  FilterOutlined,
  FolderOutlined,
  BarChartOutlined,
  RiseOutlined,
  FallOutlined,
  ThunderboltOutlined,
  DollarOutlined,
  PieChartOutlined,
  LineChartOutlined,
  WarningOutlined,
  ClockCircleOutlined
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
const { Option, OptGroup } = Select
const { TabPane } = Tabs

// 分类分组定义
const categoryGroups = {
  virtual: {
    title: '随风而逝（虚拟消耗型资产）',
    keywords: ['视频', '音乐', '知识', '外卖', '电商', '出行', '云存储', 
               '游戏', '直播', '电子书', '课程', '软件', '会员', '充值', '道具', '礼物']
  },
  fixed: {
    title: '恒产生金（固定资产）',
    keywords: ['房产', '车辆', '车位', '车库', '珠宝', '首饰', '艺术', '收藏', 
               '名包', '名表', '电脑', '手机', '数码', '摄影', '器材', 
               '家电', '家具', '智能家居']
  },
  financial: {
    title: '金融流动资产',
    keywords: ['银行', '存款', '现金', '支付宝', '微信', '股票', '基金', 
               '债券', '理财', '数字货币', '比特币', '保险', '社保', '公积金']
  },
  liability: {
    title: '负债管理',
    keywords: ['房贷', '车贷', '信用卡', '消费贷', '花呗', '白条', '借呗', 
               '经营贷款', '私人借款', '借款']
  },
  other: {
    title: '其他资产',
    keywords: ['应收', '预付', '积分', '权益', '其他']
  }
}

// 根据分类名称判断所属组
const getCategoryGroup = (categoryName) => {
  for (const [groupKey, groupConfig] of Object.entries(categoryGroups)) {
    if (groupConfig.keywords.some(keyword => categoryName.includes(keyword))) {
      return groupKey
    }
  }
  return 'other'
}

const Projects = () => {
  const [projects, setProjects] = useState([])
  const [categories, setCategories] = useState([])
  const [treeCategories, setTreeCategories] = useState([]) // 树形分类数据
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [statisticsModalVisible, setStatisticsModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [filters, setFilters] = useState({})
  const [form] = Form.useForm()

  const statistics = React.useMemo(() => {
    if (projects.length === 0) return null
    const totalAmount = projects.reduce((sum, p) => sum + p.total_amount, 0)
    const totalUsed = projects.reduce((sum, p) => sum + p.used_cost, 0)
    const totalRemaining = projects.reduce((sum, p) => sum + p.remaining_value, 0)
    const avgProgress = projects.reduce((sum, p) => sum + p.progress, 0) / projects.length
    const statusDist = projects.reduce((acc, p) => {
      if (!acc[p.status]) acc[p.status] = { count: 0, value: 0 }
      acc[p.status].count++
      acc[p.status].value += p.total_amount
      return acc
    }, {})
    const categoryDist = projects.reduce((acc, p) => {
      const key = p.category_name || '未分类'
      if (!acc[key]) acc[key] = { count: 0, value: 0, remaining: 0 }
      acc[key].count++
      acc[key].value += p.total_amount
      acc[key].remaining += p.remaining_value
      return acc
    }, {})
    const riskProjects = projects.filter(p => {
      if (!p.end_time) return false
      const daysRemaining = dayjs(p.end_time).diff(dayjs(), 'day')
      return daysRemaining <= 30 && daysRemaining > 0 && p.remaining_value > 100
    })
    const highConsumption = projects.filter(p => {
      if (!p.end_time || !p.start_time) return false
      const totalDays = dayjs(p.end_time).diff(dayjs(p.start_time), 'day')
      const usedDays = dayjs().diff(dayjs(p.start_time), 'day')
      const timeProgress = (usedDays / totalDays) * 100
      return p.progress > 70 && timeProgress < 50
    })
    return {
      overview: {
        totalProjects: projects.length,
        totalAmount,
        totalUsed,
        totalRemaining,
        avgProgress,
        activeCount: projects.filter(p => p.status === 'active').length
      },
      statusDistribution: Object.entries(statusDist).map(([status, data]) => ({ status, ...data })),
      categoryDistribution: Object.entries(categoryDist).map(([name, data]) => ({ name, ...data })),
      riskProjects,
      highConsumption
    }
  }, [projects])

  // 分组分类
  const groupedCategories = React.useMemo(() => {
    const grouped = {
      virtual: [],
      fixed: [],
      financial: [],
      liability: [],
      other: []
    }
    
    categories.forEach(category => {
      const group = getCategoryGroup(category.name)
      grouped[group].push(category)
    })
    
    return grouped
  }, [categories])

  // 将平面分类数据转换为树形结构
  const buildCategoryTree = (flatData) => {
    const tree = []
    const map = {}
    
    flatData.forEach(item => {
      map[item.id] = { ...item, children: [] }
    })
    
    flatData.forEach(item => {
      if (item.parent_id) {
        if (map[item.parent_id]) {
          map[item.parent_id].children.push(map[item.id])
        }
      } else {
        tree.push(map[item.id])
      }
    })
    
    const cleanEmptyChildren = (nodes) => {
      nodes.forEach(node => {
        if (node.children && node.children.length > 0) {
          cleanEmptyChildren(node.children)
        } else {
          delete node.children
        }
      })
    }
    cleanEmptyChildren(tree)
    
    return tree
  }

  // 构建 TreeSelect 的数据
  const buildTreeSelectData = (categories) => {
    return categories.map(cat => ({
      value: cat.id,
      title: (
        <Space>
          <FolderOutlined style={{ color: cat.color || '#1890ff' }} />
          {cat.name}
        </Space>
      ),
      children: cat.children ? buildTreeSelectData(cat.children) : undefined
    }))
  }

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
        const tree = buildCategoryTree(response.data)
        setTreeCategories(tree)
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
        start_time: values.start_time ? values.start_time.format('YYYY-MM-DD') : null,
        end_time: values.end_time ? values.end_time.format('YYYY-MM-DD') : null,
        purchase_time: values.purchase_time ? values.purchase_time.format('YYYY-MM-DD') : null,
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
    <div style={{ padding: '24px', background: '#f5f7fa', minHeight: 'calc(100vh - 64px)' }}>
      {/* 页面头部 */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '20px',
        padding: '32px',
        marginBottom: '24px',
        boxShadow: '0 20px 60px rgba(102, 126, 234, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* 浮动装饰 */}
        <div style={{ 
          position: 'absolute', 
          top: '-80px', 
          right: '-80px', 
          width: '250px', 
          height: '250px', 
          background: 'rgba(255,255,255,0.1)', 
          borderRadius: '50%',
          animation: 'float 6s ease-in-out infinite'
        }} />
        <div style={{ 
          position: 'absolute', 
          bottom: '-60px', 
          left: '-60px', 
          width: '200px', 
          height: '200px', 
          background: 'rgba(255,255,255,0.08)', 
          borderRadius: '50%',
          animation: 'float 8s ease-in-out infinite'
        }} />
        
        <Row justify="space-between" align="middle" style={{ position: 'relative', zIndex: 1 }}>
          <Col>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{
                width: '60px',
                height: '60px',
                background: 'rgba(255,255,255,0.2)',
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '16px',
                backdropFilter: 'blur(10px)'
              }}>
                <span style={{ fontSize: '32px' }}>💨</span>
              </div>
              <div>
                <Title level={2} style={{ color: 'white', margin: 0, fontWeight: 'bold' }}>
                  虚拟资产管理
                </Title>
                <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', marginTop: '4px' }}>
                  随风而逝：记录视频会员、游戏充值、云服务等虚拟消耗资产
                </div>
              </div>
            </div>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<BarChartOutlined />}
                onClick={() => setStatisticsModalVisible(true)}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  color: 'white',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '10px',
                  fontWeight: 500
                }}
              >
                统计分析
              </Button>
            <Select
              placeholder="筛选分类"
              style={{ width: 200 }}
              allowClear
              showSearch
              optionFilterProp="children"
              onChange={(value) => setFilters({ ...filters, category_id: value })}
            >
              {Object.entries(categoryGroups).map(([groupKey, groupConfig]) => {
                const groupData = groupedCategories[groupKey] || []
                if (groupData.length === 0) return null
                return (
                  <OptGroup key={groupKey} label={groupConfig.title}>
                    {groupData.map(cat => (
                      <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                    ))}
                  </OptGroup>
                )
              })}
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
                style={{
                  background: 'white',
                  color: '#667eea',
                  border: 'none',
                  borderRadius: '10px',
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(255,255,255,0.3)'
                }}
              >
                添加项目
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 风险提示区域 */}
      {statistics && (statistics.riskProjects.length > 0 || statistics.highConsumption.length > 0) && (
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          {statistics.riskProjects.length > 0 && (
            <Col span={12}>
              <Card
                size="small"
                style={{ 
                  borderColor: '#ff4d4f', 
                  background: '#fff1f0',
                  borderRadius: '16px',
                  boxShadow: '0 4px 12px rgba(255, 77, 79, 0.1)'
                }}
                title={
                  <span style={{ color: '#ff4d4f' }}>
                    <WarningOutlined style={{ marginRight: '8px' }} />
                    即将过期项目
                  </span>
                }
              >
                <Space wrap>
                  {statistics.riskProjects.map(p => (
                    <Tag key={p.id} color="error">
                      {p.name} (剩余{dayjs(p.end_time).diff(dayjs(), 'day')}天，剩余¥{p.remaining_value.toFixed(2)})
                    </Tag>
                  ))}
                </Space>
              </Card>
            </Col>
          )}
          {statistics.highConsumption.length > 0 && (
            <Col span={12}>
              <Card
                size="small"
                style={{ 
                  borderColor: '#faad14', 
                  background: '#fffbe6',
                  borderRadius: '16px',
                  boxShadow: '0 4px 12px rgba(250, 173, 20, 0.1)'
                }}
                title={
                  <span style={{ color: '#faad14' }}>
                    <ThunderboltOutlined style={{ marginRight: '8px' }} />
                    异常消耗项目
                  </span>
                }
              >
                <Space wrap>
                  {statistics.highConsumption.map(p => (
                    <Tag key={p.id} color="warning">
                      {p.name} (消耗进度{p.progress.toFixed(1)}%)
                    </Tag>
                  ))}
                </Space>
              </Card>
            </Col>
          )}
        </Row>
      )}

      {/* 数据表格 */}
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '24px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
      }}>
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
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(20px); }
        }
      `}</style>

      {/* 添加/编辑项目模态框 */}
      <Modal
        title={editingProject ? '编辑项目' : '添加项目'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
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
                label="资产分类"
                name="category_id"
                rules={[{ required: true, message: '请选择分类!' }]}
                help="支持多级分类选择"
              >
                <TreeSelect
                  placeholder="请选择分类"
                  treeDefaultExpandAll
                  treeData={buildTreeSelectData(treeCategories)}
                  showSearch
                  treeNodeFilterProp="title"
                  allowClear
                />
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
                  format="YYYY-MM-DD"
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
                  format="YYYY-MM-DD"
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
              format="YYYY-MM-DD"
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

      {/* 统计分析模态框 */}
      <Modal
        title={
          <div style={{
            fontSize: '20px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            padding: '4px 0'
          }}>
            <BarChartOutlined style={{ marginRight: '8px', color: '#667eea' }} />
            虚拟资产统计分析
          </div>
        }
        open={statisticsModalVisible}
        onCancel={() => setStatisticsModalVisible(false)}
        footer={[
          <Button
            key="close"
            type="primary"
            onClick={() => setStatisticsModalVisible(false)}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none'
            }}
          >
            关闭
          </Button>
        ]}
        width={1200}
        styles={{ body: { padding: '24px', background: '#f5f7fa' } }}
      >
        {statistics && (
          <div style={{ minHeight: '500px' }}>
            <Tabs
              defaultActiveKey="1"
              size="large"
              tabBarStyle={{
                background: 'white',
                padding: '8px 16px',
                borderRadius: '8px',
                marginBottom: '16px'
              }}
            >
              <TabPane
                tab={
                  <span>
                    <PieChartOutlined style={{ marginRight: '4px' }} />
                    总体概览
                  </span>
                }
                key="1"
              >
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  <Col span={6}>
                    <Card
                      hoverable
                      style={{
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        border: 'none',
                        boxShadow: '0 8px 16px rgba(102, 126, 234, 0.3)'
                      }}
                    >
                      <Statistic
                        title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>项目总数</span>}
                        value={statistics.overview.totalProjects}
                        suffix="个"
                        valueStyle={{ color: '#fff', fontSize: '32px', fontWeight: 'bold' }}
                        prefix={<ClockCircleOutlined style={{ color: 'rgba(255,255,255,0.8)' }} />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card
                      hoverable
                      style={{
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        border: 'none',
                        boxShadow: '0 8px 16px rgba(240, 147, 251, 0.3)'
                      }}
                    >
                      <Statistic
                        title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>总支出</span>}
                        value={statistics.overview.totalAmount}
                        precision={2}
                        suffix="元"
                        valueStyle={{ color: '#fff', fontSize: '28px', fontWeight: 'bold' }}
                        prefix={<DollarOutlined style={{ color: 'rgba(255,255,255,0.8)' }} />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card
                      hoverable
                      style={{
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                        border: 'none',
                        boxShadow: '0 8px 16px rgba(250, 112, 154, 0.3)'
                      }}
                    >
                      <Statistic
                        title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>已消耗</span>}
                        value={statistics.overview.totalUsed}
                        precision={2}
                        suffix="元"
                        valueStyle={{ color: '#fff', fontSize: '28px', fontWeight: 'bold' }}
                        prefix={<FallOutlined style={{ color: 'rgba(255,255,255,0.8)' }} />}
                      />
                    </Card>
                  </Col>
                  <Col span={6}>
                    <Card
                      hoverable
                      style={{
                        borderRadius: '12px',
                        background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                        border: 'none',
                        boxShadow: '0 8px 16px rgba(79, 172, 254, 0.3)'
                      }}
                    >
                      <Statistic
                        title={<span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>剩余价值</span>}
                        value={statistics.overview.totalRemaining}
                        precision={2}
                        suffix="元"
                        valueStyle={{ color: '#fff', fontSize: '28px', fontWeight: 'bold' }}
                        prefix={<RiseOutlined style={{ color: 'rgba(255,255,255,0.8)' }} />}
                      />
                    </Card>
                  </Col>
                </Row>

                <Card
                  style={{
                    borderRadius: '12px',
                    marginBottom: '24px',
                    border: '1px solid #e8e8e8',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
                  }}
                  title={
                    <span style={{ fontSize: '16px', fontWeight: 600 }}>
                      <LineChartOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                      整体消耗进度
                    </span>
                  }
                >
                  <div style={{ padding: '20px 0' }}>
                    <Progress
                      percent={statistics.overview.avgProgress}
                      strokeColor={{
                        '0%': '#667eea',
                        '100%': '#764ba2',
                      }}
                      strokeWidth={20}
                      format={(percent) => (
                        <span style={{ fontSize: '18px', fontWeight: 'bold' }}>
                          {percent.toFixed(1)}%
                        </span>
                      )}
                    />
                    <div style={{
                      marginTop: '16px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      color: '#666',
                      fontSize: '14px'
                    }}>
                      <span>活跃项目：{statistics.overview.activeCount} 个</span>
                      <span>已消耗：¥{statistics.overview.totalUsed.toFixed(2)}</span>
                    </div>
                  </div>
                </Card>

                <Row gutter={16}>
                  <Col span={12}>
                    <Card
                      style={{
                        borderRadius: '12px',
                        border: '1px solid #e8e8e8',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        height: '100%'
                      }}
                      title={
                        <span style={{ fontSize: '16px', fontWeight: 600 }}>
                          <DollarOutlined style={{ marginRight: '8px', color: '#52c41a' }} />
                          消耗率
                        </span>
                      }
                    >
                      <div style={{ textAlign: 'center', padding: '20px 0' }}>
                        <Progress
                          type="circle"
                          percent={(statistics.overview.totalUsed / statistics.overview.totalAmount * 100)}
                          strokeColor={{
                            '0%': '#52c41a',
                            '100%': '#f5222d',
                          }}
                          strokeWidth={10}
                          width={150}
                          format={(percent) => (
                            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                              {percent.toFixed(0)}%
                              <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>消耗率</div>
                            </div>
                          )}
                        />
                        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
                          <div>总支出：¥{statistics.overview.totalAmount.toFixed(2)}</div>
                          <div style={{ marginTop: '8px' }}>已消耗：¥{statistics.overview.totalUsed.toFixed(2)}</div>
                        </div>
                      </div>
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card
                      style={{
                        borderRadius: '12px',
                        border: '1px solid #e8e8e8',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        height: '100%'
                      }}
                      title={
                        <span style={{ fontSize: '16px', fontWeight: 600 }}>
                          <ThunderboltOutlined style={{ marginRight: '8px', color: '#faad14' }} />
                          价值保有率
                        </span>
                      }
                    >
                      <div style={{ textAlign: 'center', padding: '20px 0' }}>
                        <Progress
                          type="circle"
                          percent={(statistics.overview.totalRemaining / statistics.overview.totalAmount * 100)}
                          strokeColor={{
                            '0%': '#1890ff',
                            '100%': '#52c41a',
                          }}
                          strokeWidth={10}
                          width={150}
                          format={(percent) => (
                            <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                              {percent.toFixed(0)}%
                              <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>保有率</div>
                            </div>
                          )}
                        />
                        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
                          <div>总支出：¥{statistics.overview.totalAmount.toFixed(2)}</div>
                          <div style={{ marginTop: '8px' }}>剩余：¥{statistics.overview.totalRemaining.toFixed(2)}</div>
                        </div>
                      </div>
                    </Card>
                  </Col>
                </Row>
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <PieChartOutlined style={{ marginRight: '4px' }} />
                    状态分布
                  </span>
                }
                key="2"
              >
                <Row gutter={[16, 16]}>
                  {statistics.statusDistribution.map((item, index) => (
                    <Col span={8} key={item.status}>
                      <Card
                        hoverable
                        style={{
                          borderRadius: '12px',
                          border: '1px solid #e8e8e8',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
                        }}
                      >
                        <div style={{ textAlign: 'center' }}>
                          <Tag
                            color={getStatusColor(item.status)}
                            style={{ fontSize: '14px', padding: '6px 16px', marginBottom: '16px', borderRadius: '20px' }}
                          >
                            {getStatusText(item.status)}
                          </Tag>
                          <div style={{ fontSize: '36px', fontWeight: 'bold', margin: '12px 0' }}>
                            {item.count}
                          </div>
                          <div style={{ color: '#999', fontSize: '14px', marginBottom: '16px' }}>项目数量</div>
                          <div style={{
                            background: '#f5f5f5',
                            borderRadius: '8px',
                            padding: '12px'
                          }}>
                            <div style={{ color: '#666', fontSize: '12px' }}>总价值</div>
                            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1890ff', marginTop: '4px' }}>
                              ¥{item.value.toFixed(2)}
                            </div>
                          </div>
                        </div>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <FolderOutlined style={{ marginRight: '4px' }} />
                    分类分布
                  </span>
                }
                key="3"
              >
                <Row gutter={[16, 16]}>
                  {statistics.categoryDistribution.map((item, index) => (
                    <Col span={8} key={item.name}>
                      <Card
                        hoverable
                        style={{
                          borderRadius: '12px',
                          border: '1px solid #e8e8e8',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                          height: '100%'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
                          <div style={{
                            width: '8px',
                            height: '40px',
                            borderRadius: '4px',
                            background: `linear-gradient(135deg, ${[
                              '#667eea', '#f093fb', '#4facfe', '#fa709a',
                              '#52c41a', '#faad14', '#f5222d', '#722ed1'
                            ][index % 8]} 0%, ${[
                              '#764ba2', '#f5576c', '#00f2fe', '#fee140',
                              '#73d13d', '#ffc53d', '#ff4d4f', '#9254de'
                            ][index % 8]} 100%)`,
                            marginRight: '12px'
                          }} />
                          <div>
                            <div style={{ fontSize: '16px', fontWeight: 600 }}>{item.name}</div>
                            <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                              {item.count} 个项目
                            </div>
                          </div>
                        </div>
                        <div style={{
                          background: '#f5f5f5',
                          borderRadius: '8px',
                          padding: '16px',
                          marginTop: '12px'
                        }}>
                          <Row gutter={8}>
                            <Col span={12}>
                              <div style={{ color: '#666', fontSize: '12px', marginBottom: '4px' }}>总支出</div>
                              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#f5222d' }}>
                                ¥{item.value.toFixed(2)}
                              </div>
                            </Col>
                            <Col span={12}>
                              <div style={{ color: '#666', fontSize: '12px', marginBottom: '4px' }}>剩余价值</div>
                              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>
                                ¥{item.remaining.toFixed(2)}
                              </div>
                            </Col>
                          </Row>
                          <Progress
                            percent={((item.value - item.remaining) / item.value * 100)}
                            strokeColor={{
                              '0%': [
                                '#667eea', '#f093fb', '#4facfe', '#fa709a',
                                '#52c41a', '#faad14', '#f5222d', '#722ed1'
                              ][index % 8],
                              '100%': [
                                '#764ba2', '#f5576c', '#00f2fe', '#fee140',
                                '#73d13d', '#ffc53d', '#ff4d4f', '#9254de'
                              ][index % 8]
                            }}
                            size="small"
                            style={{ marginTop: '12px' }}
                            format={percent => `消耗${percent.toFixed(1)}%`}
                          />
                        </div>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <WarningOutlined style={{ marginRight: '4px' }} />
                    风险警告
                  </span>
                }
                key="4"
              >
                <Row gutter={16}>
                  <Col span={12}>
                    <Card
                      title={
                        <span style={{ color: '#ff4d4f' }}>
                          <WarningOutlined style={{ marginRight: '8px' }} />
                          即将过期项目 ({statistics.riskProjects.length})
                        </span>
                      }
                      style={{
                        borderRadius: '12px',
                        borderColor: '#ff4d4f',
                        boxShadow: '0 4px 12px rgba(255, 77, 79, 0.2)'
                      }}
                    >
                      {statistics.riskProjects.length > 0 ? (
                        <div>
                          {statistics.riskProjects.map(p => (
                            <Card key={p.id} size="small" style={{ marginBottom: '8px' }}>
                              <Row justify="space-between" align="middle">
                                <Col>
                                  <div style={{ fontWeight: 'bold' }}>{p.name}</div>
                                  <div style={{ color: '#666', fontSize: '12px' }}>
                                    {p.category_name}
                                  </div>
                                </Col>
                                <Col>
                                  <Tag color="error">
                                    剩余{dayjs(p.end_time).diff(dayjs(), 'day')}天
                                  </Tag>
                                  <div style={{ color: '#ff4d4f', fontWeight: 'bold', textAlign: 'right' }}>
                                    ¥{p.remaining_value.toFixed(2)}
                                  </div>
                                </Col>
                              </Row>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                          暂无即将过期的项目
                        </div>
                      )}
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card
                      title={
                        <span style={{ color: '#faad14' }}>
                          <ThunderboltOutlined style={{ marginRight: '8px' }} />
                          异常消耗项目 ({statistics.highConsumption.length})
                        </span>
                      }
                      style={{
                        borderRadius: '12px',
                        borderColor: '#faad14',
                        boxShadow: '0 4px 12px rgba(250, 173, 20, 0.2)'
                      }}
                    >
                      {statistics.highConsumption.length > 0 ? (
                        <div>
                          {statistics.highConsumption.map(p => (
                            <Card key={p.id} size="small" style={{ marginBottom: '8px' }}>
                              <Row justify="space-between" align="middle">
                                <Col>
                                  <div style={{ fontWeight: 'bold' }}>{p.name}</div>
                                  <div style={{ color: '#666', fontSize: '12px' }}>
                                    {p.category_name}
                                  </div>
                                </Col>
                                <Col>
                                  <Tag color="warning">
                                    消耗{p.progress.toFixed(1)}%
                                  </Tag>
                                  <Progress
                                    percent={p.progress}
                                    size="small"
                                    strokeColor="#faad14"
                                    style={{ width: '100px' }}
                                  />
                                </Col>
                              </Row>
                            </Card>
                          ))}
                        </div>
                      ) : (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                          暂无异常消耗的项目
                        </div>
                      )}
                    </Card>
                  </Col>
                </Row>
              </TabPane>
            </Tabs>
          </div>
        )}
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
                    {selectedProject.purchase_time ? dayjs(selectedProject.purchase_time).format('YYYY-MM-DD') : '未设置'}
                  </p>
                  <p><strong>开始时间：</strong>
                    {dayjs(selectedProject.start_time).format('YYYY-MM-DD')}
                  </p>
                  <p><strong>结束时间：</strong>
                    {dayjs(selectedProject.end_time).format('YYYY-MM-DD')}
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