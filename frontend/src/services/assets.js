import { request } from '../utils/request'

// 获取固定资产列表
export const getAssets = (params = {}) => {
  return request({
    url: '/assets',
    method: 'GET',
    params
  })
}

// 创建固定资产
export const createAsset = (data) => {
  return request({
    url: '/assets',
    method: 'POST',
    data
  })
}

// 获取固定资产详情
export const getAsset = (id) => {
  return request({
    url: `/assets/${id}`,
    method: 'GET'
  })
}

// 更新固定资产
export const updateAsset = (id, data) => {
  return request({
    url: `/assets/${id}`,
    method: 'PUT',
    data
  })
}

// 删除固定资产
export const deleteAsset = (id) => {
  return request({
    url: `/assets/${id}`,
    method: 'DELETE'
  })
}

// 批量删除固定资产
export const batchDeleteAssets = (assetIds) => {
  return request({
    url: '/assets/batch-delete',
    method: 'POST',
    data: {
      asset_ids: assetIds
    }
  })
}

// 获取固定资产折旧详情
export const getAssetDepreciation = (id, baseDate = null) => {
  return request({
    url: `/assets/${id}/depreciation`,
    method: 'GET',
    params: baseDate ? { base_date: baseDate } : {}
  })
}

// 获取固定资产统计信息
export const getAssetsStatistics = () => {
  return request({
    url: '/assets/statistics',
    method: 'GET'
  })
}