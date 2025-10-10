import api from '../utils/request'
import { setToken } from '../utils/auth'

// 用户注册
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData)
  return response
}

// 用户登录
export const login = async (credentials) => {
  const response = await api.post('/auth/login', credentials)
  if (response.code === 200 && response.data.access_token) {
    setToken(response.data.access_token)
  }
  return response
}

// 获取用户信息
export const getProfile = async () => {
  const response = await api.get('/auth/profile')
  return response
}

// 更新用户信息
export const updateProfile = async (userData) => {
  const response = await api.put('/auth/profile', userData)
  return response
}

// 验证token
export const checkToken = async () => {
  const response = await api.get('/auth/check-token')
  return response
}