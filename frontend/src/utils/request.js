import axios from 'axios'
import { getToken, removeToken } from '../utils/auth'
import { message } from 'antd'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 增加到60秒，用于AI报告生成等耗时操作
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      // 对于登录接口的401错误，不自动显示错误消息，由页面组件处理
      if (status === 401 && error.config.url.includes('/auth/login')) {
        // 不显示错误消息，交由登录页面处理
      } else if (status === 401) {
        removeToken()
        window.location.href = '/login'
        message.error('登录已过期，请重新登录')
      } else if (status === 403) {
        message.error('没有权限访问')
      } else if (status >= 500) {
        message.error('服务器错误，请稍后重试')
      } else if (data && data.message) {
        message.error(data.message)
      }
    } else if (error.code === 'ECONNABORTED') {
      // 请求超时，不显示错误（因为报告生成是异步的）
      console.log('请求超时，但后台仍在处理')
    } else if (error.request) {
      message.error('网络连接失败')
    } else {
      message.error('请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default api
export { api as request }