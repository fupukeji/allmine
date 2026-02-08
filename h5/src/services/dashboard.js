/**
 * 首页数据API
 */
import request from '../utils/request'

/**
 * 获取首页统计数据
 */
export const getDashboardStats = () => {
  return request.get('/analytics/dashboard')
}

/**
 * 获取快到期提醒
 */
export const getExpiringAlerts = () => {
  return request.get('/assets/expiring')
}
