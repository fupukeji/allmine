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
  Descriptions,
  Tabs,
  TreeSelect
} from 'antd'
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  EyeOutlined,
  BarChartOutlined,
  AlertOutlined,
  DollarOutlined,
  PlusCircleOutlined,
  FolderOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import { 
  getAssets, 
  createAsset, 
  updateAsset, 
  deleteAsset,
  batchDeleteAssets,
  getAssetDepreciation,
  getAssetsStatistics
} from '../services/assets'
import { getAssetIncomes, createAssetIncome, getAssetIncomeAnalysis } from '../services/income'
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

const FixedAssets = () => {
  const navigate = useNavigate()
  const [assets, setAssets] = useState([])
  const [categories, setCategories] = useState([])
  const [treeCategories, setTreeCategories] = useState([]) // 树形分类数据
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [statisticsModalVisible, setStatisticsModalVisible] = useState(false)
  const [incomeModalVisible, setIncomeModalVisible] = useState(false)
  const [incomeAnalysisModalVisible, setIncomeAnalysisModalVisible] = useState(false)
  const [editingAsset, setEditingAsset] = useState(null)
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
  const [filters, setFilters] = useState({})
  const [assetIncomes, setAssetIncomes] = useState([])
  const [incomeAnalysis, setIncomeAnalysis] = useState(null)
  const [incomeLoading, setIncomeLoading] = useState(false)
  const [form] = Form.useForm()
  const [incomeForm] = Form.useForm()

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
    
    // 创建映射
    flatData.forEach(item => {
      map[item.id] = { ...item, children: [] }
    })
    
    // 构建树
    flatData.forEach(item => {
      if (item.parent_id) {
        if (map[item.parent_id]) {
          map[item.parent_id].children.push(map[item.id])
        }
      } else {
        tree.push(map[item.id])
      }
    })
    
    // 清理空的 children 数组
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
    fetchAssets()
  }, [filters])

  const fetchData = async () => {
    await Promise.all([
      fetchAssets(),
      fetchCategories(),
      fetchStatistics()
    ])
  }

  const fetchAssets = async () => {
    setLoading(true)
    try {
      const response = await getAssets(filters)
      if (response.code === 200) {
        setAssets(response.data)
      }
    } catch (error) {
      console.error('获取固定资产列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await getCategories()
      if (response.code === 200) {
        setCategories(response.data)
        // 构建树形结构
        const tree = buildCategoryTree(response.data)
        setTreeCategories(tree)
      }
    } catch (error) {
      console.error('获取分类列表失败:', error)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await getAssetsStatistics()
      if (response.code === 200) {
        setStatistics(response.data)
      }
    } catch (error) {
      console.error('获取统计信息失败:', error)
    }
  }

  const handleAdd = () => {
    setEditingAsset(null)
    setModalVisible(true)
    form.resetFields()
    form.setFieldsValue({
      purchase_date: dayjs(),
      depreciation_start_date: dayjs(),
      useful_life_years: 5,
      residual_rate: 5.0,
      status: 'in_use',
      depreciation_method: 'straight_line'
    })
  }

  const handleEdit = (asset) => {
    setEditingAsset(asset)
    setModalVisible(true)
    
    form.setFieldsValue({
      ...asset,
      purchase_date: asset.purchase_date ? dayjs(asset.purchase_date) : null,
      depreciation_start_date: asset.depreciation_start_date ? dayjs(asset.depreciation_start_date) : null,
    })
  }

  const handleView = async (asset) => {
    try {
      const response = await getAssetDepreciation(asset.id)
      if (response.code === 200) {
        setSelectedAsset(response.data)
        setDetailModalVisible(true)
      }
    } catch (error) {
      console.error('获取资产详情失败:', error)
    }
  }

  const handleIncomeManagement = (asset) => {
    // 跳转到专门的收益管理页面
    navigate(`/assets/${asset.id}/income`)
  }

  const handleIncomeAnalysis = async (asset) => {
    try {
      setSelectedAsset(asset)
      const response = await getAssetIncomeAnalysis(asset.id)
      if (response.code === 200) {
        setIncomeAnalysis(response.data)
        setIncomeAnalysisModalVisible(true)
      } else {
        console.error('获取收入分析失败:', response.message)
        message.error('获取收入分析失败')
      }
    } catch (error) {
      console.error('获取收入分析失败:', error)
      message.error('获取收入分析失败，请稍后重试')
    }
  }

  const handleAddIncome = () => {
    incomeForm.resetFields()
    incomeForm.setFieldsValue({
      income_date: dayjs(),
      status: 'pending',
      income_type: 'rent'
    })
  }

  const handleIncomeSubmit = async () => {
    try {
      const values = await incomeForm.validateFields()
      const incomeData = {
        ...values,
        income_date: values.income_date.format('YYYY-MM-DD'),
        recurring_end_date: values.recurring_end_date ? values.recurring_end_date.format('YYYY-MM-DD') : null
      }
      
      const response = await createAssetIncome(selectedAsset.id, incomeData)
      if (response.code === 200) {
        message.success('收入记录添加成功')
        // 重新获取收入列表
        try {
          const incomeResponse = await getAssetIncomes(selectedAsset.id)
          if (incomeResponse.code === 200) {
            setAssetIncomes(incomeResponse.data)
          }
        } catch (error) {
          console.error('刷新收入列表失败:', error)
        }
        incomeForm.resetFields()
        // 重置表单默认值
        handleAddIncome()
      } else {
        message.error(response.message || '添加收入记录失败')
      }
    } catch (error) {
      console.error('添加收入记录失败:', error)
      if (error.response?.data?.message) {
        message.error(error.response.data.message)
      } else {
        message.error('添加收入记录失败，请检查输入信息')
      }
    }
  }

  const handleDelete = async (assetId) => {
    try {
      const response = await deleteAsset(assetId)
      if (response.code === 200) {
        message.success('删除成功')
        fetchAssets()
        fetchStatistics()
      }
    } catch (error) {
      console.error('删除固定资产失败:', error)
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的资产')
      return
    }

    try {
      const response = await batchDeleteAssets(selectedRowKeys)
      if (response.code === 200) {
        message.success(response.message)
        setSelectedRowKeys([])
        fetchAssets()
        fetchStatistics()
      }
    } catch (error) {
      console.error('批量删除失败:', error)
    }
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()
      
      // 格式化时间
      const assetData = {
        ...values,
        purchase_date: values.purchase_date ? values.purchase_date.format('YYYY-MM-DD') : null,
        depreciation_start_date: values.depreciation_start_date ? values.depreciation_start_date.format('YYYY-MM-DD') : null,
      }
      
      if (editingAsset) {
        // 更新资产
        const response = await updateAsset(editingAsset.id, assetData)
        if (response.code === 200) {
          message.success('更新成功')
          setModalVisible(false)
          fetchAssets()
          fetchStatistics()
        }
      } else {
        // 创建资产
        const response = await createAsset(assetData)
        if (response.code === 200) {
          message.success('创建成功')
          setModalVisible(false)
          fetchAssets()
          fetchStatistics()
        }
      }
    } catch (error) {
      console.error('操作失败:', error)
    }
  }

  const handleModalCancel = () => {
    setModalVisible(false)
    setEditingAsset(null)
    form.resetFields()
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'in_use': return 'green'
      case 'idle': return 'orange'
      case 'maintenance': return 'blue'
      case 'disposed': return 'red'
      default: return 'default'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'in_use': return '使用中'
      case 'idle': return '闲置'
      case 'maintenance': return '维修中'
      case 'disposed': return '已处置'
      default: return '未知'
    }
  }

  const columns = [
    {
      title: '资产编号',
      dataIndex: 'asset_code',
      key: 'asset_code',
      width: 120,
    },
    {
      title: '资产名称',
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
      title: '原值',
      dataIndex: 'original_value',
      key: 'original_value',
      render: (value) => `¥${value.toFixed(2)}`,
      width: 120,
    },
    {
      title: '当前价值',
      dataIndex: 'current_value',
      key: 'current_value',
      render: (value) => `¥${value.toFixed(2)}`,
      width: 120,
    },
    {
      title: '折旧率',
      dataIndex: 'depreciation_rate',
      key: 'depreciation_rate',
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
      title: '购买日期',
      dataIndex: 'purchase_date',
      key: 'purchase_date',
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 280,
      render: (_, record) => (
        <Space size="small" wrap>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
            size="small"
            title="查看详情"
          >
            详情
          </Button>
          <Button
            type="link"
            icon={<DollarOutlined />}
            onClick={() => handleIncomeManagement(record)}
            size="small"
            style={{ 
              color: '#52c41a', 
              fontWeight: 'bold',
              background: '#f6ffed',
              border: '1px solid #b7eb8f',
              borderRadius: '4px',
              padding: '0 8px'
            }}
            title="管理收益信息 - 恒产生金核心功能"
          >
            💰 收益
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
            title="编辑资产"
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除这个固定资产吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
              title="删除资产"
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
          <div>
            <Title level={2} style={{ marginBottom: '4px' }}>
              固定资产管理
            </Title>
            <div style={{ color: '#666', fontSize: '14px' }}>
              💰 恒产生金：点击资产列表中的绿色"💰 收益"按钮管理收入信息
            </div>
          </div>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<BarChartOutlined />}
              onClick={() => setStatisticsModalVisible(true)}
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
              <Option value="in_use">使用中</Option>
              <Option value="idle">闲置</Option>
              <Option value="maintenance">维修中</Option>
              <Option value="disposed">已处置</Option>
            </Select>
            {selectedRowKeys.length > 0 && (
              <Popconfirm
                title={`确定删除选中的${selectedRowKeys.length}个资产吗？`}
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
              添加资产
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 统计概览卡片 */}
      {statistics && (
        <Row gutter={16} style={{ marginBottom: '16px' }}>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="资产总数"
                value={statistics.overview.total_assets}
                suffix="个"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="原值总计"
                value={statistics.overview.total_original_value}
                precision={2}
                suffix="元"
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="当前价值"
                value={statistics.overview.total_current_value}
                precision={2}
                suffix="元"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="累计折旧"
                value={statistics.overview.total_accumulated_depreciation}
                precision={2}
                suffix="元"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 即将完全折旧提醒 */}
      {statistics && statistics.expiring_assets.length > 0 && (
        <Card 
          size="small" 
          style={{ marginBottom: '16px', borderColor: '#faad14' }}
          title={
            <span>
              <AlertOutlined style={{ color: '#faad14', marginRight: '8px' }} />
              即将完全折旧提醒
            </span>
          }
        >
          <Space wrap>
            {statistics.expiring_assets.map(asset => (
              <Tag key={asset.id} color="orange">
                {asset.name} (剩余{asset.remaining_months}个月)
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      <Table
        dataSource={assets}
        columns={columns}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        scroll={{ x: 1400 }}
        locale={{
          emptyText: (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <div style={{ fontSize: '18px', color: '#999', marginBottom: '16px' }}>
                📊 还没有固定资产数据
              </div>
              <div style={{ color: '#666', marginBottom: '24px' }}>
                开始添加您的第一个固定资产，开启"恒产生金"的财富管理之旅！
              </div>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={handleAdd}
                size="large"
              >
                立即添加固定资产
              </Button>
              <div style={{ marginTop: '16px', fontSize: '12px', color: '#999' }}>
                💰 核心功能：添加资产后，点击绿色"💰 收益"按钮可记录租金、授权费、分红等收入，实现真正的"恒产生金"
              </div>
            </div>
          )
        }}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      {/* 添加/编辑资产模态框 */}
      <Modal
        title={editingAsset ? '编辑固定资产' : '添加固定资产'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        destroyOnClose
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="资产名称"
                name="name"
                rules={[
                  { required: true, message: '请输入资产名称!' },
                  { max: 100, message: '资产名称不能超过100个字符!' }
                ]}
              >
                <Input placeholder="请输入资产名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="资产编号"
                name="asset_code"
                rules={[
                  { max: 50, message: '资产编号不能超过50个字符!' }
                ]}
              >
                <Input placeholder="留空自动生成" />
              </Form.Item>
            </Col>
          </Row>

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
                label="原值"
                name="original_value"
                rules={[
                  { required: true, message: '请输入原值!' },
                  { type: 'number', min: 0.01, message: '原值必须大于0!' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入原值"
                  precision={2}
                  min={0.01}
                  addonAfter="元"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="购买日期"
                name="purchase_date"
                rules={[{ required: true, message: '请选择购买日期!' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  format="YYYY-MM-DD"
                  placeholder="选择购买日期"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="使用年限"
                name="useful_life_years"
                rules={[
                  { required: true, message: '请输入使用年限!' },
                  { type: 'number', min: 1, message: '使用年限必须大于0!' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="使用年限"
                  min={1}
                  addonAfter="年"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="残值率"
                name="residual_rate"
                rules={[
                  { required: true, message: '请输入残值率!' },
                  { type: 'number', min: 0, max: 50, message: '残值率应在0-50%之间!' }
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="残值率"
                  min={0}
                  max={50}
                  precision={2}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="折旧开始日期"
                name="depreciation_start_date"
                rules={[{ required: true, message: '请选择折旧开始日期!' }]}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  format="YYYY-MM-DD"
                  placeholder="选择折旧开始日期"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="折旧方法"
                name="depreciation_method"
              >
                <Select placeholder="选择折旧方法">
                  <Option value="straight_line">直线法</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="使用状态"
                name="status"
                rules={[{ required: true, message: '请选择使用状态!' }]}
              >
                <Select placeholder="选择使用状态">
                  <Option value="in_use">使用中</Option>
                  <Option value="idle">闲置</Option>
                  <Option value="maintenance">维修中</Option>
                  <Option value="disposed">已处置</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="所在位置"
                name="location"
              >
                <Input placeholder="请输入所在位置" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="责任人"
                name="responsible_person"
              >
                <Input placeholder="请输入责任人" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="资产描述"
            name="description"
          >
            <TextArea
              rows={3}
              placeholder="请输入资产描述"
              maxLength={500}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 资产详情模态框 */}
      <Modal
        title="固定资产详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={900}
      >
        {selectedAsset && (
          <Tabs defaultActiveKey="1">
            <TabPane tab="基本信息" key="1">
              <Descriptions bordered>
                <Descriptions.Item label="资产编号" span={2}>{selectedAsset.asset_info.asset_code}</Descriptions.Item>
                <Descriptions.Item label="资产名称" span={1}>{selectedAsset.asset_info.name}</Descriptions.Item>
                <Descriptions.Item label="分类" span={1}>{selectedAsset.asset_info.category_name}</Descriptions.Item>
                <Descriptions.Item label="状态" span={2}>
                  <Tag color={getStatusColor(selectedAsset.asset_info.status)}>
                    {selectedAsset.asset_info.status_text}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="原值" span={1}>¥{selectedAsset.asset_info.original_value.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="购买日期" span={1}>{selectedAsset.asset_info.purchase_date}</Descriptions.Item>
                <Descriptions.Item label="使用年限" span={1}>{selectedAsset.asset_info.useful_life_years}年</Descriptions.Item>
                <Descriptions.Item label="所在位置" span={1}>{selectedAsset.asset_info.location || '-'}</Descriptions.Item>
                <Descriptions.Item label="责任人" span={2}>{selectedAsset.asset_info.responsible_person || '-'}</Descriptions.Item>
                <Descriptions.Item label="资产描述" span={3}>{selectedAsset.asset_info.description || '-'}</Descriptions.Item>
              </Descriptions>
            </TabPane>
            
            <TabPane tab="折旧信息" key="2">
              <Row gutter={16} style={{ marginBottom: '16px' }}>
                <Col span={6}>
                  <Card size="small">
                    <Statistic
                      title="当前价值"
                      value={selectedAsset.depreciation.current_value}
                      precision={2}
                      suffix="元"
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card size="small">
                    <Statistic
                      title="累计折旧"
                      value={selectedAsset.depreciation.accumulated_depreciation}
                      precision={2}
                      suffix="元"
                      valueStyle={{ color: '#faad14' }}
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card size="small">
                    <Statistic
                      title="折旧率"
                      value={selectedAsset.depreciation.depreciation_rate}
                      precision={1}
                      suffix="%"
                    />
                  </Card>
                </Col>
                <Col span={6}>
                  <Card size="small">
                    <Statistic
                      title="剩余月数"
                      value={selectedAsset.depreciation.remaining_life_months}
                      suffix="个月"
                      valueStyle={{ 
                        color: selectedAsset.depreciation.remaining_life_months <= 12 ? '#f5222d' : '#1890ff' 
                      }}
                    />
                  </Card>
                </Col>
              </Row>
              
              <Descriptions bordered>
                <Descriptions.Item label="折旧方法" span={1}>直线法</Descriptions.Item>
                <Descriptions.Item label="年折旧率" span={1}>{selectedAsset.asset_info.annual_depreciation_rate.toFixed(2)}%</Descriptions.Item>
                <Descriptions.Item label="月折旧额" span={1}>¥{selectedAsset.asset_info.monthly_depreciation.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="残值率" span={1}>{selectedAsset.asset_info.residual_rate.toFixed(2)}%</Descriptions.Item>
                <Descriptions.Item label="折旧开始日期" span={1}>{selectedAsset.asset_info.depreciation_start_date}</Descriptions.Item>
                <Descriptions.Item label="已折旧月数" span={1}>{selectedAsset.depreciation.months_depreciated}个月</Descriptions.Item>
                <Descriptions.Item label="是否完全折旧" span={3}>
                  <Tag color={selectedAsset.depreciation.is_fully_depreciated ? 'red' : 'green'}>
                    {selectedAsset.depreciation.is_fully_depreciated ? '是' : '否'}
                  </Tag>
                </Descriptions.Item>
              </Descriptions>
            </TabPane>
          </Tabs>
        )}
      </Modal>

      {/* 收入管理模态框 */}
      <Modal
        title={`${selectedAsset?.name} - 收入管理`}
        open={incomeModalVisible}
        onCancel={() => setIncomeModalVisible(false)}
        footer={null}
        width={1000}
      >
        {selectedAsset && (
          <div>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Button 
                  type="primary" 
                  icon={<PlusCircleOutlined />}
                  onClick={handleAddIncome}
                >
                  添加收入记录
                </Button>
                <Button 
                  style={{ marginLeft: '8px' }}
                  icon={<BarChartOutlined />}
                  onClick={() => handleIncomeAnalysis(selectedAsset)}
                >
                  收入分析
                </Button>
              </div>
            </div>
            
            {/* 添加收入记录表单 */}
            <Card title="添加收入记录" style={{ marginBottom: '16px' }} size="small">
              <Form
                form={incomeForm}
                layout="inline"
                onFinish={handleIncomeSubmit}
              >
                <Form.Item name="income_type" label="收入类型" rules={[{ required: true }]}>
                  <Select style={{ width: 120 }}>
                    <Option value="rent">租金收入</Option>
                    <Option value="license">授权费</Option>
                    <Option value="dividend">分红</Option>
                    <Option value="sale">销售收入</Option>
                    <Option value="appreciation">增值收益</Option>
                    <Option value="interest">利息收入</Option>
                    <Option value="other">其他收入</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item name="amount" label="收入金额" rules={[{ required: true }]}>
                  <InputNumber style={{ width: 120 }} precision={2} min={0} addonAfter="元" />
                </Form.Item>
                
                <Form.Item name="income_date" label="收入日期" rules={[{ required: true }]}>
                  <DatePicker format="YYYY-MM-DD" />
                </Form.Item>
                
                <Form.Item name="payer" label="付款方">
                  <Input style={{ width: 120 }} placeholder="付款方" />
                </Form.Item>
                
                <Form.Item name="status" label="状态">
                  <Select style={{ width: 80 }}>
                    <Option value="pending">待收</Option>
                    <Option value="received">已收</Option>
                    <Option value="overdue">逾期</Option>
                  </Select>
                </Form.Item>
                
                <Form.Item>
                  <Button type="primary" htmlType="submit" size="small">
                    添加
                  </Button>
                </Form.Item>
              </Form>
            </Card>
            
            {/* 收入记录列表 */}
            <Table
              dataSource={assetIncomes}
              rowKey="id"
              size="small"
              loading={incomeLoading}
              locale={{
                emptyText: '还没有收入记录，请添加一条收入记录开始记录您的资产收益！'
              }}
              columns={[
                {
                  title: '收入类型',
                  dataIndex: 'income_type_text',
                  key: 'income_type_text',
                },
                {
                  title: '金额',
                  dataIndex: 'amount',
                  key: 'amount',
                  render: (value) => `¥${value.toFixed(2)}`,
                },
                {
                  title: '净收入',
                  dataIndex: 'net_amount',
                  key: 'net_amount',
                  render: (value) => `¥${value.toFixed(2)}`,
                },
                {
                  title: '收入日期',
                  dataIndex: 'income_date',
                  key: 'income_date',
                },
                {
                  title: '付款方',
                  dataIndex: 'payer',
                  key: 'payer',
                },
                {
                  title: '状态',
                  dataIndex: 'status_text',
                  key: 'status_text',
                  render: (text, record) => (
                    <Tag color={record.status === 'received' ? 'green' : record.status === 'overdue' ? 'red' : 'orange'}>
                      {text}
                    </Tag>
                  )
                },
              ]}
              pagination={{ pageSize: 5, showSizeChanger: false }}
            />
          </div>
        )}
      </Modal>
      
      {/* 收入分析模态框 */}
      <Modal
        title={`${selectedAsset?.name} - 收入分析`}
        open={incomeAnalysisModalVisible}
        onCancel={() => setIncomeAnalysisModalVisible(false)}
        footer={[<Button key="close" onClick={() => setIncomeAnalysisModalVisible(false)}>关闭</Button>]}
        width={1000}
      >
        {incomeAnalysis && (
          <div>
            {/* ROI 指标卡片 */}
            <Row gutter={16} style={{ marginBottom: '24px' }}>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="总收入"
                    value={incomeAnalysis.total_stats.total_income}
                    precision={2}
                    suffix="元"
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="投资回报率"
                    value={incomeAnalysis.roi_analysis?.roi || 0}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="年化收益率"
                    value={incomeAnalysis.roi_analysis?.annual_return || 0}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#faad14' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card size="small">
                  <Statistic
                    title="回本周期"
                    value={incomeAnalysis.roi_analysis?.payback_months || 0}
                    precision={1}
                    suffix="月"
                    valueStyle={{ color: '#f5222d' }}
                  />
                </Card>
              </Col>
            </Row>
            
            {/* 收入类型分布 */}
            <Card title="收入类型分布" style={{ marginBottom: '16px' }}>
              <Row gutter={16}>
                {incomeAnalysis.type_distribution.map(item => (
                  <Col key={item.income_type} span={6}>
                    <Card size="small">
                      <Statistic
                        title={item.income_type_text}
                        value={item.total_amount}
                        precision={2}
                        suffix="元"
                      />
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                        {item.count} 笔收入
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
            
            {/* 预期vs实际分析 */}
            {incomeAnalysis.variance_analysis.expected_total > 0 && (
              <Card title="预期vs实际分析">
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="预期收入"
                      value={incomeAnalysis.variance_analysis.expected_total}
                      precision={2}
                      suffix="元"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="实际收入"
                      value={incomeAnalysis.variance_analysis.actual_total}
                      precision={2}
                      suffix="元"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="差异率"
                      value={incomeAnalysis.variance_analysis.variance_rate}
                      precision={2}
                      suffix="%"
                      valueStyle={{ 
                        color: incomeAnalysis.variance_analysis.variance_rate >= 0 ? '#52c41a' : '#f5222d' 
                      }}
                    />
                  </Col>
                </Row>
              </Card>
            )}
          </div>
        )}
      </Modal>

      {/* 统计分析模态框 */}
      <Modal
        title="固定资产统计分析"
        open={statisticsModalVisible}
        onCancel={() => setStatisticsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setStatisticsModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={1000}
      >
        {statistics && (
          <Tabs defaultActiveKey="1">
            <TabPane tab="总体概览" key="1">
              <Row gutter={16}>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="资产总数"
                      value={statistics.overview.total_assets}
                      suffix="个"
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="原值总计"
                      value={statistics.overview.total_original_value}
                      precision={2}
                      suffix="元"
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="整体折旧率"
                      value={statistics.overview.depreciation_rate}
                      precision={1}
                      suffix="%"
                    />
                  </Card>
                </Col>
              </Row>
            </TabPane>
            
            <TabPane tab="状态分布" key="2">
              <Row gutter={16}>
                {statistics.status_distribution.map(item => (
                  <Col span={6} key={item.status}>
                    <Card>
                      <Statistic
                        title={getStatusText(item.status)}
                        value={item.count}
                        suffix="个"
                        prefix={<Tag color={getStatusColor(item.status)}>{getStatusText(item.status)}</Tag>}
                      />
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                        价值：¥{item.total_value.toFixed(2)}
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </TabPane>
            
            <TabPane tab="分类分布" key="3">
              <Row gutter={16}>
                {statistics.category_distribution.map(item => (
                  <Col span={8} key={item.category_name} style={{ marginBottom: '16px' }}>
                    <Card>
                      <Statistic
                        title={item.category_name}
                        value={item.count}
                        suffix="个"
                      />
                      <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                        价值：¥{item.total_value.toFixed(2)}
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </TabPane>
          </Tabs>
        )}
      </Modal>
    </div>
  )
}

export default FixedAssets