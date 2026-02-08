/**
 * 虚拟资产（项目）相关API
 */
import request from '../utils/request'

/**
 * 获取项目列表
 */
export const getProjects = (params) => {
  return request.get('/projects', { params })
}

/**
 * 获取项目详情
 */
export const getProjectDetail = (id) => {
  return request.get(`/projects/${id}`)
}

/**
 * 创建项目
 */
export const createProject = (data) => {
  return request.post('/projects', data)
}

/**
 * 更新项目
 */
export const updateProject = (id, data) => {
  return request.put(`/projects/${id}`, data)
}

/**
 * 删除项目
 */
export const deleteProject = (id) => {
  return request.delete(`/projects/${id}`)
}

/**
 * 获取项目统计
 */
export const getProjectStats = () => {
  return request.get('/projects/stats')
}
