import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Progress, Tag, Typography, Empty, Badge, Tooltip, Alert } from 'antd'
import { 
  DollarOutlined, 
  ProjectOutlined, 
  ClockCircleOutlined,
  AppstoreOutlined,
  ShoppingOutlined,
  RiseOutlined,
  FallOutlined,
  WarningOutlined,
  DashboardOutlined,
  ThunderboltOutlined,
  FireOutlined,
  SafetyOutlined,
  TrophyOutlined,
  ExclamationCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons'
import { getProjects, getStatistics } from '../services/projects'
import { getAssetsStatistics } from '../services/assets'
import { getAnalyticsOverview } from '../services/analytics'
import dayjs from 'dayjs'

const { Title, Text } = Typography

const Dashboard = () => {
  const [virtualStats, setVirtualStats] = useState({})
  const [fixedStats, setFixedStats] = useState({})
  const [recentProjects, setRecentProjects] = useState([])
  const [analyticsData, setAnalyticsData] = useState({})
  const [loading, setLoading] = useState(true)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    fetchData()
    // 每秒更新时间
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [projectStatsResponse, assetStatsResponse, projectsResponse, analyticsResponse] = await Promise.all([
        getStatistics(),
        getAssetsStatistics(),
        getProjects({ sort_by: 'created_at', order: 'desc' }),
        getAnalyticsOverview().catch(() => ({ code: 500, data: {} }))
      ])

      if (projectStatsResponse.code === 200) {
        setVirtualStats(projectStatsResponse.data)
      }

      if (assetStatsResponse.code === 200) {
        setFixedStats(assetStatsResponse.data)
      }

      if (analyticsResponse.code === 200) {
        setAnalyticsData(analyticsResponse.data)
      }

      if (projectsResponse.code === 200) {
        const projects = projectsResponse.data
        // 按到期时间排序：快到期的排在前面
        const sortedProjects = projects.sort((a, b) => {
          const now = new Date()
          const endTimeA = new Date(a.end_time)
          const endTimeB = new Date(b.end_time)
          // 计算剩余天数
          const daysLeftA = Math.ceil((endTimeA - now) / (1000 * 60 * 60 * 24))
          const daysLeftB = Math.ceil((endTimeB - now) / (1000 * 60 * 60 * 24))
          return daysLeftA - daysLeftB  // 升序：快到期的在前
        })
        setRecentProjects(sortedProjects.slice(0, 5))
      }
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
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

  // 计算关键指标
  const calculateMetrics = () => {
    const totalInvest = (virtualStats.total_amount || 0) + (fixedStats.overview?.total_original_value || 0)
    const totalCurrent = (virtualStats.total_remaining_value || 0) + (fixedStats.overview?.total_current_value || 0)
    const totalIncome = fixedStats.overview?.total_income || 0
    const roi = totalInvest > 0 ? ((totalIncome / totalInvest) * 100) : 0
    const assetHealth = totalInvest > 0 ? ((totalCurrent / totalInvest) * 100) : 100
    
    return { totalInvest, totalCurrent, totalIncome, roi, assetHealth }
  }

  // 计算警告数
  const calculateWarnings = () => {
    let warnings = 0
    let criticals = 0
    
    // 检查快到期项目
    recentProjects.forEach(project => {
      const now = new Date()
      const end = new Date(project.end_time)
      const daysLeft = Math.ceil((end - now) / (1000 * 60 * 60 * 24))
      if (daysLeft < 0) criticals++
      else if (daysLeft < 7) warnings++
    })
    
    return { warnings, criticals }
  }

  // 仪表盘样式组件
  const GaugeCard = ({ title, value, max, unit, icon, color, gradient }) => {
    const percentage = Math.min((value / max) * 100, 100)
    const rotation = (percentage / 100) * 180 - 90
    
    return (
      <div style={{
        background: `linear-gradient(135deg, ${gradient[0]} 0%, ${gradient[1]} 100%)`,
        borderRadius: '20px',
        padding: '24px',
        color: 'white',
        boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
        position: 'relative',
        overflow: 'hidden',
        height: '100%'
      }}>
        <div style={{ position: 'absolute', top: 10, right: 10, fontSize: 32, opacity: 0.3 }}>
          {icon}
        </div>
        <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.9 }}>{title}</div>
        <div style={{ 
          width: 120, 
          height: 120, 
          margin: '0 auto',
          position: 'relative'
        }}>
          <svg width="120" height="70" style={{ overflow: 'visible' }}>
            <path
              d="M 10 60 A 50 50 0 0 1 110 60"
              fill="none"
              stroke="rgba(255,255,255,0.3)"
              strokeWidth="8"
              strokeLinecap="round"
            />
            <path
              d="M 10 60 A 50 50 0 0 1 110 60"
              fill="none"
              stroke="white"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${percentage * 1.57} 157`}
              style={{ transition: 'all 1s ease-out' }}
            />
          </svg>
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -20%)',
            textAlign: 'center',
            width: '100%'
          }}>
            <div style={{ fontSize: 28, fontWeight: 'bold' }}>
              {value.toFixed(1)}
            </div>
            <div style={{ fontSize: 12, opacity: 0.8 }}>{unit}</div>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: 8, fontSize: 12, opacity: 0.8 }}>
          最大值: {max}{unit}
        </div>
      </div>
    )
  }

  // 警告灯组件
  const WarningLight = ({ active, color, label, count }) => (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      padding: '8px 16px',
      background: active ? `${color}15` : '#f5f5f5',
      borderRadius: 12,
      border: `2px solid ${active ? color : '#d9d9d9'}`,
      transition: 'all 0.3s ease'
    }}>
      <div style={{
        width: 12,
        height: 12,
        borderRadius: '50%',
        background: active ? color : '#d9d9d9',
        boxShadow: active ? `0 0 12px ${color}` : 'none',
        animation: active ? 'pulse 2s infinite' : 'none'
      }} />
      <span style={{ fontWeight: 500, color: active ? color : '#999' }}>
        {label}
      </span>
      {active && count > 0 && (
        <Badge count={count} style={{ backgroundColor: color }} />
      )}
    </div>
  )

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category_name',
      key: 'category_name',
    },
    {
      title: '总金额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '剩余价值',
      dataIndex: 'remaining_value',
      key: 'remaining_value',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '剩余天数',
      dataIndex: 'end_time',
      key: 'days_left',
      render: (endTime) => {
        const now = new Date()
        const end = new Date(endTime)
        const daysLeft = Math.ceil((end - now) / (1000 * 60 * 60 * 24))
        
        let color = '#52c41a'
        let icon = null
        if (daysLeft < 0) {
          color = '#f5222d'
          icon = <WarningOutlined style={{ marginRight: 4 }} />
        } else if (daysLeft < 7) {
          color = '#faad14'
          icon = <ClockCircleOutlined style={{ marginRight: 4 }} />
        }
        
        return (
          <span style={{ color, fontWeight: 'bold' }}>
            {icon}
            {daysLeft < 0 ? `已过期${Math.abs(daysLeft)}天` : `${daysLeft}天`}
          </span>
        )
      },
    },
    {
      title: '消耗进度',
      dataIndex: 'progress',
      key: 'progress',
      render: (value) => <Progress percent={value} size="small" />,
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
    },
  ]

  const metrics = calculateMetrics()
  const warnings = calculateWarnings()

  return (
    <div style={{ padding: '0 0 24px 0' }}>
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.95); }
          }
          @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .dashboard-card {
            animation: slideIn 0.5s ease-out;
          }
        `}
      </style>

      {/* 顶部控制台 */}
      <div style={{
        background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        borderRadius: '20px',
        padding: '24px',
        marginBottom: 24,
        color: 'white',
        boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ position: 'absolute', top: -50, right: -50, width: 200, height: 200, background: 'rgba(255,255,255,0.05)', borderRadius: '50%' }} />
        <div style={{ position: 'absolute', bottom: -30, left: -30, width: 150, height: 150, background: 'rgba(255,255,255,0.03)', borderRadius: '50%' }} />
        
        <Row align="middle" justify="space-between">
          <Col>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <DashboardOutlined style={{ fontSize: 48 }} />
              <div>
                <Title level={2} style={{ color: 'white', margin: 0 }}>资产驾驶舱</Title>
                <Text style={{ color: 'rgba(255,255,255,0.8)' }}>实时监控您的资产运行状况</Text>
              </div>
            </div>
          </Col>
          <Col>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                {currentTime.toLocaleTimeString('zh-CN')}
              </div>
              <div style={{ fontSize: 14, opacity: 0.8 }}>
                {currentTime.toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              </div>
            </div>
          </Col>
        </Row>

        {/* 警告灯板 */}
        <Row gutter={16} style={{ marginTop: 24 }}>
          <Col span={8}>
            <WarningLight 
              active={warnings.criticals > 0} 
              color="#ff4d4f" 
              label="紧急警告"
              count={warnings.criticals}
            />
          </Col>
          <Col span={8}>
            <WarningLight 
              active={warnings.warnings > 0} 
              color="#faad14" 
              label="注意事项"
              count={warnings.warnings}
            />
          </Col>
          <Col span={8}>
            <WarningLight 
              active={warnings.criticals === 0 && warnings.warnings === 0} 
              color="#52c41a" 
              label="系统正常"
              count={0}
            />
          </Col>
        </Row>
      </div>

      {/* 主仪表盘区域 */}
      <Row gutter={[16, 16]}>
        {/* 核心仪表 */}
        <Col xs={24} lg={6} className="dashboard-card">
          <GaugeCard
            title="投资回报率 ROI"
            value={metrics.roi}
            max={100}
            unit="%"
            icon={<TrophyOutlined />}
            gradient={['#f093fb', '#f5576c']}
          />
        </Col>
        
        <Col xs={24} lg={6} className="dashboard-card">
          <GaugeCard
            title="资产健康度"
            value={metrics.assetHealth}
            max={100}
            unit="%"
            icon={<SafetyOutlined />}
            gradient={['#4facfe', '#00f2fe']}
          />
        </Col>

        <Col xs={24} lg={6} className="dashboard-card">
          <div style={{
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            borderRadius: '20px',
            padding: '24px',
            color: 'white',
            boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            height: '100%'
          }}>
            <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.9 }}>总投入</div>
            <div style={{ fontSize: 32, fontWeight: 'bold', marginBottom: 8 }}>
              ¥{(metrics.totalInvest / 10000).toFixed(2)}
            </div>
            <div style={{ fontSize: 14, opacity: 0.8 }}>万元</div>
            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.3)' }}>
              <Row>
                <Col span={12}>
                  <div style={{ fontSize: 12, opacity: 0.8 }}>虚拟资产</div>
                  <div style={{ fontSize: 18, fontWeight: 'bold' }}>
                    ¥{((virtualStats.total_amount || 0) / 10000).toFixed(1)}万
                  </div>
                </Col>
                <Col span={12}>
                  <div style={{ fontSize: 12, opacity: 0.8 }}>固定资产</div>
                  <div style={{ fontSize: 18, fontWeight: 'bold' }}>
                    ¥{((fixedStats.overview?.total_original_value || 0) / 10000).toFixed(1)}万
                  </div>
                </Col>
              </Row>
            </div>
          </div>
        </Col>

        <Col xs={24} lg={6} className="dashboard-card">
          <div style={{
            background: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
            borderRadius: '20px',
            padding: '24px',
            color: 'white',
            boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            height: '100%'
          }}>
            <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.9 }}>累计收益</div>
            <div style={{ fontSize: 32, fontWeight: 'bold', marginBottom: 8 }}>
              ¥{(metrics.totalIncome / 10000).toFixed(2)}
            </div>
            <div style={{ fontSize: 14, opacity: 0.8 }}>万元</div>
            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.3)' }}>
              <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>当前总值</div>
              <div style={{ fontSize: 18, fontWeight: 'bold' }}>
                ¥{(metrics.totalCurrent / 10000).toFixed(2)}万
              </div>
            </div>
          </div>
        </Col>
      </Row>

      {/* 详细统计区域 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        {/* 虚拟资产统计 */}
        <Col xs={24} lg={12}>
          <Card 
            title={
              <span>
                <AppstoreOutlined style={{ marginRight: 8, color: '#ff6b6b' }} />
                随风而逝 - 虚拟资产
              </span>
            }
            loading={loading}
            bordered={false}
            style={{ 
              borderRadius: 16,
              boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
            }}
          >
            <Row gutter={[16, 16]}>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: 16, background: '#f0f5ff', borderRadius: 12 }}>
                  <ProjectOutlined style={{ fontSize: 32, color: '#1890ff', marginBottom: 8 }} />
                  <div style={{ fontSize: 28, fontWeight: 'bold', color: '#1890ff' }}>
                    {virtualStats.total_projects || 0}
                  </div>
                  <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>项目总数</div>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: 16, background: '#f6ffed', borderRadius: 12 }}>
                  <RiseOutlined style={{ fontSize: 32, color: '#52c41a', marginBottom: 8 }} />
                  <div style={{ fontSize: 28, fontWeight: 'bold', color: '#52c41a' }}>
                    {virtualStats.status_distribution?.active || 0}
                  </div>
                  <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>消耗中</div>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: 16, background: '#fff1f0', borderRadius: 12 }}>
                  <FallOutlined style={{ fontSize: 32, color: '#f5222d', marginBottom: 8 }} />
                  <div style={{ fontSize: 28, fontWeight: 'bold', color: '#f5222d' }}>
                    {virtualStats.status_distribution?.expired || 0}
                  </div>
                  <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>已过期</div>
                </div>
              </Col>
            </Row>

            <div style={{ marginTop: 24 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="已消耗金额"
                    value={virtualStats.total_used_cost || 0}
                    precision={2}
                    prefix={<FireOutlined style={{ color: '#faad14' }} />}
                    suffix="元"
                    valueStyle={{ color: '#faad14' }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="剩余价值"
                    value={virtualStats.total_remaining_value || 0}
                    precision={2}
                    prefix={<ThunderboltOutlined style={{ color: '#52c41a' }} />}
                    suffix="元"
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
              </Row>
            </div>
          </Card>
        </Col>

        {/* 固定资产统计 */}
        <Col xs={24} lg={12}>
          <Card 
            title={
              <span>
                <ShoppingOutlined style={{ marginRight: 8, color: '#5c7cfa' }} />
                恒产生金 - 固定资产
              </span>
            }
            loading={loading}
            bordered={false}
            style={{ 
              borderRadius: 16,
              boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
            }}
          >
            <Row gutter={[16, 16]}>
              {fixedStats.status_distribution && fixedStats.status_distribution.length > 0 && (() => {
                const statusMap = {}
                fixedStats.status_distribution.forEach(item => {
                  statusMap[item.status] = item.count
                })
                return (
                  <>
                    <Col span={6}>
                      <div style={{ textAlign: 'center', padding: 16, background: '#f6ffed', borderRadius: 12 }}>
                        <CheckCircleOutlined style={{ fontSize: 28, color: '#52c41a', marginBottom: 8 }} />
                        <div style={{ fontSize: 24, fontWeight: 'bold', color: '#52c41a' }}>
                          {statusMap.in_use || 0}
                        </div>
                        <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>使用中</div>
                      </div>
                    </Col>
                    <Col span={6}>
                      <div style={{ textAlign: 'center', padding: 16, background: '#fffbe6', borderRadius: 12 }}>
                        <ClockCircleOutlined style={{ fontSize: 28, color: '#faad14', marginBottom: 8 }} />
                        <div style={{ fontSize: 24, fontWeight: 'bold', color: '#faad14' }}>
                          {statusMap.idle || 0}
                        </div>
                        <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>闲置</div>
                      </div>
                    </Col>
                    <Col span={6}>
                      <div style={{ textAlign: 'center', padding: 16, background: '#f0f5ff', borderRadius: 12 }}>
                        <ExclamationCircleOutlined style={{ fontSize: 28, color: '#1890ff', marginBottom: 8 }} />
                        <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                          {statusMap.maintenance || 0}
                        </div>
                        <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>维修中</div>
                      </div>
                    </Col>
                    <Col span={6}>
                      <div style={{ textAlign: 'center', padding: 16, background: '#fafafa', borderRadius: 12 }}>
                        <div style={{ fontSize: 24, fontWeight: 'bold', color: '#8c8c8c', marginTop: 8 }}>
                          {statusMap.disposed || 0}
                        </div>
                        <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>已处置</div>
                      </div>
                    </Col>
                  </>
                )
              })()}
            </Row>

            <div style={{ marginTop: 24 }}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="当前总值"
                    value={fixedStats.overview?.total_current_value || 0}
                    precision={2}
                    prefix={<DollarOutlined style={{ color: '#1890ff' }} />}
                    suffix="元"
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="累计折旧"
                    value={fixedStats.overview?.total_accumulated_depreciation || 0}
                    precision={2}
                    prefix={<FallOutlined style={{ color: '#faad14' }} />}
                    suffix="元"
                    valueStyle={{ color: '#faad14' }}
                  />
                </Col>
              </Row>
              
              {fixedStats.overview?.depreciation_rate !== undefined && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ fontSize: 12, color: '#999', marginBottom: 8 }}>整体折旧率</div>
                  <Progress 
                    percent={parseFloat(fixedStats.overview.depreciation_rate || 0)} 
                    strokeColor={{
                      '0%': '#52c41a',
                      '50%': '#faad14',
                      '100%': '#f5222d',
                    }}
                    strokeWidth={12}
                    format={percent => `${percent.toFixed(2)}%`}
                  />
                </div>
              )}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 紧急关注区域 */}
      {(warnings.criticals > 0 || warnings.warnings > 0) && (
        <Card 
          title={
            <span>
              <WarningOutlined style={{ marginRight: 8, color: '#ff4d4f' }} />
              需要关注的项目
            </span>
          }
          style={{ 
            marginTop: 16,
            borderRadius: 16,
            boxShadow: '0 4px 16px rgba(0,0,0,0.08)'
          }}
          bordered={false}
        >
          <Table
            dataSource={recentProjects.filter(p => {
              const now = new Date()
              const end = new Date(p.end_time)
              const daysLeft = Math.ceil((end - now) / (1000 * 60 * 60 * 24))
              return daysLeft < 7
            })}
            columns={columns}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </Card>
      )}
    </div>
  )
}

export default Dashboard