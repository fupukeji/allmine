import { request } from '../utils/request'

// 获取资产维护记录列表
export const getAssetMaintenances = (assetId, params = {}) => {
  return request({
    url: `/assets/${assetId}/maintenances`,
    method: 'GET',
    params
  })
}

// 创建资产维护记录
export const createAssetMaintenance = (assetId, data) => {
  return request({
    url: `/assets/${assetId}/maintenances`,
    method: 'POST',
    data
  })
}

// 更新资产维护记录
export const updateAssetMaintenance = (assetId, maintenanceId, data) => {
  return request({
    url: `/assets/${assetId}/maintenances/${maintenanceId}`,
    method: 'PUT',
    data
  })
}

// 删除资产维护记录
export const deleteAssetMaintenance = (assetId, maintenanceId) => {
  return request({
    url: `/assets/${assetId}/maintenances/${maintenanceId}`,
    method: 'DELETE'
  })
}

// 获取资产维护统计
export const getAssetMaintenanceStats = (assetId) => {
  return request({
    url: `/assets/${assetId}/maintenance-stats`,
    method: 'GET'
  })
}

// 获取用户所有资产维护概览
export const getMaintenanceOverview = () => {
  return request({
    url: '/maintenance-overview',
    method: 'GET'
  })
}

// 获取维护日历
export const getMaintenanceCalendar = (params = {}) => {
  return request({
    url: '/maintenance-calendar',
    method: 'GET',
    params
  })
}

// 获取维护提醒列表
export const getMaintenanceReminders = () => {
  return request({
    url: '/maintenance-reminders',
    method: 'GET'
  })
}

// 创建维护提醒
export const createMaintenanceReminder = (data) => {
  return request({
    url: '/maintenance-reminders',
    method: 'POST',
    data
  })
}

// 获取到期的提醒
export const getDueReminders = () => {
  return request({
    url: '/maintenance-reminders/due',
    method: 'GET'
  })
}