import React, { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, Avatar, Dropdown, message } from 'antd'
import { 
  DashboardOutlined, 
  ProjectOutlined, 
  TagsOutlined, 
  UserOutlined, 
  LogoutOutlined,
  SettingOutlined,
  AreaChartOutlined,
  TeamOutlined,
  BankOutlined,
  CloudServerOutlined,
  FileTextOutlined
} from '@ant-design/icons'
import { getProfile } from '../services/auth'

const { Header, Sider, Content } = Layout

const AppLayout = ({ onLogout, userInfo }) => {
  const [collapsed, setCollapsed] = useState(false)
  const [localUserInfo, setLocalUserInfo] = useState(userInfo || {})
  const navigate = useNavigate()
  const location = useLocation()

  // 使用传入的userInfo作为主要数据源，确保权限判断的准确性
  const currentUser = userInfo || localUserInfo

  useEffect(() => {
    if (userInfo) {
      setLocalUserInfo(userInfo)
    } else {
      fetchUserInfo()
    }
    
    // 监听用户信息更新事件
    const handleUserProfileUpdate = (event) => {
      if (event.detail) {
        setLocalUserInfo(event.detail)
      } else {
        // 如果没有详细信息，重新获取
        fetchUserInfo()
      }
    }
    
    window.addEventListener('userProfileUpdated', handleUserProfileUpdate)
    
    return () => {
      window.removeEventListener('userProfileUpdated', handleUserProfileUpdate)
    }
  }, [userInfo])

  // 单独监听userInfo变化，确保及时更新本地状态
  useEffect(() => {
    if (userInfo && userInfo.username) {
      setLocalUserInfo(userInfo)
    }
  }, [userInfo])

  const fetchUserInfo = async () => {
    try {
      const response = await getProfile()
      if (response.code === 200) {
        setLocalUserInfo(response.data)
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/virtual-assets',
      icon: <ProjectOutlined />,
      label: '随风而逝',
    },
    {
      key: '/assets',
      icon: <BankOutlined />,
      label: '恒产生金',
    },
    {
      key: '/categories',
      icon: <TagsOutlined />,
      label: '分类管理',
    },
    {
      key: '/analytics',
      icon: <AreaChartOutlined />,
      label: 'BI 分析',
    },
    {
      key: '/reports',
      icon: <FileTextOutlined />,
      label: '智能报告',
    },
    ...(currentUser?.role === 'admin' ? [
      {
        key: '/users',
        icon: <TeamOutlined />,
        label: '用户管理',
      },
      {
        key: '/nginx',
        icon: <CloudServerOutlined />,
        label: 'Nginx配置',
      }
    ] : [])
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <SettingOutlined />,
      label: '个人设置',
      onClick: () => navigate('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: onLogout,
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  const handleUserMenuClick = ({ key }) => {
    if (key === 'profile') {
      navigate('/profile')
    } else if (key === 'logout') {
      onLogout()
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          background: '#fff',
          boxShadow: '2px 0 8px rgba(0,0,0,0.15)'
        }}
      >
        <div style={{ 
          height: '64px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0',
          flexDirection: 'column'
        }}>
          {!collapsed && (
            <>
              <h2 style={{ margin: '4px 0 0 0', color: '#1890ff', fontSize: '16px' }}>时间价值</h2>
              <div style={{ fontSize: '10px', color: '#999', lineHeight: '1' }}>
                by 孚普科技
              </div>
            </>
          )}
        </div>
        <Menu
          theme="light"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0 }}
        />
      </Sider>
      
      <Layout>
        <Header style={{ 
          padding: '0 24px', 
          background: '#fff', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
        }}>
          <Button
            type="text"
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: '64px', height: '64px' }}
          >
            {collapsed ? '☰' : '✕'}
          </Button>
          
          <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenuClick }} placement="bottomRight">
            <div style={{ 
              cursor: 'pointer', 
              display: 'flex', 
              alignItems: 'center',
              padding: '8px 16px',
              borderRadius: '20px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              transition: 'all 0.3s ease',
              boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)'
            }}
            >
              <Avatar 
                icon={<UserOutlined />} 
                style={{ 
                  marginRight: '10px',
                  background: 'rgba(255, 255, 255, 0.3)',
                  border: '2px solid rgba(255, 255, 255, 0.5)'
                }} 
              />
              <span style={{ color: '#fff', fontWeight: '500' }}>
                {currentUser.username || '用户'}
              </span>
              {currentUser.role === 'admin' && (
                <span style={{ 
                  marginLeft: '8px', 
                  fontSize: '11px', 
                  color: '#ffd700',
                  background: 'rgba(255, 215, 0, 0.2)',
                  padding: '2px 8px',
                  borderRadius: '10px',
                  fontWeight: 'bold'
                }}>
                  [管理员]
                </span>
              )}
            </div>
          </Dropdown>
        </Header>
        
        <Content style={{ 
          margin: '24px', 
          padding: '24px', 
          background: '#fff',
          borderRadius: '8px',
          minHeight: 'calc(100vh - 160px)'
        }}>
          <Outlet />
        </Content>
        
        {/* 底部版权信息 */}
        <div style={{
          textAlign: 'center',
          padding: '16px 24px',
          borderTop: '1px solid #f0f0f0',
          backgroundColor: '#fafafa',
          color: '#666',
          fontSize: '12px'
        }}>
          <div>
            © 2024 TimeValue - 个人资产管理系统
          </div>
          <div style={{ marginTop: '4px' }}>
            🚀 Powered by 孚普科技（北京）有限公司 | 
            🤖 AI驱动的MVP快速迭代解决方案 | 
            🌐 <a href="https://fupukeji.com" target="_blank" rel="noopener noreferrer">了解更多AI产品</a>
          </div>
        </div>
      </Layout>
    </Layout>
  )
}

export default AppLayout