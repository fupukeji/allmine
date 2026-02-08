/**
 * HTTP请求封装
 * 基于axios，添加了token、错误处理等
 */

import axios from 'axios'
import { Toast } from 'antd-mobile'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    console.error('[请求错误]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data } = response
    
    // 后端统一返回格式：{ code, message, data }
    if (data.code === 200) {
      return data
    }
    
    // 处理业务错误
    Toast.show({
      icon: 'fail',
      content: data.message || '请求失败'
    })
    
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  (error) => {
    console.error('[响应错误]', error)
    
    // 处理HTTP错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，清除token并跳转登录
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          
          // 如果在微信浏览器中，跳转微信登录
          const ua = navigator.userAgent.toLowerCase()
          if (ua.includes('micromessenger')) {
            // 跳转微信登录
            window.location.href = '/wechat-login'
          } else {
            // 跳转普通登录页
            window.location.href = '/login'
          }
          
          Toast.show({
            icon: 'fail',
            content: '登录已过期，请重新登录'
          })
          break
          
        case 403:
          Toast.show({
            icon: 'fail',
            content: '没有权限访问'
          })
          break
          
        case 404:
          Toast.show({
            icon: 'fail',
            content: '请求的资源不存在'
          })
          break
          
        case 400:
          // 业务错误，返回后端的错误信息
          Toast.show({
            icon: 'fail',
            content: data?.message || '请求参数错误'
          })
          // 返回数据而不是抛出异常，让调用方可以获取具体错误信息
          return { code: 400, message: data?.message || '请求参数错误' }
          
        case 500:
          Toast.show({
            icon: 'fail',
            content: data?.message || '服务器错误'
          })
          break
          
        default:
          Toast.show({
            icon: 'fail',
            content: data?.message || '请求失败'
          })
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      Toast.show({
        icon: 'fail',
        content: '网络连接失败，请检查网络'
      })
    } else {
      // 其他错误
      Toast.show({
        icon: 'fail',
        content: error.message || '请求失败'
      })
    }
    
    return Promise.reject(error)
  }
)

export { request }
export default request
