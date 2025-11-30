import React, { useState, useEffect } from 'react'
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Spin, 
  Alert, 
  Select, 
  DatePicker, 
  Button,
  Table,
  Progress,
  Tag,
  Typography,
  Tooltip,
  Tabs,
  Space
} from 'antd'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  ResponsiveContainer 
} from 'recharts'
import { 
  DollarOutlined, 
  ProjectOutlined, 
  TrophyOutlined, 
  ClockCircleOutlined,
  AreaChartOutlined,
  PieChartOutlined,
  BarChartOutlined,
  BankOutlined,
  AlertOutlined
} from '@ant-design/icons'
import { getAnalyticsOverview, getAnalyticsTrends, getCategoryAnalysis } from '../services/analytics'
import { getAssetsStatistics } from '../services/assets'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { Option } = Select
const { RangePicker } = DatePicker
const { TabPane } = Tabs

const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#fa8c16', '#13c2c2', '#eb2f96']

const Analytics = () => {
  const [loading, setLoading] = useState(true)
  const [overviewData, setOverviewData] = useState({})
  const [trendsData, setTrendsData] = useState([])
  const [categoryData, setCategoryData] = useState([])
  const [assetsStatistics, setAssetsStatistics] = useState(null) // 固定资产统计
  const [selectedPeriod, setSelectedPeriod] = useState('month')
  const [dateRange, setDateRange] = useState([])
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('projects') // 默认显示项目分析

  useEffect(() => {
    fetchData()
  }, [selectedPeriod, dateRange, activeTab]) // 添加activeTab依赖

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      if (activeTab === 'projects') {
        // 项目分析数据
        const [overviewResponse, trendsResponse, categoryResponse] = await Promise.all([
          getAnalyticsOverview(),
          getAnalyticsTrends({ 
            period: selectedPeriod,
            start_date: dateRange[0]?.format('YYYY-MM-DD'),
            end_date: dateRange[1]?.format('YYYY-MM-DD')
          }),
          getCategoryAnalysis()
        ])

        if (overviewResponse.code === 200) {
          setOverviewData(overviewResponse.data)
        } else {
          throw new Error(overviewResponse.message || '获取概览数据失败')
        }

        if (trendsResponse.code === 200) {
          setTrendsData(trendsResponse.data.trends)
        } else {
          throw new Error(trendsResponse.message || '获取趋势数据失败')
        }

        if (categoryResponse.code === 200) {
          setCategoryData(categoryResponse.data)
        } else {
          throw new Error(categoryResponse.message || '获取分类数据失败')
        }
      } else if (activeTab === 'assets') {
        // 固定资产分析数据
        const assetsResponse = await getAssetsStatistics()
        if (assetsResponse.code === 200) {
          setAssetsStatistics(assetsResponse.data)
        } else {
          throw new Error(assetsResponse.message || '获取资产数据失败')
        }
      }

    } catch (err) {
      console.error('获取分析数据失败:', err)
      const errorMessage = err.response?.data?.message || err.message || '获取数据失败，请稍后重试'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handlePeriodChange = (value) => {
    setSelectedPeriod(value)
  }

  const handleDateRangeChange = (dates) => {
    setDateRange(dates || [])
  }

  const handleRefresh = () => {
    fetchData()
  }

  // 格式化饼图数据
  const formatPieChartData = (data) => {
    return data.map(item => ({
      name: item.category_name,
      value: item.total_amount,
      count: item.project_count
    }))
  }

  // 状态分布数据
  const statusDistributionData = overviewData.status_distribution ? [
    { name: '未开始', value: overviewData.status_distribution.not_started, color: '#1890ff' },
    { name: '消耗中', value: overviewData.status_distribution.active, color: '#52c41a' },
    { name: '已过期', value: overviewData.status_distribution.expired, color: '#f5222d' }
  ] : []

  // 分类分析表格列定义
  const categoryColumns = [
    {
      title: '分类',
      dataIndex: 'category_name',
      key: 'category_name',
      render: (text, record) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div 
            style={{
              width: 12,
              height: 12,
              backgroundColor: record.category_color,
              borderRadius: '50%',
              marginRight: 8
            }}
          />
          {text}
        </div>
      )
    },
    {
      title: '项目数',
      dataIndex: 'project_count',
      key: 'project_count',
    },
    {
      title: '投入金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.total_amount - b.total_amount,
    },
    {
      title: '已消耗',
      dataIndex: 'used_cost',
      key: 'used_cost',
      render: (value) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.used_cost - b.used_cost,
    },
    {
      title: '剩余价值',
      dataIndex: 'remaining_value',
      key: 'remaining_value',
      render: (value) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.remaining_value - b.remaining_value,
    },
    {
      title: '利用率',
      dataIndex: 'utilization_rate',
      key: 'utilization_rate',
      render: (value) => (
        <div>
          <Progress percent={value} size="small" />
          <Text type="secondary">{value.toFixed(1)}%</Text>
        </div>
      ),
      sorter: (a, b) => a.utilization_rate - b.utilization_rate,
    },
    {
      title: '状态分布',
      key: 'status',
      render: (_, record) => (
        <div>
          <Tag color="green">消耗中: {record.status_breakdown.active}</Tag>
          <Tag color="orange">未开始: {record.status_breakdown.not_started}</Tag>
          <Tag color="red">已过期: {record.status_breakdown.expired}</Tag>
        </div>
      )
    }
  ]

  if (error) {
    return (
      <div>
        <Title level={2}><AreaChartOutlined /> BI 分析</Title>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button size="small" danger onClick={handleRefresh}>
              重新加载
            </Button>
          }
        />
      </div>
    )
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
            <div style={{ display: 'flex', alignItems: 'center' }}>
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
                <AreaChartOutlined style={{ fontSize: '32px', color: 'white' }} />
              </div>
              <div>
                <Title level={2} style={{ color: 'white', margin: 0, fontWeight: 'bold' }}>
                  BI 分析
                </Title>
                <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', marginTop: '4px' }}>
                  数据驱动决策，智能分析您的资产状况
                </div>
              </div>
            </div>
          </Col>
          <Col>
            <Space>
              {activeTab === 'projects' && (
                <>
                  <Select
                    value={selectedPeriod}
                    onChange={handlePeriodChange}
                    style={{ 
                      width: 120,
                      borderRadius: '10px'
                    }}
                  >
                    <Option value="day">按天</Option>
                    <Option value="week">按周</Option>
                    <Option value="month">按月</Option>
                    <Option value="year">按年</Option>
                  </Select>
                  
                  <RangePicker
                    value={dateRange}
                    onChange={handleDateRangeChange}
                    allowClear
                    style={{ borderRadius: '10px' }}
                  />
                </>
              )}
              
              <Button 
                onClick={handleRefresh} 
                loading={loading}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  color: 'white',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '10px',
                  fontWeight: 500
                }}
              >
                刷新数据
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {error ? (
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '24px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
        }}>
          <Alert
            message="加载失败"
            description={error}
            type="error"
            showIcon
            action={
              <Button size="small" danger onClick={handleRefresh}>
                重新加载
              </Button>
            }
          />
        </div>
      ) : (
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '24px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
        }}>
          <Tabs 
            activeKey={activeTab} 
            onChange={setActiveTab}
            items={[
            {
              key: 'projects',
              label: (
                <span>
                  <ProjectOutlined />
                  项目分析
                </span>
              ),
              children: (
                <ProjectAnalytics 
                  loading={loading}
                  overviewData={overviewData}
                  trendsData={trendsData}
                  categoryData={categoryData}
                  statusDistributionData={statusDistributionData}
                  categoryColumns={categoryColumns}
                  formatPieChartData={formatPieChartData}
                />
              )
            },
            {
              key: 'assets',
              label: (
                <span>
                  <BankOutlined />
                  资产分析
                </span>
              ),
              children: (
                <AssetsAnalytics 
                  loading={loading}
                  assetsStatistics={assetsStatistics}
                />
              )
            }
          ]}
        />
        </div>
      )}

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(20px); }
        }
      `}</style>
    </div>
  )
}

export default Analytics

// 项目分析组件
const ProjectAnalytics = ({ 
  loading, 
  overviewData, 
  trendsData, 
  categoryData, 
  statusDistributionData,
  categoryColumns,
  formatPieChartData 
}) => (
  <Spin spinning={loading}>
    <div style={{ background: '#f5f7fa', padding: '16px', borderRadius: '12px' }}>
      {/* 核心指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="hover-lift" style={{ borderRadius: '16px' }}>
            <Statistic
              title="项目总数"
              value={overviewData.total_projects || 0}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#667eea', fontWeight: 'bold' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="hover-lift" style={{ borderRadius: '16px' }}>
            <Statistic
              title="总投入"
              value={overviewData.total_amount || 0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="hover-lift" style={{ borderRadius: '16px' }}>
            <Statistic
              title="已消耗"
              value={overviewData.total_used_cost || 0}
              precision={2}
              prefix={<ClockCircleOutlined />}
              suffix="元"
              valueStyle={{ color: '#faad14', fontWeight: 'bold' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="hover-lift" style={{ borderRadius: '16px' }}>
            <Statistic
              title="剩余价值"
              value={overviewData.total_remaining_value || 0}
              precision={2}
              prefix={<TrophyOutlined />}
              suffix="元"
              valueStyle={{ color: '#764ba2', fontWeight: 'bold' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 趋势图和状态分布 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card 
            title={<><BarChartOutlined /> 投入趋势分析</>}
            className="hover-lift"
            style={{ borderRadius: '16px' }}
          >
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <RechartsTooltip />
              <Bar dataKey="total_amount" fill="#1890ff" />
            </BarChart>
          </ResponsiveContainer>
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card 
            title={<><PieChartOutlined /> 项目状态分布</>}
            className="hover-lift"
            style={{ borderRadius: '16px' }}
          >
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusDistributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <RechartsTooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </Col>
    </Row>

      {/* 分类投入分布饼图 */}
      {categoryData.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Card 
              title={<><PieChartOutlined /> 分类投入分布</>}
              className="hover-lift"
              style={{ borderRadius: '16px' }}
            >
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={formatPieChartData(categoryData)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, count }) => `${name}: ¥${value.toFixed(2)} (${count}个项目)`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  formatter={(value, name) => [`¥${value.toFixed(2)}`, '投入金额']}
                />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
      )}

      {/* 分类详细分析表格 */}
      <Card 
        title="分类详细分析" 
        extra={
          <Text type="secondary">点击表格行可查看该分类的项目明细</Text>
        }
        className="hover-lift"
        style={{ borderRadius: '16px' }}
      >
      <Table
        columns={categoryColumns}
        dataSource={categoryData}
        rowKey="category_id"
        pagination={{ pageSize: 10 }}
        onRow={(record) => ({
          onClick: () => {
            // TODO: 跳转到项目明细页面，传递分类ID
            console.log('跳转到分类明细:', record.category_id)
          },
          style: { cursor: 'pointer' }
        })}
      />
      </Card>
    </div>

    <style>{`
      .hover-lift {
        transition: all 0.3s ease;
      }
      .hover-lift:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15) !important;
      }
    `}</style>
  </Spin>
)

// 固定资产分析组件
const AssetsAnalytics = ({ loading, assetsStatistics }) => {
  if (!assetsStatistics) {
    return (
      <Spin spinning={loading}>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Text type="secondary">暂无固定资产数据</Text>
        </div>
      </Spin>
    )
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

  // ROI表格列定义
  const roiColumns = [
    {
      title: '资产名称',
      dataIndex: 'asset_name',
      key: 'asset_name',
    },
    {
      title: '原值',
      dataIndex: 'original_value',
      key: 'original_value',
      render: (value) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.original_value - b.original_value,
    },
    {
      title: '累计收益',
      dataIndex: 'total_income',
      key: 'total_income',
      render: (value) => `¥${value.toFixed(2)}`,
      sorter: (a, b) => a.total_income - b.total_income,
    },
    {
      title: 'ROI',
      dataIndex: 'roi',
      key: 'roi',
      render: (value) => (
        <Tag color={value >= 10 ? 'green' : value >= 5 ? 'orange' : 'red'}>
          {value.toFixed(2)}%
        </Tag>
      ),
      sorter: (a, b) => a.roi - b.roi,
    },
    {
      title: '收入记录数',
      dataIndex: 'income_count',
      key: 'income_count',
      sorter: (a, b) => a.income_count - b.income_count,
    }
  ]

  return (
    <Spin spinning={loading}>
      <div style={{ background: '#f5f7fa', padding: '16px', borderRadius: '12px' }}>
      {/* 检查 assetsStatistics 是否有效 */}
      {!assetsStatistics?.overview ? (
        <Alert
          message="暂无资产数据"
          description="请先添加资产信息"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      ) : (
        <>
          {/* 核心指标卡片 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card className="hover-lift" style={{ borderRadius: '16px' }}>
                <Statistic
                  title="资产总数"
                  value={assetsStatistics.overview.total_assets}
                  prefix={<BankOutlined />}
                  valueStyle={{ color: '#667eea', fontWeight: 'bold' }}
                  suffix="个"
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card className="hover-lift" style={{ borderRadius: '16px' }}>
                <Statistic
                  title="原值总计"
                  value={assetsStatistics.overview.total_original_value}
                  precision={2}
                  prefix={<DollarOutlined />}
                  suffix="元"
                  valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card className="hover-lift" style={{ borderRadius: '16px' }}>
                <Statistic
                  title="当前价值"
                  value={assetsStatistics.overview.total_current_value}
                  precision={2}
                  prefix={<TrophyOutlined />}
                  suffix="元"
                  valueStyle={{ color: '#faad14', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card className="hover-lift" style={{ borderRadius: '16px' }}>
                <Statistic
                  title="累计折旧"
                  value={assetsStatistics.overview.total_accumulated_depreciation}
                  precision={2}
                  prefix={<ClockCircleOutlined />}
                  suffix="元"
                  valueStyle={{ color: '#764ba2', fontWeight: 'bold' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 状态分布 */}
          {assetsStatistics.status_distribution && assetsStatistics.status_distribution.length > 0 && (
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col span={24}>
                <Card 
                  title={<><PieChartOutlined /> 资产状态分布</>}
                  className="hover-lift"
                  style={{ borderRadius: '16px' }}
                >
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={assetsStatistics.status_distribution.map(item => ({
                          name: getStatusText(item.status),
                          value: item.count
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}个`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {assetsStatistics.status_distribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          )}
        </>
      )}
      </div>

      <style>{`
        .hover-lift {
          transition: all 0.3s ease;
        }
        .hover-lift:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 40px rgba(0,0,0,0.15) !important;
        }
      `}</style>
    </Spin>
  )
}
