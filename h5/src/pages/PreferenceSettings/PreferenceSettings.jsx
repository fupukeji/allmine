/**
 * 偏好设置页面 - 晶莹剔透现代风格
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { NavBar, List, Radio, Input, Button, Toast, SpinLoading, Popup } from 'antd-mobile'
import { 
  LeftOutline,
  CheckCircleFill,
  CloseCircleFill
} from 'antd-mobile-icons'
import { getPreferences, updateAIModel, updateAPIKey, testAPIKey } from '../../services/preferences'
import './PreferenceSettings.css'

export default function PreferenceSettings() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [settings, setSettings] = useState(null)
  const [showApiKeyPopup, setShowApiKeyPopup] = useState(false)
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [testing, setTesting] = useState(false)
  
  useEffect(() => {
    loadSettings()
  }, [])
  
  const loadSettings = async () => {
    try {
      const res = await getPreferences()
      if (res.code === 200) {
        setSettings(res.data)
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '加载失败' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleModelChange = async (model) => {
    try {
      const res = await updateAIModel(model)
      if (res.code === 200) {
        setSettings(prev => ({
          ...prev,
          ai_settings: { ...prev.ai_settings, model }
        }))
        Toast.show({ icon: 'success', content: '模型已切换' })
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '切换失败' })
    }
  }
  
  const handleSaveApiKey = async () => {
    try {
      const res = await updateAPIKey(apiKeyInput)
      if (res.code === 200) {
        setSettings(prev => ({
          ...prev,
          ai_settings: { ...prev.ai_settings, has_custom_api_key: res.data.has_custom_api_key }
        }))
        setShowApiKeyPopup(false)
        setApiKeyInput('')
        Toast.show({ icon: 'success', content: res.message })
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '保存失败' })
    }
  }
  
  const handleTestApiKey = async () => {
    setTesting(true)
    try {
      const res = await testAPIKey(apiKeyInput || undefined)
      if (res.code === 200) {
        Toast.show({ icon: 'success', content: res.message })
      } else {
        Toast.show({ icon: 'fail', content: res.message })
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '测试失败' })
    } finally {
      setTesting(false)
    }
  }
  
  if (loading) {
    return (
      <div className="preference-settings-page">
        <NavBar onBack={() => navigate(-1)}>偏好设置</NavBar>
        <div className="loading-container">
          <SpinLoading color="primary" />
        </div>
      </div>
    )
  }
  
  const aiSettings = settings?.ai_settings || {}
  const appearance = settings?.appearance || {}
  
  return (
    <div className="preference-settings-page">
      <NavBar 
        onBack={() => navigate(-1)}
        backArrow={<LeftOutline />}
      >
        偏好设置
      </NavBar>
      
      <div className="settings-content">
        {/* AI智能设置 */}
        <div className="settings-section glass-card">
          <div className="section-header">
            <span className="section-icon">🤖</span>
            <span>AI 智能设置</span>
          </div>
          
          <div className="model-section">
            <div className="model-title">选择大模型</div>
            <div className="model-list">
              {aiSettings.available_models?.map(model => (
                <div 
                  key={model.value}
                  className={`model-item ${aiSettings.model === model.value ? 'selected' : ''}`}
                  onClick={() => handleModelChange(model.value)}
                >
                  <div className="model-info">
                    <div className="model-name">{model.label}</div>
                    <div className="model-desc">{model.description}</div>
                  </div>
                  {aiSettings.model === model.value && (
                    <CheckCircleFill className="model-check" />
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <div className="api-key-section">
            <div className="api-key-header">
              <div className="api-key-title">自定义 API Key</div>
              <div className={`api-key-status ${aiSettings.has_custom_api_key ? 'active' : ''}`}>
                {aiSettings.has_custom_api_key ? '已配置' : '使用系统默认'}
              </div>
            </div>
            <div className="api-key-desc">
              配置您自己的智谱AI API Key，享受更高调用额度
            </div>
            <Button 
              size="small" 
              color="primary" 
              fill="outline"
              onClick={() => setShowApiKeyPopup(true)}
            >
              {aiSettings.has_custom_api_key ? '修改 API Key' : '配置 API Key'}
            </Button>
          </div>
        </div>
        
        {/* 外观设置 */}
        <div className="settings-section glass-card">
          <div className="section-header">
            <span className="section-icon">🎨</span>
            <span>外观设置</span>
          </div>
          
          <List className="settings-list">
            <List.Item
              extra={
                <div className="theme-options">
                  {appearance.available_themes?.map(theme => (
                    <div 
                      key={theme.value}
                      className={`theme-option ${appearance.theme === theme.value ? 'selected' : ''}`}
                      title={theme.label}
                    >
                      {theme.icon}
                    </div>
                  ))}
                </div>
              }
            >
              主题模式
            </List.Item>
            
            <List.Item extra={
              appearance.available_languages?.find(l => l.value === appearance.language)?.label || '简体中文'
            }>
              显示语言
            </List.Item>
          </List>
        </div>
        
        {/* 关于AI服务 */}
        <div className="settings-section glass-card">
          <div className="section-header">
            <span className="section-icon">💡</span>
            <span>关于 AI 服务</span>
          </div>
          
          <div className="about-content">
            <p>TimeValue 使用智谱AI大模型提供智能分析服务，包括：</p>
            <ul>
              <li>资产报告智能生成</li>
              <li>风险评估</li>
              <li>数据趋势预测</li>
            </ul>
            <p className="tip">
              💡 配置自定义 API Key 可以获得更高的调用频率和更稳定的服务
            </p>
            <div className="disclaimer">
              <span className="disclaimer-icon">⚠️</span>
              <div className="disclaimer-text">
                <strong>风险提示</strong>
                <p>本软件提供的所有分析结果仅供参考，不构成任何投资建议。您应当根据自身情况独立判断，并对您的投资决策承担全部责任。</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* API Key 配置弹窗 */}
      <Popup
        visible={showApiKeyPopup}
        onMaskClick={() => setShowApiKeyPopup(false)}
        bodyStyle={{
          borderTopLeftRadius: '16px',
          borderTopRightRadius: '16px',
          padding: '20px'
        }}
      >
        <div className="api-key-popup">
          <h3>配置 API Key</h3>
          
          <div className="input-section">
            <label>智谱AI API Key</label>
            <Input
              value={apiKeyInput}
              onChange={setApiKeyInput}
              placeholder="请输入您的 API Key"
              clearable
              type="password"
            />
            <div className="input-tip">
              前往 <a href="https://open.bigmodel.cn" target="_blank" rel="noopener noreferrer">智谱AI开放平台</a> 获取
            </div>
          </div>
          
          <div className="popup-actions">
            <Button 
              block 
              onClick={handleTestApiKey}
              loading={testing}
              disabled={!apiKeyInput && !aiSettings.has_custom_api_key}
            >
              测试连接
            </Button>
            <Button 
              block 
              color="primary" 
              onClick={handleSaveApiKey}
            >
              保存
            </Button>
          </div>
          
          {aiSettings.has_custom_api_key && (
            <Button 
              block 
              color="danger" 
              fill="none"
              onClick={() => {
                setApiKeyInput('')
                handleSaveApiKey()
              }}
            >
              清除自定义 Key，使用系统默认
            </Button>
          )}
        </div>
      </Popup>
    </div>
  )
}
