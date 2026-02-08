/**
 * 关于我们页面 - 晶莹剔透现代风格
 */
import { useNavigate } from 'react-router-dom'
import { NavBar } from 'antd-mobile'
import { LeftOutline } from 'antd-mobile-icons'
import './AboutUs.css'

export default function AboutUs() {
  const navigate = useNavigate()
  
  return (
    <div className="about-us-page">
      <NavBar 
        onBack={() => navigate(-1)}
        backArrow={<LeftOutline />}
      >
        关于我们
      </NavBar>
      
      <div className="about-content">
        {/* 公司介绍 */}
        <div className="about-section glass-card">
          <div className="section-header">
            <span className="section-icon">🏢</span>
            <span>关于孚普科技</span>
          </div>
          
          <div className="section-content">
            <div className="company-logo">
              <span className="logo-text">孚普科技</span>
            </div>
            <p className="company-intro">
              <strong>孚普科技（北京）有限公司</strong>是一家基于MVP快速迭代的AI研发公司。
              我们专注于人工智能技术的创新应用，通过敏捷开发和快速迭代，为用户提供智能、高效的产品解决方案。
            </p>
            <div className="company-values">
              <div className="value-item">
                <span className="value-icon">🎯</span>
                <div className="value-text">
                  <strong>使命</strong>
                  <p>用AI技术让复杂问题变简单</p>
                </div>
              </div>
              <div className="value-item">
                <span className="value-icon">👁️</span>
                <div className="value-text">
                  <strong>理念</strong>
                  <p>MVP快速迭代，用户需求驱动产品进化</p>
                </div>
              </div>
              <div className="value-item">
                <span className="value-icon">💎</span>
                <div className="value-text">
                  <strong>价值观</strong>
                  <p>创新、敏捷、安全、用户至上</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* 软件介绍 */}
        <div className="about-section glass-card">
          <div className="section-header">
            <span className="section-icon">📱</span>
            <span>TimeValue 简介</span>
          </div>
          
          <div className="section-content">
            <p>
              <strong>TimeValue</strong> 是孚普科技旗下的AI智能资产管理工具，
              帮助您轻松管理各类资产，实现财富的可视化与智能分析。
            </p>
            
            <div className="feature-list">
              <div className="feature-item">
                <span className="feature-icon">⏳</span>
                <div className="feature-info">
                  <strong>虚拟资产管理</strong>
                  <p>管理会员、域名、软件许可证等时间敏感型资产，到期自动提醒</p>
                </div>
              </div>
              
              <div className="feature-item">
                <span className="feature-icon">🏠</span>
                <div className="feature-info">
                  <strong>固定资产管理</strong>
                  <p>管理房产、车辆等固定资产，支持出租管理、收租提醒、费用记录</p>
                </div>
              </div>
              
              <div className="feature-item">
                <span className="feature-icon">🤖</span>
                <div className="feature-info">
                  <strong>AI智能分析</strong>
                  <p>基于大模型的智能分析，提供资产报告、投资建议、趋势预测</p>
                </div>
              </div>
              
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <div className="feature-info">
                  <strong>数据可视化</strong>
                  <p>直观的图表展示，让您的资产状况一目了然</p>
                </div>
              </div>
              
              <div className="feature-item">
                <span className="feature-icon">🔔</span>
                <div className="feature-info">
                  <strong>智能提醒</strong>
                  <p>收租日、到期日、费用缴纳等重要事项自动提醒</p>
                </div>
              </div>
              
              <div className="feature-item">
                <span className="feature-icon">🔒</span>
                <div className="feature-info">
                  <strong>安全可靠</strong>
                  <p>数据加密存储，账户隔离，保护您的隐私安全</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* 使用指南 */}
        <div className="about-section glass-card">
          <div className="section-header">
            <span className="section-icon">📖</span>
            <span>快速上手</span>
          </div>
          
          <div className="section-content">
            <div className="guide-steps">
              <div className="guide-step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <strong>添加资产</strong>
                  <p>进入"随风而逝"或"恒产生金"页面，点击右下角 + 按钮添加资产</p>
                </div>
              </div>
              
              <div className="guide-step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <strong>管理分类</strong>
                  <p>在"我的"页面进行资产分类管理，自定义您的资产类别</p>
                </div>
              </div>
              
              <div className="guide-step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <strong>查看分析</strong>
                  <p>首页展示资产概览，点击资产可查看详情和AI智能分析</p>
                </div>
              </div>
              
              <div className="guide-step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <strong>设置提醒</strong>
                  <p>在"通知设置"中开启收租、到期等提醒功能</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* 联系我们 */}
        <div className="about-section glass-card">
          <div className="section-header">
            <span className="section-icon">📞</span>
            <span>联系我们</span>
          </div>
          
          <div className="section-content contact-info">
            <div className="contact-item">
              <span className="contact-label">公司名称</span>
              <span className="contact-value">孚普科技（北京）有限公司</span>
            </div>
            <div className="contact-item">
              <span className="contact-label">官方网站</span>
              <span className="contact-value link">www.fupukeji.com</span>
            </div>
            <div className="contact-item">
              <span className="contact-label">技术支持</span>
              <span className="contact-value">support@fupukeji.com</span>
            </div>
          </div>
        </div>
        
        {/* 版权信息 */}
        <div className="copyright-section">
          <p>TimeValue v1.0.0</p>
          <p>© 2024 孚普科技（北京）有限公司</p>
          <p>保留所有权利</p>
        </div>
      </div>
    </div>
  )
}
