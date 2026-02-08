/**
 * 通知设置服务
 */
import request from '../utils/request'

// 获取通知设置
export const getNotificationSettings = () => {
  return request.get('/notification-settings')
}

// 更新通知设置
export const updateNotificationSettings = (data) => {
  return request.put('/notification-settings', data)
}

// 快捷切换单个开关
export const toggleNotification = (key, value) => {
  return request.post('/notification-settings/toggle', { key, value })
}
