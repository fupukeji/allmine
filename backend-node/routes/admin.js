import express from 'express'
import pool from '../config/database.js'
import { authMiddleware, adminMiddleware } from '../middleware/auth.js'

const router = express.Router()

// 获取所有用户
router.get('/admin/users', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, username, email, role, created_at, is_active
       FROM users
       ORDER BY created_at DESC`
    )
    
    res.json({
      code: 200,
      data: result.rows
    })
  } catch (error) {
    console.error('Get users error:', error)
    res.status(500).json({ code: 500, message: '获取用户列表失败' })
  }
})

// 更新用户状态
router.put('/admin/users/:id/status', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    const { is_active } = req.body
    
    const result = await pool.query(
      'UPDATE users SET is_active = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *',
      [is_active, id]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '用户不存在' })
    }
    
    res.json({
      code: 200,
      message: '状态更新成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Update user status error:', error)
    res.status(500).json({ code: 500, message: '更新状态失败' })
  }
})

// 获取管理员统计数据
router.get('/admin/statistics', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    // 获取用户总数
    const userCount = await pool.query('SELECT COUNT(*) as count FROM users')
    
    // 获取活跃用户数
    const activeUserCount = await pool.query('SELECT COUNT(*) as count FROM users WHERE is_active = true')
    
    // 获取项目总数
    const projectCount = await pool.query('SELECT COUNT(*) as count FROM projects')
    
    // 获取资产总数
    const assetCount = await pool.query('SELECT COUNT(*) as count FROM fixed_assets')
    
    // 获取分类总数
    const categoryCount = await pool.query('SELECT COUNT(*) as count FROM categories')
    
    res.json({
      code: 200,
      data: {
        total_users: parseInt(userCount.rows[0].count),
        active_users: parseInt(activeUserCount.rows[0].count),
        total_projects: parseInt(projectCount.rows[0].count),
        total_assets: parseInt(assetCount.rows[0].count),
        total_categories: parseInt(categoryCount.rows[0].count)
      }
    })
  } catch (error) {
    console.error('Get admin statistics error:', error)
    res.status(500).json({ code: 500, message: '获取统计数据失败' })
  }
})

export default router
