/**
 * 偏好设置服务
 */
import request from '../utils/request'

// 获取偏好设置
export const getPreferences = () => {
  return request.get('/preferences')
}

// 更新偏好设置
export const updatePreferences = (data) => {
  return request.put('/preferences', data)
}

// 快捷更新AI模型
export const updateAIModel = (model) => {
  return request.put('/preferences/ai-model', { model })
}

// 更新API Key
export const updateAPIKey = (api_key) => {
  return request.put('/preferences/api-key', { api_key })
}

// 测试API Key
export const testAPIKey = (api_key) => {
  return request.post('/preferences/api-key/test', { api_key })
}
