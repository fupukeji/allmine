import express from 'express'
import bcrypt from 'bcrypt'
import jwt from 'jsonwebtoken'
import pool from '../config/database.js'
import { authMiddleware } from '../middleware/auth.js'

const router = express.Router()

// 生成JWT Token
const generateToken = (userId) => {
  const secret = process.env.JWT_SECRET_KEY || 'jwt-secret-key'
  return jwt.sign({ userId }, secret, { expiresIn: '30d' })
}

// 用户注册
router.post('/register', async (req, res) => {
  const client = await pool.connect()
  
  try {
    const { username, email, password } = req.body
    
    // 验证必填字段
    if (!username || !email || !password) {
      return res.status(400).json({
        code: 400,
        message: '用户名、邮箱和密码不能为空'
      })
    }
    
    // 验证用户名长度
    if (username.length < 3 || username.length > 20) {
      return res.status(400).json({
        code: 400,
        message: '用户名长度应在3-20个字符之间'
      })
    }
    
    // 验证密码长度
    if (password.length < 6) {
      return res.status(400).json({
        code: 400,
        message: '密码长度至少6位'
      })
    }
    
    await client.query('BEGIN')
    
    // 检查用户名是否已存在
    const userCheck = await client.query(
      'SELECT id FROM users WHERE username = $1 OR email = $2',
      [username, email]
    )
    
    if (userCheck.rows.length > 0) {
      await client.query('ROLLBACK')
      return res.status(400).json({
        code: 400,
        message: '用户名或邮箱已存在'
      })
    }
    
    // 加密密码
    const passwordHash = await bcrypt.hash(password, 10)
    
    // 创建用户
    const result = await client.query(
      `INSERT INTO users (username, email, password_hash, role)
       VALUES ($1, $2, $3, 'user')
       RETURNING id, username, email, role, created_at, is_active`,
      [username, email, passwordHash]
    )
    
    const user = result.rows[0]
    
    // 创建默认分类
    const defaultCategories = [
      { name: '视频会员', color: '#ff6b6b', icon: 'play-circle' },
      { name: '音乐会员', color: '#ff8787', icon: 'customer-service' },
      { name: '知识付费', color: '#ffa94d', icon: 'read' },
      { name: '外卖会员', color: '#fab005', icon: 'coffee' },
      { name: '电商会员', color: '#fd7e14', icon: 'shopping' },
      { name: '房产', color: '#5c7cfa', icon: 'home' },
      { name: '车辆', color: '#4c6ef5', icon: 'car' },
      { name: '电脑设备', color: '#748ffc', icon: 'laptop' },
      { name: '手机数码', color: '#339af0', icon: 'mobile' }
    ]
    
    for (const cat of defaultCategories) {
      await client.query(
        'INSERT INTO categories (name, color, icon, user_id) VALUES ($1, $2, $3, $4)',
        [cat.name, cat.color, cat.icon, user.id]
      )
    }
    
    await client.query('COMMIT')
    
    res.status(201).json({
      code: 200,
      message: '注册成功',
      data: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
        is_active: user.is_active
      }
    })
  } catch (error) {
    await client.query('ROLLBACK')
    console.error('Registration error:', error)
    res.status(500).json({
      code: 500,
      message: '注册失败：' + error.message
    })
  } finally {
    client.release()
  }
})

// 用户登录
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body
    
    if (!username || !password) {
      return res.status(400).json({
        code: 400,
        message: '用户名和密码不能为空'
      })
    }
    
    // 查找用户（支持用户名或邮箱登录）
    const result = await pool.query(
      'SELECT * FROM users WHERE username = $1 OR email = $1',
      [username]
    )
    
    if (result.rows.length === 0) {
      return res.status(401).json({
        code: 401,
        message: '用户名或密码错误'
      })
    }
    
    const user = result.rows[0]
    
    // 验证密码
    const isValidPassword = await bcrypt.compare(password, user.password_hash)
    
    if (!isValidPassword) {
      return res.status(401).json({
        code: 401,
        message: '用户名或密码错误'
      })
    }
    
    // 检查用户是否被禁用
    if (!user.is_active) {
      return res.status(403).json({
        code: 403,
        message: '账户已被禁用'
      })
    }
    
    // 生成Token
    const token = generateToken(user.id)
    
    res.json({
      code: 200,
      message: '登录成功',
      data: {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          is_active: user.is_active
        },
        access_token: token
      }
    })
  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({
      code: 500,
      message: '登录失败：' + error.message
    })
  }
})

