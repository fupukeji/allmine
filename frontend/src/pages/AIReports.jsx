import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Table,
  Tag,
  Modal,
  Form,
  Input,
  DatePicker,
  Select,
  message,
  Space,
  Divider,
  Typography,
  Row,
  Col,
  Statistic,
  Alert,
  Spin
} from 'antd';
import {
  FileTextOutlined,
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  BarChartOutlined,
  ReloadOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import request from '../utils/request';
import dayjs from 'dayjs';
import ReportRenderer from '../components/ReportRenderer'; // 引入增强渲染器

const { Title, Paragraph, Text } = Typography;
const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { Option } = Select;

const AIReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [hasToken, setHasToken] = useState(false);
  const [maskedKey, setMaskedKey] = useState(null);
  const [tokenModalVisible, setTokenModalVisible] = useState(false);
  const [generateModalVisible, setGenerateModalVisible] = useState(false);
  const [reportDetailVisible, setReportDetailVisible] = useState(false);
  const [currentReport, setCurrentReport] = useState(null);
  const [form] = Form.useForm();
  const [tokenForm] = Form.useForm();
  const [autoRefreshTimer, setAutoRefreshTimer] = useState(null); // 自动刷新定时器
  const [showFullKey, setShowFullKey] = useState(false); // 是否显示完整Key
  const [fullKey, setFullKey] = useState(''); // 完整的Key

  // 加载数据
  useEffect(() => {
    checkApiToken();
    loadStats();
    loadReports();
    
    // 组件卸载时清除定时器
    return () => {
      if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
      }
    };
  }, []);

  // 检查API Token
  const checkApiToken = async () => {
    try {
      const response = await request.get('/reports/token');
      if (response.success) {
        setHasToken(response.data.has_token);
        setMaskedKey(response.data.masked_key);
        
        if (!response.data.has_token) {
          message.warning('请先配置智谱AI API Key');
        }
      }
    } catch (error) {
      console.error('检查Token失败:', error);
    }
  };

  // 加载统计信息
  const loadStats = async () => {
    try {
      const response = await request.get('/reports/stats');
      if (response.success) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('加载统计信息失败:', error);
    }
  };

  // 加载报告列表
  const loadReports = async () => {
    setLoading(true);
    try {
      const response = await request.get('/reports');
      if (response.success) {
        setReports(response.data.reports);
      }
    } catch (error) {
      message.error('加载报告列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存API Key
  const handleSaveToken = async (values) => {
    try {
      const response = await request.post('/reports/token', {
        api_key: values.api_key
      });
      if (response.success) {
        message.success('API Key保存成功');
        setTokenModalVisible(false);
        tokenForm.resetFields();
        setShowFullKey(false);
        setFullKey('');
        // 重新检查Token状态
        checkApiToken();
      } else {
        message.error(response.message || 'Key保存失败');
      }
    } catch (error) {
      console.error('Key保存错误:', error);
    }
  };

  // 显示完整Key（需要密码验证）
  const handleRevealKey = async () => {
    Modal.confirm({
      title: '验证密码',
      content: (
        <Input.Password
          id="reveal-password"
          placeholder="请输入你的登录密码"
          onPressEnter={(e) => {
            document.querySelector('.ant-modal-confirm-btns .ant-btn-primary').click();
          }}
        />
      ),
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        const password = document.getElementById('reveal-password').value;
        if (!password) {
          message.error('请输入密码');
          return Promise.reject();
        }
        
        try {
          const response = await request.post('/reports/token/reveal', { password });
          if (response.success) {
            setFullKey(response.data.api_key);
            setShowFullKey(true);
            message.success('已显示完整Key');
          }
        } catch (error) {
          if (error.response?.status === 401) {
            message.error('密码错误');
          } else {
            message.error('获取失败');
          }
          return Promise.reject();
        }
      }
    });
  };

  // 隐藏Key
  const handleHideKey = () => {
    setShowFullKey(false);
    setFullKey('');
  };

  // 生成报告
  const handleGenerateReport = async (values) => {  
    try {
      const payload = {
        report_type: values.report_type
      };

      if (values.report_type === 'custom') {
        payload.start_date = values.date_range[0].format('YYYY-MM-DD');
        payload.end_date = values.date_range[1].format('YYYY-MM-DD');
        if (values.focus_areas) {
          payload.focus_areas = values.focus_areas.split(',').map(s => s.trim());
        }
      }

      // 立即关闭窗口
      setGenerateModalVisible(false);
      form.resetFields();
      
      // 显示提示，告诉用户报告正在生成
      const hideLoading = message.loading('报告生成中，请稍候...', 0);
      
      // 先清除之前的定时器
      if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
      }
      
      // 启动定时刷新（每3秒刷新一次）
      let refreshCount = 0;
      const maxRefreshCount = 10; // 最多刷新30秒（10次 x 3秒）
      
      const timer = setInterval(async () => {
        refreshCount++;
        await loadReports();
        await loadStats();
        
        // 达到最大刷新次数，停止刷新
        if (refreshCount >= maxRefreshCount) {
          clearInterval(timer);
          setAutoRefreshTimer(null);
          hideLoading();
          message.info('已停止自动刷新，请手动查看报告');
        }
      }, 3000); // 每3秒刷新一次
      
      setAutoRefreshTimer(timer);

      // 发送生成请求（异步，不等待结果）
      request.post('/reports/generate', payload).then(response => {
        if (response.success) {
          // 成功后立即停止刷新
          if (timer) {
            clearInterval(timer);
            setAutoRefreshTimer(null);
          }
          hideLoading();
          message.success('报告生成成功！');
          // 立即刷新一次
          loadReports();
          loadStats();
        }
      }).catch(error => {
        // 错误后也停止刷新
        if (timer) {
          clearInterval(timer);
          setAutoRefreshTimer(null);
        }
        hideLoading();
        
        // 如果是超时错误，不显示，因为后台仍在处理
        if (error.code === 'ECONNABORTED') {
          message.warning('请求超时，但报告正在后台生成，请稍后查看...');
          return; // 不显示错误
        }
        
        console.error('报告生成错误:', error);
        
        // 如果是API Token配置问题，提示用户配置
        if (error.response?.status === 400 && error.response?.data?.message?.includes('API')) {
          Modal.confirm({
            title: '未配置API Key',
            content: '请先配置AI API Key才能生成智能报告',
            okText: '立即配置',
            cancelText: '取消',
            onOk: () => setTokenModalVisible(true)
          });
        } else {
          message.error('报告生成失败：' + (error.response?.data?.message || error.message || '未知错误'));
        }
      });
      
    } catch (error) {
      console.error('提交报告生成请求失败:', error);
      message.error('提交失败，请重试');
    }
  };

  // 查看报告详情
  const handleViewReport = async (reportId) => {
    try {
      const response = await request.get(`/reports/${reportId}`);
      if (response.success) {
        setCurrentReport(response.data);
        setReportDetailVisible(true);
      }
    } catch (error) {
      message.error('加载报告详情失败');
    }
  };

  // 删除报告
  const handleDeleteReport = (reportId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这份报告吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await request.delete(`/reports/${reportId}`);
          if (response.success) {
            message.success('报告删除成功');
            loadReports();
            loadStats();
          }
        } catch (error) {
          message.error('删除报告失败');
        }
      },
    });
  };

  // 渲染报告内容
  const renderReportContent = (report) => {
    try {
      const content = typeof report.content === 'string' ? JSON.parse(report.content) : report.content;
      
      // 使用增强渲染器（支持结构化、表格、图表）
      return <ReportRenderer content={content} />;

    } catch (error) {
      console.error('报告内容解析错误:', error);
      return <Text type="danger">报告内容解析失败</Text>;
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '报告标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '类型',
      dataIndex: 'report_type_text',
      key: 'report_type',
      render: (text, record) => (
        <Tag color={record.report_type === 'weekly' ? 'blue' : record.report_type === 'monthly' ? 'green' : 'purple'}>
          {text}
        </Tag>
      ),
    },
    {
      title: '时间范围',
      key: 'date_range',
      render: (_, record) => (
        <span>
          {dayjs(record.start_date).format('YYYY-MM-DD')} 至 {dayjs(record.end_date).format('YYYY-MM-DD')}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status, record) => {
        const config = {
          generating: { icon: <SyncOutlined spin />, color: 'blue', text: record.status_text },
          completed: { icon: <CheckCircleOutlined />, color: 'green', text: record.status_text },
          failed: { icon: <CloseCircleOutlined />, color: 'red', text: record.status_text }
        };
        const { icon, color, text } = config[status] || {};
        return <Tag icon={icon} color={color}>{text}</Tag>;
      },
    },
    {
      title: '生成时间',
      dataIndex: 'generated_at',
      key: 'generated_at',
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          {record.status === 'completed' && (
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewReport(record.id)}
            >
              查看
            </Button>
          )}
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteReport(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>
        <BarChartOutlined /> 智能报告
      </Title>
      <Paragraph type="secondary">
        基于智谱AI GLM大模型，为您的资产数据提供深度AI分析
      </Paragraph>

      {!hasToken && (
        <Alert
          message="未配置API Key"
          description="请先配置智谱AI API Key才能生成智能报告"
          type="warning"
          showIcon
          action={
            <Button size="small" type="primary" onClick={() => setTokenModalVisible(true)}>
              立即配置
            </Button>
          }
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 统计卡片 */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="报告总数"
                value={stats.total}
                prefix={<FileTextOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="周报"
                value={stats.by_type.weekly}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="月报"
                value={stats.by_type.monthly}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="自定义报告"
                value={stats.by_type.custom}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 操作按钮 */}
      <Space style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setGenerateModalVisible(true)}
          disabled={!hasToken}
        >
          生成报告
        </Button>
        <Button icon={<ReloadOutlined />} onClick={loadReports}>
          刷新
        </Button>
        <Button icon={<SettingOutlined />} onClick={() => setTokenModalVisible(true)}>
          配置API Key
        </Button>
      </Space>

      {/* 报告列表 */}
      <Card>
        <Table
          dataSource={reports}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* API Key配置弹窗 */}
      <Modal
        title="配置AI服务API Key"
        open={tokenModalVisible}
        onCancel={() => {
          setTokenModalVisible(false);
          setShowFullKey(false);
          setFullKey('');
        }}
        footer={null}
        width={600}
      >
        <Alert
          message="配置智谱AI API Key"
          description="将用于生成智能报告和资产分析"
          type="info"
          style={{ marginBottom: 16 }}
        />
        
        {/* 显示已保存的Key */}
        {hasToken && maskedKey && (
          <Alert
            message="已保存的API Key"
            description={
              <div>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <strong>Key: </strong>
                    {showFullKey ? (
                      <span style={{ fontFamily: 'monospace' }}>{fullKey}</span>
                    ) : (
                      <span style={{ fontFamily: 'monospace' }}>{maskedKey}</span>
                    )}
                  </div>
                  <Space>
                    {!showFullKey ? (
                      <Button size="small" onClick={handleRevealKey}>
                        显示完整Key
                      </Button>
                    ) : (
                      <Button size="small" onClick={handleHideKey}>
                        隐藏Key
                      </Button>
                    )}
                  </Space>
                </Space>
              </div>
            }
            type="success"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form form={tokenForm} onFinish={handleSaveToken} layout="vertical">
          <Alert
            message="如何获取智谱AI API Key？"
            description={
              <div>
                <p>1. 访问智谱AI开放平台：<a href="https://open.bigmodel.cn" target="_blank" rel="noopener noreferrer">https://open.bigmodel.cn</a></p>
                <p>2. 注册并登录您的账户</p>
                <p>3. 在API Keys管理页面创建API Key</p>
                <p>4. 将API Key粘贴到下方输入框</p>
              </div>
            }
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          
          <Form.Item
            label="API Key"
            name="api_key"
            rules={[{ required: true, message: '请输入API Key' }]}
          >
            <TextArea 
              rows={4} 
              placeholder="请粘贴您的智谱AI API Key"
            />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => {
                setTokenModalVisible(false);
                setShowFullKey(false);
                setFullKey('');
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 生成报告弹窗 */}
      <Modal
        title="生成智能报告"
        open={generateModalVisible}
        onCancel={() => setGenerateModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} onFinish={handleGenerateReport} layout="vertical">
          <Form.Item
            label="报告类型"
            name="report_type"
            rules={[{ required: true, message: '请选择报告类型' }]}
          >
            <Select placeholder="请选择报告类型">
              <Option value="weekly">周报（本周）</Option>
              <Option value="monthly">月报（本月）</Option>
              <Option value="custom">自定义时间段</Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => prevValues.report_type !== currentValues.report_type}
          >
            {({ getFieldValue }) =>
              getFieldValue('report_type') === 'custom' ? (
                <>
                  <Form.Item
                    label="时间范围"
                    name="date_range"
                    rules={[{ required: true, message: '请选择时间范围' }]}
                  >
                    <RangePicker style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item
                    label="关注领域（可选）"
                    name="focus_areas"
                    tooltip="多个领域用逗号分隔，如：资产配置,风险控制,收益分析"
                  >
                    <Input placeholder="例如：资产配置,风险控制,收益分析" />
                  </Form.Item>
                </>
              ) : null
            }
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                生成报告
              </Button>
              <Button onClick={() => setGenerateModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 报告详情弹窗 */}
      <Modal
        title={currentReport?.title}
        open={reportDetailVisible}
        onCancel={() => setReportDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setReportDetailVisible(false)}>
            关闭
          </Button>,
        ]}
        width={1200}
        style={{ top: 20 }}
        bodyStyle={{ maxHeight: '80vh', overflow: 'auto' }}
      >
        {currentReport && (
          <div>
            <Space style={{ marginBottom: 16 }}>
              <Tag>{currentReport.report_type_text}</Tag>
              <Tag>
                {dayjs(currentReport.start_date).format('YYYY-MM-DD')} 至{' '}
                {dayjs(currentReport.end_date).format('YYYY-MM-DD')}
              </Tag>
            </Space>
            <Divider />
            {renderReportContent(currentReport)}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AIReports;
