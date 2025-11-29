import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'
import dayjs from 'dayjs'

const router = express.Router()

// 计算折旧
const calculateDepreciation = (asset, baseDate = null) => {
  const purchaseDate = dayjs(asset.purchase_date)
  const currentDate = baseDate ? dayjs(baseDate) : dayjs()
  const monthsElapsed = currentDate.diff(purchaseDate, 'month')
  const usefulLifeMonths = asset.useful_life * 12
  
  const originalValue = parseFloat(asset.original_value)
  const salvageValue = parseFloat(asset.salvage_value || 0)
  const depreciableAmount = originalValue - salvageValue
  
  let accumulatedDepreciation = 0
  let currentValue = originalValue
  let depreciationRate = 0
  
  if (asset.depreciation_method === 'straight_line') {
    // 直线法
    const monthlyDepreciation = depreciableAmount / usefulLifeMonths
    accumulatedDepreciation = Math.min(monthlyDepreciation * monthsElapsed, depreciableAmount)
  } else if (asset.depreciation_method === 'declining_balance') {
    // 双倍余额递减法
    const annualRate = (2 / asset.useful_life)
    for (let i = 0; i < monthsElapsed && i < usefulLifeMonths; i++) {
      const remainingValue = originalValue - accumulatedDepreciation
      const monthlyDep = (remainingValue * annualRate) / 12
      accumulatedDepreciation += monthlyDep
    }
    accumulatedDepreciation = Math.min(accumulatedDepreciation, depreciableAmount)
  }
  
  currentValue = originalValue - accumulatedDepreciation
  depreciationRate = (accumulatedDepreciation / originalValue) * 100
  
  return {
    ...asset,
    accumulated_depreciation: Math.round(accumulatedDepreciation * 100) / 100,
    current_value: Math.round(currentValue * 100) / 100,
    depreciation_rate: Math.round(depreciationRate * 100) / 100,
    months_elapsed: monthsElapsed,
    remaining_life_months: Math.max(0, usefulLifeMonths - monthsElapsed)
  }
}

// 获取资产列表
router.get('/assets', authMiddleware, async (req, res) => {
  try {
    const { category_id, status } = req.query
    
    let query = `
      SELECT a.*, c.name as category_name, c.color as category_color
      FROM fixed_assets a
      LEFT JOIN categories c ON a.category_id = c.id
      WHERE a.user_id = $1
    `
    const params = [req.userId]
    
    if (category_id) {
      query += ' AND a.category_id = $2'
      params.push(category_id)
    }
    if (status) {
      query += ` AND a.status = $${params.length + 1}`
      params.push(status)
    }
    
    query += ' ORDER BY a.created_at DESC'
    
    const result = await pool.query(query, params)
    const assets = result.rows.map(a => calculateDepreciation(a))
    
    res.json({
      code: 200,
      data: assets
    })
  } catch (error) {
    console.error('Get assets error:', error)
    res.status(500).json({
      code: 500,
      message: '获取资产列表失败'
    })
  }
})

// 创建资产
router.post('/assets', authMiddleware, async (req, res) => {
  try {
    const { name, original_value, purchase_date, depreciation_method, useful_life,
            salvage_value, category_id, status, location, description } = req.body
    
    if (!name || !original_value || !purchase_date || !useful_life || !category_id) {
      return res.status(400).json({
        code: 400,
        message: '缺少必填字段'
      })
    }
    
    const result = await pool.query(
      `INSERT INTO fixed_assets 
       (name, original_value, purchase_date, depreciation_method, useful_life,
        salvage_value, category_id, user_id, status, location, description)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
       RETURNING *`,
      [name, original_value, purchase_date, depreciation_method || 'straight_line',
       useful_life, salvage_value || 0, category_id, req.userId,
       status || 'in_use', location, description]
    )
    
    res.status(201).json({
      code: 200,
      message: '资产创建成功',
      data: calculateDepreciation(result.rows[0])
    })
  } catch (error) {
    console.error('Create asset error:', error)
    res.status(500).json({
      code: 500,
      message: '创建资产失败'
    })
  }
})

