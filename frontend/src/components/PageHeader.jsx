import React from 'react'
import { Typography } from 'antd'

const { Title } = Typography

/**
 * 统一的页面头部组件
 * 包含现代化的顶部横幅和标题
 */
const PageHeader = ({ 
  title, 
  subtitle, 
  extra,
  showBanner = true,
  icon 
}) => {
  return (
    <div>
      {/* 现代化顶部横幅 */}
      {showBanner && (
        <>
          <div style={{
            background: 'linear-gradient(90deg, #ffd700 0%, #ffed4e 25%, #00f2fe 50%, #764ba2 75%, #ffd700 100%)',
            backgroundSize: '200% 100%',
            height: '4px',
            marginBottom: '24px',
            animation: 'gradientFlow 3s ease infinite',
            borderRadius: '2px',
            boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
          }} />
          <style>
            {`
              @keyframes gradientFlow {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
              }
            `}
          </style>
        </>
      )}

      {/* 页面标题区域 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        padding: '16px 24px',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
        borderRadius: '12px',
        border: '1px solid rgba(102, 126, 234, 0.1)',
        boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {icon && (
            <div style={{
              fontSize: '32px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: 1
            }}>
              {icon}
            </div>
          )}
          <div>
            <Title 
              level={2} 
              style={{ 
                margin: 0,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold',
                letterSpacing: '0.5px'
              }}
            >
              {title}
            </Title>
            {subtitle && (
              <div style={{
                fontSize: '14px',
                color: '#8c8c8c',
                marginTop: '4px'
              }}>
                {subtitle}
              </div>
            )}
          </div>
        </div>
        {extra && (
          <div>{extra}</div>
        )}
      </div>
    </div>
  )
}

export default PageHeader
