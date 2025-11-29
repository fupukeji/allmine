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

export default router
