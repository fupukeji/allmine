/**
 * 我的 - 个人中心页面
 * 包含用户信息、资产类型管理（虚拟资产/固定资产分开）、设置等
 */

import { useState, useEffect } from 'react'
import { Card, List, Button, Dialog, Popup, SwipeAction, Input, Toast, SpinLoading } from 'antd-mobile'
import { useNavigate } from 'react-router-dom'
import { 
  SetOutline, 
  BellOutline, 
  InformationCircleOutline,
  AddOutline,
  LeftOutline
} from 'antd-mobile-icons'
import { DndContext, closestCenter, PointerSensor, TouchSensor, useSensor, useSensors } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { getCategories, createCategory, updateCategory, deleteCategory, reorderCategories } from '../../services/categories'
import { useSwipeBack } from '../../hooks'
import './Profile.css'

// 图标名称到emoji的映射
const ICON_MAP = {
  // 虚拟资产专用图标
  'sync': '🔄', 'crown': '👑', 'safety': '🛡️', 'global': '🌐',
  'laptop': '💻', 'cloud': '☁️', 'phone': '📱', 'folder': '📁',
  // 固定资产专用图标
  'home': '🏠', 'car': '🚗', 'appstore': '🎮', 'skin': '💎',
  'gift': '🎁', 'trophy': '🏆',
  // 通用图标
  'dollar': '💵', 'bank': '🏦', 'fund': '📈', 'stock': '📊',
  'account-book': '📒', 'pie-chart': '🧩', 'rise': '📈',
  'shop': '🏪', 'file-text': '📄', 'safety-certificate': '📜', 'cluster': '🎯',
  'bulb': '💡', 'copyright': '©️', 'code': '💻',
  'read': '📖', 'book': '📕', 'solution': '🎓',
  'heart': '❤️', 'team': '👨‍👩‍👧', 'picture': '🎨',
  'golden': '🏆', 'gold': '🥇', 'container': '📦',
  'link': '🔗', 'transaction': '🪙', 'star': '⭐',
  'credit-card': '💳',
  // 新增图标
  'camera': '📷', 'headphone': '🎧', 'watch': '⌚',
  'default': '📋'
}
const getEmojiIcon = (iconName) => ICON_MAP[iconName] || ICON_MAP['default']

// 资产类型配置
const ASSET_TYPES = {
  virtual: {
    title: '虚拟资产分类',
    description: '管理会员、订阅、保险等有时效的资产分类',
    icon: '⏳',
    color: '#667eea'
  },
  fixed: {
    title: '固定资产分类',
    description: '管理房产、车辆、设备等长期持有的资产分类',
    icon: '🏠',
    color: '#52c41a'
  }
}

// 可拖拽分类项组件
const SortableCategoryItem = ({ category, assetTypeConfig, onEdit, onDelete, isReordering }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id: category.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.8 : 1,
    zIndex: isDragging ? 1000 : 1
  }

  if (isReordering) {
    return (
      <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
        <List.Item
          prefix={
            <div className="category-icon" style={{ background: category.color || assetTypeConfig?.color }}>
              {getEmojiIcon(category.icon)}
            </div>
          }
          extra={<span className="drag-handle">☰</span>}
        >
          {category.name}
        </List.Item>
      </div>
    )
  }

  return (
    <SwipeAction
      rightActions={[
        { key: 'edit', text: '编辑', color: 'primary', onClick: () => onEdit(category) },
        { key: 'delete', text: '删除', color: 'danger', onClick: () => onDelete(category) }
      ]}
    >
      <List.Item
        prefix={
          <div className="category-icon" style={{ background: category.color || assetTypeConfig?.color }}>
            {getEmojiIcon(category.icon)}
          </div>
        }
        description={category.description}
      >
        {category.name}
      </List.Item>
    </SwipeAction>
  )
}

