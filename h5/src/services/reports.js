/**
 * AI报告相关API
 */
import request from '../utils/request'

/**
 * 获取AI报告列表
 */
export const getReports = (params) => {
  return request.get('/reports', { params })
}

/**
 * 获取报告详情
 */
export const getReportDetail = (id) => {
  return request.get(`/reports/${id}`)
}

/**
 * 生成新报告
 */
export const generateReport = (data) => {
  return request.post('/reports/generate', data)
}

/**
 * 删除报告
 */
export const deleteReport = (id) => {
  return request.delete(`/reports/${id}`)
}
