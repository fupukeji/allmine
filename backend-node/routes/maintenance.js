import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'

const router = express.Router()

// 获取维护记录
router.get('/maintenance/:assetId', authMiddleware, async (req, res) => {
  try {
    const { assetId } = req.params
    
    const assetCheck = await pool.query(
      'SELECT id FROM fixed_assets WHERE id = $1 AND user_id = $2',
      [assetId, req.userId]
    )
    
    if (assetCheck.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    const result = await pool.query(
      'SELECT * FROM asset_maintenance WHERE asset_id = $1 ORDER BY maintenance_date DESC',
      [assetId]
    )
    
    res.json({
      code: 200,
      data: result.rows
    })
  } catch (error) {
    console.error('Get maintenance error:', error)
    res.status(500).json({ code: 500, message: '获取维护记录失败' })
  }
})

// 创建维护记录
router.post('/maintenance', authMiddleware, async (req, res) => {
  try {
    const { asset_id, maintenance_date, cost, maintenance_type, description, next_maintenance_date } = req.body
    
    const assetCheck = await pool.query(
      'SELECT id FROM fixed_assets WHERE id = $1 AND user_id = $2',
      [asset_id, req.userId]
    )
    
    if (assetCheck.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    const result = await pool.query(
      `INSERT INTO asset_maintenance 
       (asset_id, maintenance_date, cost, maintenance_type, description, next_maintenance_date)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [asset_id, maintenance_date, cost, maintenance_type, description, next_maintenance_date]
    )
    
    res.status(201).json({
      code: 200,
      message: '维护记录创建成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Create maintenance error:', error)
    res.status(500).json({ code: 500, message: '创建维护记录失败' })
  }
})

// 删除维护记录
router.delete('/maintenance/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const check = await pool.query(
      `SELECT m.id FROM asset_maintenance m
       JOIN fixed_assets a ON m.asset_id = a.id
       WHERE m.id = $1 AND a.user_id = $2`,
      [id, req.userId]
    )
    
    if (check.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '维护记录不存在或无权限' })
    }
    
    await pool.query('DELETE FROM asset_maintenance WHERE id = $1', [id])
    
    res.json({ code: 200, message: '删除成功' })
  } catch (error) {
    console.error('Delete maintenance error:', error)
    res.status(500).json({ code: 500, message: '删除维护记录失败' })
  }
})

export default router
