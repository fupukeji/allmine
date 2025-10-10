import { request } from '../utils/request'

// 获取用户个人信息
export const getUserProfile = () => {
  return request({
    url: '/auth/profile',
    method: 'GET'
  })
}

// 更新用户个人信息
export const updateUserProfile = (data) => {
  return request({
    url: '/auth/profile',
    method: 'PUT',
    data
  })
}

// 修改密码
export const changePassword = (data) => {
  return request({
    url: '/auth/profile',
    method: 'PUT',
    data: {
      password: data.newPassword
    }
  })
}