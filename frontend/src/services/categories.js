import api from '../utils/request'

// 获取分类列表
export const getCategories = async () => {
  const response = await api.get('/categories')
  return response
}

// 创建分类
export const createCategory = async (categoryData) => {
  const response = await api.post('/categories', categoryData)
  return response
}

// 更新分类
export const updateCategory = async (categoryId, categoryData) => {
  const response = await api.put(`/categories/${categoryId}`, categoryData)
  return response
}

// 删除分类
export const deleteCategory = async (categoryId) => {
  const response = await api.delete(`/categories/${categoryId}`)
  return response
}

// 获取分类详情
export const getCategoryDetail = async (categoryId) => {
  const response = await api.get(`/categories/${categoryId}`)
  return response
}