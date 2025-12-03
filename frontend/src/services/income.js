import request from '../utils/request'

// 获取资产收入列表
export const getAssetIncomes = (assetId, params = {}) => {
  return request.get(`/assets/${assetId}/incomes`, { params })
}

// 创建资产收入记录
export const createAssetIncome = (assetId, data) => {
  return request.post(`/assets/${assetId}/incomes`, data)
}

// 更新资产收入记录
export const updateAssetIncome = (assetId, incomeId, data) => {
  return request.put(`/assets/${assetId}/incomes/${incomeId}`, data)
}

// 删除资产收入记录
export const deleteAssetIncome = (assetId, incomeId) => {
  return request.delete(`/assets/${assetId}/incomes/${incomeId}`)
}

// 获取资产收入分析
export const getAssetIncomeAnalysis = (assetId) => {
  return request.get(`/assets/${assetId}/income-analysis`)
}

// 获取用户所有资产收入概览
export const getIncomeOverview = () => {
  return request.get('/income-overview')
}