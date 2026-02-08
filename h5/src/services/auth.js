/**
 * 认证相关API服务
 */

import request from '../utils/request'

/**
 * 用户名密码登录
 * @param {string} username 用户名
 * @param {string} password 密码
 */
export const login = (username, password) => {
  return request.post('/auth/login', { username, password })
}

/**
 * 微信登录
 * @param {string} code 微信授权码
 */
export const wechatLogin = (code) => {
  return request.post('/wechat/login', { code })
}

/**
 * 退出登录
 */
export const logout = () => {
  return request.post('/auth/logout')
}

/**
 * 获取用户信息
 */
export const getUserInfo = () => {
  return request.get('/auth/user')
}
