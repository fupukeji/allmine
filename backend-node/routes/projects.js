import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'
import dayjs from 'dayjs'

const router = express.Router()

// 计算项目当前值
const calculateProjectValue = (project, baseTime = null) => {
  const now = baseTime ? dayjs(baseTime) : dayjs()
  const start = dayjs(project.start_time)
  const end = dayjs(project.end_time)
  
  const totalDays = end.diff(start, 'day')
  const elapsedDays = now.diff(start, 'day')
  const remainingDays = end.diff(now, 'day')
  
  let status = 'not_started'
  let progress = 0
  let usedCost = 0
  let remainingValue = parseFloat(project.total_amount)
  
  if (now.isBefore(start)) {
    status = 'not_started'
    progress = 0
    usedCost = 0
    remainingValue = parseFloat(project.total_amount)
  } else if (now.isAfter(end)) {
    status = 'expired'
    progress = 100
    usedCost = parseFloat(project.total_amount)
    remainingValue = 0
  } else {
    status = 'active'
    progress = Math.min((elapsedDays / totalDays) * 100, 100)
    usedCost = (parseFloat(project.total_amount) * elapsedDays) / totalDays
    remainingValue = parseFloat(project.total_amount) - usedCost
  }
  
  return {
    ...project,
    status,
    progress: Math.round(progress * 100) / 100,
    used_cost: Math.round(usedCost * 100) / 100,
    remaining_value: Math.round(remainingValue * 100) / 100,
    total_days: totalDays,
    elapsed_days: Math.max(0, elapsedDays),
    remaining_days: Math.max(0, remainingDays)
  }
}

// 获取项目列表
router.get('/projects', authMiddleware, async (req, res) => {
  try {
    const { category_id, status, sort_by = 'created_at', order = 'desc' } = req.query
    
    let query = `
      SELECT p.*, c.name as category_name, c.color as category_color
      FROM projects p
      LEFT JOIN categories c ON p.category_id = c.id
      WHERE p.user_id = $1
    `
    const params = [req.userId]
    
    if (category_id) {
      query += ' AND p.category_id = $2'
      params.push(category_id)
    }
    
    query += ` ORDER BY p.${sort_by} ${order.toUpperCase()}`
    
    const result = await pool.query(query, params)
    
    let projects = result.rows.map(p => calculateProjectValue(p))
    
    // 状态筛选
    if (status) {
      projects = projects.filter(p => p.status === status)
    }
    
    res.json({
      code: 200,
      data: projects
    })
  } catch (error) {
    console.error('Get projects error:', error)
    res.status(500).json({
      code: 500,
      message: '获取项目列表失败'
    })
  }
})

// 创建项目
router.post('/projects', authMiddleware, async (req, res) => {
  try {
    const { name, total_amount, start_time, end_time, category_id, purpose, purchase_time } = req.body
    
    if (!name || !total_amount || !start_time || !end_time || !category_id) {
      return res.status(400).json({
        code: 400,
        message: '缺少必填字段'
      })
    }
    
    // 验证分类
    const catCheck = await pool.query(
      'SELECT id FROM categories WHERE id = $1 AND user_id = $2',
      [category_id, req.userId]
    )
    
    if (catCheck.rows.length === 0) {
      return res.status(400).json({
        code: 400,
        message: '分类不存在或无权限'
      })
    }
    
    const result = await pool.query(
      `INSERT INTO projects (name, total_amount, start_time, end_time, category_id, user_id, purpose, purchase_time)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       RETURNING *`,
      [name, total_amount, start_time, end_time, category_id, req.userId, purpose || '', purchase_time]
    )
    
    res.status(201).json({
      code: 200,
      message: '项目创建成功',
      data: calculateProjectValue(result.rows[0])
    })
  } catch (error) {
    console.error('Create project error:', error)
    res.status(500).json({
      code: 500,
      message: '创建项目失败：' + error.message
    })
  }
})

