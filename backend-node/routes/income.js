import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'

const router = express.Router()

// 获取收入记录
router.get('/income/:assetId', authMiddleware, async (req, res) => {
  try {
    const { assetId } = req.params
    
    // 验证资产所有权
    const assetCheck = await pool.query(
      'SELECT id FROM fixed_assets WHERE id = $1 AND user_id = $2',
      [assetId, req.userId]
    )
    
    if (assetCheck.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    const result = await pool.query(
      'SELECT * FROM asset_income WHERE asset_id = $1 ORDER BY income_date DESC',
      [assetId]
    )
    
    res.json({
      code: 200,
      data: result.rows
    })
  } catch (error) {
    console.error('Get income error:', error)
    res.status(500).json({ code: 500, message: '获取收入记录失败' })
  }
})

// 创建收入记录
router.post('/income', authMiddleware, async (req, res) => {
  try {
    const { asset_id, income_date, amount, income_type, description } = req.body
    
    // 验证资产所有权
    const assetCheck = await pool.query(
      'SELECT id FROM fixed_assets WHERE id = $1 AND user_id = $2',
      [asset_id, req.userId]
    )
    
    if (assetCheck.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    const result = await pool.query(
      `INSERT INTO asset_income (asset_id, income_date, amount, income_type, description)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [asset_id, income_date, amount, income_type || 'rental', description]
    )
    
    res.status(201).json({
      code: 200,
      message: '收入记录创建成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Create income error:', error)
    res.status(500).json({ code: 500, message: '创建收入记录失败' })
  }
})

// 删除收入记录
router.delete('/income/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    // 验证所有权
    const check = await pool.query(
      `SELECT i.id FROM asset_income i
       JOIN fixed_assets a ON i.asset_id = a.id
       WHERE i.id = $1 AND a.user_id = $2`,
      [id, req.userId]
    )
    
    if (check.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '收入记录不存在或无权限' })
    }
    
    await pool.query('DELETE FROM asset_income WHERE id = $1', [id])
    
    res.json({ code: 200, message: '删除成功' })
  } catch (error) {
    console.error('Delete income error:', error)
    res.status(500).json({ code: 500, message: '删除收入记录失败' })
  }
})

export default router
