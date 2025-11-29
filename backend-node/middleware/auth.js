import jwt from 'jsonwebtoken'
import pool from '../config/database.js'

export const authMiddleware = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        code: 401,
        message: '未提供认证令牌'
      })
    }
    
    const token = authHeader.substring(7)
    const secret = process.env.JWT_SECRET_KEY || 'jwt-secret-key'
    
    try {
      const decoded = jwt.verify(token, secret)
      req.userId = decoded.userId
      
      // 验证用户是否存在且激活
      const result = await pool.query(
        'SELECT id, username, role, is_active FROM users WHERE id = $1',
        [req.userId]
      )
      
      if (result.rows.length === 0 || !result.rows[0].is_active) {
        return res.status(401).json({
          code: 401,
          message: 'Token无效或用户已被禁用'
        })
      }
      
      req.user = result.rows[0]
      next()
    } catch (err) {
      return res.status(401).json({
        code: 401,
        message: 'Token无效或已过期'
      })
    }
  } catch (error) {
    return res.status(500).json({
      code: 500,
      message: '认证失败'
    })
  }
}

export const adminMiddleware = async (req, res, next) => {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({
      code: 403,
      message: '需要管理员权限'
    })
  }
  next()
}