// 获取项目详情
router.get('/projects/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      `SELECT p.*, c.name as category_name, c.color as category_color
       FROM projects p
       LEFT JOIN categories c ON p.category_id = c.id
       WHERE p.id = $1 AND p.user_id = $2`,
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '项目不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      data: calculateProjectValue(result.rows[0])
    })
  } catch (error) {
    console.error('Get project error:', error)
    res.status(500).json({
      code: 500,
      message: '获取项目详情失败'
    })
  }
})

// 更新项目
router.put('/projects/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    const { name, total_amount, start_time, end_time, category_id, purpose, purchase_time } = req.body
    
    const updates = []
    const values = []
    let paramIndex = 1
    
    if (name) {
      updates.push(`name = $${paramIndex++}`)
      values.push(name)
    }
    if (total_amount !== undefined) {
      updates.push(`total_amount = $${paramIndex++}`)
      values.push(total_amount)
    }
    if (start_time) {
      updates.push(`start_time = $${paramIndex++}`)
      values.push(start_time)
    }
    if (end_time) {
      updates.push(`end_time = $${paramIndex++}`)
      values.push(end_time)
    }
    if (category_id) {
      updates.push(`category_id = $${paramIndex++}`)
      values.push(category_id)
    }
    if (purpose !== undefined) {
      updates.push(`purpose = $${paramIndex++}`)
      values.push(purpose)
    }
    if (purchase_time !== undefined) {
      updates.push(`purchase_time = $${paramIndex++}`)
      values.push(purchase_time)
    }
    
    if (updates.length === 0) {
      return res.json({
        code: 200,
        message: '没有需要更新的内容'
      })
    }
    
    updates.push(`updated_at = CURRENT_TIMESTAMP`)
    values.push(id, req.userId)
    
    const result = await pool.query(
      `UPDATE projects
       SET ${updates.join(', ')}
       WHERE id = $${paramIndex} AND user_id = $${paramIndex + 1}
       RETURNING *`,
      values
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '项目不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      message: '更新成功',
      data: calculateProjectValue(result.rows[0])
    })
  } catch (error) {
    console.error('Update project error:', error)
    res.status(500).json({
      code: 500,
      message: '更新项目失败'
    })
  }
})

// 删除项目
router.delete('/projects/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      'DELETE FROM projects WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '项目不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      message: '删除成功'
    })
  } catch (error) {
    console.error('Delete project error:', error)
    res.status(500).json({
      code: 500,
      message: '删除项目失败'
    })
  }
})

// 批量删除项目
router.post('/projects/batch-delete', authMiddleware, async (req, res) => {
  try {
    const { project_ids } = req.body
    
    if (!project_ids || !Array.isArray(project_ids) || project_ids.length === 0) {
      return res.status(400).json({
        code: 400,
        message: '请提供要删除的项目ID列表'
      })
    }
    
    const placeholders = project_ids.map((_, i) => `$${i + 2}`).join(',')
    const result = await pool.query(
      `DELETE FROM projects WHERE user_id = $1 AND id IN (${placeholders}) RETURNING id`,
      [req.userId, ...project_ids]
    )
    
    res.json({
      code: 200,
      message: `成功删除${result.rows.length}个项目`
    })
  } catch (error) {
    console.error('Batch delete projects error:', error)
    res.status(500).json({
      code: 500,
      message: '批量删除失败'
    })
  }
})

// 计算项目价值
router.get('/projects/:id/calculate', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    const { base_time } = req.query
    
    const result = await pool.query(
      'SELECT * FROM projects WHERE id = $1 AND user_id = $2',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '项目不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      data: calculateProjectValue(result.rows[0], base_time)
    })
  } catch (error) {
    console.error('Calculate project error:', error)
    res.status(500).json({
      code: 500,
      message: '计算失败'
    })
  }
})

// 获取统计数据
router.get('/statistics', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM projects WHERE user_id = $1',
      [req.userId]
    )
    
    const projects = result.rows.map(p => calculateProjectValue(p))
    
    const stats = {
      total_projects: projects.length,
      total_amount: projects.reduce((sum, p) => sum + parseFloat(p.total_amount), 0),
      total_used_cost: projects.reduce((sum, p) => sum + p.used_cost, 0),
      total_remaining_value: projects.reduce((sum, p) => sum + p.remaining_value, 0),
      status_distribution: {
        not_started: projects.filter(p => p.status === 'not_started').length,
        active: projects.filter(p => p.status === 'active').length,
        expired: projects.filter(p => p.status === 'expired').length
      }
    }
    
    res.json({
      code: 200,
      data: stats
    })
  } catch (error) {
    console.error('Get statistics error:', error)
    res.status(500).json({
      code: 500,
      message: '获取统计数据失败'
    })
  }
})

export default router
