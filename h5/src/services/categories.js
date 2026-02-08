/**
 * 分类相关API
 */
import request from '../utils/request'

/**
 * 获取分类列表
 * @param {Object} params - 查询参数
 * @param {string} params.asset_type - 资产类型: virtual/fixed
 * @param {boolean} params.tree - 是否返回树形结构
 */
export const getCategories = (params) => {
  return request.get('/categories', { params })
}

/**
 * 获取分类详情
 */
export const getCategoryDetail = (id) => {
  return request.get(`/categories/${id}`)
}

/**
 * 创建分类
 */
export const createCategory = (data) => {
  return request.post('/categories', data)
}

/**
 * 更新分类
 */
export const updateCategory = (id, data) => {
  return request.put(`/categories/${id}`, data)
}

/**
 * 删除分类
 */
export const deleteCategory = (id) => {
  return request.delete(`/categories/${id}`)
}

/**
 * 批量更新分类排序
 * @param {Array} orders - 排序数据 [{id: 1, sort_order: 0}, ...]
 */
export const reorderCategories = (orders) => {
  return request.post('/categories/reorder', { orders })
}