// 获取资产详情
router.get('/assets/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      `SELECT a.*, c.name as category_name
       FROM fixed_assets a
       LEFT JOIN categories c ON a.category_id = c.id
       WHERE a.id = $1 AND a.user_id = $2`,
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '资产不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      data: calculateDepreciation(result.rows[0])
    })
  } catch (error) {
    console.error('Get asset error:', error)
    res.status(500).json({
      code: 500,
      message: '获取资产详情失败'
    })
  }
})

// 更新资产
router.put('/assets/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    const updates = []
    const values = []
    let paramIndex = 1
    
    const fields = ['name', 'original_value', 'purchase_date', 'depreciation_method',
                   'useful_life', 'salvage_value', 'category_id', 'status', 'location', 'description']
    
    fields.forEach(field => {
      if (req.body[field] !== undefined) {
        updates.push(`${field} = $${paramIndex++}`)
        values.push(req.body[field])
      }
    })
    
    if (updates.length === 0) {
      return res.json({ code: 200, message: '没有需要更新的内容' })
    }
    
    updates.push(`updated_at = CURRENT_TIMESTAMP`)
    values.push(id, req.userId)
    
    const result = await pool.query(
      `UPDATE fixed_assets SET ${updates.join(', ')}
       WHERE id = $${paramIndex} AND user_id = $${paramIndex + 1}
       RETURNING *`,
      values
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    res.json({
      code: 200,
      message: '更新成功',
      data: calculateDepreciation(result.rows[0])
    })
  } catch (error) {
    console.error('Update asset error:', error)
    res.status(500).json({ code: 500, message: '更新资产失败' })
  }
})

// 删除资产
router.delete('/assets/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      'DELETE FROM fixed_assets WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    res.json({ code: 200, message: '删除成功' })
  } catch (error) {
    console.error('Delete asset error:', error)
    res.status(500).json({ code: 500, message: '删除资产失败' })
  }
})

// 批量删除资产
router.post('/assets/batch-delete', authMiddleware, async (req, res) => {
  try {
    const { asset_ids } = req.body
    
    if (!asset_ids || !Array.isArray(asset_ids) || asset_ids.length === 0) {
      return res.status(400).json({ code: 400, message: '请提供要删除的资产ID列表' })
    }
    
    const placeholders = asset_ids.map((_, i) => `$${i + 2}`).join(',')
    const result = await pool.query(
      `DELETE FROM fixed_assets WHERE user_id = $1 AND id IN (${placeholders}) RETURNING id`,
      [req.userId, ...asset_ids]
    )
    
    res.json({
      code: 200,
      message: `成功删除${result.rows.length}个资产`
    })
  } catch (error) {
    console.error('Batch delete assets error:', error)
    res.status(500).json({ code: 500, message: '批量删除失败' })
  }
})

// 获取资产折旧详情
router.get('/assets/:id/depreciation', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    const { base_date } = req.query
    
    const result = await pool.query(
      'SELECT * FROM fixed_assets WHERE id = $1 AND user_id = $2',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({ code: 404, message: '资产不存在或无权限' })
    }
    
    res.json({
      code: 200,
      data: calculateDepreciation(result.rows[0], base_date)
    })
  } catch (error) {
    console.error('Get depreciation error:', error)
    res.status(500).json({ code: 500, message: '获取折旧详情失败' })
  }
})

// 获取资产统计信息
router.get('/assets/statistics', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM fixed_assets WHERE user_id = $1',
      [req.userId]
    )
    
    const assets = result.rows.map(a => calculateDepreciation(a))
    
    const stats = {
      overview: {
        total_assets: assets.length,
        total_original_value: assets.reduce((sum, a) => sum + parseFloat(a.original_value), 0),
        total_current_value: assets.reduce((sum, a) => sum + a.current_value, 0),
        total_accumulated_depreciation: assets.reduce((sum, a) => sum + a.accumulated_depreciation, 0),
        depreciation_rate: 0
      },
      status_distribution: [
        { status: 'in_use', count: assets.filter(a => a.status === 'in_use').length },
        { status: 'idle', count: assets.filter(a => a.status === 'idle').length },
        { status: 'maintenance', count: assets.filter(a => a.status === 'maintenance').length },
        { status: 'disposed', count: assets.filter(a => a.status === 'disposed').length }
      ]
    }
    
    if (stats.overview.total_original_value > 0) {
      stats.overview.depreciation_rate = 
        (stats.overview.total_accumulated_depreciation / stats.overview.total_original_value) * 100
    }
    
    res.json({
      code: 200,
      data: stats
    })
  } catch (error) {
    console.error('Get assets statistics error:', error)
    res.status(500).json({ code: 500, message: '获取统计信息失败' })
  }
})

export default router
