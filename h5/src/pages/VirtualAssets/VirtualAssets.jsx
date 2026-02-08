/**
 * 虚拟资产管理页面
 * 支持左侧分类筛选、资产列表、详情页
 */

import { useState, useEffect, useMemo, useRef } from 'react'
import { Card, List, Tag, Toast, PullToRefresh, Empty, Skeleton, Dialog, SwipeAction, Button, Popup, SideBar, Swiper } from 'antd-mobile'
import { AddOutline, ClockCircleOutline, RightOutline, LeftOutline } from 'antd-mobile-icons'
import { getProjects, deleteProject } from '../../services/projects'
import { getCategories } from '../../services/categories'
import VirtualAssetForm from '../../components/VirtualAssetForm'
import VirtualAssetDetail from './VirtualAssetDetail'
import YearStatsDetail from '../../components/YearStatsDetail'
import dayjs from 'dayjs'
import './VirtualAssets.css'

// 图标名称到emoji的映射
const ICON_MAP = {
  // 虚拟资产专用图标
  'sync': '🔄',
  'crown': '👑',
  'safety': '🛡️',
  'global': '🌐',
  'laptop': '💻',
  'cloud': '☁️',
  'phone': '📱',
  'folder': '📁',
  // 通用图标
  'home': '🏠',
  'car': '🚗',
  'appstore': '📦',
  'dollar': '💵',
  'bank': '🏦',
  'fund': '📈',
  'stock': '📊',
  'account-book': '📒',
  'pie-chart': '🧩',
  'rise': '📈',
  'shop': '🏪',
  'file-text': '📄',
  'safety-certificate': '📜',
  'cluster': '🎯',
  'bulb': '💡',
  'copyright': '©️',
  'code': '💻',
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
  // 默认图标
  'default': '📋'
}

// 获取emoji图标
const getEmojiIcon = (iconName) => {
  return ICON_MAP[iconName] || ICON_MAP['default']
}

