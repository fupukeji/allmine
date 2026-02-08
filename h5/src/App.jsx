import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import MobileLayout from './layouts/MobileLayout'
import { WeChatCallback } from './pages/Auth'
import Dashboard from './pages/Dashboard'
import VirtualAssets from './pages/VirtualAssets'
import FixedAssets from './pages/FixedAssets'
import Reports from './pages/Reports'
import Profile from './pages/Profile'
import NotificationSettings from './pages/NotificationSettings/NotificationSettings'
import PreferenceSettings from './pages/PreferenceSettings/PreferenceSettings'
import AboutUs from './pages/AboutUs/AboutUs'
import LoginModal from './components/LoginModal'
import wechatSDK from './utils/wechat'
import { ConfigProvider } from 'antd-mobile'
import zhCN from 'antd-mobile/es/locales/zh-CN'
import { login } from './services/auth'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [loading, setLoading] = useState(true)
  const [showLoginModal, setShowLoginModal] = useState(false)

  useEffect(() => {
    initApp()
  }, [])

  const initApp = async () => {
    // 检查登录状态
    const token = localStorage.getItem('token')
    
    if (token) {
      // 验证token是否有效
      try {
        const { getUserInfo } = await import('./services/auth')
        await getUserInfo()
        setIsLoggedIn(true)
        console.log('使用已保存的token登录成功')
      } catch (error) {
        console.warn('Token已失效，重新登录', error)
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        
        // 开发模式：自动重新登录
        if (import.meta.env.DEV && !wechatSDK.isWeChatBrowser) {
          await performAutoLogin()
        } else {
          setShowLoginModal(true)
        }
      }
    } else {
      // 开发模式：自动使用admin登录
      if (import.meta.env.DEV && !wechatSDK.isWeChatBrowser) {
        await performAutoLogin()
      } else {
        // 生产环境：显示登录模态框
        setShowLoginModal(true)
      }
    }
    
    setLoading(false)

    // 初始化微信SDK
    if (wechatSDK.isWeChatBrowser) {
      wechatSDK.init().catch(err => {
        console.error('微信SDK初始化失败:', err)
      })
    }
  }

  const performAutoLogin = async () => {
    try {
      const res = await login('admin', 'admin123')
      if (res.code === 200 && res.data.token) {
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('userInfo', JSON.stringify(res.data.user))
        setIsLoggedIn(true)
        console.log('开发模式：已自动使用admin账号登录')
      }
    } catch (error) {
      console.error('开发模式自动登录失败:', error)
      setShowLoginModal(true)
    }
  }

  const handleLoginSuccess = (data) => {
    setIsLoggedIn(true)
    setShowLoginModal(false)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    setIsLoggedIn(false)
    setShowLoginModal(true)
  }

  if (loading) {
    return null // 显示loading动画（由index.html处理）
  }

  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <Routes>
          {/* 微信回调路由 */}
          <Route path="/wechat-callback" element={<WeChatCallback onLoginSuccess={handleLoginSuccess} />} />
          <Route path="/wechat-qrcode-callback" element={<WeChatCallback onLoginSuccess={handleLoginSuccess} />} />

          {/* 主应用路由 */}
          <Route
            path="/"
            element={
              isLoggedIn ? (
                <MobileLayout onLogout={handleLogout} />
              ) : (
                <Navigate to="/" replace />
              )
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="virtual-assets" element={<VirtualAssets />} />
            <Route path="fixed-assets" element={<FixedAssets />} />
            <Route path="reports" element={<Reports />} />
            <Route path="profile" element={<Profile />} />
            <Route path="notification-settings" element={<NotificationSettings />} />
            <Route path="preference-settings" element={<PreferenceSettings />} />
            <Route path="about-us" element={<AboutUs />} />
          </Route>

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>

      {/* 登录模态框 */}
      <LoginModal
        visible={showLoginModal}
        onLoginSuccess={handleLoginSuccess}
        onCancel={() => setShowLoginModal(false)}
      />
    </ConfigProvider>
  )
}

export default App
