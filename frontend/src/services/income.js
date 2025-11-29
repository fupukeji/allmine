import { request } from '../utils/request'

// 获取资产收入列表
export const getAssetIncomes = (assetId, params = {}) => {
  return request({
    url: `/income/${assetId}`,
    method: 'GET',
    params
  })
}

// 创建资产收入记录
export const createAssetIncome = (assetId, data) => {
  return request({
    url: '/income',
    method: 'POST',
    data: {
      ...data,
      asset_id: assetId
    }
  })
}

// 更新资产收入记录
export const updateAssetIncome = (assetId, incomeId, data) => {
  return request({
    url: `/income/${incomeId}`,
    method: 'PUT',
    data
  })
}

// 删除资产收入记录
export const deleteAssetIncome = (assetId, incomeId) => {
  return request({
    url: `/income/${incomeId}`,
    method: 'DELETE'
  })
}

// 获取资产收入分析
export const getAssetIncomeAnalysis = (assetId) => {
  return request({
    url: `/income/${assetId}/analysis`,
    method: 'GET'
  })
}

// 获取用户所有资产收入概览
export const getIncomeOverview = () => {
  return request({
    url: '/income/overview',
    method: 'GET'
  })
}

// 获取单个收入记录详情
export const getIncomeDetail = (assetId, incomeId) => {
  return request({
    url: `/income/${incomeId}`,
    method: 'GET'
  })
}

// 批量操作收入记录
export const batchUpdateIncomes = (assetId, operations) => {
  return request({
    url: '/income/batch',
    method: 'POST',
    data: operations
  })
}

// 导出收入数据
export const exportIncomeData = (assetId, params = {}) => {
  return request({
    url: `/income/${assetId}/export`,
    method: 'GET',
    params,
    responseType: 'blob'
  })
}