const VirtualAssets = () => {
  const [loading, setLoading] = useState(false)
  const [projects, setProjects] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [showStatsDetail, setShowStatsDetail] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showDetail, setShowDetail] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [categories, setCategories] = useState([])
  
  const [stats, setStats] = useState({
    totalCount: 0,
    totalAmount: 0,
    activeCount: 0,
    expiredCount: 0,
    expiringCount: 0
  })

  // 年份切换相关
  const [selectedYear, setSelectedYear] = useState(dayjs().year())
  const swiperRef = useRef(null)

  // 获取所有年份列表（包含所有项目覆盖的年份）
  const yearList = useMemo(() => {
    const years = new Set()
    const currentYear = dayjs().year()
    years.add(currentYear) // 始终包含当前年份
    
    projects.forEach(p => {
      const start = dayjs(p.start_time || p.start_date)
      const end = dayjs(p.end_time || p.end_date)
      // 添加项目覆盖的所有年份
      for (let y = start.year(); y <= end.year(); y++) {
        if (y >= 2020) years.add(y)
      }
    })
    
    return Array.from(years).sort((a, b) => b - a) // 降序，最新年份在前
  }, [projects])

  // 计算项目在某年的分摊金额
  const calcYearAmount = (project, year) => {
    const start = dayjs(project.start_time || project.start_date)
    const end = dayjs(project.end_time || project.end_date)
    const totalDays = end.diff(start, 'day') + 1
    const totalAmount = project.total_amount || 0
    
    if (totalDays <= 0 || totalAmount <= 0) return 0
    
    // 计算该年的有效区间
    const yearStart = dayjs(`${year}-01-01`)
    const yearEnd = dayjs(`${year}-12-31`)
    
    const effectiveStart = start.isAfter(yearStart) ? start : yearStart
    const effectiveEnd = end.isBefore(yearEnd) ? end : yearEnd
    
    if (effectiveStart.isAfter(effectiveEnd)) return 0
    
    const daysInYear = effectiveEnd.diff(effectiveStart, 'day') + 1
    return (totalAmount * daysInYear) / totalDays
  }

  // 根据年份计算统计数据（按时间分摊成本）
  const yearStats = useMemo(() => {
    const result = {}
    const today = dayjs()
    
    yearList.forEach(year => {
      const yearStart = dayjs(`${year}-01-01`)
      const yearEnd = dayjs(`${year}-12-31`)
      
      // 筛选该年份有效的项目（有效期覆盖该年份）
      const yearProjects = projects.filter(p => {
        const start = dayjs(p.start_time || p.start_date)
        const end = dayjs(p.end_time || p.end_date)
        return start.year() <= year && end.year() >= year
      })
      
      let totalAmount = 0
      let activeCount = 0
      let expiredCount = 0
      let expiringCount = 0
      
      yearProjects.forEach(p => {
        // 按时间比例分摊金额
        totalAmount += calcYearAmount(p, year)
        
        const endDate = dayjs(p.end_time || p.end_date)
        const daysLeft = endDate.diff(today, 'day')
        
        if (daysLeft < 0) {
          expiredCount++
        } else if (daysLeft <= 7) {
          expiringCount++
        } else {
          activeCount++
        }
      })
      
      result[year] = {
        totalCount: yearProjects.length,
        totalAmount: totalAmount.toFixed(2),
        activeCount,
        expiredCount,
        expiringCount
      }
    })
    
    return result
  }, [projects, yearList])

  useEffect(() => {
    loadCategories()
    loadProjects()
  }, [])

  // 加载分类（只加载虚拟资产分类）
  const loadCategories = async () => {
    try {
      const res = await getCategories({ asset_type: 'virtual' })
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

  const loadProjects = async (isRefresh = false) => {
    try {
      setLoading(true)
      const res = await getProjects({ page: 1, per_page: 100 })
      
      if (res.code === 200 && res.data) {
        const newProjects = res.data.items || res.data
        setProjects(newProjects)
        calculateStats(newProjects)
      }
    } catch (error) {
      console.error('加载项目失败:', error)
      Toast.show({ icon: 'fail', content: '加载失败' })
    } finally {
      setLoading(false)
    }
  }

  // 根据分类筛选项目
  const filteredProjects = useMemo(() => {
    if (selectedCategory === 'all') {
      return projects
    }
    // 按category_id筛选
    return projects.filter(p => String(p.category_id) === selectedCategory)
  }, [projects, selectedCategory])

  // 计算各分类数量
  const categoryStats = useMemo(() => {
    const stats = { all: projects.length }
    categories.forEach(cat => {
      stats[String(cat.id)] = projects.filter(p => p.category_id === cat.id).length
    })
    return stats
  }, [projects, categories])

  const calculateStats = (projectList) => {
    const today = dayjs()
    let totalAmount = 0
    let activeCount = 0
    let expiredCount = 0
    let expiringCount = 0

    projectList.forEach(project => {
      totalAmount += project.total_amount || 0
      
      const endDate = dayjs(project.end_time || project.end_date)
      const daysLeft = endDate.diff(today, 'day')
      
      if (daysLeft < 0) {
        expiredCount++
      } else if (daysLeft <= 7) {
        expiringCount++
      } else {
        activeCount++
      }
    })

    setStats({
      totalCount: projectList.length,
      totalAmount: totalAmount.toFixed(2),
      activeCount,
      expiredCount,
      expiringCount
    })
  }

  const handleRefresh = async () => {
    await loadProjects(true)
  }

  const handleAdd = () => {
    setEditingProject(null)
    setShowForm(true)
  }

  const handleEdit = (project) => {
    setEditingProject(project)
    setShowForm(true)
  }

  const handleDelete = (project) => {
    Dialog.confirm({
      content: `确认删除「${project.name}」吗？`,
      confirmText: '删除',
      cancelText: '取消',
      onConfirm: async () => {
        try {
          const res = await deleteProject(project.id)
          if (res.code === 200) {
            Toast.show({ icon: 'success', content: '已删除' })
            await loadProjects(true)
          } else {
            Toast.show({ icon: 'fail', content: res.message || '删除失败' })
          }
        } catch (error) {
          Toast.show({ icon: 'fail', content: '删除失败' })
        }
      }
    })
  }

  const handleViewDetail = (project) => {
    setSelectedAsset(project)
    setShowDetail(true)
  }

  const calculateDaysLeft = (endDate) => {
    const today = new Date()
    const end = new Date(endDate)
    const diffTime = end - today
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  const getStatusTag = (project) => {
    const daysLeft = calculateDaysLeft(project.end_date || project.end_time)
    
    if (daysLeft < 0) {
      return <Tag color="default">已结束</Tag>
    } else if (daysLeft <= 7) {
      return <Tag color="danger">即将到期</Tag>
    } else if (daysLeft <= 30) {
      return <Tag color="warning">进行中</Tag>
    } else {
      return <Tag color="success">进行中</Tag>
    }
  }

  if (loading && projects.length === 0) {
    return (
      <div className="virtual-assets-page">
        <div className="page-header">
          <Skeleton.Title animated />
        </div>
        <div className="assets-list">
          <Card><Skeleton.Paragraph lineCount={3} animated /></Card>
        </div>
      </div>
    )
  }

  return (
    <div className="virtual-assets-page">
      {/* 页面头部 */}
      <div className="page-header">
        <div className="header-content">
          <div className="header-icon">
            <ClockCircleOutline fontSize={24} />
          </div>
          <div className="header-text">
            <h1>随风而逝</h1>
            <p>管理那些随时间流逝的资产</p>
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
      {projects.length > 0 && (
        <div className="stats-panel">
          <Swiper
            ref={swiperRef}
            defaultIndex={0}
            onIndexChange={(index) => setSelectedYear(yearList[index])}
            indicator={() => null}
            style={{ '--height': 'auto' }}
          >
            {yearList.map(year => {
              const ys = yearStats[year] || { totalCount: 0, totalAmount: '0', activeCount: 0, expiredCount: 0, expiringCount: 0 }
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
                      <div className="stat-value primary">￥{parseFloat(ys.totalAmount).toLocaleString()}</div>
                      <div className="stat-label">总金额</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value success">{ys.activeCount}</div>
                      <div className="stat-label">进行中</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value warning">{ys.expiringCount}</div>
                      <div className="stat-label">即将结束</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value danger">{ys.expiredCount}</div>
                      <div className="stat-label">已过期</div>
                    </div>
                  </div>
                </Swiper.Item>
              )
            })}
          </Swiper>
          <div className="stats-more" onClick={() => setShowStatsDetail(true)}>
            查看详情 <RightOutline />
          </div>
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
            {filteredProjects.length === 0 ? (
              <Empty
                description={selectedCategory === 'all' ? '还没有虚拟资产' : '该分类下暂无资产'}
                style={{ padding: '64px 0' }}
              >
                <Button color="primary" onClick={handleAdd}>
                  <AddOutline /> 立即添加
                </Button>
              </Empty>
            ) : (
              <List className="asset-list">
                {filteredProjects.map((project) => {
                  const daysLeft = calculateDaysLeft(project.end_date || project.end_time)
                  const startDate = new Date(project.start_date || project.start_time)
                  const endDate = new Date(project.end_date || project.end_time)
                  const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
                  const usedDays = Math.ceil((new Date() - startDate) / (1000 * 60 * 60 * 24))
                  const progress = Math.min(100, Math.max(0, (usedDays / totalDays) * 100))
                  
                  return (
                    <SwipeAction
                      key={project.id}
                      rightActions={[
                        {
                          key: 'edit',
                          text: '编辑',
                          color: 'primary',
                          onClick: () => handleEdit(project)
                        },
                        {
                          key: 'delete',
                          text: '删除',
                          color: 'danger',
                          onClick: () => handleDelete(project)
                        }
                      ]}
                    >
                      <List.Item
                        key={project.id}
                        prefix={
                          <div className="asset-icon-box">
                            {project.name?.charAt(0) || 'V'}
                          </div>
                        }
                        description={
                          <div className="asset-desc">
                            <div className="asset-tags">
                              {getStatusTag(project)}
                            </div>
                            <div className="asset-days">
                              {daysLeft >= 0 ? `剩余 ${daysLeft} 天` : `已过期 ${Math.abs(daysLeft)} 天`}
                            </div>
                            <div className="asset-progress">
                              <div 
                                className="progress-fill"
                                style={{
                                  width: `${progress}%`,
                                  background: progress > 80 ? '#ff4d4f' : progress > 50 ? '#faad14' : '#52c41a'
                                }}
                              />
                            </div>
                          </div>
                        }
                        arrow={<RightOutline />}
                        onClick={() => handleViewDetail(project)}
                      >
                        <div className="asset-title">
                          <span className="name">{project.name}</span>
                          <span className="amount">￥{parseFloat(project.total_amount || 0).toLocaleString()}</span>
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
      <VirtualAssetForm
        visible={showForm}
        onClose={() => setShowForm(false)}
        onSuccess={() => {
          setShowForm(false)
          loadProjects(true)
        }}
        initialData={editingProject}
      />

      {/* 详情页 */}
      <VirtualAssetDetail
        visible={showDetail}
        onClose={() => setShowDetail(false)}
        asset={selectedAsset}
      />

      {/* 统计详情弹窗 */}
      <Popup
        visible={showStatsDetail}
        onMaskClick={() => setShowStatsDetail(false)}
        bodyStyle={{
          borderTopLeftRadius: '16px',
          borderTopRightRadius: '16px',
          minHeight: '40vh'
        }}
      >
        <div style={{ padding: '24px 16px' }}>
          <h2 style={{ margin: '0 0 24px', fontSize: '18px', fontWeight: 'bold', textAlign: 'center' }}>
            资产统计详情
          </h2>
          
          <List>
            <List.Item extra={<span style={{ fontSize: '18px', fontWeight: 'bold' }}>{stats.totalCount}</span>}>
              资产总数
            </List.Item>
            <List.Item extra={<span style={{ fontSize: '18px', fontWeight: 'bold', color: '#667eea' }}>￥{parseFloat(stats.totalAmount).toLocaleString()}</span>}>
              总金额
            </List.Item>
            <List.Item extra={<span style={{ fontSize: '18px', fontWeight: 'bold', color: '#52c41a' }}>{stats.activeCount}</span>}>
              进行中
            </List.Item>
            <List.Item extra={<span style={{ fontSize: '18px', fontWeight: 'bold', color: '#faad14' }}>{stats.expiringCount}</span>}>
              即将结束
            </List.Item>
            <List.Item extra={<span style={{ fontSize: '18px', fontWeight: 'bold', color: '#ff4d4f' }}>{stats.expiredCount}</span>}>
              已过期
            </List.Item>
          </List>

          <div style={{ marginTop: '24px' }}>
            <Button block color="primary" onClick={() => setShowStatsDetail(false)}>
              关闭
            </Button>
          </div>
        </div>
      </Popup>

      {/* 年度统计详情弹窗 */}
      <YearStatsDetail
        visible={showStatsDetail}
        onClose={() => setShowStatsDetail(false)}
        year={selectedYear}
        projects={projects}
        type="virtual"
      />
    </div>
  )
}

export default VirtualAssets
