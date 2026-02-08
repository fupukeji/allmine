import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { SpinLoading, Toast } from 'antd-mobile'
import wechatSDK from '../../utils/wechat'
import { wechatLogin } from '../../services/auth'

const WeChatCallback = ({ onLoginSuccess }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [status, setStatus] = useState('处理中...')

  useEffect(() => {
    handleWeChatCallback()
  }, [])

  const handleWeChatCallback = async () => {
    try {
      // 1. 获取URL参数中的code
      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get('code')
      const state = urlParams.get('state')

      if (!code) {
        throw new Error('未获取到授权码')
      }

      setStatus('正在登录...')

      // 2. 调用后端接口，用code换取token和用户信息
      const response = await wechatLogin(code)

      if (response.code === 200) {
        const { token, user } = response.data

        // 3. 保存token和用户信息
        localStorage.setItem('token', token)
        localStorage.setItem('userInfo', JSON.stringify(user))

        setStatus('登录成功！')
        
        Toast.show({
          icon: 'success',
          content: '登录成功',
          duration: 1000
        })

        // 4. 如果是扫码登录，通知后端
        if (state && state.startsWith('qrcode_')) {
          // 通知后端扫码成功
          fetch(`/api/wechat/qrcode-confirm?ticket=${state}&token=${token}`, {
            method: 'POST'
          }).catch(err => console.error('通知后端失败:', err))
          
          // 扫码登录成功提示
          setStatus('扫码成功，请在电脑上查看')
          return
        }

        // 5. 通知父组件登录成功
        if (onLoginSuccess) {
          onLoginSuccess(response.data)
        }

        // 6. 跳转到首页
        setTimeout(() => {
          navigate('/', { replace: true })
        }, 1000)
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error) {
      console.error('微信登录回调处理失败:', error)
      
      setStatus('登录失败')
      
      Toast.show({
        icon: 'fail',
        content: error.message || '登录失败，请重试'
      })

      // 3秒后返回首页
      setTimeout(() => {
        navigate('/', { replace: true })
      }, 3000)
    }
  }

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}
    >
      <SpinLoading color="white" style={{ '--size': '48px' }} />
      <p style={{ marginTop: '20px', color: 'white', fontSize: '16px' }}>
        {status}
      </p>
    </div>
  )
}

export default WeChatCallback
