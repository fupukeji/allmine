/**
 * 登录模态框组件
 * 支持微信快捷登录和扫码登录两种方式
 */

import { useState, useEffect } from 'react'
import { Modal, Button, Toast, SpinLoading } from 'antd-mobile'
import wechatSDK from '../utils/wechat'
import { wechatLogin } from '../services/auth'
import QRCode from 'qrcode'
import './LoginModal.css'

const LoginModal = ({ visible, onLoginSuccess, onCancel }) => {
  const [loginType, setLoginType] = useState('loading') // loading | wechat | qrcode
  const [qrCodeUrl, setQrCodeUrl] = useState('')
  const [polling, setPolling] = useState(false)
  const [qrCodeExpired, setQrCodeExpired] = useState(false)

  useEffect(() => {
    if (visible) {
      detectLoginType()
    } else {
      // 关闭时清理状态
      setPolling(false)
      setQrCodeExpired(false)
    }
  }, [visible])

  // 检测登录类型
  const detectLoginType = () => {
    if (wechatSDK.isWeChatBrowser) {
      setLoginType('wechat')
    } else {
      setLoginType('qrcode')
      generateQRCode()
    }
  }

  // 微信快捷登录
  const handleWeChatLogin = async () => {
    try {
      Toast.show({
        icon: 'loading',
        content: '正在跳转微信授权...',
        duration: 0
      })

      // 构建授权URL
      const appId = import.meta.env.VITE_WECHAT_APPID
      const redirectUri = encodeURIComponent(window.location.origin + '/wechat-callback')
      const state = Math.random().toString(36).substring(7)
      
      const authUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo&state=${state}#wechat_redirect`
      
      window.location.href = authUrl
    } catch (error) {
      Toast.show({
        icon: 'fail',
        content: '微信登录失败，请重试'
      })
      console.error('微信登录错误:', error)
    }
  }

  // 生成二维码
  const generateQRCode = async () => {
    try {
      // 生成一个唯一的登录票据
      const ticket = `qrcode_${Date.now()}_${Math.random().toString(36).substring(7)}`
      
      // 构建二维码内容（微信公众号扫码登录链接）
      const appId = import.meta.env.VITE_WECHAT_APPID
      const redirectUri = encodeURIComponent(window.location.origin + '/wechat-qrcode-callback')
      const qrContent = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_userinfo&state=${ticket}#wechat_redirect`
      
      // 生成二维码图片
      const qrDataUrl = await QRCode.toDataURL(qrContent, {
        width: 250,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      })
      
      setQrCodeUrl(qrDataUrl)
      
      // 开始轮询检查扫码状态
      startPolling(ticket)
      
      // 5分钟后二维码过期
      setTimeout(() => {
        setQrCodeExpired(true)
        setPolling(false)
      }, 5 * 60 * 1000)
    } catch (error) {
      Toast.show({
        icon: 'fail',
        content: '生成二维码失败'
      })
      console.error('生成二维码错误:', error)
    }
  }

  // 轮询检查扫码状态
  const startPolling = (ticket) => {
    setPolling(true)
    
    const pollInterval = setInterval(async () => {
      try {
        // 调用后端接口检查扫码状态
        const response = await fetch(`/api/wechat/qrcode-status?ticket=${ticket}`)
        const result = await response.json()
        
        if (result.code === 200 && result.data.status === 'scanned') {
          // 扫码成功，获取token
          clearInterval(pollInterval)
          setPolling(false)
          
          localStorage.setItem('token', result.data.token)
          localStorage.setItem('userInfo', JSON.stringify(result.data.user))
          
          Toast.show({
            icon: 'success',
            content: '登录成功'
          })
          
          if (onLoginSuccess) {
            onLoginSuccess(result.data)
          }
        }
      } catch (error) {
        console.error('轮询扫码状态错误:', error)
      }
    }, 2000) // 每2秒轮询一次
    
    // 组件卸载时清理定时器
    return () => clearInterval(pollInterval)
  }

  // 刷新二维码
  const refreshQRCode = () => {
    setQrCodeExpired(false)
    generateQRCode()
  }

  // 开发模式：快速登录
  const handleDevLogin = async () => {
    try {
      Toast.show({
        icon: 'loading',
        content: '登录中...',
        duration: 0
      })

      const { login } = await import('../services/auth')
      const res = await login('admin', 'admin123')
      
      if (res.code === 200 && res.data.token) {
        localStorage.setItem('token', res.data.token)
        localStorage.setItem('userInfo', JSON.stringify(res.data.user))
        
        Toast.show({
          icon: 'success',
          content: '登录成功'
        })
        
        if (onLoginSuccess) {
          onLoginSuccess(res.data)
        }
      }
    } catch (error) {
      Toast.show({
        icon: 'fail',
        content: '登录失败'
      })
      console.error('开发模式登录错误:', error)
    }
  }

  return (
    <Modal
      visible={visible}
      onClose={onCancel}
      title="登录 TimeValue"
      content={
        <div className="login-modal-content">
          {loginType === 'loading' && (
            <div className="login-loading">
              <SpinLoading color="primary" />
              <p>正在检测登录方式...</p>
            </div>
          )}

          {loginType === 'wechat' && (
            <div className="wechat-login">
              <div className="login-icon">
                <img src="/logo.jpg" alt="TimeValue" />
              </div>
              <h3>微信快捷登录</h3>
              <p className="login-tip">使用微信授权登录，快速便捷</p>
              <Button
                block
                color="success"
                size="large"
                onClick={handleWeChatLogin}
              >
                微信授权登录
              </Button>
            </div>
          )}

          {loginType === 'qrcode' && (
            <div className="qrcode-login">
              <div className="qrcode-container">
                {qrCodeUrl && !qrCodeExpired ? (
                  <>
                    <img src={qrCodeUrl} alt="登录二维码" className="qrcode-image" />
                    {polling && (
                      <div className="qrcode-mask">
                        <SpinLoading color="white" />
                        <p>等待扫码...</p>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="qrcode-expired">
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>⏱️</div>
                    <p>二维码已过期</p>
                    <Button size="small" onClick={refreshQRCode}>
                      刷新二维码
                    </Button>
                  </div>
                )}
              </div>
              <h3>微信扫码登录</h3>
              <p className="login-tip">
                使用微信扫描二维码登录
              </p>
            </div>
          )}

          {/* 开发模式快速入口 */}
          {import.meta.env.DEV && (
            <div className="dev-login">
              <Button
                size="small"
                fill="none"
                onClick={handleDevLogin}
              >
                开发模式：Admin登录
              </Button>
            </div>
          )}
        </div>
      }
      closeOnMaskClick
    />
  )
}

export default LoginModal
