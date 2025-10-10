import api from '../utils/request'

// 获取项目列表
export const getProjects = async (params = {}) => {
  const response = await api.get('/projects', { params })
  return response
}

// 创建项目
export const createProject = async (projectData) => {
  const response = await api.post('/projects', projectData)
  return response
}

// 获取项目详情
export const getProjectDetail = async (projectId) => {
  const response = await api.get(`/projects/${projectId}`)
  return response
}

// 更新项目
export const updateProject = async (projectId, projectData) => {
  const response = await api.put(`/projects/${projectId}`, projectData)
  return response
}

// 删除项目
export const deleteProject = async (projectId) => {
  const response = await api.delete(`/projects/${projectId}`)
  return response
}

// 批量删除项目
export const batchDeleteProjects = async (projectIds) => {
  const response = await api.post('/projects/batch-delete', { project_ids: projectIds })
  return response
}

// 计算项目价值
export const calculateProject = async (projectId, baseTime = null) => {
  const params = baseTime ? { base_time: baseTime } : {}
  const response = await api.get(`/projects/${projectId}/calculate`, { params })
  return response
}

// 获取统计数据
export const getStatistics = async () => {
  const response = await api.get('/statistics')
  return response
}