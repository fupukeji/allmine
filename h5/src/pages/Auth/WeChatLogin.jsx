import { useEffect } from 'react'
import { Button, SpinLoading } from 'antd-mobile'
import { SmileOutline } from 'antd-mobile-icons'
import wechatSDK from '../../utils/wechat'
import './WeChatLogin.css'

const WeChatLogin = () => {
  const isWeChatBrowser = wechatSDK.isWeChatBrowser

  useEffect(() => {
    // 如果在微信浏览器中，自动跳转授权
    if (isWeChatBrowser) {
      // 延迟1秒后自动跳转，给用户看到提示
      const timer = setTimeout(() => {
        handleWeChatLogin()
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [isWeChatBrowser])

  const handleWeChatLogin = () => {
    const redirectUri = window.location.origin + '/wechat-callback'
    wechatSDK.constructor.login(redirectUri)
  }

  return (
    <div className="wechat-login-page">
      {/* 背景装饰 */}
      <div className="bg-decoration">
        <div className="circle circle-1"></div>
        <div className="circle circle-2"></div>
        <div className="circle circle-3"></div>
      </div>

      <div className="login-content">
        {/* Logo */}
        <div className="logo-container">
          <img src="/logo.jpg" alt="TimeValue Logo" className="logo" />
          <h1 className="app-name">TimeValue</h1>
          <p className="app-slogan">恒产生金 · 智慧理财</p>
        </div>

        {/* 登录卡片 */}
        <div className="login-card">
          {isWeChatBrowser ? (
            <>
              <div className="loading-container">
                <SpinLoading color="primary" style={{ '--size': '48px' }} />
                <p className="loading-text">正在跳转微信授权...</p>
              </div>
            </>
          ) : (
            <>
              <div className="tip-icon">
                <SmileOutline fontSize={64} color="#faad14" />
              </div>
              <h2 className="tip-title">请在微信中打开</h2>
              <p className="tip-desc">
                TimeValue 需要在微信浏览器中使用
                <br />
                请通过微信扫描二维码或分享链接打开
              </p>
              <div className="qr-placeholder">
                <p>将此页面分享给微信好友</p>
                <p>或在微信中输入链接访问</p>
              </div>
            </>
          )}
        </div>

        {/* 底部信息 */}
        <div className="footer-info">
          <p>🚀 Powered by 孚普科技</p>
          <p>AI驱动的MVP快速迭代解决方案</p>
        </div>
      </div>
    </div>
  )
}

export default WeChatLogin
