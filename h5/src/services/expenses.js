/**
 * 资产费用管理服务
 */
import request from '../utils/request'

// 获取资产费用列表
export const getExpenses = (assetId) => {
  return request.get(`/assets/${assetId}/expenses`)
}

// 添加费用
export const createExpense = (assetId, data) => {
  return request.post(`/assets/${assetId}/expenses`, data)
}

// 更新费用
export const updateExpense = (expenseId, data) => {
  return request.put(`/expenses/${expenseId}`, data)
}

// 删除费用
export const deleteExpense = (expenseId) => {
  return request.delete(`/expenses/${expenseId}`)
}

// 获取费用类型
export const getExpenseTypes = (category) => {
  return request.get('/expense-types', { params: { category } })
}

// 获取费用统计
export const getExpenseSummary = (assetId) => {
  return request.get(`/assets/${assetId}/expenses/summary`)
}
