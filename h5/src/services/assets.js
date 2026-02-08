/**
 * 固定资产相关API
 */
import request from '../utils/request'

/**
 * 获取固定资产列表
 */
export const getAssets = (params) => {
  return request.get('/assets', { params })
}

/**
 * 获取固定资产详情
 */
export const getAssetDetail = (id) => {
  return request.get(`/assets/${id}`)
}

/**
 * 创建固定资产
 */
export const createAsset = (data) => {
  return request.post('/assets', data)
}

/**
 * 更新固定资产
 */
export const updateAsset = (id, data) => {
  return request.put(`/assets/${id}`, data)
}

/**
 * 删除固定资产
 */
export const deleteAsset = (id) => {
  return request.delete(`/assets/${id}`)
}

/**
 * 获取固定资产统计
 */
export const getAssetStats = () => {
  return request.get('/assets/stats')
}

/**
 * 获取快到期资产
 */
export const getExpiringAssets = () => {
  return request.get('/assets/expiring')
}