// 获取用户信息
router.get('/profile', authMiddleware, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, username, email, role, created_at, updated_at, is_active,
              phone, location, bio, website, company, avatar,
              language, timezone, theme, email_notifications, sms_notifications
       FROM users WHERE id = $1`,
      [req.userId]
    )
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        code: 404,
        message: '用户不存在'
      })
    }
    
    res.json({
      code: 200,
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Get profile error:', error)
    res.status(500).json({
      code: 500,
      message: '获取用户信息失败'
    })
  }
})

// 更新用户信息
router.put('/profile', authMiddleware, async (req, res) => {
  try {
    const { username, email, password, phone, location, bio, website, company, avatar,
            language, timezone, theme, email_notifications, sms_notifications } = req.body
    
    const updates = []
    const values = []
    let paramIndex = 1
    
    if (username) {
      updates.push(`username = $${paramIndex++}`)
      values.push(username)
    }
    if (email) {
      updates.push(`email = $${paramIndex++}`)
      values.push(email)
    }
    if (password) {
      const passwordHash = await bcrypt.hash(password, 10)
      updates.push(`password_hash = $${paramIndex++}`)
      values.push(passwordHash)
    }
    if (phone !== undefined) {
      updates.push(`phone = $${paramIndex++}`)
      values.push(phone)
    }
    if (location !== undefined) {
      updates.push(`location = $${paramIndex++}`)
      values.push(location)
    }
    if (bio !== undefined) {
      updates.push(`bio = $${paramIndex++}`)
      values.push(bio)
    }
    if (website !== undefined) {
      updates.push(`website = $${paramIndex++}`)
      values.push(website)
    }
    if (company !== undefined) {
      updates.push(`company = $${paramIndex++}`)
      values.push(company)
    }
    if (avatar !== undefined) {
      updates.push(`avatar = $${paramIndex++}`)
      values.push(avatar)
    }
    if (language !== undefined) {
      updates.push(`language = $${paramIndex++}`)
      values.push(language)
    }
    if (timezone !== undefined) {
      updates.push(`timezone = $${paramIndex++}`)
      values.push(timezone)
    }
    if (theme !== undefined) {
      updates.push(`theme = $${paramIndex++}`)
      values.push(theme)
    }
    if (email_notifications !== undefined) {
      updates.push(`email_notifications = $${paramIndex++}`)
      values.push(email_notifications)
    }
    if (sms_notifications !== undefined) {
      updates.push(`sms_notifications = $${paramIndex++}`)
      values.push(sms_notifications)
    }
    
    if (updates.length === 0) {
      return res.json({
        code: 200,
        message: '没有需要更新的内容'
      })
    }
    
    updates.push(`updated_at = CURRENT_TIMESTAMP`)
    values.push(req.userId)
    
    const query = `
      UPDATE users
      SET ${updates.join(', ')}
      WHERE id = $${paramIndex}
      RETURNING id, username, email, role, is_active
    `
    
    const result = await pool.query(query, values)
    
    res.json({
      code: 200,
      message: '更新成功',
      data: result.rows[0]
    })
  } catch (error) {
    console.error('Update profile error:', error)
    res.status(500).json({
      code: 500,
      message: '更新失败：' + error.message
    })
  }
})

// 验证Token
router.get('/check-token', authMiddleware, (req, res) => {
  res.json({
    code: 200,
    message: 'Token有效',
    data: req.user
  })
})

export default router
