import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout, message } from 'antd'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Categories from './pages/Categories'
import FixedAssets from './pages/FixedAssets'
import AssetIncomeManagement from './pages/AssetIncomeManagement'
import Analytics from './pages/Analytics'
import UserManagement from './pages/UserManagement'
import UserProfile from './pages/UserProfile'
import NginxConfig from './pages/NginxConfig'
import AIReports from './pages/AIReports'
import AppLayout from './components/Layout'
import { getToken, removeToken } from './utils/auth'
import { checkToken } from './services/auth'

const { Content } = Layout

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await checkToken()
      if (response.code === 200) {
        setIsAuthenticated(true)
        setUserInfo(response.data)
      }
    } catch (error) {
      removeToken()
      message.error('登录已过期，请重新登录')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (userData = null) => {
    setIsAuthenticated(true)
    
    if (userData) {
      // 如果登录时直接传入了用户数据，直接使用
      setUserInfo(userData)
    } else {
      // 否则重新获取用户信息
      try {
        const response = await checkToken()
        if (response.code === 200) {
          setUserInfo(response.data)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    }
  }

  const handleLogout = () => {
    removeToken()
    setIsAuthenticated(false)
    setUserInfo(null) // 清空用户信息
    message.success('已退出登录')
  }

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh' }}>
        <Content style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div>加载中...</div>
        </Content>
      </Layout>
    )
  }

  return (
    <Router>
      <Routes>
        {!isAuthenticated ? (
          <>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="/register" element={<Register />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </>
        ) : (
          <>
            <Route path="/" element={<AppLayout onLogout={handleLogout} userInfo={userInfo} />}>
              <Route index element={<Dashboard />} />
              <Route path="projects" element={<Projects />} />
              <Route path="categories" element={<Categories />} />
              <Route path="assets" element={<FixedAssets />} />
              <Route path="assets/:assetId/income" element={<AssetIncomeManagement />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="reports" element={<AIReports />} />
              <Route path="profile" element={<UserProfile />} />
              {userInfo?.role === 'admin' && (
                <>
                  <Route path="users" element={<UserManagement />} />
                  <Route path="nginx" element={<NginxConfig />} />
                </>
              )}
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        )}
      </Routes>
    </Router>
  )
}

export default App