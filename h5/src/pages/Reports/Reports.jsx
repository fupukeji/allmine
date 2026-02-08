import { useState, useEffect } from 'react'
import { Card, List, Button, Toast, Empty, Skeleton } from 'antd-mobile'
import { FileOutline } from 'antd-mobile-icons'
import { getReports } from '../../services/reports'

const Reports = () => {
  const [loading, setLoading] = useState(false)
  const [reports, setReports] = useState([])

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      setLoading(true)
      const res = await getReports()
      
      if (res.code === 200 && res.data) {
        setReports(res.data.items || res.data || [])
      }
    } catch (error) {
      console.error('加载报告失败:', error)
      Toast.show({ icon: 'fail', content: '加载失败' })
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div style={{ padding: '12px' }}>
        <Card><Skeleton.Title animated /><Skeleton.Paragraph lineCount={3} animated /></Card>
      </div>
    )
  }

  return (
    <div style={{ padding: '12px' }}>
      <Button
        block
        color="primary"
        size="large"
        style={{ marginBottom: '12px' }}
        onClick={() => Toast.show('功能开发中...')}
      >
        生成新报告
      </Button>

      {reports.length === 0 ? (
        <Empty description="暂无AI报告" style={{ padding: '64px 0' }} />
      ) : (
        <List>
          {reports.map((report) => (
            <List.Item
              key={report.id}
              prefix={<FileOutline fontSize={24} color="#faad14" />}
              description={formatDate(report.created_at)}
              onClick={() => Toast.show('功能开发中...')}
            >
              {report.report_type}报告
            </List.Item>
          ))}
        </List>
      )}
    </div>
  )
}

export default Reports
