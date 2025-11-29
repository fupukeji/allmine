import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'

const router = express.Router()

// 获取分类列表
router.get('/categories', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM categories WHERE user_id = $1 ORDER BY created_at DESC',
      [req.userId]
    )
    
    res.json({
      code: 200,
      data: result.rows
    })
  } catch (error) {
    console.error('Get categories error:', error)
    res.status(500).json({
      code: 500,
      message: '获取分类列表失败'
    })
  }
})

// 创建分类
router.post('/categories', authMiddleware, async (req, res) => {
  try {
    const { name, color, icon } = req.body
    
    if (!name) {
      return res.status(400).json({
        code: 400,
        message: '分类名称不能为空'
      })
    }
    
    // 检查同名分类
    const existing = await pool.query(
      'SELECT id FROM categories WHERE name = $1 AND user_id = $2',
      [name, req.userId]
    )
    
    if (existing.rows.length > 0) {
      return res.status(400).json({
        code: 400,
        message: '分类名称已存在'
      })
    }
    
    const result = await pool.query(
      `INSERT INTO categories (name, color, icon, user_id)
       VALUES ($1, $2, $3, $4)
       RETURNING *`,
      [name, color || '#1890ff', icon || 'folder', req.userId]
    )
    
    res.status(201).json({
      code: 200,
      message: '分类创建成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Create category error:', error)
    res.status(500).json({
      code: 500,
      message: '创建分类失败'
    })
  }
})

// 更新分类
router.put('/categories/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    const { name, color, icon } = req.body
    
    const updates = []
    const values = []
    let paramIndex = 1
    
    if (name) {
      updates.push(`name = $${paramIndex++}`)
      values.push(name)
    }
    if (color) {
      updates.push(`color = $${paramIndex++}`)
      values.push(color)
    }
    if (icon) {
      updates.push(`icon = $${paramIndex++}`)
      values.push(icon)
    }
    
    if (updates.length === 0) {
      return res.json({
        code: 200,
        message: '没有需要更新的内容'
      })
    }
    
    values.push(id, req.userId)
    
    const result = await pool.query(
      `UPDATE categories
       SET ${updates.join(', ')}
       WHERE id = $${paramIndex} AND user_id = $${paramIndex + 1}
       RETURNING *`,
      values
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '分类不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      message: '更新成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Update category error:', error)
    res.status(500).json({
      code: 500,
      message: '更新分类失败'
    })
  }
})

// 删除分类
router.delete('/categories/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params
    
    const result = await pool.query(
      'DELETE FROM categories WHERE id = $1 AND user_id = $2 RETURNING id',
      [id, req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '分类不存在或无权限'
      })
    }
    
    res.json({
      code: 200,
      message: '删除成功'
    })
  } catch (error) {
    console.error('Delete category error:', error)
    res.status(500).json({
      code: 500,
      message: '删除分类失败'
    })
  }
})

export default router
