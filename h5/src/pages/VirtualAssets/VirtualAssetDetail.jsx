/**
 * 虚拟资产详情页
 * 包含资产信息、时间进度、预测分析
 */

import { useState, useMemo } from 'react'
import { Popup, Card, List, Button, ProgressBar, Tag, Toast } from 'antd-mobile'
import { 
  LeftOutline,
  ClockCircleOutline, 
  PayCircleOutline,
  CalendarOutline,
  PieOutline,
  EyeOutline,
  EyeInvisibleOutline
} from 'antd-mobile-icons'
import dayjs from 'dayjs'
import { useSwipeBack } from '../../hooks'
import './VirtualAssetDetail.css'

const VirtualAssetDetail = ({ visible, onClose, asset }) => {
  const [activeTab, setActiveTab] = useState('overview')
  const [showPassword, setShowPassword] = useState(false)
  
  // 左滑返回手势
  const swipeHandlers = useSwipeBack(onClose)

  // 计算资产相关数据
  const assetData = useMemo(() => {
    if (!asset) return null

    const today = dayjs()
    const startDate = dayjs(asset.start_date || asset.start_time)
    const endDate = dayjs(asset.end_date || asset.end_time)
    
    const totalDays = endDate.diff(startDate, 'day')
    const usedDays = today.diff(startDate, 'day')
    const remainingDays = endDate.diff(today, 'day')
    const progress = Math.min(100, Math.max(0, (usedDays / totalDays) * 100))
    
    // 日均价值
    const dailyValue = asset.total_amount / totalDays
    // 已消耗价值
    const usedValue = dailyValue * Math.max(0, usedDays)
    // 剩余价值
    const remainingValue = asset.total_amount - usedValue
    
    // 预测：如果续费，年化成本
    const annualCost = dailyValue * 365
    
    // 状态判断
    let status = 'active'
    let statusText = '进行中'
    let statusColor = '#52c41a'
    
    if (remainingDays < 0) {
      status = 'expired'
      statusText = '已过期'
      statusColor = '#999'
    } else if (remainingDays <= 7) {
      status = 'expiring'
      statusText = '即将到期'
      statusColor = '#ff4d4f'
    } else if (remainingDays <= 30) {
      status = 'warning'
      statusText = '注意续费'
      statusColor = '#faad14'
    }

    return {
      totalDays,
      usedDays: Math.max(0, usedDays),
      remainingDays: Math.max(0, remainingDays),
      progress,
      dailyValue,
      usedValue: Math.max(0, usedValue),
      remainingValue: Math.max(0, remainingValue),
      annualCost,
      status,
      statusText,
      statusColor,
      startDate,
      endDate
    }
  }, [asset])

  if (!asset || !assetData) return null

  return (
    <Popup
      visible={visible}
      onMaskClick={onClose}
      position="right"
      bodyStyle={{
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <div 
        className="asset-detail-page" 
        style={{ flex: 1, overflow: 'auto' }}
        {...swipeHandlers}
      >
        {/* 顶部头部 */}
        <div className="detail-header">
          <div className="header-bg"></div>
          <div 
            className="back-btn"
            onClick={onClose}
          >
            <LeftOutline fontSize={20} color="#fff" />
          </div>
          
          <div className="header-content">
            <div className="asset-icon">
              {asset.name?.charAt(0) || 'V'}
            </div>
            
            <div className="header-info">
              <h1 className="asset-name">
                {asset.name}
                <Tag 
                  className="status-tag"
                  style={{ '--background-color': assetData.statusColor }}
                >
                  {assetData.statusText}
                </Tag>
              </h1>
            </div>
            
            <div className="asset-amount">
              <span className="currency">￥</span>
              <span className="value">{parseFloat(asset.total_amount).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* 时间进度卡片 */}
        <Card className="progress-card">
          <div className="progress-header">
            <ClockCircleOutline fontSize={18} color="#667eea" />
            <span>时间进度</span>
          </div>
          
          <div className="progress-bar-wrapper">
            <ProgressBar 
              percent={assetData.progress} 
              style={{
                '--fill-color': assetData.progress > 80 ? '#ff4d4f' : assetData.progress > 50 ? '#faad14' : '#52c41a',
                '--track-color': '#f5f5f5',
                '--track-width': '8px'
              }}
            />
            <div className="progress-labels">
              <span>{assetData.startDate.format('YYYY-MM-DD')}</span>
              <span>{assetData.endDate.format('YYYY-MM-DD')}</span>
            </div>
          </div>
          
          <div className="time-stats">
            <div className="time-stat-item">
              <div className="stat-number">{assetData.totalDays}</div>
              <div className="stat-label">总天数</div>
            </div>
            <div className="time-stat-item">
              <div className="stat-number used">{assetData.usedDays}</div>
              <div className="stat-label">已使用</div>
            </div>
            <div className="time-stat-item">
              <div className="stat-number remaining">{assetData.remainingDays}</div>
              <div className="stat-label">剩余</div>
            </div>
          </div>
        </Card>

        {/* 价值分析卡片 */}
        <Card className="analysis-card">
          <div className="card-title">
            <PayCircleOutline fontSize={18} color="#667eea" />
            <span>价值分析</span>
          </div>
          
          <div className="value-chart">
            <div className="chart-bar">
              <div 
                className="used-portion" 
                style={{ width: `${assetData.progress}%` }}
              >
                <span>已消耗</span>
              </div>
              <div 
                className="remaining-portion"
                style={{ width: `${100 - assetData.progress}%` }}
              >
                <span>剩余</span>
              </div>
            </div>
          </div>
          
          <List className="value-list">
            <List.Item 
              extra={<span className="value-text">￥{assetData.dailyValue.toFixed(2)}</span>}
            >
              日均成本
            </List.Item>
            <List.Item 
              extra={<span className="value-text used">￥{assetData.usedValue.toFixed(2)}</span>}
            >
              已消耗价值
            </List.Item>
            <List.Item 
              extra={<span className="value-text remaining">￥{assetData.remainingValue.toFixed(2)}</span>}
            >
              剩余价值
            </List.Item>
          </List>
        </Card>

        {/* 预测与建议卡片 */}
        <Card className="prediction-card">
          <div className="card-title">
            <PieOutline fontSize={16} color="#667eea" />
            <span>智能预测</span>
          </div>
          
          <div className="prediction-items">
            <div className="prediction-item">
              <div className="prediction-icon annual">📅</div>
              <div className="prediction-content">
                <div className="prediction-label">年化成本预测</div>
                <div className="prediction-value">￥{assetData.annualCost.toFixed(2)}</div>
                <div className="prediction-desc">如果持续使用，预计每年支出</div>
              </div>
            </div>
            
            <div className="prediction-item">
              <div className="prediction-icon suggestion">💡</div>
              <div className="prediction-content">
                <div className="prediction-label">续费建议</div>
                <div className="prediction-value suggestion-text">
                  {assetData.remainingDays <= 7 
                    ? '建议立即续费'
                    : assetData.remainingDays <= 30 
                    ? '可以开始准备续费'
                    : '时间充裕，无需急于续费'}
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* 资产详情卡片 */}
        <Card className="info-card">
          <div className="card-title">
            <CalendarOutline fontSize={18} color="#667eea" />
            <span>资产详情</span>
          </div>
          
          <List>
            <List.Item extra={asset.category_name || '未分类'}>
              资产分类
            </List.Item>
            <List.Item extra={assetData.startDate.format('YYYY-MM-DD')}>
              开始日期
            </List.Item>
            <List.Item extra={assetData.endDate.format('YYYY-MM-DD')}>
              结束日期
            </List.Item>
            {asset.description && (
              <List.Item extra={asset.description}>
                备注说明
              </List.Item>
            )}
          </List>
        </Card>

        {/* 账号信息卡片 */}
        {(asset.account_username || asset.account_password) && (
          <Card className="account-card">
            <div className="card-title">
              <span style={{ marginRight: 6 }}>🔐</span>
              <span>账号信息</span>
            </div>
            
            <List>
              {asset.account_username && (
                <List.Item 
                  extra={
                    <span 
                      className="account-value"
                      onClick={() => {
                        navigator.clipboard?.writeText(asset.account_username)
                        Toast.show({ content: '账号已复制', position: 'bottom' })
                      }}
                    >
                      {asset.account_username}
                      <span className="copy-hint">点击复制</span>
                    </span>
                  }
                >
                  登录账号
                </List.Item>
              )}
              {asset.account_password && (
                <List.Item 
                  extra={
                    <div className="password-wrapper">
                      <span 
                        className="account-value"
                        onClick={() => {
                          navigator.clipboard?.writeText(asset.account_password)
                          Toast.show({ content: '密码已复制', position: 'bottom' })
                        }}
                      >
                        {showPassword ? asset.account_password : '••••••••'}
                      </span>
                      <span 
                        className="toggle-eye"
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowPassword(!showPassword)
                        }}
                      >
                        {showPassword ? <EyeInvisibleOutline /> : <EyeOutline />}
                      </span>
                    </div>
                  }
                >
                  登录密码
                </List.Item>
              )}
            </List>
          </Card>
        )}
      </div>

      {/* 底部操作按钮 */}
      <div className="bottom-actions">
        <Button block color="primary" size="large">
          续费提醒
        </Button>
      </div>
    </Popup>
  )
}

export default VirtualAssetDetail
