/**
 * 通知设置页面 - 晶莹剔透现代风格
 */
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { NavBar, List, Switch, Toast, Stepper, SpinLoading } from 'antd-mobile'
import { 
  BellOutline, 
  MailOutline, 
  MessageOutline,
  PayCircleOutline,
  ClockCircleOutline,
  FileOutline,
  SetOutline,
  LeftOutline
} from 'antd-mobile-icons'
import { getNotificationSettings, toggleNotification, updateNotificationSettings } from '../../services/notifications'
import './NotificationSettings.css'

export default function NotificationSettings() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [settings, setSettings] = useState(null)
  
  useEffect(() => {
    loadSettings()
  }, [])
  
  const loadSettings = async () => {
    try {
      const res = await getNotificationSettings()
      if (res.code === 200) {
        setSettings(res.data)
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '加载失败' })
    } finally {
      setLoading(false)
    }
  }
  
  const handleToggle = async (key, value) => {
    try {
      const res = await toggleNotification(key, value)
      if (res.code === 200) {
        // 重新加载以确保数据同步
        loadSettings()
      }
    } catch (error) {
      Toast.show({ icon: 'fail', content: '更新失败' })
    }
  }
  
  const handleDaysChange = async (type, days) => {
    try {
      const data = {
        business_notifications: {
          [type]: { days }
        }
      }
      await updateNotificationSettings(data)
      loadSettings()
    } catch (error) {
      Toast.show({ icon: 'fail', content: '更新失败' })
    }
  }
  
  if (loading) {
    return (
      <div className="notification-settings-page">
        <NavBar onBack={() => navigate(-1)}>通知设置</NavBar>
        <div className="loading-container">
          <SpinLoading color="primary" />
        </div>
      </div>
    )
  }
  
  const channels = settings?.notification_channels || {}
  const business = settings?.business_notifications || {}
  
  return (
    <div className="notification-settings-page">
      <NavBar 
        onBack={() => navigate(-1)}
        backArrow={<LeftOutline />}
      >
        通知设置
      </NavBar>
      
      <div className="settings-content">
        {/* 通知方式 */}
        <div className="settings-section glass-card">
          <div className="section-header">
            <BellOutline className="section-icon" />
            <span>通知方式</span>
          </div>
          
          <List className="settings-list">
            <List.Item
              prefix={<div className="item-icon push"><BellOutline /></div>}
              extra={
                <Switch 
                  checked={channels.push_enabled} 
                  onChange={v => handleToggle('push_enabled', v)}
                />
              }
              description="应用内消息推送"
            >
              系统推送
            </List.Item>
            
            <List.Item
              prefix={<div className="item-icon email"><MailOutline /></div>}
              extra={
                <Switch 
                  checked={channels.email_enabled} 
                  onChange={v => handleToggle('email_enabled', v)}
                />
              }
              description="发送到您的邮箱"
            >
              邮件通知
            </List.Item>
            
            <List.Item
              prefix={<div className="item-icon sms"><MessageOutline /></div>}
              extra={
                <Switch 
                  checked={channels.sms_enabled} 
                  onChange={v => handleToggle('sms_enabled', v)}
                />
              }
              description="发送到您的手机"
            >
              短信通知
            </List.Item>
            
            <List.Item
              prefix={<div className="item-icon wechat">
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.045c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89a.506.506 0 0 1-.045-.006zm-2.834 3.089c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.857 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982z"/>
                </svg>
              </div>}
              extra={
                <Switch 
                  checked={channels.wechat_enabled} 
                  onChange={v => handleToggle('wechat_enabled', v)}
                />
              }
              description="微信服务号模板消息"
            >
              微信通知
            </List.Item>
          </List>
        </div>
        
        {/* 业务通知 */}
        <div className="settings-section glass-card">
          <div className="section-header">
            <SetOutline className="section-icon" />
            <span>业务通知</span>
          </div>
          
          <List className="settings-list">
            {/* 收租提醒 */}
            <List.Item
              prefix={<div className="item-icon rent"><PayCircleOutline /></div>}
              extra={
                <Switch 
                  checked={business.rent_reminder?.enabled} 
                  onChange={v => handleToggle('rent_reminder_enabled', v)}
                />
              }
              description={
                business.rent_reminder?.enabled && (
                  <div className="days-config">
                    提前 
                    <Stepper 
                      value={business.rent_reminder?.days || 3}
                      min={1} 
                      max={30}
                      onChange={v => handleDaysChange('rent_reminder', v)}
                    /> 
                    天提醒
                  </div>
                )
              }
            >
              收租提醒
            </List.Item>
            
            {/* 资产到期 */}
            <List.Item
              prefix={<div className="item-icon expiry"><ClockCircleOutline /></div>}
              extra={
                <Switch 
                  checked={business.asset_expiry?.enabled} 
                  onChange={v => handleToggle('asset_expiry_enabled', v)}
                />
              }
              description={
                business.asset_expiry?.enabled && (
                  <div className="days-config">
                    提前 
                    <Stepper 
                      value={business.asset_expiry?.days || 7}
                      min={1} 
                      max={60}
                      onChange={v => handleDaysChange('asset_expiry', v)}
                    /> 
                    天提醒
                  </div>
                )
              }
            >
              资产到期
            </List.Item>
            
            {/* 费用提醒 */}
            <List.Item
              prefix={<div className="item-icon expense"><PayCircleOutline /></div>}
              extra={
                <Switch 
                  checked={business.expense_reminder?.enabled} 
                  onChange={v => handleToggle('expense_reminder_enabled', v)}
                />
              }
              description={
                business.expense_reminder?.enabled && (
                  <div className="days-config">
                    提前 
                    <Stepper 
                      value={business.expense_reminder?.days || 3}
                      min={1} 
                      max={30}
                      onChange={v => handleDaysChange('expense_reminder', v)}
                    /> 
                    天提醒
                  </div>
                )
              }
            >
              费用提醒
            </List.Item>
            
            {/* 折旧提醒 */}
            <List.Item
              prefix={<div className="item-icon depreciation"><FileOutline /></div>}
              extra={
                <Switch 
                  checked={business.depreciation?.enabled} 
                  onChange={v => handleToggle('depreciation_enabled', v)}
                />
              }
              description="资产完全折旧时提醒"
            >
              折旧提醒
            </List.Item>
          </List>
        </div>
        
        {/* 报告订阅 */}
        <div className="settings-section glass-card">
          <div className="section-header">
            <FileOutline className="section-icon" />
            <span>报告订阅</span>
          </div>
          
          <List className="settings-list">
            <List.Item
              prefix={<div className="item-icon weekly"><FileOutline /></div>}
              extra={
                <Switch 
                  checked={business.weekly_report?.enabled} 
                  onChange={v => handleToggle('weekly_report_enabled', v)}
                />
              }
              description="每周一发送上周资产汇总"
            >
              周报
            </List.Item>
            
            <List.Item
              prefix={<div className="item-icon monthly"><FileOutline /></div>}
              extra={
                <Switch 
                  checked={business.monthly_report?.enabled} 
                  onChange={v => handleToggle('monthly_report_enabled', v)}
                />
              }
              description="每月1日发送上月资产汇总"
            >
              月报
            </List.Item>
          </List>
        </div>
      </div>
    </div>
  )
}
