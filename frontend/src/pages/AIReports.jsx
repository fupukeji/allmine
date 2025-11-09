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

const { Title, Paragraph, Text } = Typography;
const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { Option } = Select;

const AIReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [hasToken, setHasToken] = useState(false);
  const [tokenModalVisible, setTokenModalVisible] = useState(false);
  const [generateModalVisible, setGenerateModalVisible] = useState(false);
  const [reportDetailVisible, setReportDetailVisible] = useState(false);
  const [currentReport, setCurrentReport] = useState(null);
  const [form] = Form.useForm();
  const [tokenForm] = Form.useForm();

  // 加载数据
  useEffect(() => {
    checkApiToken();
    loadStats();
    loadReports();
  }, []);

  // 检查API Token
  const checkApiToken = async () => {
    try {
      const response = await request.get('/reports/token');
      if (response.success) {
        setHasToken(response.data.has_token);
        if (!response.data.has_token) {
          message.warning('请先配置阿里云API Token');
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

  // 保存API Token
  const handleSaveToken = async (values) => {
    try {
      const response = await request.post('/reports/token', {
        api_token: values.api_token
      });
      if (response.success) {
        message.success('API Token保存成功');
        setHasToken(true);
        setTokenModalVisible(false);
        tokenForm.resetFields();
      } else {
        message.error(response.message || 'Token保存失败');
      }
    } catch (error) {
      message.error(error.response?.data?.message || 'Token保存失败');
    }
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

      message.loading('正在生成报告，请稍候...', 0);

      const response = await request.post('/reports/generate', payload);
      
      message.destroy();

      if (response.success) {
        message.success('报告生成成功');
        setGenerateModalVisible(false);
        form.resetFields();
        loadReports();
        loadStats();
      }
    } catch (error) {
      message.destroy();
      message.error(error.response?.data?.message || '报告生成失败');
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
      const content = JSON.parse(report.content);
      
      // 周报格式
      if (report.report_type === 'weekly' && content.executive_summary) {
        return (
          <div>
            <Title level={4}>执行摘要</Title>
            <Paragraph>{content.executive_summary}</Paragraph>

            {content.asset_analysis && (
              <>
                <Divider />
                <Title level={4}>资产分析</Title>
                <Paragraph><strong>整体健康度：</strong>{content.asset_analysis.overall_health}</Paragraph>
                <Paragraph><strong>价值趋势：</strong>{content.asset_analysis.value_trends}</Paragraph>
                <Paragraph><strong>折旧分析：</strong>{content.asset_analysis.depreciation_analysis}</Paragraph>
              </>
            )}

            {content.income_analysis && (
              <>
                <Divider />
                <Title level={4}>收入分析</Title>
                <Paragraph><strong>收入表现：</strong>{content.income_analysis.income_performance}</Paragraph>
                <Paragraph><strong>ROI估算：</strong>{content.income_analysis.roi_estimation}</Paragraph>
              </>
            )}

            {content.risk_assessment && (
              <>
                <Divider />
                <Title level={4}>风险评估</Title>
                <Tag color={content.risk_assessment.risk_level === 'low' ? 'green' : content.risk_assessment.risk_level === 'medium' ? 'orange' : 'red'}>
                  风险等级：{content.risk_assessment.risk_level}
                </Tag>
                {content.risk_assessment.risk_factors && content.risk_assessment.risk_factors.length > 0 && (
                  <>
                    <Paragraph style={{ marginTop: 16 }}><strong>风险因素：</strong></Paragraph>
                    <ul>
                      {content.risk_assessment.risk_factors.map((factor, index) => (
                        <li key={index}>{factor}</li>
                      ))}
                    </ul>
                  </>
                )}
              </>
            )}

            {content.recommendations && content.recommendations.length > 0 && (
              <>
                <Divider />
                <Title level={4}>建议</Title>
                <ul>
                  {content.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </>
            )}

            {content.next_week_focus && content.next_week_focus.length > 0 && (
              <>
                <Divider />
                <Title level={4}>下周关注点</Title>
                <ul>
                  {content.next_week_focus.map((focus, index) => (
                    <li key={index}>{focus}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        );
      }

      // 月报格式
      if (report.report_type === 'monthly' && content.executive_summary) {
        return (
          <div>
            <Title level={4}>执行摘要</Title>
            <Paragraph>{content.executive_summary}</Paragraph>

            {content.monthly_highlights && content.monthly_highlights.length > 0 && (
              <>
                <Divider />
                <Title level={4}>本月亮点</Title>
                <ul>
                  {content.monthly_highlights.map((highlight, index) => (
                    <li key={index}>{highlight}</li>
                  ))}
                </ul>
              </>
            )}

            {content.asset_analysis && (
              <>
                <Divider />
                <Title level={4}>资产分析</Title>
                {Object.entries(content.asset_analysis).map(([key, value]) => (
                  <Paragraph key={key}><strong>{key}：</strong>{value}</Paragraph>
                ))}
              </>
            )}

            {content.recommendations && (
              <>
                <Divider />
                <Title level={4}>建议</Title>
                {content.recommendations.short_term && (
                  <>
                    <Paragraph><strong>短期建议：</strong></Paragraph>
                    <ul>
                      {content.recommendations.short_term.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </>
                )}
                {content.recommendations.long_term && (
                  <>
                    <Paragraph><strong>长期建议：</strong></Paragraph>
                    <ul>
                      {content.recommendations.long_term.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </>
                )}
              </>
            )}
          </div>
        );
      }

      // 通用格式（包括自定义报告）
      if (content.raw_response) {
        return (
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
            {content.raw_response}
          </div>
        );
      }

      return <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(content, null, 2)}</pre>;

    } catch (error) {
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
      render: (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-',
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
        title="配置智谱AI API Key"
        visible={tokenModalVisible}
        onCancel={() => setTokenModalVisible(false)}
        footer={null}
      >
        <Alert
          message="如何获取API Key？"
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
        <Form form={tokenForm} onFinish={handleSaveToken} layout="vertical">
          <Form.Item
            label="API Key"
            name="api_token"
            rules={[{ required: true, message: '请输入API Key' }]}
          >
            <TextArea rows={4} placeholder="请粘贴您的智谱AI API Key" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => setTokenModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 生成报告弹窗 */}
      <Modal
        title="生成智能报告"
        visible={generateModalVisible}
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
        visible={reportDetailVisible}
        onCancel={() => setReportDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setReportDetailVisible(false)}>
            关闭
          </Button>,
        ]}
        width={900}
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
