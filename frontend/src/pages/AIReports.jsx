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
  Spin,
  InputNumber,
  Tabs
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
  SyncOutlined,
  NodeIndexOutlined
} from '@ant-design/icons';
import request from '../utils/request';
import dayjs from 'dayjs';
import isoWeek from 'dayjs/plugin/isoWeek'; // 引入ISO周插件
import ReportRenderer from '../components/ReportRenderer'; // 引入增强渲染器
import WorkflowVisualization from '../components/WorkflowVisualization'; // 工作流可视化组件

// 扩展dayjs支持ISO周
dayjs.extend(isoWeek);

const { Title, Paragraph, Text } = Typography;
const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { Option } = Select;

const AIReports = () => {
  const [reports, setReports] = useState([]);
  const [filteredReports, setFilteredReports] = useState([]); // 筛选后的报告
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
  const [autoRefreshTimer, setAutoRefreshTimer] = useState(null);
  const [showFullKey, setShowFullKey] = useState(false);
  const [fullKey, setFullKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('glm-4.5-flash');
  
  // 搜索相关状态
  const [searchText, setSearchText] = useState(''); // 搜索文本
  const [searchType, setSearchType] = useState('all'); // 搜索类型筛选
  
  // 批量删除相关状态
  const [selectedRowKeys, setSelectedRowKeys] = useState([]); // 选中的报告ID
  const [workflowModalVisible, setWorkflowModalVisible] = useState(false); // 工作流模态框
  const [workflowReportId, setWorkflowReportId] = useState(null); // 当前查看工作流的报告ID

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
        setFilteredReports(response.data.reports); // 初始化筛选列表
      }
    } catch (error) {
      message.error('加载报告列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 搜索和筛选功能
  const handleSearch = (value) => {
    setSearchText(value);
    filterReports(value, searchType);
  };

  const handleTypeFilter = (value) => {
    setSearchType(value);
    filterReports(searchText, value);
  };

  const filterReports = (text, type) => {
    let filtered = reports;

    // 按类型筛选
    if (type !== 'all') {
      filtered = filtered.filter(report => report.report_type === type);
    }

    // 按文本搜索（搜索标题和摘要）
    if (text) {
      const lowerText = text.toLowerCase();
      filtered = filtered.filter(report => 
        (report.title && report.title.toLowerCase().includes(lowerText)) ||
        (report.summary && report.summary.toLowerCase().includes(lowerText))
      );
    }

    setFilteredReports(filtered);
  };

  // 保存API Key
  const handleSaveToken = async (values) => {
    try {
      const response = await request.post('/reports/token', {
        api_key: values.api_key,
        model: values.model || 'glm-4-flash'  // 保存选中的模型
      });
      if (response.success) {
        message.success('API Key和模型配置保存成功');
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

      // 根据报告类型构建参数
      if (values.report_type === 'weekly') {
        payload.year = values.year || dayjs().year();
        payload.week = values.week || dayjs().isoWeek();
      } else if (values.report_type === 'monthly') {
        payload.year = values.year || dayjs().year();
        payload.month = values.month || dayjs().month() + 1;
      } else if (values.report_type === 'yearly') {
        payload.year = values.year || dayjs().year();
        if (values.focus_areas) {
          payload.focus_areas = values.focus_areas.split(',').map(s => s.trim());
        }
      } else if (values.report_type === 'custom') {
        payload.start_date = values.date_range[0].format('YYYY-MM-DD');
        payload.end_date = values.date_range[1].format('YYYY-MM-DD');
        if (values.focus_areas) {
          payload.focus_areas = values.focus_areas.split(',').map(s => s.trim());
        }
      }

      setGenerateModalVisible(false);
      form.resetFields();
      
      const hideLoading = message.loading('报告生成任务已提交，正在后台处理...', 0);
      
      // 发送生成请求（异步，立即返回）
      const response = await request.post('/reports/generate', payload);
      
      if (response.success) {
        hideLoading();
        const reportId = response.data.id;
        message.success('报告生成任务已提交，正在后台处理...');
        
        // 立即刷新列表
        await loadReports();
        await loadStats();
        
        // 清除之前的定时器
        if (autoRefreshTimer) {
          clearInterval(autoRefreshTimer);
          setAutoRefreshTimer(null);
        }
        
        // 启动轮询：每3秒检查报告状态
        let checkCount = 0;
        const maxCheckCount = 100; // 最多轮询5分钟 (100次 x 3秒)
        let timer = null; // 在外部声明
        
        const pollReport = async () => {
          try {
            const reportResponse = await request.get(`/reports/${reportId}`);
            console.log('轮询报告状态:', reportResponse); // 调试日志
            
            if (reportResponse.success) {
              const report = reportResponse.data;
              console.log('报告状态:', report.status, '报告ID:', reportId); // 调试
              
              if (report.status === 'completed') {
                // 生成成功
                console.log('✅ 报告生成完成，停止轮询');
                if (timer) {
                  clearInterval(timer);
                }
                setAutoRefreshTimer(null);
                message.success('报告生成成功！');
                await loadReports();
                await loadStats();
                return; // 立即退出
              } else if (report.status === 'failed') {
                // 生成失败
                console.log('❌ 报告生成失败，停止轮询');
                if (timer) {
                  clearInterval(timer);
                }
                setAutoRefreshTimer(null);
                message.error(`报告生成失败：${report.error_message || '未知错误'}`);
                await loadReports();
                return; // 立即退出
              } else {
                console.log('🔄 报告仍在生成中...', `第${checkCount + 1}次轮询`);
              }
            }
          } catch (error) {
            console.error('轮询报告状态失败:', error);
          }
          
          checkCount++;
          if (checkCount >= maxCheckCount) {
            console.log('⚠️ 轮询超时，停止轮询');
            if (timer) {
              clearInterval(timer);
            }
            setAutoRefreshTimer(null);
            message.warning('轮询超时，请手动刷新查看报告状态');
          }
        };
        
        timer = setInterval(pollReport, 3000); // 每3秒轮询一次
        setAutoRefreshTimer(timer);
        
        // 立即执行第一次轮询
        pollReport();
      }
      
    } catch (error) {
      console.error('提交报告生成请求失败:', error);
      
      // 如果是API Token配置问题
      if (error.response?.status === 400 && error.response?.data?.message?.includes('API')) {
        Modal.confirm({
          title: '未配置API Key',
          content: '请先配置AI API Key才能生成智能报告',
          okText: '立即配置',
          cancelText: '取消',
          onOk: () => setTokenModalVisible(true)
        });
      } else {
        message.error('提交失败：' + (error.response?.data?.message || error.message || '请重试'));
      }
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
  
  // 批量删除报告
  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的报告');
      return;
    }
    
    Modal.confirm({
      title: '批量删除',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个报告吗？此操作不可恢复。`,
      okText: '确认',
      cancelText: '取消',
      okType: 'danger',
      onOk: async () => {
        try {
          // 逐个删除
          const deletePromises = selectedRowKeys.map(id => 
            request.delete(`/reports/${id}`)
          );
          
          await Promise.all(deletePromises);
          message.success(`成功删除 ${selectedRowKeys.length} 个报告`);
          setSelectedRowKeys([]);
          loadReports();
          loadStats();
        } catch (error) {
          message.error('批量删除失败');
        }
      },
    });
  };
  
  // 查看工作流轨迹
  const handleViewWorkflow = (reportId) => {
    setWorkflowReportId(reportId);
    setWorkflowModalVisible(true);
  };
  
  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys) => {
      setSelectedRowKeys(selectedKeys);
    },
  };

  // 渲染报告内容
  const renderReportContent = (report) => {
    try {
      const content = typeof report.content === 'string' ? JSON.parse(report.content) : report.content;
      
      // 判断是否为Markdown/Text格式
      if (content.report_type === 'markdown' || content.report_type === 'text') {
        // 传递完整的content对象,包含markdown内容和图表数据
        return <ReportRenderer content={content} />;
      }
      
      // 传统JSON结构
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
      render: (text, record) => {
        const colorMap = {
          weekly: 'blue',
          monthly: 'green',
          yearly: 'orange',
          custom: 'purple'
        };
        return (
          <Tag color={colorMap[record.report_type] || 'default'}>
            {text}
          </Tag>
        );
      },
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
            <>
              <Button
                type="link"
                icon={<EyeOutlined />}
                onClick={() => handleViewReport(record.id)}
              >
                查看
              </Button>
              <Button
                type="link"
                icon={<NodeIndexOutlined />}
                onClick={() => handleViewWorkflow(record.id)}
              >
                工作流
              </Button>
            </>
          )}
          {record.status === 'generating' && (
            <Button
              type="link"
              icon={<SyncOutlined spin />}
              onClick={() => handleViewWorkflow(record.id)}
            >
              实时查看
            </Button>
          )}
          {record.status === 'failed' && (
            <Button
              type="link"
              icon={<NodeIndexOutlined />}
              onClick={() => handleViewWorkflow(record.id)}
            >
              查看失败原因
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
                title="自定义/年报"
                value={stats.by_type.custom}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 操作按钮 */}
      <Space style={{ marginBottom: 16 }} wrap>
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
        <Button 
          danger
          icon={<DeleteOutlined />} 
          onClick={handleBatchDelete}
          disabled={selectedRowKeys.length === 0}
        >
          批量删除 {selectedRowKeys.length > 0 && `(${selectedRowKeys.length})`}
        </Button>
        <Button icon={<SettingOutlined />} onClick={() => setTokenModalVisible(true)}>
          配置API Key
        </Button>
        
        {/* 搜索栏 */}
        <Input.Search
          placeholder="搜索报告标题或摘要..."
          allowClear
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => handleSearch(e.target.value)}
          onSearch={handleSearch}
        />
        
        {/* 类型筛选 */}
        <Select
          style={{ width: 150 }}
          value={searchType}
          onChange={handleTypeFilter}
          placeholder="筛选类型"
        >
          <Option value="all">全部类型</Option>
          <Option value="weekly">周报</Option>
          <Option value="monthly">月报</Option>
          <Option value="yearly">年报</Option>
          <Option value="custom">自定义</Option>
        </Select>
        
        {/* 显示筛选结果 */}
        <Text type="secondary">
          共 {filteredReports.length} 条结果
          {searchText || searchType !== 'all' ? ` (已筛选)` : ''}
        </Text>
      </Space>

      {/* 报告列表 */}
      <Card>
        <Table
          dataSource={filteredReports}
          columns={columns}
          rowKey="id"
          rowSelection={rowSelection}
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
      
      {/* 工作流可视化独立模态框 */}
      <Modal
        title={<span><NodeIndexOutlined /> 工作流执行轨迹</span>}
        open={workflowModalVisible}
        onCancel={() => {
          setWorkflowModalVisible(false);
          setWorkflowReportId(null);
        }}
        footer={null}
        width={1000}
        destroyOnClose
      >
        {workflowReportId && (
          <WorkflowVisualization 
            reportId={workflowReportId}
            refreshInterval={3000}
          />
        )}
      </Modal>

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
            label="选择模型"
            name="model"
            initialValue="glm-4-flash"
            rules={[{ required: true, message: '请选择模型' }]}
          >
            <Select placeholder="请选择AI模型" size="large">
              <Option value="glm-4-flash">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4-Flash (推荐⭐)</div>
                  <div style={{ fontSize: 12, color: '#52c41a', marginTop: 2 }}>
                    完全免费 | 高速响应 | 1000次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-z1-flash">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-Z1-Flash</div>
                  <div style={{ fontSize: 12, color: '#52c41a', marginTop: 2 }}>
                    完全免费 | 推理增强 | 40次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-4-air">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4-Air</div>
                  <div style={{ fontSize: 12, color: '#1890ff', marginTop: 2 }}>
                    超低成本 0.0005元/千Tokens | 200次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-4-airx">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4-AirX</div>
                  <div style={{ fontSize: 12, color: '#1890ff', marginTop: 2 }}>
                    超轻量 0.01元/千Tokens | 30次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-4-flashx">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4-FlashX</div>
                  <div style={{ fontSize: 12, color: '#1890ff', marginTop: 2 }}>
                    极低成本 0.0001元/千Tokens | 100次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-4-plus">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4-Plus</div>
                  <div style={{ fontSize: 12, color: '#fa8c16', marginTop: 2 }}>
                    增强版 0.005元/千Tokens | 50次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-4-long">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4-Long</div>
                  <div style={{ fontSize: 12, color: '#1890ff', marginTop: 2 }}>
                    长文本 0.001元/千Tokens | 30次/分
                  </div>
                </div>
              </Option>
              
              <Option value="glm-4">
                <div style={{ padding: '4px 0' }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>GLM-4</div>
                  <div style={{ fontSize: 12, color: '#fa8c16', marginTop: 2 }}>
                    通用版 0.1元/千Tokens | 50次/分
                  </div>
                </div>
              </Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            label="API Key"
            name="api_key"
            rules={[{ required: true, message: '请输入API Key' }]}
          >
            <Input 
              placeholder="请粘贴您的智谱AI API Key"
              size="large"
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
              <Option value="weekly">周报</Option>
              <Option value="monthly">月报</Option>
              <Option value="yearly">年报</Option>
              <Option value="custom">自定义时间段</Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => prevValues.report_type !== currentValues.report_type}
          >
            {({ getFieldValue }) => {
              const reportType = getFieldValue('report_type');
              
              if (reportType === 'weekly') {
                return (
                  <>
                    <Form.Item
                      label="年份"
                      name="year"
                      initialValue={dayjs().year()}
                    >
                      <InputNumber 
                        min={2020} 
                        max={2099} 
                        style={{ width: '100%' }}
                        placeholder="请输入年份"
                      />
                    </Form.Item>
                    <Form.Item
                      label="周数"
                      name="week"
                      initialValue={dayjs().isoWeek()}
                      tooltip="ISO 8601周数，一年有约52-53周"
                    >
                      <InputNumber 
                        min={1} 
                        max={53} 
                        style={{ width: '100%' }}
                        placeholder="请输入周数 (1-53)"
                      />
                    </Form.Item>
                  </>
                );
              }
              
              if (reportType === 'monthly') {
                return (
                  <>
                    <Form.Item
                      label="年份"
                      name="year"
                      initialValue={dayjs().year()}
                    >
                      <InputNumber 
                        min={2020} 
                        max={2099} 
                        style={{ width: '100%' }}
                        placeholder="请输入年份"
                      />
                    </Form.Item>
                    <Form.Item
                      label="月份"
                      name="month"
                      initialValue={dayjs().month() + 1}
                    >
                      <Select placeholder="请选择月份">
                        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(m => (
                          <Option key={m} value={m}>{m}月</Option>
                        ))}
                      </Select>
                    </Form.Item>
                  </>
                );
              }
              
              if (reportType === 'yearly') {
                return (
                  <>
                    <Form.Item
                      label="年份"
                      name="year"
                      initialValue={dayjs().year()}
                    >
                      <InputNumber 
                        min={2020} 
                        max={2099} 
                        style={{ width: '100%' }}
                        placeholder="请输入年份"
                      />
                    </Form.Item>
                    <Form.Item
                      label="关注领域（可选）"
                      name="focus_areas"
                      tooltip="多个领域用逗号分隔，如：年度资产增长,收益分析"
                    >
                      <Input placeholder="例如：年度资产增长,收益分析,风险控制" />
                    </Form.Item>
                  </>
                );
              }
              
              if (reportType === 'custom') {
                return (
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
                );
              }
              
              return null;
            }}
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
        styles={{ body: { maxHeight: '80vh', overflow: 'auto' } }}
      >
        {currentReport && (
          <Tabs defaultActiveKey="content">
            {/* 报告内容Tab */}
            <Tabs.TabPane tab="📊 报告内容" key="content">
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
            </Tabs.TabPane>
            
            {/* 工作流轨迹Tab */}
            <Tabs.TabPane 
              tab={
                <span>
                  <NodeIndexOutlined /> 工作流轨迹
                </span>
              } 
              key="workflow"
            >
              <WorkflowVisualization 
                reportId={currentReport.id}
                refreshInterval={3000}
              />
            </Tabs.TabPane>
          </Tabs>
        )}
      </Modal>
    </div>
  );
};

export default AIReports;
