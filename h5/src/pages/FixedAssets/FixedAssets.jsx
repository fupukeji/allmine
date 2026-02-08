/**
 * 固定资产管理页面
 * 支持左侧分类筛选、资产列表、详情页
 */

import { useState, useEffect, useMemo, useRef } from 'react'
import { Card, List, Tag, Toast, PullToRefresh, Empty, Skeleton, Dialog, SwipeAction, Button, SideBar, ProgressBar, Popup, Form, Input, Picker, Swiper } from 'antd-mobile'
import { AddOutline, FileOutline, RightOutline, LeftOutline } from 'antd-mobile-icons'
import { getAssets, deleteAsset, updateAsset } from '../../services/assets'
import { getCategories } from '../../services/categories'
import FixedAssetForm from '../../components/FixedAssetForm'
import FixedAssetDetail from './FixedAssetDetail'
import YearStatsDetail from '../../components/YearStatsDetail'
import AssetExpenseManager from '../../components/AssetExpenseManager'
import dayjs from 'dayjs'
import './FixedAssets.css'

// 图标名称到emoji的映射
const ICON_MAP = {
  'home': '🏠',
  'car': '🚗',
  'laptop': '💻',
  'appstore': '📦',
  'dollar': '💵',
  'bank': '🏦',
  'fund': '📈',
  'stock': '📊',
  'account-book': '📒',
  'pie-chart': '🧩',
  'safety': '🛡️',
  'rise': '📈',
  'shop': '🏪',
  'file-text': '📄',
  'safety-certificate': '📜',
  'cluster': '🎯',
  'bulb': '💡',
  'copyright': '©️',
  'global': '🌐',
  'code': '💻',
  'crown': '👑',
  'read': '📖',
  'book': '📕',
  'solution': '🎓',
  'heart': '❤️',
  'team': '👨‍👩‍👧',
  'gift': '🎁',
  'picture': '🖼️',
  'golden': '🏆',
  'skin': '💎',
  'gold': '🥇',
  'container': '📦',
  'link': '🔗',
  'transaction': '🪙',
  'trophy': '🏆',
  'star': '⭐',
  'credit-card': '💳',
  'folder': '📁',
  'default': '📋'
}

// 获取emoji图标
const getEmojiIcon = (iconName) => {
  return ICON_MAP[iconName] || ICON_MAP['default']
}

