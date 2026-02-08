/**
 * 年度统计详情组件
 * 展示年度消费/收入的图表和趋势
 */

import { useMemo } from 'react'
import { Popup, NavBar, Grid, Divider } from 'antd-mobile'
import dayjs from 'dayjs'
import './YearStatsDetail.css'

const YearStatsDetail = ({ 
  visible, 
  onClose, 
  year, 
  projects = [],  // 虚拟资产数据
  assets = [],    // 固定资产数据
  type = 'virtual' // virtual 或 fixed
}) => {

  // 计算月度数据
  const monthlyData = useMemo(() => {
    const data = []
    
    for (let month = 0; month < 12; month++) {
      const monthStart = dayjs(`${year}-${String(month + 1).padStart(2, '0')}-01`)
      const monthEnd = monthStart.endOf('month')
      
      let amount = 0
      
      if (type === 'virtual') {
        // 虚拟资产：按时间分摊计算每月消费
        projects.forEach(p => {
          const start = dayjs(p.start_time || p.start_date)
          const end = dayjs(p.end_time || p.end_date)
          const totalDays = end.diff(start, 'day') + 1
          const totalAmount = p.total_amount || 0
          
          if (totalDays <= 0 || totalAmount <= 0) return
          
          // 计算该月的有效区间
          const effectiveStart = start.isAfter(monthStart) ? start : monthStart
          const effectiveEnd = end.isBefore(monthEnd) ? end : monthEnd
          
          if (effectiveStart.isAfter(effectiveEnd)) return
          
          const daysInMonth = effectiveEnd.diff(effectiveStart, 'day') + 1
          amount += (totalAmount * daysInMonth) / totalDays
        })
      } else {
        // 固定资产：计算租金收入
        assets.forEach(a => {
          if (a.rent_price && (a.status === 'rent' || a.status === 'rented')) {
            const rentStart = a.rent_start_date ? dayjs(a.rent_start_date) : dayjs(a.purchase_date)
            const rentEnd = a.rent_end_date ? dayjs(a.rent_end_date) : dayjs(`${year}-12-31`)
            
            if (monthStart.isBefore(rentEnd) && monthEnd.isAfter(rentStart)) {
              amount += parseFloat(a.rent_price || 0)
            }
          }
        })
      }
      
      data.push({
        month: `${month + 1}月`,
        monthNum: month + 1,
        amount: parseFloat(amount.toFixed(2))
      })
    }
    
    return data
  }, [year, projects, assets, type])

  // 计算分类占比数据
  const categoryData = useMemo(() => {
    const categoryMap = {}
    
    if (type === 'virtual') {
      projects.forEach(p => {
        const categoryName = p.category_name || '未分类'
        if (!categoryMap[categoryName]) {
          categoryMap[categoryName] = 0
        }
        categoryMap[categoryName] += p.total_amount || 0
      })
    } else {
      assets.forEach(a => {
        const categoryName = a.category_name || '未分类'
        if (!categoryMap[categoryName]) {
          categoryMap[categoryName] = 0
        }
        categoryMap[categoryName] += parseFloat(a.current_value || a.original_value || 0)
      })
    }
    
    return Object.entries(categoryMap)
      .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(2)) }))
      .sort((a, b) => b.value - a.value)
  }, [projects, assets, type])

  // 计算总览数据
  const summary = useMemo(() => {
    const totalAmount = monthlyData.reduce((sum, d) => sum + d.amount, 0)
    const maxMonth = monthlyData.reduce((max, d) => d.amount > max.amount ? d : max, monthlyData[0] || { month: '-', amount: 0 })
    const avgAmount = totalAmount / 12
    
    return {
      totalAmount: totalAmount.toFixed(2),
      avgAmount: avgAmount.toFixed(2),
      maxMonth: maxMonth?.month || '-',
      maxAmount: maxMonth?.amount?.toFixed(2) || '0'
    }
  }, [monthlyData])

  // 获取最大值用于计算柱状图高度比例
  const maxAmount = useMemo(() => {
    return Math.max(...monthlyData.map(d => d.amount), 1)
  }, [monthlyData])

  // 获取分类总额用于计算占比
  const categoryTotal = useMemo(() => {
    return categoryData.reduce((sum, d) => sum + d.value, 0) || 1
  }, [categoryData])

  // 分类颜色
  const categoryColors = ['#667eea', '#52c41a', '#faad14', '#ff4d4f', '#13c2c2', '#722ed1', '#eb2f96']

  return (
    <Popup
      visible={visible}
      onMaskClick={onClose}
      position="right"
      bodyStyle={{ width: '100vw', height: '100vh', overflow: 'auto' }}
    >
      <div className={`year-stats-detail ${type === 'fixed' ? 'fixed-type' : ''}`}>
        <NavBar onBack={onClose}>
          {year}年{type === 'virtual' ? '消费' : '资产'}统计
        </NavBar>
        
        {/* 总览卡片 */}
        <div className="summary-card">
          <div className="summary-title">年度总览</div>
          <Grid columns={2} gap={16}>
            <Grid.Item>
              <div className="summary-item">
                <div className="summary-value primary">
                  ￥{parseFloat(summary.totalAmount).toLocaleString()}
                </div>
                <div className="summary-label">
                  {type === 'virtual' ? '年度总消费' : '年度总收入'}
                </div>
              </div>
            </Grid.Item>
            <Grid.Item>
              <div className="summary-item">
                <div className="summary-value">
                  ￥{parseFloat(summary.avgAmount).toLocaleString()}
                </div>
                <div className="summary-label">月均金额</div>
              </div>
            </Grid.Item>
            <Grid.Item>
              <div className="summary-item">
                <div className="summary-value warning">{summary.maxMonth}</div>
                <div className="summary-label">最高月份</div>
              </div>
            </Grid.Item>
            <Grid.Item>
              <div className="summary-item">
                <div className="summary-value danger">
                  ￥{parseFloat(summary.maxAmount).toLocaleString()}
                </div>
                <div className="summary-label">最高金额</div>
              </div>
            </Grid.Item>
          </Grid>
        </div>

        {/* 月度趋势图 - CSS柱状图 */}
        <div className="chart-section">
          <div className="chart-title">
            月度{type === 'virtual' ? '消费' : '收入'}趋势
          </div>
          <div className="bar-chart">
            {monthlyData.map((item, index) => (
              <div key={index} className="bar-item">
                <div className="bar-value">
                  {item.amount > 0 ? `￥${item.amount >= 1000 ? (item.amount/1000).toFixed(1) + 'k' : item.amount.toFixed(0)}` : ''}
                </div>
                <div className="bar-wrapper">
                  <div 
                    className="bar" 
                    style={{ height: `${(item.amount / maxAmount) * 100}%` }}
                  />
                </div>
                <div className="bar-label">{item.monthNum}</div>
              </div>
            ))}
          </div>
        </div>

        <Divider />

        {/* 分类占比 - CSS进度条 */}
        <div className="chart-section">
          <div className="chart-title">分类占比</div>
          <div className="pie-chart-css">
            {categoryData.slice(0, 5).map((item, index) => {
              const percent = (item.value / categoryTotal * 100).toFixed(1)
              return (
                <div key={item.name} className="pie-item">
                  <div className="pie-info">
                    <span 
                      className="pie-dot" 
                      style={{ background: categoryColors[index % categoryColors.length] }}
                    />
                    <span className="pie-name">{item.name}</span>
                    <span className="pie-percent">{percent}%</span>
                  </div>
                  <div className="pie-bar-bg">
                    <div 
                      className="pie-bar" 
                      style={{ 
                        width: `${percent}%`,
                        background: categoryColors[index % categoryColors.length]
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* 分类明细列表 */}
        <div className="category-list">
          <div className="chart-title">分类明细</div>
          {categoryData.map((item, index) => {
            const percent = (item.value / categoryTotal * 100).toFixed(1)
            return (
              <div key={item.name} className="category-item">
                <div className="category-rank">{index + 1}</div>
                <div className="category-name">{item.name}</div>
                <div className="category-percent">{percent}%</div>
                <div className="category-value">￥{item.value.toLocaleString()}</div>
              </div>
            )
          })}
          {categoryData.length === 0 && (
            <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
              暂无数据
            </div>
          )}
        </div>
      </div>
    </Popup>
  )
}

export default YearStatsDetail
