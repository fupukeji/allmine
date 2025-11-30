import request from '../utils/request'

// 获取用户列表
export const getUsers = (params) => {
  return request.get('/admin/users', { params })
}

// 创建用户
export const createUser = (data) => {
  return request.post('/admin/users', data)
}

// 更新用户
export const updateUser = (userId, data) => {
  return request.put(`/admin/users/${userId}`, data)
}

// 删除用户
export const deleteUser = (userId, confirmData) => {
  return request.delete(`/admin/users/${userId}`, { data: confirmData })  
}

// 切换用户状态
export const toggleUserStatus = (userId) => {
  return request.put(`/admin/users/${userId}/toggle-status`)
}

// 获取管理员统计数据
export const getAdminStats = () => {
  return request.get('/admin/stats')
}