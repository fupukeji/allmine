import pool from '../config/database.js'

const createTables = async () => {
  const client = await pool.connect()
  
  try {
    await client.query('BEGIN')
    
    // 创建用户表
    await client.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT true,
        phone VARCHAR(20),
        location VARCHAR(100),
        bio TEXT,
        website VARCHAR(200),
        company VARCHAR(100),
        avatar TEXT,
        language VARCHAR(10) DEFAULT 'zh-CN',
        timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
        theme VARCHAR(20) DEFAULT 'light',
        email_notifications BOOLEAN DEFAULT true,
        sms_notifications BOOLEAN DEFAULT false,
        zhipu_api_key_encrypted TEXT,
        zhipu_model VARCHAR(50) DEFAULT 'glm-4-flash'
      )
    `)
    
    // 创建分类表
    await client.query(`
      CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        color VARCHAR(20) DEFAULT '#1890ff',
        icon VARCHAR(50) DEFAULT 'folder',
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name, user_id)
      )
    `)
    
    // 创建项目表（虚拟资产）
    await client.query(`
      CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        total_amount DECIMAL(15, 2) NOT NULL,
        purchase_time TIMESTAMP,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        purpose TEXT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `)
    
    // 创建固定资产表
    await client.query(`
      CREATE TABLE IF NOT EXISTS fixed_assets (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        original_value DECIMAL(15, 2) NOT NULL,
        purchase_date DATE NOT NULL,
        depreciation_method VARCHAR(20) DEFAULT 'straight_line',
        useful_life INTEGER NOT NULL,
        salvage_value DECIMAL(15, 2) DEFAULT 0,
        category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        status VARCHAR(20) DEFAULT 'in_use',
        location VARCHAR(200),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `)
    
    // 创建资产收入表
    await client.query(`
      CREATE TABLE IF NOT EXISTS asset_income (
        id SERIAL PRIMARY KEY,
        asset_id INTEGER NOT NULL REFERENCES fixed_assets(id) ON DELETE CASCADE,
        income_date DATE NOT NULL,
        amount DECIMAL(15, 2) NOT NULL,
        income_type VARCHAR(50) DEFAULT 'rental',
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `)
    
    // 创建维护记录表
    await client.query(`
      CREATE TABLE IF NOT EXISTS asset_maintenance (
        id SERIAL PRIMARY KEY,
        asset_id INTEGER NOT NULL REFERENCES fixed_assets(id) ON DELETE CASCADE,
        maintenance_date DATE NOT NULL,
        cost DECIMAL(15, 2) NOT NULL,
        maintenance_type VARCHAR(50),
        description TEXT,
        next_maintenance_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `)
    
    // 创建维护提醒表
    await client.query(`
      CREATE TABLE IF NOT EXISTS maintenance_reminders (
        id SERIAL PRIMARY KEY,
        asset_id INTEGER NOT NULL REFERENCES fixed_assets(id) ON DELETE CASCADE,
        reminder_date DATE NOT NULL,
        reminder_type VARCHAR(50),
        message TEXT,
        is_sent BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `)
    
    // 创建AI报告表
    await client.query(`
      CREATE TABLE IF NOT EXISTS ai_reports (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        report_type VARCHAR(50) NOT NULL,
        title VARCHAR(200) NOT NULL,
        content TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
      )
    `)
    
    // 创建Nginx配置表
    await client.query(`
      CREATE TABLE IF NOT EXISTS nginx_configs (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        domain VARCHAR(200),
        config_content TEXT NOT NULL,
        is_active BOOLEAN DEFAULT false,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `)
    
    // 创建索引
    await client.query('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    await client.query('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    await client.query('CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id)')
    await client.query('CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)')
    await client.query('CREATE INDEX IF NOT EXISTS idx_projects_category_id ON projects(category_id)')
    await client.query('CREATE INDEX IF NOT EXISTS idx_fixed_assets_user_id ON fixed_assets(user_id)')
    await client.query('CREATE INDEX IF NOT EXISTS idx_fixed_assets_category_id ON fixed_assets(category_id)')
    
    await client.query('COMMIT')
    
    console.log('✅ Database tables created successfully')
    
    // 创建默认管理员用户
    await createDefaultAdmin(client)
    
  } catch (err) {
    await client.query('ROLLBACK')
    console.error('❌ Error creating tables:', err)
    throw err
  } finally {
    client.release()
  }
}

const createDefaultAdmin = async (client) => {
  try {
    const result = await client.query('SELECT id FROM users WHERE username = $1', ['admin'])
    
    if (result.rows.length === 0) {
      // 使用bcrypt创建密码哈希
      const bcrypt = await import('bcrypt')
      const passwordHash = await bcrypt.hash('admin123', 10)
      
      await client.query(`
        INSERT INTO users (username, email, password_hash, role)
        VALUES ($1, $2, $3, $4)
      `, ['admin', 'admin@timevalue.com', passwordHash, 'admin'])
      
      console.log('✅ Default admin user created (admin/admin123)')
    } else {
      console.log('ℹ️  Admin user already exists')
    }
  } catch (err) {
    console.error('Error creating admin user:', err)
  }
}

// 执行迁移
createTables()
  .then(() => {
    console.log('🎉 Migration completed')
    process.exit(0)
  })
  .catch((err) => {
    console.error('Migration failed:', err)
    process.exit(1)
  })