const Profile = () => {
  const navigate = useNavigate()
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  
  // 类型管理状态
  const [showCategoryManager, setShowCategoryManager] = useState(false)
  const [currentAssetType, setCurrentAssetType] = useState('virtual') // virtual | fixed
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  
  // 分类计数
  const [virtualCount, setVirtualCount] = useState(0)
  const [fixedCount, setFixedCount] = useState(0)
  
  // 编辑分类状态
  const [showEditCategory, setShowEditCategory] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [categoryName, setCategoryName] = useState('')
  const [categoryIcon, setCategoryIcon] = useState('default')
  const [categoryDescription, setCategoryDescription] = useState('')
  
  // 排序模式
  const [isReordering, setIsReordering] = useState(false)

  // 左滑返回
  const swipeHandlers = useSwipeBack(() => setShowCategoryManager(false))

  // 加载分类计数
  const loadCategoryCounts = async () => {
    try {
      const [virtualRes, fixedRes] = await Promise.all([
        getCategories({ asset_type: 'virtual' }),
        getCategories({ asset_type: 'fixed' })
      ])
      if (virtualRes.code === 200) setVirtualCount(virtualRes.data?.length || 0)
      if (fixedRes.code === 200) setFixedCount(fixedRes.data?.length || 0)
    } catch (error) {
      console.error('加载分类计数失败:', error)
    }
  }

  // 加载分类列表
  const loadCategories = async (assetType) => {
    try {
      setLoading(true)
      const res = await getCategories({ asset_type: assetType })
      if (res.code === 200) {
        setCategories(res.data || [])
      }
    } catch (error) {
      console.error('加载分类失败:', error)
      Toast.show({ icon: 'fail', content: '加载失败' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCategoryCounts()
  }, [])

  const handleLogout = async () => {
    const result = await Dialog.confirm({
      content: '确定要退出登录吗？',
    })
    
    if (result) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      navigate('/wechat-login', { replace: true })
    }
  }

  const openCategoryManager = (assetType) => {
    setCurrentAssetType(assetType)
    setShowCategoryManager(true)
    loadCategories(assetType)
  }

  const handleAddCategory = () => {
    setEditingCategory(null)
    setCategoryName('')
    setCategoryIcon('default')
    setCategoryDescription('')
    setShowEditCategory(true)
  }

  const handleEditCategory = (category) => {
    setEditingCategory(category)
    setCategoryName(category.name)
    setCategoryIcon(category.icon || 'default')
    setCategoryDescription(category.description || '')
    setShowEditCategory(true)
  }

  const handleDeleteCategory = (category) => {
    Dialog.confirm({
      content: `确定删除「${category.name}」分类吗？`,
      onConfirm: async () => {
        try {
          const res = await deleteCategory(category.id)
          if (res.code === 200) {
            Toast.show({ icon: 'success', content: '已删除' })
            loadCategories(currentAssetType)
            loadCategoryCounts()
          } else {
            // 显示后端返回的具体错误信息
            Toast.show({ icon: 'fail', content: res.message || '删除失败' })
          }
        } catch (error) {
          // 尝试从错误对象获取后端返回的消息
          const errorMsg = error.response?.data?.message || error.message || '删除失败'
          Toast.show({ icon: 'fail', content: errorMsg })
        }
      }
    })
  }

  const handleSaveCategory = async () => {
    if (!categoryName.trim()) {
      Toast.show({ icon: 'fail', content: '请输入分类名称' })
      return
    }

    try {
      const data = {
        name: categoryName.trim(),
        icon: categoryIcon || 'default',
        description: categoryDescription.trim(),
        color: ASSET_TYPES[currentAssetType].color,
        asset_type: currentAssetType  // 关键：指定资产类型
      }

      let res
      if (editingCategory) {
        res = await updateCategory(editingCategory.id, data)
      } else {
        res = await createCategory(data)
      }

      if (res.code === 200 || res.code === 201) {
        Toast.show({ icon: 'success', content: editingCategory ? '已更新' : '已添加' })
        setShowEditCategory(false)
        loadCategories(currentAssetType)
        loadCategoryCounts()
      } else {
        Toast.show({ icon: 'fail', content: res.message || '操作失败' })
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '操作失败' })
    }
  }

  // 拖拽传感器配置
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 5 } })
  )

  // 拖拽结束处理
  const handleDragEnd = async (event) => {
    const { active, over } = event
    
    if (active.id !== over?.id) {
      const oldIndex = categories.findIndex(c => c.id === active.id)
      const newIndex = categories.findIndex(c => c.id === over.id)
      
      const newCategories = arrayMove(categories, oldIndex, newIndex)
      setCategories(newCategories)
      
      // 保存到后端
      const orders = newCategories.map((cat, idx) => ({
        id: cat.id,
        sort_order: idx
      }))
      
      try {
        await reorderCategories(orders)
      } catch (error) {
        console.error('保存排序失败:', error)
        loadCategories(currentAssetType)
      }
    }
  }

  // 图标选项（使用icon name）
  const iconOptions = [
    { name: 'default', emoji: '📋' },
    { name: 'sync', emoji: '🔄' },
    { name: 'crown', emoji: '👑' },
    { name: 'safety', emoji: '🛡️' },
    { name: 'global', emoji: '🌐' },
    { name: 'laptop', emoji: '💻' },
    { name: 'phone', emoji: '📱' },
    { name: 'appstore', emoji: '🎮' },
    { name: 'camera', emoji: '📷' },
    { name: 'headphone', emoji: '🎧' },
    { name: 'watch', emoji: '⌚' },
    { name: 'car', emoji: '🚗' },
    { name: 'home', emoji: '🏠' },
    { name: 'skin', emoji: '💎' },
    { name: 'picture', emoji: '🎨' },
    { name: 'container', emoji: '📦' }
  ]

  const assetTypeConfig = ASSET_TYPES[currentAssetType]

  return (
    <div className="profile-page">
      {/* 用户信息卡片 */}
      <div className="user-header">
        <div className="user-avatar">
          {userInfo.username?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div className="user-info">
          <div className="user-name">{userInfo.username || '用户'}</div>
          <div className="user-email">{userInfo.email || '欢迎使用 TimeValue'}</div>
        </div>
      </div>

      {/* 资产分类管理 - 分开两种 */}
      <Card className="section-card" title="资产分类管理">
        <List>
          <List.Item
            prefix={<span className="list-icon">⏳</span>}
            arrow
            onClick={() => openCategoryManager('virtual')}
            description={`${virtualCount} 个分类`}
          >
            虚拟资产分类
          </List.Item>
          <List.Item
            prefix={<span className="list-icon">🏠</span>}
            arrow
            onClick={() => openCategoryManager('fixed')}
            description={`${fixedCount} 个分类`}
          >
            固定资产分类
          </List.Item>
        </List>
      </Card>

      {/* 功能设置 */}
      <Card className="section-card" title="功能设置">
        <List>
          <List.Item
            prefix={<BellOutline fontSize={20} color="#faad14" />}
            arrow
            onClick={() => navigate('/notification-settings')}
          >
            通知设置
          </List.Item>
          <List.Item
            prefix={<SetOutline fontSize={20} color="#667eea" />}
            arrow
            onClick={() => navigate('/preference-settings')}
          >
            偏好设置
          </List.Item>
          <List.Item
            prefix={<InformationCircleOutline fontSize={20} color="#52c41a" />}
            arrow
            onClick={() => navigate('/about-us')}
          >
            关于我们
          </List.Item>
        </List>
      </Card>

      {/* 退出登录 */}
      <div className="logout-section">
        <Button block color="danger" onClick={handleLogout}>
          退出登录
        </Button>
      </div>

      {/* 版本信息 */}
      <div className="version-info">
        <p>TimeValue v1.0.0</p>
        <p>🚀 Powered by 孚普科技</p>
      </div>

      {/* 分类管理弹窗 */}
      <Popup
        visible={showCategoryManager}
        onMaskClick={() => setShowCategoryManager(false)}
        position="right"
        bodyStyle={{ width: '100vw', height: '100vh' }}
      >
        <div className="category-manager" {...swipeHandlers}>
          <div className="manager-header">
            <div className="back-btn" onClick={() => setShowCategoryManager(false)}>
              <LeftOutline fontSize={20} />
            </div>
            <h2>
              <span style={{ marginRight: 8 }}>{assetTypeConfig?.icon}</span>
              {assetTypeConfig?.title}
            </h2>
            <Button fill="none" color="primary" onClick={handleAddCategory}>
              <AddOutline /> 添加
            </Button>
          </div>

          {/* 类型说明 + 排序按钮 */}
          <div className="type-description" style={{ background: assetTypeConfig?.color + '10' }}>
            <p style={{ color: assetTypeConfig?.color, flex: 1 }}>{assetTypeConfig?.description}</p>
            <Button 
              size="mini" 
              color={isReordering ? 'success' : 'default'}
              onClick={() => setIsReordering(!isReordering)}
            >
              {isReordering ? '✓ 完成' : '调序'}
            </Button>
          </div>

          <div className="category-list">
            {loading ? (
              <div className="loading-container">
                <SpinLoading color="primary" />
              </div>
            ) : categories.length === 0 ? (
              <div className="empty-tip">
                暂无分类，点击右上角添加
              </div>
            ) : isReordering ? (
              // 拖拽排序模式
              <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                <SortableContext items={categories.map(c => c.id)} strategy={verticalListSortingStrategy}>
                  <List>
                    {categories.map(category => (
                      <SortableCategoryItem
                        key={category.id}
                        category={category}
                        assetTypeConfig={assetTypeConfig}
                        isReordering={true}
                      />
                    ))}
                  </List>
                </SortableContext>
              </DndContext>
            ) : (
              // 普通模式
              <List>
                {categories.map(category => (
                  <SortableCategoryItem
                    key={category.id}
                    category={category}
                    assetTypeConfig={assetTypeConfig}
                    onEdit={handleEditCategory}
                    onDelete={handleDeleteCategory}
                    isReordering={false}
                  />
                ))}
              </List>
            )}
          </div>

          <div className="manager-tip">
            💡 {isReordering ? '拖动分类项调整顺序' : '左滑分类项可以编辑或删除'}
          </div>
        </div>
      </Popup>

      {/* 编辑分类弹窗 */}
      <Popup
        visible={showEditCategory}
        onMaskClick={() => setShowEditCategory(false)}
        bodyStyle={{
          borderTopLeftRadius: '16px',
          borderTopRightRadius: '16px',
          padding: '20px'
        }}
      >
        <div className="edit-category-form">
          <h3>{editingCategory ? '编辑分类' : '添加分类'}</h3>
          
          <div className="form-item">
            <label>分类名称</label>
            <Input
              value={categoryName}
              onChange={setCategoryName}
              placeholder="请输入分类名称"
              clearable
            />
          </div>

          <div className="form-item">
            <label>分类说明</label>
            <Input
              value={categoryDescription}
              onChange={setCategoryDescription}
              placeholder="例如：Netflix、Spotify、视频网站等订阅"
              clearable
            />
          </div>

          <div className="form-item">
            <label>选择图标</label>
            <div className="emoji-grid">
              {iconOptions.map(opt => (
                <div
                  key={opt.name}
                  className={`emoji-item ${categoryIcon === opt.name ? 'selected' : ''}`}
                  onClick={() => setCategoryIcon(opt.name)}
                >
                  {opt.emoji}
                </div>
              ))}
            </div>
          </div>

          <div className="form-actions">
            <Button block onClick={() => setShowEditCategory(false)}>取消</Button>
            <Button block color="primary" onClick={handleSaveCategory}>
              {editingCategory ? '更新' : '添加'}
            </Button>
          </div>
        </div>
      </Popup>
    </div>
  )
}

export default Profile
