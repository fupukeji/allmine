import { useState, useEffect } from 'react'
import { Card, Grid, ProgressBar, Toast, Skeleton } from 'antd-mobile'
import { AppstoreOutline, BillOutline, FileOutline, PieOutline } from 'antd-mobile-icons'
import { useNavigate } from 'react-router-dom'
import { getDashboardStats, getExpiringAlerts } from '../../services/dashboard'
import './Dashboard.css'

const Dashboard = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalValue: 0,
    fixedValue: 0,
    virtualValue: 0,
    projectCount: 0,
    assetCount: 0
  })
  const [expiringList, setExpiringList] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // 并发请求统计数据和到期提醒
      const [statsRes, expiringRes] = await Promise.all([
        getDashboardStats().catch(() => ({ data: null })),
        getExpiringAlerts().catch(() => ({ data: [] }))
      ])

      if (statsRes.data) {
        setStats({
          totalValue: statsRes.data.total_value || 0,
          fixedValue: statsRes.data.fixed_asset_value || 0,
          virtualValue: statsRes.data.virtual_asset_value || 0,
          projectCount: statsRes.data.project_count || 0,
          assetCount: statsRes.data.asset_count || 0
        })
      }

      if (expiringRes.data && expiringRes.data.length > 0) {
        setExpiringList(expiringRes.data.slice(0, 3)) // 只显示前3个
      }
    } catch (error) {
      console.error('加载数据失败:', error)
      Toast.show({
        icon: 'fail',
        content: '加载数据失败'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleNavigation = (path) => {
    navigate(path)
  }

  const calculateDaysLeft = (expiryDate) => {
    const today = new Date()
    const expiry = new Date(expiryDate)
    const diffTime = expiry - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const calculateProgress = (purchaseDate, expiryDate) => {
    const purchase = new Date(purchaseDate)
    const expiry = new Date(expiryDate)
    const today = new Date()
    
    const totalDays = (expiry - purchase) / (1000 * 60 * 60 * 24)
    const usedDays = (today - purchase) / (1000 * 60 * 60 * 24)
    
    return Math.min(100, Math.max(0, (usedDays / totalDays) * 100))
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <Card>
          <Skeleton.Title animated />
          <Skeleton.Paragraph lineCount={3} animated />
        </Card>
        <Card style={{ marginTop: '12px' }}>
          <Skeleton.Paragraph lineCount={5} animated />
        </Card>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      {/* 顶部Logo和问候 */}
      <div className="dashboard-header">
        <img src="/logo.jpg" alt="TimeValue" className="header-logo" />
        <div className="header-text">
          <h1>TimeValue</h1>
          <p>恒产生金 - 让每一份资产都创造价值</p>
        </div>
      </div>

      {/* 顶部资产卡片 */}
      <Card className="total-card">
        <div className="total-label">总资产价值</div>
        <div className="total-value">¥{stats.totalValue.toLocaleString()}</div>
        <div className="total-breakdown">
          固定资产 ¥{stats.fixedValue.toLocaleString()} | 虚拟资产 ¥{stats.virtualValue.toLocaleString()}
        </div>
        <div className="total-count">
          {stats.assetCount} 个固定资产 · {stats.projectCount} 个虚拟资产
        </div>
      </Card>

      {/* 功能网格 */}
      <Card className="function-card">
        <Grid columns={4} gap={12}>
          <Grid.Item onClick={() => handleNavigation('/virtual-assets')}>
            <div className="function-item">
              <AppstoreOutline fontSize={28} color="#667eea" />
              <div className="function-name">随风而逝</div>
            </div>
          </Grid.Item>
          <Grid.Item onClick={() => handleNavigation('/fixed-assets')}>
            <div className="function-item">
              <BillOutline fontSize={28} color="#52c41a" />
              <div className="function-name">恒产生金</div>
            </div>
          </Grid.Item>
          <Grid.Item onClick={() => handleNavigation('/reports')}>
            <div className="function-item">
              <FileOutline fontSize={28} color="#faad14" />
              <div className="function-name">AI报告</div>
            </div>
          </Grid.Item>
          <Grid.Item onClick={() => Toast.show('功能开发中...')}>
            <div className="function-item">
              <PieOutline fontSize={28} color="#f5222d" />
              <div className="function-name">数据分析</div>
            </div>
          </Grid.Item>
        </Grid>
      </Card>

      {/* 快到期提醒 */}
      {expiringList.length > 0 && (
        <Card title="⚠️ 快到期提醒" className="alert-card">
          {expiringList.map((item, index) => {
            const daysLeft = calculateDaysLeft(item.expiry_date)
            const progress = calculateProgress(item.purchase_date, item.expiry_date)
            
            return (
              <div key={index} className="alert-item" style={{ marginBottom: index < expiringList.length - 1 ? '16px' : 0 }}>
                <div className="alert-info">
                  <div className="alert-name">{item.name}</div>
                  <div className="alert-days">
                    {daysLeft > 0 ? `剩余 ${daysLeft} 天` : '已过期'}
                  </div>
                </div>
                <div className="alert-value">¥{item.purchase_price?.toLocaleString()}</div>
                <ProgressBar percent={progress} style={{ marginTop: '8px' }} />
              </div>
            )
          })}
        </Card>
      )}
    </div>
  )
}

export default Dashboard
