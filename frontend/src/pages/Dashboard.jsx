import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Progress, Tag, Typography, Empty, Divider, Tabs } from 'antd'
import { 
  DollarOutlined, 
  ProjectOutlined, 
  TrophyOutlined, 
  ClockCircleOutlined,
  AppstoreOutlined,
  ShoppingOutlined,
  RiseOutlined,
  FallOutlined,
  PercentageOutlined,
  WarningOutlined
} from '@ant-design/icons'
import { getProjects, getStatistics } from '../services/projects'
import { getAssetsStatistics } from '../services/assets'
import dayjs from 'dayjs'

const { Title } = Typography
const { TabPane } = Tabs

const Dashboard = () => {
  const [virtualStats, setVirtualStats] = useState({})
  const [fixedStats, setFixedStats] = useState({})
  const [recentProjects, setRecentProjects] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [projectStatsResponse, assetStatsResponse, projectsResponse] = await Promise.all([
        getStatistics(),
        getAssetsStatistics(),
        getProjects({ sort_by: 'created_at', order: 'desc' })
      ])

      if (projectStatsResponse.code === 200) {
        setVirtualStats(projectStatsResponse.data)
      }

      if (assetStatsResponse.code === 200) {
        setFixedStats(assetStatsResponse.data)
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

  return (
    <div>
      <Title level={2}>仪表盘</Title>
      
      <Row gutter={16}>
        {/* 左侧: 统计数据 */}
        <Col xs={24} lg={10}>
          {/* 虚拟资产（随风而逝） */}
          <Card 
            title={
              <span>
                <AppstoreOutlined style={{ marginRight: 8, color: '#ff6b6b' }} />
                随风而逝
              </span>
            }
            loading={loading}
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic
                  title="项目总数"
                  value={virtualStats.total_projects || 0}
                  prefix={<ProjectOutlined />}
                  valueStyle={{ color: '#1890ff', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="总投入"
                  value={virtualStats.total_amount || 0}
                  precision={2}
                  suffix="元"
                  valueStyle={{ color: '#52c41a', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="已消耗"
                  value={virtualStats.total_used_cost || 0}
                  precision={2}
                  suffix="元"
                  valueStyle={{ color: '#faad14', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="剩余价值"
                  value={virtualStats.total_remaining_value || 0}
                  precision={2}
                  suffix="元"
                  valueStyle={{ color: '#f5222d', fontSize: 18 }}
                />
              </Col>
            </Row>
            
            <Divider style={{ margin: '12px 0' }} />
            
            {virtualStats.status_distribution && (
              <Row gutter={8}>
                <Col span={8}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 20, color: '#1890ff', fontWeight: 'bold' }}>
                      {virtualStats.status_distribution.not_started || 0}
                    </div>
                    <div style={{ fontSize: 12, color: '#999' }}>未开始</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 20, color: '#52c41a', fontWeight: 'bold' }}>
                      {virtualStats.status_distribution.active || 0}
                    </div>
                    <div style={{ fontSize: 12, color: '#999' }}>消耗中</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 20, color: '#f5222d', fontWeight: 'bold' }}>
                      {virtualStats.status_distribution.expired || 0}
                    </div>
                    <div style={{ fontSize: 12, color: '#999' }}>已过期</div>
                  </div>
                </Col>
              </Row>
            )}
          </Card>

          {/* 固定资产（恒产生金） */}
          <Card 
            title={
              <span>
                <ShoppingOutlined style={{ marginRight: 8, color: '#5c7cfa' }} />
                恒产生金
              </span>
            }
            loading={loading}
            size="small"
            style={{ marginBottom: 16 }}
          >
            <Row gutter={[8, 8]}>
              <Col span={12}>
                <Statistic
                  title="资产总数"
                  value={fixedStats.overview?.total_assets || 0}
                  prefix={<ShoppingOutlined />}
                  valueStyle={{ color: '#5c7cfa', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="资产原值"
                  value={fixedStats.overview?.total_original_value || 0}
                  precision={2}
                  suffix="元"
                  valueStyle={{ color: '#52c41a', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="当前总值"
                  value={fixedStats.overview?.total_current_value || 0}
                  precision={2}
                  suffix="元"
                  valueStyle={{ color: '#1890ff', fontSize: 18 }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="累计折旧"
                  value={fixedStats.overview?.total_accumulated_depreciation || 0}
                  precision={2}
                  suffix="元"
                  valueStyle={{ color: '#faad14', fontSize: 18 }}
                />
              </Col>
            </Row>

            <Divider style={{ margin: '12px 0' }} />

            {fixedStats.status_distribution && fixedStats.status_distribution.length > 0 && (() => {
              const statusMap = {}
              fixedStats.status_distribution.forEach(item => {
                statusMap[item.status] = item.count
              })
              return (
                <Row gutter={8}>
                  <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 18, color: '#52c41a', fontWeight: 'bold' }}>
                        {statusMap.in_use || 0}
                      </div>
                      <div style={{ fontSize: 12, color: '#999' }}>使用中</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 18, color: '#faad14', fontWeight: 'bold' }}>
                        {statusMap.idle || 0}
                      </div>
                      <div style={{ fontSize: 12, color: '#999' }}>闲置</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 18, color: '#1890ff', fontWeight: 'bold' }}>
                        {statusMap.maintenance || 0}
                      </div>
                      <div style={{ fontSize: 12, color: '#999' }}>维修中</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 18, color: '#8c8c8c', fontWeight: 'bold' }}>
                        {statusMap.disposed || 0}
                      </div>
                      <div style={{ fontSize: 12, color: '#999' }}>已处置</div>
                    </div>
                  </Col>
                </Row>
              )
            })()}

            {fixedStats.overview?.depreciation_rate !== undefined && (
              <>
                <Divider style={{ margin: '12px 0' }} />
                <div>
                  <div style={{ fontSize: 12, color: '#999', marginBottom: 8 }}>整体折旧率</div>
                  <Progress 
                    percent={parseFloat(fixedStats.overview.depreciation_rate || 0)} 
                    strokeColor={{
                      '0%': '#52c41a',
                      '50%': '#faad14',
                      '100%': '#f5222d',
                    }}
                    format={percent => `${percent.toFixed(2)}%`}
                  />
                </div>
              </>
            )}
          </Card>
        </Col>

        {/* 右侧: 最近项目明细 */}
        <Col xs={24} lg={14}>
          <Card title="最近虚拟资产项目" loading={loading} size="small">
            {recentProjects.length === 0 ? (
              <Empty description="暂无项目数据" />
            ) : (
              <Table
                dataSource={recentProjects}
                columns={columns}
                rowKey="id"
                pagination={false}
                size="small"
                scroll={{ y: 600 }}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard