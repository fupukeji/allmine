import express from 'express'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'
import dayjs from 'dayjs'

const router = express.Router()

// 获取仪表盘数据
router.get('/analytics/dashboard', authMiddleware, async (req, res) => {
  try {
    // 获取项目统计
    const projectStats = await pool.query(
      'SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total FROM projects WHERE user_id = $1',
      [req.userId]
    )
    
    // 获取资产统计
    const assetStats = await pool.query(
      'SELECT COUNT(*) as count, COALESCE(SUM(original_value), 0) as total FROM fixed_assets WHERE user_id = $1',
      [req.userId]
    )
    
    // 获取分类统计
    const categoryStats = await pool.query(
      'SELECT COUNT(*) as count FROM categories WHERE user_id = $1',
      [req.userId]
    )
    
    res.json({
      code: 200,
      data: {
        total_projects: parseInt(projectStats.rows[0].count),
        total_project_value: parseFloat(projectStats.rows[0].total),
        total_assets: parseInt(assetStats.rows[0].count),
        total_asset_value: parseFloat(assetStats.rows[0].total),
        total_categories: parseInt(categoryStats.rows[0].count)
      }
    })
  } catch (error) {
    console.error('Get dashboard data error:', error)
    res.status(500).json({ code: 500, message: '获取仪表盘数据失败' })
  }
})

// 获取概览统计
router.get('/analytics/overview', authMiddleware, async (req, res) => {
  try {
    // 获取项目统计
    const projectStats = await pool.query(
      'SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total FROM projects WHERE user_id = $1',
      [req.userId]
    )
    
    // 获取资产统计
    const assetStats = await pool.query(
      'SELECT COUNT(*) as count, COALESCE(SUM(original_value), 0) as total FROM fixed_assets WHERE user_id = $1',
      [req.userId]
    )
    
    res.json({
      code: 200,
      data: {
        total_value: parseFloat(projectStats.rows[0].total) + parseFloat(assetStats.rows[0].total),
        monthly_growth: 0,
        asset_count: parseInt(assetStats.rows[0].count) + parseInt(projectStats.rows[0].count)
      }
    })
  } catch (error) {
    console.error('Get analytics overview error:', error)
    res.status(500).json({ code: 500, message: '获取概览数据失败' })
  }
})

// 获取趋势分析
router.get('/analytics/trends', authMiddleware, async (req, res) => {
  try {
    res.json({
      code: 200,
      data: []
    })
  } catch (error) {
    console.error('Get analytics trends error:', error)
    res.status(500).json({ code: 500, message: '获取趋势数据失败' })
  }
})

// 获取分类分析
router.get('/analytics/category-analysis', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT c.id, c.name, c.color, 
              COUNT(DISTINCT p.id) as project_count,
              COUNT(DISTINCT a.id) as asset_count,
              COALESCE(SUM(p.total_amount), 0) as project_total,
              COALESCE(SUM(a.original_value), 0) as asset_total
       FROM categories c
       LEFT JOIN projects p ON c.id = p.category_id
       LEFT JOIN fixed_assets a ON c.id = a.category_id
       WHERE c.user_id = $1
       GROUP BY c.id, c.name, c.color
       ORDER BY (COALESCE(SUM(p.total_amount), 0) + COALESCE(SUM(a.original_value), 0)) DESC`,
      [req.userId]
    )
    
    res.json({
      code: 200,
      data: result.rows.map(row => ({
        category_id: row.id,
        category_name: row.name,
        color: row.color,
        project_count: parseInt(row.project_count),
        asset_count: parseInt(row.asset_count),
        total_value: parseFloat(row.project_total) + parseFloat(row.asset_total)
      }))
    })
  } catch (error) {
    console.error('Get category analysis error:', error)
    res.status(500).json({ code: 500, message: '获取分类分析失败' })
  }
})

// 获取项目明细数据
router.get('/analytics/project-details', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT p.*, c.name as category_name, c.color as category_color
       FROM projects p
       LEFT JOIN categories c ON p.category_id = c.id
       WHERE p.user_id = $1
       ORDER BY p.created_at DESC`,
      [req.userId]
    )
    
    res.json({
      code: 200,
      data: result.rows
    })
  } catch (error) {
    console.error('Get project details error:', error)
    res.status(500).json({ code: 500, message: '获取项目明细失败' })
  }
})

export default router
