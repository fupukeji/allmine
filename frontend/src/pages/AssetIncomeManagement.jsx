import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Table,
  Button,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Radio,
  Switch,
  Tabs,
  Row,
  Col,
  Statistic,
  Progress,
  Tag,
  Space,
  Modal,
  message,
  Descriptions,
  Divider,
  Alert,
  Timeline,
  Tooltip
} from 'antd'
import {
  ArrowLeftOutlined,
  PlusOutlined,
  DollarOutlined,
  CalendarOutlined,
  LineChartOutlined,
  FileTextOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'
import { 
  getAssetIncomes, 
  createAssetIncome, 
  updateAssetIncome, 
  deleteAssetIncome,
  getAssetIncomeAnalysis 
} from '../services/income'
import { getAsset } from '../services/assets'

const { Option } = Select
const { TextArea } = Input
const { TabPane } = Tabs
const { RangePicker } = DatePicker

const AssetIncomeManagement = () => {
  const { assetId } = useParams()
  const navigate = useNavigate()
  
  // 基础状态
  const [asset, setAsset] = useState(null)
  const [incomes, setIncomes] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingIncome, setEditingIncome] = useState(null)
  const [activeTab, setActiveTab] = useState('list')
  
  // 表单
  const [form] = Form.useForm()
  
  // 筛选条件
  const [filters, setFilters] = useState({
    dateRange: null,
    incomeType: '',
    status: '',
    paymentMethod: ''
  })

  useEffect(() => {
    if (assetId) {
      fetchAssetData()
      fetchIncomes()
      fetchAnalysis()
    }
  }, [assetId])

  const fetchAssetData = async () => {
    try {
      const response = await getAsset(assetId)
      if (response.code === 200) {
        setAsset(response.data)
      }
    } catch (error) {
      console.error('获取资产信息失败:', error)
    }
  }

  const fetchIncomes = async () => {
    try {
      setLoading(true)
      const response = await getAssetIncomes(assetId, filters)
      if (response.code === 200) {
        setIncomes(response.data)
      }
    } catch (error) {
      console.error('获取收入记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAnalysis = async () => {
    try {
      const response = await getAssetIncomeAnalysis(assetId)
      if (response.code === 200) {
        setAnalysis(response.data)
      }
    } catch (error) {
      console.error('获取收入分析失败:', error)
    }
  }

  const handleAddIncome = () => {
    setEditingIncome(null)
    setModalVisible(true)
    form.resetFields()
    // 设置默认值
    form.setFieldsValue({
      income_date: dayjs(),
      status: 'pending',
      income_type: 'rent',
      payment_method: 'bank_transfer',
      is_recurring: false,
      tax_rate: 0
    })
  }

  const handleEditIncome = (record) => {
    setEditingIncome(record)
    setModalVisible(true)
    form.setFieldsValue({
      ...record,
      income_date: dayjs(record.income_date),
      expected_date: record.expected_date ? dayjs(record.expected_date) : null,
      actual_date: record.actual_date ? dayjs(record.actual_date) : null,
      recurring_end_date: record.recurring_end_date ? dayjs(record.recurring_end_date) : null
    })
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      // 数据处理
      const incomeData = {
        ...values,
        income_date: values.income_date.format('YYYY-MM-DD'),
        expected_date: values.expected_date ? values.expected_date.format('YYYY-MM-DD') : null,
        actual_date: values.actual_date ? values.actual_date.format('YYYY-MM-DD') : null,
        recurring_end_date: values.recurring_end_date ? values.recurring_end_date.format('YYYY-MM-DD') : null,
        // 计算净收入
        net_amount: values.amount - (values.cost || 0) - (values.amount * (values.tax_rate || 0) / 100)
      }

      let response
      if (editingIncome) {
        response = await updateAssetIncome(assetId, editingIncome.id, incomeData)
      } else {
        response = await createAssetIncome(assetId, incomeData)
      }

      if (response.code === 200) {
        message.success(editingIncome ? '更新成功' : '添加成功')
        setModalVisible(false)
        fetchIncomes()
        fetchAnalysis()
      }
    } catch (error) {
      console.error('操作失败:', error)
      message.error('操作失败')
    }
  }

  const handleDelete = async (id) => {
    try {
      const response = await deleteAssetIncome(assetId, id)
      if (response.code === 200) {
        message.success('删除成功')
        fetchIncomes()
        fetchAnalysis()
      }
    } catch (error) {
      console.error('删除失败:', error)
      message.error('删除失败')
    }
  }

  // 收入类型映射
  const incomeTypeMap = {
    rent: '租金收入',
    license: '授权费',
    dividend: '分红',
    sale: '销售收入',
    appreciation: '增值收益',
    interest: '利息收入',
    royalty: '版权费',
    service: '服务费',
    other: '其他收入'
  }

  // 支付方式映射
  const paymentMethodMap = {
    bank_transfer: '银行转账',
    cash: '现金',
    check: '支票',
    online_payment: '在线支付',
    credit_card: '信用卡',
    other: '其他方式'
  }

  // 状态映射
  const statusMap = {
    pending: '待收',
    received: '已收',
    overdue: '逾期',
    cancelled: '已取消',
    partial: '部分收取'
  }

  const getStatusColor = (status) => {
    const colorMap = {
      pending: 'orange',
      received: 'green',
      overdue: 'red',
      cancelled: 'gray',
      partial: 'blue'
    }
    return colorMap[status] || 'default'
  }

  const columns = [
    {
      title: '收入类型',
      dataIndex: 'income_type',
      key: 'income_type',
      render: (type) => (
        <Tag color="blue">{incomeTypeMap[type] || type}</Tag>
      )
    },
    {
      title: '金额信息',
      key: 'amount_info',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>¥{record.amount?.toFixed(2)}</div>
          {record.cost > 0 && (
            <div style={{ fontSize: '12px', color: '#999' }}>
              成本: ¥{record.cost?.toFixed(2)}
            </div>
          )}
          <div style={{ fontSize: '12px', color: '#52c41a' }}>
            净收入: ¥{record.net_amount?.toFixed(2)}
          </div>
        </div>
      )
    },
    {
      title: '时间信息',
      key: 'date_info',
      render: (_, record) => (
        <div>
          <div>收入日期: {record.income_date}</div>
          {record.expected_date && record.expected_date !== record.income_date && (
            <div style={{ fontSize: '12px', color: '#999' }}>
              预期: {record.expected_date}
            </div>
          )}
          {record.actual_date && (
            <div style={{ fontSize: '12px', color: '#52c41a' }}>
              实际: {record.actual_date}
            </div>
          )}
        </div>
      )
    },
    {
      title: '付款信息',
      key: 'payment_info',
      render: (_, record) => (
        <div>
          <div>{record.payer || '未填写'}</div>
          <div style={{ fontSize: '12px', color: '#999' }}>
            {paymentMethodMap[record.payment_method] || record.payment_method}
          </div>
        </div>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {statusMap[status] || status}
        </Tag>
      )
    },
    {
      title: '周期性',
      dataIndex: 'is_recurring',
      key: 'is_recurring',
      render: (isRecurring, record) => (
        <div>
          {isRecurring ? (
            <Tag color="purple">
              <CalendarOutlined /> 周期性
            </Tag>
          ) : (
            <Tag>一次性</Tag>
          )}
          {record.recurring_frequency && (
            <div style={{ fontSize: '12px', color: '#999' }}>
              {record.recurring_frequency}
            </div>
          )}
        </div>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              size="small"
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEditIncome(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
              size="small"
            />
          </Tooltip>
        </Space>
      )
    }
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* 页面头部 */}
        <div style={{ marginBottom: '24px' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/assets')}
            style={{ marginBottom: '16px' }}
          >
            返回资产列表
          </Button>
          
          <Card>
            <Row gutter={16} align="middle">
              <Col span={16}>
                <Descriptions title={`${asset?.name || '资产'} - 收益管理`} column={3}>
                  <Descriptions.Item label="资产编号">{asset?.asset_code}</Descriptions.Item>
                  <Descriptions.Item label="资产类别">{asset?.category_name}</Descriptions.Item>
                  <Descriptions.Item label="资产原值">¥{asset?.original_value?.toFixed(2)}</Descriptions.Item>
                </Descriptions>
              </Col>
              <Col span={8}>
                {analysis && (
                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic
                        title="总收入"
                        value={analysis.total_stats?.total_income || 0}
                        precision={2}
                        prefix="¥"
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="投资回报率"
                        value={analysis.roi_analysis?.roi || 0}
                        precision={2}
                        suffix="%"
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Col>
                  </Row>
                )}
              </Col>
            </Row>
          </Card>
        </div>

        {/* 主要内容 */}
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          {/* 收入记录列表 */}
          <TabPane tab={<span><FileTextOutlined />收入记录</span>} key="list">
            <Card
              title="收入记录管理"
              extra={
                <Space>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAddIncome}
                  >
                    添加收入记录
                  </Button>
                  <Button icon={<DownloadOutlined />}>导出数据</Button>
                </Space>
              }
            >
              {/* 筛选条件 */}
              <Row gutter={16} style={{ marginBottom: '16px' }}>
                <Col span={6}>
                  <Select
                    placeholder="收入类型"
                    allowClear
                    style={{ width: '100%' }}
                    onChange={(value) => setFilters({...filters, incomeType: value})}
                  >
                    {Object.entries(incomeTypeMap).map(([key, value]) => (
                      <Option key={key} value={key}>{value}</Option>
                    ))}
                  </Select>
                </Col>
                <Col span={6}>
                  <Select
                    placeholder="收款状态"
                    allowClear
                    style={{ width: '100%' }}
                    onChange={(value) => setFilters({...filters, status: value})}
                  >
                    {Object.entries(statusMap).map(([key, value]) => (
                      <Option key={key} value={key}>{value}</Option>
                    ))}
                  </Select>
                </Col>
                <Col span={8}>
                  <RangePicker
                    placeholder={['开始日期', '结束日期']}
                    style={{ width: '100%' }}
                    onChange={(dates) => setFilters({...filters, dateRange: dates})}
                  />
                </Col>
                <Col span={4}>
                  <Button type="primary" onClick={fetchIncomes} style={{ width: '100%' }}>
                    查询
                  </Button>
                </Col>
              </Row>

              <Table
                dataSource={incomes}
                columns={columns}
                rowKey="id"
                loading={loading}
                pagination={{
                  showSizeChanger: true,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 条记录`
                }}
              />
            </Card>
          </TabPane>

          {/* 收益分析 */}
          <TabPane tab={<span><LineChartOutlined />收益分析</span>} key="analysis">
            <Row gutter={16}>
              <Col span={24}>
                <Card title="收益概览" style={{ marginBottom: '16px' }}>
                  {analysis && (
                    <Row gutter={16}>
                      <Col span={6}>
                        <Statistic
                          title="总收入"
                          value={analysis.total_stats?.total_income || 0}
                          precision={2}
                          prefix="¥"
                          valueStyle={{ color: '#52c41a' }}
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="净收入"
                          value={analysis.total_stats?.net_income || 0}
                          precision={2}
                          prefix="¥"
                          valueStyle={{ color: '#1890ff' }}
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="投资回报率"
                          value={analysis.roi_analysis?.roi || 0}
                          precision={2}
                          suffix="%"
                          valueStyle={{ color: '#faad14' }}
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="回本周期"
                          value={analysis.roi_analysis?.payback_months || 0}
                          precision={1}
                          suffix="月"
                          valueStyle={{ color: '#f5222d' }}
                        />
                      </Col>
                    </Row>
                  )}
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* 预期vs实际 */}
          <TabPane tab={<span><AlertOutlined />预期追踪</span>} key="forecast">
            <Card title="预期收入 vs 实际收入">
              <Alert
                message="收入预期管理"
                description="通过对比预期收入与实际收入，帮助您更好地规划资产收益。"
                type="info"
                showIcon
                style={{ marginBottom: '16px' }}
              />
              
              {/* 这里可以添加预期vs实际的图表和数据 */}
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <p>预期收入分析功能开发中...</p>
              </div>
            </Card>
          </TabPane>
        </Tabs>

        {/* 添加/编辑收入记录弹窗 */}
        <Modal
          title={editingIncome ? '编辑收入记录' : '添加收入记录'}
          open={modalVisible}
          onOk={handleSubmit}
          onCancel={() => setModalVisible(false)}
          width={800}
          okText="保存"
          cancelText="取消"
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="收入类型"
                  name="income_type"
                  rules={[{ required: true, message: '请选择收入类型' }]}
                >
                  <Select placeholder="选择收入类型">
                    {Object.entries(incomeTypeMap).map(([key, value]) => (
                      <Option key={key} value={key}>{value}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="收入金额"
                  name="amount"
                  rules={[
                    { required: true, message: '请输入收入金额' },
                    { type: 'number', min: 0.01, message: '金额必须大于0' }
                  ]}
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="收入金额"
                    precision={2}
                    min={0}
                    addonAfter="元"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="相关成本"
                  name="cost"
                  tooltip="产生此收入所需的直接成本（如维护费、手续费等）"
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="相关成本"
                    precision={2}
                    min={0}
                    addonAfter="元"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="税率"
                  name="tax_rate"
                  tooltip="适用税率百分比"
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    placeholder="税率"
                    precision={2}
                    min={0}
                    max={50}
                    addonAfter="%"
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  label="收入日期"
                  name="income_date"
                  rules={[{ required: true, message: '请选择收入日期' }]}
                >
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  label="预期收款日期"
                  name="expected_date"
                >
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  label="实际收款日期"
                  name="actual_date"
                >
                  <DatePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="付款方"
                  name="payer"
                >
                  <Input placeholder="付款方名称" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="支付方式"
                  name="payment_method"
                >
                  <Select placeholder="选择支付方式">
                    {Object.entries(paymentMethodMap).map(([key, value]) => (
                      <Option key={key} value={key}>{value}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="收款状态"
                  name="status"
                  rules={[{ required: true, message: '请选择收款状态' }]}
                >
                  <Select placeholder="选择收款状态">
                    {Object.entries(statusMap).map(([key, value]) => (
                      <Option key={key} value={key}>{value}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="周期性收入"
                  name="is_recurring"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="是" unCheckedChildren="否" />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              label="备注说明"
              name="notes"
            >
              <TextArea
                rows={3}
                placeholder="添加备注信息..."
                maxLength={500}
                showCount
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  )
}

export default AssetIncomeManagement