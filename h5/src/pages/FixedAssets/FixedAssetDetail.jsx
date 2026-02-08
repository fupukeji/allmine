/**
 * 固定资产详情页
 * 包含资产信息、折旧分析、使用状态
 */

import { useState, useMemo } from 'react'
import { Popup, Card, List, Button, ProgressBar, Tag, Toast } from 'antd-mobile'
import { 
  LeftOutline,
  ClockCircleOutline, 
  PayCircleOutline,
  CalendarOutline,
  PieOutline,
  LocationOutline,
  UserOutline
} from 'antd-mobile-icons'
import dayjs from 'dayjs'
import { useSwipeBack } from '../../hooks'
import './FixedAssetDetail.css'

const FixedAssetDetail = ({ visible, onClose, asset }) => {
  // 左滑返回手势
  const swipeHandlers = useSwipeBack(onClose)

  // 计算资产相关数据
  const assetData = useMemo(() => {
    if (!asset) return null

    const today = dayjs()
    const purchaseDate = dayjs(asset.purchase_date)
    const usefulLifeYears = asset.useful_life_years || 5
    const endDate = purchaseDate.add(usefulLifeYears, 'year')
    
    // 已使用时间
    const usedMonths = today.diff(purchaseDate, 'month')
    const usedYears = Math.floor(usedMonths / 12)
    const remainingMonths = Math.max(0, endDate.diff(today, 'month'))
    const remainingYears = Math.floor(remainingMonths / 12)
    
    // 总月数
    const totalMonths = usefulLifeYears * 12
    
    // 折旧进度
    const depreciationProgress = Math.min(100, Math.max(0, (usedMonths / totalMonths) * 100))
    
    // 原值和残值
    const originalValue = asset.original_value || 0
    const residualRate = asset.residual_rate || 5
    const residualValue = originalValue * (residualRate / 100)
    const depreciableValue = originalValue - residualValue
    
    // 累计折旧
    const monthlyDepreciation = depreciableValue / totalMonths
    const accumulatedDepreciation = Math.min(depreciableValue, monthlyDepreciation * usedMonths)
    
    // 净值（现值）
    const currentValue = originalValue - accumulatedDepreciation
    
    // 年折旧额
    const annualDepreciation = depreciableValue / usefulLifeYears
    
    // 状态
    let statusText = '使用中'
    let statusColor = '#52c41a'
    
    const statusMap = {
      'in_use': { text: '使用中', color: '#52c41a' },
      'rent': { text: '出租中', color: '#1890ff' },
      'sell': { text: '待出售', color: '#faad14' },
      'idle': { text: '闲置', color: '#faad14' },
      'maintenance': { text: '维护中', color: '#1890ff' },
      'disposed': { text: '已处置', color: '#999' }
    }
    
    if (statusMap[asset.status]) {
      statusText = statusMap[asset.status].text
      statusColor = statusMap[asset.status].color
    }

    return {
      purchaseDate,
      endDate,
      usedMonths: Math.max(0, usedMonths),
      usedYears,
      remainingMonths,
      remainingYears,
      totalMonths,
      depreciationProgress,
      originalValue,
      residualRate,
      residualValue,
      depreciableValue,
      monthlyDepreciation,
      accumulatedDepreciation,
      currentValue,
      annualDepreciation,
      statusText,
      statusColor
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
        className="fixed-asset-detail-page" 
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
            <LeftOutline fontSize={18} color="#fff" />
          </div>
          
          <div className="header-content">
            <div className="asset-icon">
              {asset.name?.charAt(0) || 'F'}
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
              <p className="asset-code">{asset.asset_code}</p>
            </div>
            
            <div className="asset-values">
              <div className="value-item">
                <span className="label">原值</span>
                <span className="value">￥{assetData.originalValue.toLocaleString()}</span>
              </div>
              <div className="value-item">
                <span className="label">净值</span>
                <span className="value primary">￥{Math.round(assetData.currentValue).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 折旧进度卡片 */}
        <Card className="depreciation-card">
          <div className="card-title">
            <ClockCircleOutline fontSize={18} color="#52c41a" />
            <span>使用寿命</span>
          </div>
          
          <div className="progress-bar-wrapper">
            <ProgressBar 
              percent={assetData.depreciationProgress} 
              style={{
                '--fill-color': assetData.depreciationProgress > 80 ? '#ff4d4f' : assetData.depreciationProgress > 50 ? '#faad14' : '#52c41a',
                '--track-color': '#f5f5f5',
                '--track-width': '8px'
              }}
            />
            <div className="progress-labels">
              <span>{assetData.purchaseDate.format('YYYY-MM-DD')}</span>
              <span>{assetData.endDate.format('YYYY-MM-DD')}</span>
            </div>
          </div>
          
          <div className="time-stats">
            <div className="time-stat-item">
              <div className="stat-number">{asset.useful_life_years || 5}</div>
              <div className="stat-label">总年限</div>
            </div>
            <div className="time-stat-item">
              <div className="stat-number used">{assetData.usedYears}年{assetData.usedMonths % 12}月</div>
              <div className="stat-label">已使用</div>
            </div>
            <div className="time-stat-item">
              <div className="stat-number remaining">{assetData.remainingYears}年{assetData.remainingMonths % 12}月</div>
              <div className="stat-label">剩余</div>
            </div>
          </div>
        </Card>

        {/* 折旧分析卡片 */}
        <Card className="analysis-card">
          <div className="card-title">
            <PayCircleOutline fontSize={16} color="#52c41a" />
            <span>折旧分析</span>
          </div>
          
          <div className="value-chart">
            <div className="chart-bar">
              <div 
                className="depreciated-portion" 
                style={{ width: `${Math.max(20, assetData.depreciationProgress)}%` }}
              >
                <span>已折旧</span>
              </div>
              <div 
                className="remaining-portion"
                style={{ width: `${Math.max(20, 100 - assetData.depreciationProgress)}%` }}
              >
                <span>净值</span>
              </div>
            </div>
          </div>
          
          <List className="value-list">
            <List.Item 
              extra={<span className="value-text">￥{assetData.annualDepreciation.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>}
            >
              年折旧额
            </List.Item>
            <List.Item 
              extra={<span className="value-text">￥{assetData.monthlyDepreciation.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>}
            >
              月折旧额
            </List.Item>
            <List.Item 
              extra={<span className="value-text depreciated">￥{assetData.accumulatedDepreciation.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>}
            >
              累计折旧
            </List.Item>
            <List.Item 
              extra={<span className="value-text remaining">￥{assetData.residualValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>}
            >
              预计残值
            </List.Item>
          </List>
        </Card>

        {/* 预测与建议卡片 */}
        <Card className="prediction-card">
          <div className="card-title">
            <PieOutline fontSize={16} color="#52c41a" />
            <span>资产评估</span>
          </div>
          
          <div className="prediction-items">
            <div className="prediction-item">
              <div className="prediction-icon rate">📊</div>
              <div className="prediction-content">
                <div className="prediction-label">折旧率</div>
                <div className="prediction-value">{assetData.depreciationProgress.toFixed(1)}%</div>
                <div className="prediction-desc">当前已折旧比例</div>
              </div>
            </div>
            
            <div className="prediction-item">
              <div className="prediction-icon suggestion">💡</div>
              <div className="prediction-content">
                <div className="prediction-label">使用建议</div>
                <div className="prediction-value suggestion-text">
                  {assetData.remainingMonths <= 12 
                    ? '建议考虑更新换代'
                    : assetData.remainingMonths <= 24 
                    ? '注意维护保养'
                    : '状态良好'}
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* 出租信息卡片 */}
        {asset.status === 'rent' && asset.rent_price && (
          <Card className="rent-card">
            <div className="card-title">
              <PayCircleOutline fontSize={16} color="#1890ff" />
              <span>出租信息</span>
            </div>
            
            <div className="rent-summary">
              <div className="rent-amount">
                <span className="label">月租金</span>
                <span className="value">￥{asset.rent_price.toLocaleString()}</span>
              </div>
              {asset.rent_deposit > 0 && (
                <div className="rent-deposit">
                  <span className="label">押金</span>
                  <span className="value">￥{asset.rent_deposit.toLocaleString()}</span>
                </div>
              )}
            </div>
            
            <List className="rent-detail-list">
              {asset.rent_start_date && (
                <List.Item extra={asset.rent_start_date}>
                  租期开始
                </List.Item>
              )}
              {asset.rent_end_date && (
                <List.Item extra={asset.rent_end_date}>
                  租期结束
                </List.Item>
              )}
              <List.Item extra={`每月${asset.rent_due_day || 1}号`}>
                收租日
              </List.Item>
              {asset.tenant_name && (
                <List.Item extra={asset.tenant_name}>
                  租客姓名
                </List.Item>
              )}
              {asset.tenant_phone && (
                <List.Item extra={asset.tenant_phone}>
                  租客电话
                </List.Item>
              )}
            </List>
          </Card>
        )}

        {/* 资产详情卡片 */}
        <Card className="info-card">
          <div className="card-title">
            <CalendarOutline fontSize={18} color="#52c41a" />
            <span>资产详情</span>
          </div>
          
          <List>
            <List.Item extra={asset.category_name || '未分类'}>
              资产分类
            </List.Item>
            <List.Item extra={assetData.purchaseDate.format('YYYY-MM-DD')}>
              购买日期
            </List.Item>
            <List.Item extra={`${asset.useful_life_years || 5}年`}>
              使用年限
            </List.Item>
            <List.Item extra={`${assetData.residualRate}%`}>
              残值率
            </List.Item>
            <List.Item extra={asset.depreciation_method === 'straight_line' ? '直线法' : '其他'}>
              折旧方法
            </List.Item>
            {asset.location && (
              <List.Item 
                prefix={<LocationOutline color="#52c41a" />}
                extra={asset.location}
              >
                所在位置
              </List.Item>
            )}
            {asset.responsible_person && (
              <List.Item 
                prefix={<UserOutline color="#52c41a" />}
                extra={asset.responsible_person}
              >
                责任人
              </List.Item>
            )}
            {asset.description && (
              <List.Item extra={asset.description}>
                备注说明
              </List.Item>
            )}
          </List>
        </Card>
      </div>

      {/* 底部操作按钮 */}
      <div className="bottom-actions">
        <Button block color="primary" size="large" style={{ '--background-color': '#52c41a' }}>
          资产盘点
        </Button>
      </div>
    </Popup>
  )
}

export default FixedAssetDetail