const FixedAssets = () => {
  const [loading, setLoading] = useState(false)
  const [assets, setAssets] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingAsset, setEditingAsset] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [categories, setCategories] = useState([])
  const [showDetail, setShowDetail] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState(null)
  
  // 处置状态管理
  const [showDispose, setShowDispose] = useState(false)
  const [disposingAsset, setDisposingAsset] = useState(null)
  const [disposeType, setDisposeType] = useState(['rent']) // rent/sell/idle/disposed
  const [disposeForm] = Form.useForm()
  
  const [stats, setStats] = useState({
    totalCount: 0,
    totalValue: 0,
    totalDepreciation: 0,
    inUseCount: 0,
    idleCount: 0
  })

  // 年度统计详情弹窗
  const [showStatsDetail, setShowStatsDetail] = useState(false)

  // 费用管理弹窗
  const [showExpense, setShowExpense] = useState(false)
  const [expenseAsset, setExpenseAsset] = useState(null)

  // 年份切换相关
  const [selectedYear, setSelectedYear] = useState(dayjs().year())
  const swiperRef = useRef(null)

  // 获取所有年份列表
  const yearList = useMemo(() => {
    const years = new Set()
    const currentYear = dayjs().year()
    years.add(currentYear)
    
    assets.forEach(a => {
      const purchaseYear = dayjs(a.purchase_date).year()
      if (purchaseYear >= 2020) years.add(purchaseYear)
      // 如果有处置日期，也加入
      if (a.dispose_date) {
        const disposeYear = dayjs(a.dispose_date).year()
        if (disposeYear >= 2020) years.add(disposeYear)
      }
    })
    
    return Array.from(years).sort((a, b) => b - a)
  }, [assets])

  // 根据年份计算统计数据
  const yearStats = useMemo(() => {
    const result = {}
    
    yearList.forEach(year => {
      // 筛选该年份有效的资产（购买日期 <= 年底，且未处置或处置日期 >= 年初）
      const yearAssets = assets.filter(a => {
        const purchaseDate = dayjs(a.purchase_date)
        const disposeDate = a.dispose_date ? dayjs(a.dispose_date) : null
        
        // 资产在该年底之前购买
        if (purchaseDate.year() > year) return false
        // 如果已处置，处置日期要在该年或之后
        if (disposeDate && disposeDate.year() < year) return false
        
        return true
      })
      
      // 计算该年的统计数据
      let totalValue = 0
      let totalDepreciation = 0
      let totalIncome = 0
      let inUseCount = 0
      let idleCount = 0
      
      yearAssets.forEach(a => {
        // 资产价值（使用当前价值或原值）
        totalValue += parseFloat(a.current_value || a.original_value || 0)
        
        // 累计折旧
        totalDepreciation += parseFloat(a.accumulated_depreciation || 0)
        
        // 收入（租金等）- 使用rent_price字段
        if (a.rent_price && (a.status === 'rent' || a.status === 'rented')) {
          // 计算该年的租金收入
          const rentStart = a.rent_start_date ? dayjs(a.rent_start_date) : dayjs(a.purchase_date)
          const rentEnd = a.rent_end_date ? dayjs(a.rent_end_date) : dayjs(`${year}-12-31`)
          
          // 计算该年内的租赁月份
          const yearStart = dayjs(`${year}-01-01`)
          const yearEnd = dayjs(`${year}-12-31`)
          
          const effectiveStart = rentStart.isAfter(yearStart) ? rentStart : yearStart
          const effectiveEnd = rentEnd.isBefore(yearEnd) ? rentEnd : yearEnd
          
          if (effectiveStart.isBefore(effectiveEnd) || effectiveStart.isSame(effectiveEnd)) {
            const months = effectiveEnd.diff(effectiveStart, 'month') + 1
            totalIncome += parseFloat(a.rent_price || 0) * months
          }
        }
        
        // 状态统计
        if (a.status === 'in_use' || a.status === 'rent' || a.status === 'rented') {
          inUseCount++
        } else if (a.status === 'idle') {
          idleCount++
        }
      })
      
      result[year] = {
        totalCount: yearAssets.length,
        totalValue: totalValue.toFixed(2),
        totalDepreciation: totalDepreciation.toFixed(2),
        totalIncome: totalIncome.toFixed(2),
        inUseCount,
        idleCount
      }
    })
    
    return result
  }, [assets, yearList])

  useEffect(() => {
    loadCategories()
    loadAssets()
  }, [])

  // 加载分类（只加载固定资产分类）
  const loadCategories = async () => {
    try {
      const res = await getCategories({ asset_type: 'fixed' })
      if (res.code === 200 && res.data) {
        setCategories(res.data)
      }
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  // 生成侧边栏分类列表
  const sidebarItems = useMemo(() => {
    const items = [
      { key: 'all', title: '全部', icon: '📋' }
    ]
    categories.forEach(cat => {
      items.push({
        key: String(cat.id),
        title: cat.name,
        icon: getEmojiIcon(cat.icon)
      })
    })
    return items
  }, [categories])

  const loadAssets = async () => {
    try {
      setLoading(true)
      const res = await getAssets()
      
      if (res.code === 200 && res.data) {
        const assetList = res.data.items || res.data || []
        setAssets(assetList)
        calculateStats(assetList)
      }
    } catch (error) {
      console.error('加载资产失败:', error)
      Toast.show({ icon: 'fail', content: '加载失败' })
    } finally {
      setLoading(false)
    }
  }

  // 根据分类筛选资产
  const filteredAssets = useMemo(() => {
    if (selectedCategory === 'all') {
      return assets
    }
    // 按category_id筛选
    return assets.filter(a => String(a.category_id) === selectedCategory)
  }, [assets, selectedCategory])

  // 计算各分类数量
  const categoryStats = useMemo(() => {
    const stats = { all: assets.length }
    categories.forEach(cat => {
      stats[String(cat.id)] = assets.filter(a => a.category_id === cat.id).length
    })
    return stats
  }, [assets, categories])

  const calculateStats = (assetList) => {
    const totalValue = assetList.reduce((sum, asset) => sum + (asset.current_value || 0), 0)
    const totalDepreciation = assetList.reduce((sum, asset) => sum + (asset.accumulated_depreciation || 0), 0)
    const inUseCount = assetList.filter(a => a.status === 'in_use').length
    const idleCount = assetList.filter(a => a.status === 'idle').length

    setStats({
      totalCount: assetList.length,
      totalValue: totalValue.toFixed(2),
      totalDepreciation: totalDepreciation.toFixed(2),
      inUseCount,
      idleCount
    })
  }

  const handleAdd = () => {
    setEditingAsset(null)
    setShowForm(true)
  }

  const handleViewDetail = (asset) => {
    setSelectedAsset(asset)
    setShowDetail(true)
  }

  const handleEdit = (asset) => {
    setEditingAsset(asset)
    setShowForm(true)
  }

  const handleDelete = (asset) => {
    Dialog.confirm({
      content: `确认删除「${asset.name}」吗？此操作不可恢复。`,
      onConfirm: async () => {
        try {
          const res = await deleteAsset(asset.id)
          if (res.code === 200) {
            Toast.show({ icon: 'success', content: '删除成功' })
            await loadAssets()
          } else {
            Toast.show({ icon: 'fail', content: res.message || '删除失败' })
          }
        } catch (error) {
          Toast.show({ icon: 'fail', content: '删除失败' })
        }
      }
    })
  }

  // 处置资产
  const handleDispose = (asset) => {
    setDisposingAsset(asset)
    setDisposeType([asset.status || 'in_use'])
    disposeForm.setFieldsValue({
      rent_price: asset.rent_price || '',
      rent_deposit: asset.rent_deposit || '',
      rent_start_date: asset.rent_start_date || '',
      rent_end_date: asset.rent_end_date || '',
      rent_due_day: asset.rent_due_day || '1',
      tenant_name: asset.tenant_name || '',
      tenant_phone: asset.tenant_phone || '',
      sell_price: asset.sell_price || '',
      dispose_date: asset.dispose_date || dayjs().format('YYYY-MM-DD'),
      dispose_note: asset.dispose_note || ''
    })
    setShowDispose(true)
  }

  // 提交处置
  const handleDisposeSubmit = async () => {
    try {
      const values = await disposeForm.validateFields()
      const status = disposeType[0]
      
      const data = {
        status: status,
        dispose_note: values.dispose_note || ''
      }
      
      // 根据状态添加不同参数
      if (status === 'rent') {
        data.rent_price = parseFloat(values.rent_price) || 0
        data.rent_deposit = parseFloat(values.rent_deposit) || 0
        data.rent_start_date = values.rent_start_date
        data.rent_end_date = values.rent_end_date
        data.rent_due_day = parseInt(values.rent_due_day) || 1
        data.tenant_name = values.tenant_name || ''
        data.tenant_phone = values.tenant_phone || ''
      } else if (status === 'sell') {
        data.sell_price = parseFloat(values.sell_price) || 0
        data.dispose_date = values.dispose_date
      }
      
      const res = await updateAsset(disposingAsset.id, data)
      if (res.code === 200) {
        Toast.show({ icon: 'success', content: '处置成功' })
        setShowDispose(false)
        await loadAssets()
      } else {
        Toast.show({ icon: 'fail', content: res.message || '处置失败' })
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '处置失败' })
    }
  }

  // 处置类型选项
  const disposeOptions = [
    [
      { label: '🏠 使用中', value: 'in_use' },
      { label: '💰 出租', value: 'rent' },
      { label: '🎯 出售', value: 'sell' },
      { label: '💭 闲置', value: 'idle' },
      { label: '🛠️ 维修中', value: 'maintenance' },
      { label: '✅ 已处置', value: 'disposed' }
    ]
  ]

  const handleFormSuccess = async () => {
    await loadAssets()
  }

  const handleRefresh = async () => {
    await loadCategories()
    await loadAssets()
  }

  const getStatusColor = (status) => {
    const colorMap = {
      'in_use': 'success',
      'rent': 'primary',
      'sell': 'warning',
      'idle': 'default',
      'maintenance': 'primary',
      'disposed': 'default'
    }
    return colorMap[status] || 'default'
  }

  const getStatusText = (status) => {
    const textMap = {
      'in_use': '使用中',
      'rent': '出租中',
      'sell': '待出售',
      'idle': '闲置',
      'maintenance': '维护中',
      'disposed': '已处置'
    }
    return textMap[status] || '未知'
  }

  // 计算下次收租日期
  const getNextRentDate = (asset) => {
    if (asset.status !== 'rent' || !asset.rent_due_day) return null
    
    const today = dayjs()
    const dueDay = asset.rent_due_day
    let nextDate = today.date(dueDay)
    
    // 如果当月收租日已过，计算下个月
    if (today.date() >= dueDay) {
      nextDate = nextDate.add(1, 'month')
    }
    
    // 检查是否在租期内
    if (asset.rent_end_date && nextDate.isAfter(dayjs(asset.rent_end_date))) {
      return null
    }
    
    return nextDate
  }

  // 计算收租状态
  const getRentStatus = (asset) => {
    const nextDate = getNextRentDate(asset)
    if (!nextDate) return null
    
    const daysUntil = nextDate.diff(dayjs(), 'day')
    
    if (daysUntil <= 0) {
      return { text: '今日收租', color: '#ff4d4f', urgent: true }
    } else if (daysUntil <= 3) {
      return { text: `${daysUntil}天后收租`, color: '#faad14', urgent: true }
    } else if (daysUntil <= 7) {
      return { text: `${daysUntil}天后收租`, color: '#1890ff', urgent: false }
    }
    return { text: `${nextDate.format('MM/DD')}收租`, color: '#52c41a', urgent: false }
  }

  const calculateRemainingLife = (purchaseDate, usefulLifeYears) => {
    if (!purchaseDate || !usefulLifeYears) return null
    const endDate = dayjs(purchaseDate).add(usefulLifeYears, 'year')
    const monthsLeft = endDate.diff(dayjs(), 'month')
    return Math.max(0, monthsLeft)
  }

  if (loading && assets.length === 0) {
    return (
      <div className="fixed-assets-page">
        <div className="page-header">
          <Skeleton.Title animated />
        </div>
        <div className="stats-panel">
          <Skeleton.Paragraph lineCount={2} animated />
        </div>
        <div className="main-content">
          <Card><Skeleton.Paragraph lineCount={3} animated /></Card>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed-assets-page">
      {/* 页面头部 */}
      <div className="page-header">
        <div className="header-content">
          <div className="header-icon">
            <FileOutline fontSize={24} />
          </div>
          <div className="header-text">
            <h1>恒产生金</h1>
            <p>科学管理 · 价值跟踪 · 折旧计算</p>
          </div>
        </div>
        <Button
          color="primary"
          fill="solid"
          size="small"
          onClick={handleAdd}
          className="add-button-header"
        >
          <AddOutline /> 添加
        </Button>
      </div>

      {/* 统计面板 - 支持年份切换 */}
      {assets.length > 0 && (
        <div className="stats-panel">
          <Swiper
            ref={swiperRef}
            defaultIndex={0}
            onIndexChange={(index) => setSelectedYear(yearList[index])}
            indicator={() => null}
            style={{ '--height': 'auto' }}
          >
            {yearList.map(year => {
              const ys = yearStats[year] || { totalCount: 0, totalValue: '0', totalDepreciation: '0', totalIncome: '0', inUseCount: 0, idleCount: 0 }
              return (
                <Swiper.Item key={year}>
                  <div className="stats-year-header">
                    <LeftOutline className="year-arrow" />
                    <span className="year-title">{year}年</span>
                    <RightOutline className="year-arrow" />
                  </div>
                  <div className="stats-grid" onClick={() => setShowStatsDetail(true)}>
                    <div className="stat-item">
                      <div className="stat-value">{ys.totalCount}</div>
                      <div className="stat-label">总数量</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value primary">￥{parseFloat(ys.totalValue).toLocaleString()}</div>
                      <div className="stat-label">总价值</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value danger">￥{parseFloat(ys.totalDepreciation).toLocaleString()}</div>
                      <div className="stat-label">累计折旧</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value success">{ys.inUseCount}</div>
                      <div className="stat-label">使用中</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value warning">{ys.idleCount}</div>
                      <div className="stat-label">闲置</div>
                    </div>
                  </div>
                  {parseFloat(ys.totalIncome) > 0 && (
                    <div className="stats-income">
                      <span className="income-label">年度收入</span>
                      <span className="income-value">￥{parseFloat(ys.totalIncome).toLocaleString()}</span>
                    </div>
                  )}
                </Swiper.Item>
              )
            })}
          </Swiper>
        </div>
      )}

      {/* 主体区域：左侧分类 + 右侧列表 */}
      <div className="main-content">
        {/* 左侧分类栏 */}
        <div className="category-sidebar">
          <SideBar 
            activeKey={selectedCategory} 
            onChange={setSelectedCategory}
          >
            {sidebarItems.map(cat => (
              <SideBar.Item 
                key={cat.key} 
                title={
                  <div className="sidebar-item">
                    <span className="sidebar-icon">{cat.icon}</span>
                    <span className="sidebar-title">{cat.title}</span>
                    {categoryStats[cat.key] > 0 && (
                      <span className="sidebar-badge">{categoryStats[cat.key]}</span>
                    )}
                  </div>
                }
              />
            ))}
          </SideBar>
        </div>

        {/* 右侧列表区域 */}
        <div className="assets-content">
          <PullToRefresh onRefresh={handleRefresh}>
            {filteredAssets.length === 0 ? (
              <Empty
                description={selectedCategory === 'all' ? '还没有固定资产' : '该分类下暂无资产'}
                style={{ padding: '64px 0' }}
              >
                <Button color="primary" onClick={handleAdd}>
                  <AddOutline /> 立即添加
                </Button>
              </Empty>
            ) : (
              <List className="asset-list">
                {filteredAssets.map((asset) => {
                  const remainingMonths = calculateRemainingLife(asset.purchase_date, asset.useful_life_years)
                  const depreciationRate = asset.original_value > 0 
                    ? ((asset.accumulated_depreciation / asset.original_value) * 100).toFixed(1)
                    : 0
                  const rentStatus = asset.status === 'rent' ? getRentStatus(asset) : null
                  
                  return (
                    <SwipeAction
                      key={asset.id}
                      rightActions={[
                        {
                          key: 'expense',
                          text: '费用',
                          color: '#ff6b35',
                          onClick: () => {
                            setExpenseAsset(asset)
                            setShowExpense(true)
                          }
                        },
                        {
                          key: 'dispose',
                          text: '处置',
                          color: 'warning',
                          onClick: () => handleDispose(asset)
                        },
                        {
                          key: 'edit',
                          text: '编辑',
                          color: 'primary',
                          onClick: () => handleEdit(asset)
                        },
                        {
                          key: 'delete',
                          text: '删除',
                          color: 'danger',
                          onClick: () => handleDelete(asset)
                        }
                      ]}
                    >
                      <List.Item
                        prefix={
                          <div className="asset-icon-box">
                            {asset.name?.charAt(0) || 'A'}
                          </div>
                        }
                        onClick={() => handleViewDetail(asset)}
                        arrow={<RightOutline />}
                      >
                        <div className="asset-title">
                          <span className="name">{asset.name}</span>
                          <span className="amount">￥{asset.current_value?.toLocaleString()}</span>
                        </div>
                        <div className="asset-desc">
                          <div className="asset-tags">
                            <Tag color="primary" fill="outline" style={{ marginRight: 6 }}>
                              {asset.category_name || '未分类'}
                            </Tag>
                            <Tag color={getStatusColor(asset.status)}>
                              {getStatusText(asset.status)}
                            </Tag>
                          </div>
                          
                          <div className="asset-info-row">
                            <span className="label">原值：</span>
                            <span className="value">￥{asset.original_value?.toLocaleString()}</span>
                            {remainingMonths !== null && (
                              <>
                                <span className="label" style={{ marginLeft: 12 }}>剩余：</span>
                                <span className="value">{Math.floor(remainingMonths / 12)}年{remainingMonths % 12}月</span>
                              </>
                            )}
                          </div>
                          
                          <div className="depreciation-row">
                            <span className="depreciation-label">折旧率: {depreciationRate}%</span>
                            <ProgressBar
                              percent={parseFloat(depreciationRate)}
                              style={{
                                '--fill-color': depreciationRate > 80 ? '#ff4d4f' : depreciationRate > 50 ? '#faad14' : '#52c41a',
                                marginTop: 4
                              }}
                            />
                          </div>
                          
                          {asset.location && (
                            <div className="asset-location">
                              📍 {asset.location}
                            </div>
                          )}
                          
                          {/* 出租信息 */}
                          {asset.status === 'rent' && asset.rent_price && (
                            <div className="rent-info-row">
                              <span className="rent-price">💰 月租￥{asset.rent_price.toLocaleString()}</span>
                              {rentStatus && (
                                <span 
                                  className="rent-due" 
                                  style={{ 
                                    color: rentStatus.color,
                                    fontWeight: rentStatus.urgent ? 600 : 400
                                  }}
                                >
                                  ⏰ {rentStatus.text}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </List.Item>
                    </SwipeAction>
                  )
                })}
              </List>
            )}
          </PullToRefresh>
        </div>
      </div>

      {/* 添加/编辑表单 */}
      <FixedAssetForm
        visible={showForm}
        onClose={() => setShowForm(false)}
        onSuccess={handleFormSuccess}
        initialData={editingAsset}
      />

      {/* 详情页 */}
      <FixedAssetDetail
        visible={showDetail}
        onClose={() => setShowDetail(false)}
        asset={selectedAsset}
      />

      {/* 处置弹窗 */}
      <Popup
        visible={showDispose}
        onMaskClick={() => setShowDispose(false)}
        bodyStyle={{
          borderTopLeftRadius: '16px',
          borderTopRightRadius: '16px',
          padding: '20px'
        }}
      >
        <div className="dispose-popup">
          <h3 style={{ margin: '0 0 16px', textAlign: 'center' }}>
            资产处置 - {disposingAsset?.name}
          </h3>
          
          <Form form={disposeForm} layout="horizontal">
            {/* 处置类型 */}
            <Form.Item label="处置类型">
              <Picker
                columns={disposeOptions}
                value={disposeType}
                onConfirm={setDisposeType}
              >
                {(items, { open }) => (
                  <div onClick={open} style={{ padding: '8px 0', cursor: 'pointer' }}>
                    {disposeOptions[0].find(o => o.value === disposeType[0])?.label || '请选择'}
                  </div>
                )}
              </Picker>
            </Form.Item>
            
            {/* 出租信息 */}
            {disposeType[0] === 'rent' && (
              <>
                <Form.Item name="rent_price" label="月租金(元)" rules={[{ required: true }]}>
                  <Input type="number" placeholder="请输入每月租金" />
                </Form.Item>
                <Form.Item name="rent_deposit" label="押金(元)">
                  <Input type="number" placeholder="选填，押金金额" />
                </Form.Item>
                <Form.Item name="rent_start_date" label="租期开始" rules={[{ required: true }]}>
                  <Input type="date" />
                </Form.Item>
                <Form.Item name="rent_end_date" label="租期结束" rules={[{ required: true }]}>
                  <Input type="date" />
                </Form.Item>
                <Form.Item name="rent_due_day" label="收租日" extra="每月几号收租(1-28)">
                  <Input type="number" placeholder="例如: 1" min="1" max="28" />
                </Form.Item>
                <Form.Item name="tenant_name" label="租客姓名">
                  <Input placeholder="选填，租客姓名" />
                </Form.Item>
                <Form.Item name="tenant_phone" label="租客电话">
                  <Input type="tel" placeholder="选填，租客联系电话" />
                </Form.Item>
              </>
            )}
            
            {/* 出售价格 */}
            {disposeType[0] === 'sell' && (
              <>
                <Form.Item name="sell_price" label="售价(元)">
                  <Input type="number" placeholder="请输入售出价格" />
                </Form.Item>
                <Form.Item name="dispose_date" label="售出日期">
                  <Input type="date" />
                </Form.Item>
              </>
            )}
            
            {/* 备注 */}
            <Form.Item name="dispose_note" label="备注">
              <Input placeholder="选填，处置说明" />
            </Form.Item>
          </Form>
          
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <Button block onClick={() => setShowDispose(false)}>取消</Button>
            <Button block color="primary" onClick={handleDisposeSubmit}>确认处置</Button>
          </div>
        </div>
      </Popup>

      {/* 年度统计详情弹窗 */}
      <YearStatsDetail
        visible={showStatsDetail}
        onClose={() => setShowStatsDetail(false)}
        year={selectedYear}
        assets={assets}
        type="fixed"
      />

      {/* 费用管理弹窗 */}
      <AssetExpenseManager
        visible={showExpense}
        onClose={() => {
          setShowExpense(false)
          setExpenseAsset(null)
        }}
        asset={expenseAsset}
      />
    </div>
  )
}

export default FixedAssets
