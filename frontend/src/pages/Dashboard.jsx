import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Progress, Tag, Typography, Empty } from 'antd'
import { 
  DollarOutlined, 
  ProjectOutlined, 
  TrophyOutlined, 
  ClockCircleOutlined 
} from '@ant-design/icons'
import { getProjects, getStatistics } from '../services/projects'
import dayjs from 'dayjs'

const { Title } = Typography

const Dashboard = () => {
  const [statistics, setStatistics] = useState({})
  const [recentProjects, setRecentProjects] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [statsResponse, projectsResponse] = await Promise.all([
        getStatistics(),
        getProjects({ sort_by: 'created_at', order: 'desc' })
      ])

      if (statsResponse.code === 200) {
        setStatistics(statsResponse.data)
      }

      if (projectsResponse.code === 200) {
        setRecentProjects(projectsResponse.data.slice(0, 5))
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
      
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="项目总数"
              value={statistics.total_projects || 0}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总投入金额"
              value={statistics.total_amount || 0}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="元"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="已消耗成本"
              value={statistics.total_used_cost || 0}
              precision={2}
              prefix={<ClockCircleOutlined />}
              suffix="元"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="剩余价值"
              value={statistics.total_remaining_value || 0}
              precision={2}
              prefix={<TrophyOutlined />}
              suffix="元"
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 项目状态分布 */}
      {statistics.status_distribution && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={24}>
            <Card title="项目状态分布">
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="未开始"
                    value={statistics.status_distribution.not_started || 0}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="消耗中"
                    value={statistics.status_distribution.active || 0}
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="已过期"
                    value={statistics.status_distribution.expired || 0}
                    valueStyle={{ color: '#f5222d' }}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}

      {/* 最近项目 */}
      <Card title="最近项目" loading={loading}>
        {recentProjects.length === 0 ? (
          <Empty description="暂无项目数据" />
        ) : (
          <Table
            dataSource={recentProjects}
            columns={columns}
            rowKey="id"
            pagination={false}
            size="small"
          />
        )}
      </Card>
    </div>
  )
}

export default Dashboard