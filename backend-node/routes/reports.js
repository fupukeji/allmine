import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'

const router = express.Router()

// 获取报告列表
router.get('/reports', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM ai_reports WHERE user_id = $1 ORDER BY created_at DESC',
      [req.userId]
    )
    
    res.json({
      code: 200,
      data: result.rows
    })
  } catch (error) {
    console.error('Get reports error:', error)
    res.status(500).json({ code: 500, message: '获取报告列表失败' })
  }
})

// 创建报告
router.post('/reports', authMiddleware, async (req, res) => {
  try {
    const { report_type, title } = req.body
    
    const result = await pool.query(
      `INSERT INTO ai_reports (user_id, report_type, title, status)
       VALUES ($1, $2, $3, 'pending')
       RETURNING *`,
      [req.userId, report_type, title]
    )
    
    res.status(201).json({
      code: 200,
      message: '报告创建成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Create report error:', error)
    res.status(500).json({ code: 500, message: '创建报告失败' })
  }
})

// 获取报告详情
router.get('/reports/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      'SELECT * FROM ai_reports WHERE id = $1 AND user_id = $2',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '报告不存在或无权限' })
    }
    
    res.json({
      code: 200,
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Get report error:', error)
    res.status(500).json({ code: 500, message: '获取报告详情失败' })
  }
})

// 删除报告
router.delete('/reports/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      'DELETE FROM ai_reports WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '报告不存在或无权限' })
    }
    
    res.json({ code: 200, message: '删除成功' })
  } catch (error) {
    console.error('Delete report error:', error)
    res.status(500).json({ code: 500, message: '删除报告失败' })
  }
})

export default router
