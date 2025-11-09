import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  Space,
  message,
  Tabs,
  Modal,
  Table,
  Tag,
  Divider,
  Alert,
  Typography,
  Row,
  Col
} from 'antd';
import {
  SaveOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  DeleteOutlined,
  PlusOutlined,
  WarningOutlined
} from '@ant-design/icons';
import request from '../utils/request';

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Title, Paragraph, Text } = Typography;

const NginxConfig = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [configs, setConfigs] = useState([]);
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [nginxStatus, setNginxStatus] = useState(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewContent, setPreviewContent] = useState('');

  // 加载配置列表
  const loadConfigs = async () => {
    try {
      const response = await request.get('/nginx/configs');
      if (response.data.success) {
        setConfigs(response.data.data);
      }
    } catch (error) {
      message.error('加载配置失败');
    }
  };

  // 加载Nginx状态
  const loadNginxStatus = async () => {
    try {
      const response = await request.get('/nginx/status');
      if (response.data.success) {
        setNginxStatus(response.data.data);
      }
    } catch (error) {
      console.error('加载Nginx状态失败:', error);
    }
  };

  useEffect(() => {
    loadConfigs();
    loadNginxStatus();
  }, []);

  // 创建新配置
  const handleCreate = async (values) => {
    setLoading(true);
    try {
      const response = await request.post('/nginx/configs', values);
      if (response.data.success) {
        message.success('配置创建成功');
        loadConfigs();
        form.resetFields();
      }
    } catch (error) {
      message.error(error.response?.data?.message || '创建配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新配置
  const handleUpdate = async (configId, values) => {
    setLoading(true);
    try {
      const response = await request.put(`/nginx/configs/${configId}`, values);
      if (response.data.success) {
        message.success('配置更新成功');
        loadConfigs();
      }
    } catch (error) {
      message.error(error.response?.data?.message || '更新配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除配置
  const handleDelete = (configId) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个配置吗？',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          const response = await request.delete(`/nginx/configs/${configId}`);
          if (response.data.success) {
            message.success('配置删除成功');
            loadConfigs();
          }
        } catch (error) {
          message.error(error.response?.data?.message || '删除配置失败');
        }
      },
    });
  };

  // 预览配置
  const handlePreview = async (configId) => {
    try {
      const response = await request.get(`/nginx/configs/${configId}/preview`);
      if (response.data.success) {
        setPreviewContent(response.data.data.content);
        setPreviewVisible(true);
      }
    } catch (error) {
      message.error('预览配置失败');
    }
  };

  // 应用配置
  const handleApply = (configId) => {
    Modal.confirm({
      title: '确认应用配置',
      content: (
        <div>
          <Alert
            message="重要提示"
            description="应用此配置将重载Nginx服务，可能会短暂中断服务。请确保配置正确后再执行此操作。"
            type="warning"
            showIcon
            icon={<WarningOutlined />}
            style={{ marginBottom: 16 }}
          />
          <Paragraph>确定要应用这个配置并重载Nginx吗？</Paragraph>
        </div>
      ),
      okText: '确认应用',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          const response = await request.post(`/nginx/configs/${configId}/apply`);
          if (response.data.success) {
            message.success('配置应用成功');
            loadConfigs();
            loadNginxStatus();
          }
        } catch (error) {
          message.error(error.response?.data?.message || '应用配置失败');
        }
      },
    });
  };

  // 配置表格列
  const columns = [
    {
      title: '服务器名称',
      dataIndex: 'server_name',
      key: 'server_name',
    },
    {
      title: '监听端口',
      dataIndex: 'listen_port',
      key: 'listen_port',
    },
    {
      title: 'SSL',
      dataIndex: 'ssl_enabled',
      key: 'ssl_enabled',
      render: (enabled) => (
        <Tag color={enabled ? 'green' : 'default'}>
          {enabled ? '已启用' : '未启用'}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'success' : 'default'} icon={active ? <CheckCircleOutlined /> : null}>
          {active ? '激活中' : '未激活'}
        </Tag>
      ),
    },
    {
      title: '最后应用',
      dataIndex: 'last_applied',
      key: 'last_applied',
      render: (date) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record.id)}
          >
            预览
          </Button>
          <Button
            type="link"
            onClick={() => {
              setSelectedConfig(record);
              form.setFieldsValue(record);
            }}
          >
            编辑
          </Button>
          <Button
            type="primary"
            size="small"
            icon={<CheckCircleOutlined />}
            onClick={() => handleApply(record.id)}
            disabled={record.is_active}
          >
            应用
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
            disabled={record.is_active}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Nginx 配置管理</Title>
      <Paragraph type="secondary">
        在此页面可以配置和管理Nginx反向代理设置，包括域名、SSL证书、端口等。
      </Paragraph>

      {/* Nginx状态卡片 */}
      {nginxStatus && (
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Space>
                <Text strong>Nginx状态:</Text>
                <Tag color={nginxStatus.is_running ? 'success' : 'error'}>
                  {nginxStatus.is_running ? '运行中' : '已停止'}
                </Tag>
              </Space>
            </Col>
            <Col span={12}>
              <Space>
                <Text strong>当前激活配置:</Text>
                <Text>{nginxStatus.active_config?.server_name || '无'}</Text>
              </Space>
            </Col>
          </Row>
        </Card>
      )}

      <Tabs defaultActiveKey="1">
        <TabPane tab="配置列表" key="1">
          <Card>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setSelectedConfig(null);
                form.resetFields();
              }}
              style={{ marginBottom: 16 }}
            >
              新建配置
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadConfigs}
              style={{ marginLeft: 8, marginBottom: 16 }}
            >
              刷新
            </Button>
            <Table
              dataSource={configs}
              columns={columns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        <TabPane tab={selectedConfig ? '编辑配置' : '新建配置'} key="2">
          <Card>
            <Form
              form={form}
              layout="vertical"
              onFinish={(values) => {
                if (selectedConfig) {
                  handleUpdate(selectedConfig.id, values);
                } else {
                  handleCreate(values);
                }
              }}
              initialValues={{
                server_name: '_',
                listen_port: 80,
                ssl_enabled: false,
                ssl_port: 443,
                force_https: false,
                frontend_proxy_enabled: true,
                frontend_port: 3000,
                backend_port: 5000,
                client_max_body_size: '20M',
                gzip_enabled: true,
                access_log_enabled: true,
              }}
            >
              <Title level={4}>基础配置</Title>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="服务器名称（域名）"
                    name="server_name"
                    tooltip="输入域名或使用 _ 接受所有请求"
                    rules={[{ required: true, message: '请输入服务器名称' }]}
                  >
                    <Input placeholder="example.com 或 _" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="监听端口"
                    name="listen_port"
                    rules={[{ required: true, message: '请输入监听端口' }]}
                  >
                    <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Title level={4}>SSL配置</Title>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="启用SSL" name="ssl_enabled" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="SSL端口" name="ssl_port">
                    <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="强制HTTPS" name="force_https" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    label="SSL证书路径"
                    name="ssl_certificate"
                    tooltip="服务器上SSL证书文件的完整路径"
                  >
                    <Input placeholder="/etc/ssl/certs/cert.pem" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    label="SSL私钥路径"
                    name="ssl_certificate_key"
                    tooltip="服务器上SSL私钥文件的完整路径"
                  >
                    <Input placeholder="/etc/ssl/private/key.pem" />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Title level={4}>代理配置</Title>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="前端代理" name="frontend_proxy_enabled" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="前端端口" name="frontend_port">
                    <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="后端API端口" name="backend_port">
                    <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>

              <Divider />

              <Title level={4}>高级配置</Title>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item label="最大上传大小" name="client_max_body_size">
                    <Input placeholder="20M" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="Gzip压缩" name="gzip_enabled" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item label="访问日志" name="access_log_enabled" valuePropName="checked">
                    <Switch />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                label="自定义配置"
                name="custom_config"
                tooltip="添加自定义的Nginx配置指令（每行一个）"
              >
                <TextArea
                  rows={6}
                  placeholder="示例：&#10;location /static/ {&#10;    alias /var/www/static/;&#10;}"
                />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                    {selectedConfig ? '更新配置' : '创建配置'}
                  </Button>
                  {selectedConfig && (
                    <Button
                      icon={<EyeOutlined />}
                      onClick={() => handlePreview(selectedConfig.id)}
                    >
                      预览配置
                    </Button>
                  )}
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>

      {/* 预览模态框 */}
      <Modal
        title="Nginx配置预览"
        visible={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        <pre style={{ backgroundColor: '#f5f5f5', padding: 16, borderRadius: 4, maxHeight: 600, overflow: 'auto' }}>
          {previewContent}
        </pre>
      </Modal>
    </div>
  );
};

export default NginxConfig;
