import express from 'express'
import cors from 'cors'
import morgan from 'morgan'
import dotenv from 'dotenv'
import authRoutes from './routes/auth.js'
import categoriesRoutes from './routes/categories.js'
import projectsRoutes from './routes/projects.js'
import assetsRoutes from './routes/assets.js'
import analyticsRoutes from './routes/analytics.js'
import adminRoutes from './routes/admin.js'
import incomeRoutes from './routes/income.js'
import maintenanceRoutes from './routes/maintenance.js'
import reportsRoutes from './routes/reports.js'

dotenv.config()

const app = express()

// 中间件
app.use(cors({ 
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true 
}))
app.use(express.json({ limit: '10mb' }))
app.use(express.urlencoded({ extended: true, limit: '10mb' }))
app.use(morgan('combined'))

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'timevalue-backend-node',
    timestamp: new Date().toISOString()
  })
})

// 路由
app.use('/api/auth', authRoutes)
app.use('/api', categoriesRoutes)
app.use('/api', projectsRoutes)
app.use('/api', assetsRoutes)
app.use('/api', analyticsRoutes)
app.use('/api', adminRoutes)
app.use('/api', incomeRoutes)
app.use('/api', maintenanceRoutes)
app.use('/api', reportsRoutes)

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error('Error:', err)
  res.status(500).json({
    code: 500,
    message: '服务器内部错误',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  })
})

// 404处理
app.use((req, res) => {
  res.status(404).json({
    code: 404,
    message: '接口不存在'
  })
})

const PORT = process.env.PORT || 5000
app.listen(PORT, '0.0.0.0', () => {
  console.log('\n' + '='.repeat(60))
  console.log('🚀 TimeValue Node.js Backend')
  console.log('💰 恒产生金 - 让每一份资产都创造价值')
  console.log('')
  console.log('🏢 Powered by 孚普科技（北京）有限公司')
  console.log('🤖 AI驱动的MVP快速迭代解决方案')
  console.log('='.repeat(60))
  console.log(`✅ Server running at http://0.0.0.0:${PORT}`)
  console.log(`📖 API Base URL: http://0.0.0.0:${PORT}/api`)
  console.log(`🗄️  Database: PostgreSQL`)
  console.log('='.repeat(60) + '\n')
})

export default app
