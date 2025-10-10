import request from '../utils/request'

// 获取概览统计数据
export const getAnalyticsOverview = () => {
  return request.get('/analytics/overview')
}

// 获取趋势分析数据
export const getAnalyticsTrends = (params) => {
  return request.get('/analytics/trends', { params })
}

// 获取分类分析数据
export const getCategoryAnalysis = () => {
  return request.get('/analytics/category-analysis')
}

// 获取项目明细数据
export const getProjectDetails = (params) => {
  return request.get('/analytics/project-details', { params })
}