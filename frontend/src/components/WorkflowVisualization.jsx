import React, { useState, useEffect } from 'react';
import { Card, Steps, Tag, Timeline, Spin, Alert, Row, Col } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  LoadingOutlined,
  WarningOutlined
} from '@ant-design/icons';
import request from '../utils/request'; // 使用统一的request工具

const { Step } = Steps;

/**
 * 工作流可视化组件
 * 实时展示报告生成的工作流执行进度
 */
const WorkflowVisualization = ({ reportId, refreshInterval = 3000 }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [workflowData, setWorkflowData] = useState(null);
  const [executionPath, setExecutionPath] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);

  // 节点名称映射 - 优化版
  const nodeNameMap = {
    'init_task': '初始化任务',
    'collect_fixed_assets': '采集固定资产',
    'collect_virtual_assets': '采集虚拟资产',
    'ai_integrated_analysis': 'AI综合分析',
    'query_compare_previous': '上期对比分析',
    'generate_qualitative_conclusion': '生成定性结论',
    'generate_report': '生成报告',
    'evaluate_quality': '质量评估',
    'save_report': '保存报告',
    'handle_retry': '重试处理',
    'handle_failure': '失败处理',
    // 兼容旧版节点
    'collect_data': '数据采集',
    'compress_data': '数据压缩',
    'agent_decide_comparison': 'Agent决策',
    'query_previous_data': '查询上期数据',
    'ai_preanalysis': 'AI定性分析'
  };

  // 获取工作流执行轨迹
  const fetchWorkflowTrace = async () => {
    try {
      console.log('[WorkflowVisualization] 开始获取工作流数据, reportId:', reportId);
      
      const response = await request.get(`/reports/${reportId}/workflow-trace`);

      console.log('[WorkflowVisualization] API响应:', response);

      if (response.success) {
        const data = response.data;
        console.log('[WorkflowVisualization] 工作流数据:', data);
        console.log('[WorkflowVisualization] execution_path 长度:', data.execution_path?.length);
        
        setWorkflowData(data);
        setExecutionPath(data.execution_path || []);
        
        // 计算当前步骤
        const completedNodes = (data.execution_path || []).filter(
          node => node.status === 'completed'
        );
        setCurrentStep(completedNodes.length);
        
        setError(null);
      } else {
        console.error('[WorkflowVisualization] API返回失败:', response.message);
        setError(response.message || '获取工作流轨迹失败');
      }
    } catch (err) {
      console.error('[WorkflowVisualization] 获取工作流轨迹失败:', err);
      console.error('[WorkflowVisualization] 错误详情:', err.response);
      setError(err.message || '获取工作流轨迹失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!reportId) return;

    console.log('🔄 [WorkflowVisualization] 初始化, reportId:', reportId);
    
    // 初始加载
    fetchWorkflowTrace();

    // 定时器引用
    let timer = null;
    
    // 只有在生成中才开启定时刷新
    const startPolling = () => {
      if (timer) {
        clearInterval(timer);
      }
      
      timer = setInterval(() => {
        console.log('⏰ [WorkflowVisualization] 定时检查工作流状态...');
        fetchWorkflowTrace();
      }, refreshInterval);
      
      console.log('▶️ [WorkflowVisualization] 启动轮询定时器');
    };
    
    // 检查是否需要轮询
    const checkAndStartPolling = () => {
      if (workflowData) {
        if (workflowData.status === 'generating') {
          console.log('🔄 [WorkflowVisualization] 报告生成中，启动轮询');
          startPolling();
        } else {
          console.log('⛔ [WorkflowVisualization] 报告已完成/失败，不需轮询');
          if (timer) {
            clearInterval(timer);
            timer = null;
          }
        }
      }
    };
    
    // 监听workflowData变化
    checkAndStartPolling();

    return () => {
      console.log('🧹 [WorkflowVisualization] 组件卸载，清除定时器');
      if (timer) {
        clearInterval(timer);
      }
    };
  }, [reportId, workflowData?.status]);

  // 获取节点状态图标
  const getNodeStatusIcon = (node) => {
    switch (node.status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'skipped':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return <LoadingOutlined style={{ color: '#1890ff' }} />;
    }
  };

  // 获取节点状态颜色
  const getNodeStatusColor = (node) => {
    switch (node.status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'skipped':
        return 'warning';
      default:
        return 'processing';
    }
  };

  // 格式化时间
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN');
  };

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="加载工作流数据..." />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <Alert
          message="加载失败"
          description={error}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  return (
    <div>
      {/* 生成中提示 */}
      {workflowData?.status === 'generating' && (
        <Alert
          message="报告正在生成中"
          description="工作流正在实时执行，页面每3秒自动刷新..."
          type="info"
          showIcon
          icon={<SyncOutlined spin />}
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 完成提示 */}
      {workflowData?.status === 'completed' && (
        <Alert
          message="报告生成完成"
          description="工作流已成功执行完毕"
          type="success"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 失败提示 - 优化样式 */}
      {workflowData?.status === 'failed' && (
        <Alert
          message="🚫 报告生成失败"
          description={
            <div>
              <p style={{ marginBottom: 8, fontSize: 13 }}>请查看下方执行轨迹了解失败原因</p>
              <div style={{ 
                background: '#fff1f0', 
                border: '1px solid #ffccc7',
                borderRadius: 6,
                padding: '12px 16px',
                fontSize: 12
              }}>
                <div style={{ fontWeight: 'bold', marginBottom: 8, color: '#cf1322' }}>
                  <WarningOutlined /> 常见问题排查:
                </div>
                <ul style={{ margin: 0, paddingLeft: 20, lineHeight: '1.8' }}>
                  <li>检查是否已配置智谱AI API Key(系统设置 → API配置)</li>
                  <li>确保至少有一个固定资产或虚拟资产</li>
                  <li>查看下方红色错误节点的详细信息</li>
                  <li>检查后端服务是否正常运行</li>
                </ul>
              </div>
            </div>
          }
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          closable
        />
      )}
      
      {/* 执行进度条 - 优化样式 */}
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📊 工作流执行进度</span>
            {workflowData?.status === 'generating' && (
              <Tag icon={<SyncOutlined spin />} color="processing">生成中</Tag>
            )}
            {workflowData?.status === 'completed' && (
              <Tag icon={<CheckCircleOutlined />} color="success">已完成</Tag>
            )}
            {workflowData?.status === 'failed' && (
              <Tag icon={<CloseCircleOutlined />} color="error">已失败</Tag>
            )}
          </div>
        }
        style={{ marginBottom: 16 }}
        bodyStyle={{ padding: '24px 32px' }}
      >
        <Steps 
          current={currentStep} 
          status={workflowData?.status === 'failed' ? 'error' : 'process'}
          size="small"
        >
          <Step title="初始化" description="准备任务" />
          <Step title="固定资产" description="采集+分析" />
          <Step title="虚拟资产" description="采集+分析" />
          <Step title="综合分析" description="AI整合" />
          <Step title="对比分析" description="同比环比" />
          <Step title="定性结论" description="生成结论" />
          <Step title="生成报告" description="完整报告" />
          <Step title="质量评估" description="评估报告" />
          <Step title="完成" description="保存报告" />
        </Steps>
      </Card>

      {/* 执行轨迹时间线 - 优化样式 */}
      <Card 
        title={
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>🔍 执行轨迹详情</span>
            <span style={{ fontSize: 12, fontWeight: 'normal', color: '#999' }}>
              共 {executionPath.length} 个节点
            </span>
          </div>
        }
        bodyStyle={{ padding: '16px 24px' }}
      >
        {executionPath.length > 0 ? (
          <Timeline
            mode="left"
            style={{ marginTop: 16 }}
          >
            {executionPath.map((node, index) => {
              const isError = node.status === 'failed';
              const isSuccess = node.status === 'completed';
              const isSkipped = node.status === 'skipped';
              
              return (
                <Timeline.Item
                  key={index}
                  dot={getNodeStatusIcon(node)}
                  color={isError ? 'red' : isSuccess ? 'green' : isSkipped ? 'gray' : 'blue'}
                >
                  {/* 节点标题卡片 */}
                  <div style={{ 
                    marginBottom: 8,
                    padding: '12px 16px',
                    background: isError ? '#fff1f0' : isSuccess ? '#f6ffed' : isSkipped ? '#fafafa' : '#e6f7ff',
                    borderLeft: `4px solid ${isError ? '#ff4d4f' : isSuccess ? '#52c41a' : isSkipped ? '#d9d9d9' : '#1890ff'}`,
                    borderRadius: 6,
                    boxShadow: '0 1px 4px rgba(0,0,0,0.05)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 600, fontSize: 14 }}>
                        {nodeNameMap[node.node] || node.node}
                      </span>
                      <Tag
                        color={getNodeStatusColor(node)}
                        style={{ marginLeft: 8, fontWeight: 500 }}
                      >
                        {node.status === 'completed' ? '✅ 已完成' :
                         node.status === 'failed' ? '❌ 失败' :
                         node.status === 'skipped' ? '⏭️ 跳过' : '🔄 执行中'}
                      </Tag>
                    </div>
                    
                    {node.timestamp && (
                      <div style={{ fontSize: 12, color: '#666', marginTop: 6 }}>
                        🕐 执行时间: {formatTime(node.timestamp)}
                      </div>
                    )}
                  </div>
                  
                {/* 显示节点额外信息 */}
                {node.summary && (
                  <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                    {node.node === 'collect_fixed_assets' && (
                      <>
                        固定资产: {node.summary.asset_count}项 | 
                        健康度: {node.summary.health_score?.toFixed(1)}/100 |
                        ROI: {node.summary.roi?.toFixed(2)}%
                      </>
                    )}
                    {node.node === 'collect_virtual_assets' && (
                      <>
                        虚拟资产: {node.summary.project_count}项 | 
                        效率: {node.summary.efficiency_score?.toFixed(1)}/100 |
                        利用率: {node.summary.utilization_rate?.toFixed(1)}%
                      </>
                    )}
                    {node.node === 'ai_integrated_analysis' && node.summary && (
                      <>
                        评估: {node.summary.assessment} | 
                        优势: {node.summary.strengths_count}个 | 
                        风险: {node.summary.risks_count}个
                      </>
                    )}
                    {node.node === 'query_compare_previous' && node.summary && (
                      <>
                        固定资产增长: {node.summary.fixed_growth?.toFixed(2)}% | 
                        虚拟资产增长: {node.summary.virtual_growth?.toFixed(2)}% |
                        趋势: {node.summary.overall_trend}
                      </>
                    )}
                    {node.node === 'generate_qualitative_conclusion' && node.summary && (
                      <>
                        评级: {node.summary.overall_rating} | 
                        风险: {node.summary.risk_level} | 
                        紧急度: {node.summary.severity_level}
                      </>
                    )}
                  </div>
                )}
                
                {/* 兼容旧版数据格式 */}
                {node.data_summary && (
                  <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                    固定资产: {node.data_summary.fixed_assets_count}项 | 
                    虚拟资产: {node.data_summary.virtual_assets_count}项
                  </div>
                )}
                
                {/* 【新增】定性结论结果展示 */}
                {node.node === 'generate_qualitative_conclusion' && node.summary && (
                  <div style={{ 
                    marginTop: 8, 
                    padding: 12, 
                    background: '#f6ffed', 
                    borderLeft: '3px solid #52c41a',
                    borderRadius: 4
                  }}>
                    <div style={{ fontSize: 13, fontWeight: 'bold', color: '#52c41a', marginBottom: 6 }}>
                      🎯 定性结论
                    </div>
                    <div style={{ fontSize: 12 }}>
                      <p style={{ margin: '4px 0' }}>
                        <strong>整体评级:</strong> 
                        <Tag color={
                          node.summary.overall_rating?.startsWith('A') ? 'green' :
                          node.summary.overall_rating?.startsWith('B') ? 'blue' :
                          node.summary.overall_rating?.startsWith('C') ? 'orange' : 'red'
                        }>
                          {node.summary.overall_rating || '未知'}
                        </Tag>
                      </p>
                      <p style={{ margin: '4px 0' }}>
                        <strong>风险等级:</strong> 
                        <Tag color={
                          node.summary.risk_level === '低' ? 'green' :
                          node.summary.risk_level === '中' ? 'orange' : 'red'
                        }>
                          {node.summary.risk_level || '未知'}
                        </Tag>
                      </p>
                      <p style={{ margin: '4px 0' }}>
                        <strong>紧急程度:</strong> 
                        <Tag color={
                          node.summary.severity_level === '低' ? 'green' :
                          node.summary.severity_level === '中' ? 'orange' : 'red'
                        }>
                          {node.summary.severity_level || '未知'}
                        </Tag>
                      </p>
                      {node.summary.key_findings_count > 0 && (
                        <p style={{ margin: '4px 0' }}>
                          <strong>关键发现:</strong> {node.summary.key_findings_count} 个
                        </p>
                      )}
                      {node.summary.priority_actions_count > 0 && (
                        <p style={{ margin: '4px 0' }}>
                          <strong>优先行动:</strong> {node.summary.priority_actions_count} 项
                        </p>
                      )}
                    </div>
                  </div>
                )}
                
                {/* 【兼容】旧版定性分析结果展示 */}
                {node.node === 'ai_preanalysis' && node.qualitative_summary && (
                  <div style={{ 
                    marginTop: 8, 
                    padding: 12, 
                    background: '#f0f5ff', 
                    borderLeft: '3px solid #1890ff',
                    borderRadius: 4
                  }}>
                    <div style={{ fontSize: 13, fontWeight: 'bold', color: '#1890ff', marginBottom: 6 }}>
                      🧐 定性分析结论
                    </div>
                    <div style={{ fontSize: 12 }}>
                      <p style={{ margin: '4px 0' }}>
                        <strong>整体评估:</strong> 
                        <Tag color={
                          node.qualitative_summary.assessment?.includes('优秀') ? 'green' :
                          node.qualitative_summary.assessment?.includes('良好') ? 'blue' :
                          node.qualitative_summary.assessment?.includes('中等') ? 'orange' : 'red'
                        }>
                          {node.qualitative_summary.assessment || '未知'}
                        </Tag>
                      </p>
                      <p style={{ margin: '4px 0' }}>
                        <strong>紧急程度:</strong> 
                        <Tag color={
                          node.qualitative_summary.severity === '低' ? 'green' :
                          node.qualitative_summary.severity === '中' ? 'orange' : 'red'
                        }>
                          {node.qualitative_summary.severity || '未知'}
                        </Tag>
                      </p>
                      {node.qualitative_summary.issues_count > 0 && (
                        <p style={{ margin: '4px 0', color: '#ff4d4f' }}>
                          <strong>关键问题:</strong> {node.qualitative_summary.issues_count} 个
                        </p>
                      )}
                      {node.qualitative_summary.focus_areas && node.qualitative_summary.focus_areas.length > 0 && (
                        <p style={{ margin: '4px 0' }}>
                          <strong>重点关注:</strong> {node.qualitative_summary.focus_areas.slice(0, 2).join(', ')}
                          {node.qualitative_summary.focus_areas.length > 2 && ' ...'}
                        </p>
                      )}
                    </div>
                  </div>
                )}
                
                {node.text_length && (
                  <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                    压缩后文本: {node.text_length} 字符
                  </div>
                )}
                
                {node.decision && (
                  <div style={{ fontSize: 12, color: '#1890ff', marginTop: 4 }}>
                    决策: {node.decision.reason}
                  </div>
                )}
                
                {node.quality_score && (
                  <div style={{ fontSize: 12, color: '#52c41a', marginTop: 4 }}>
                    质量评分: {node.quality_score.total_score?.toFixed(1)}/100
                  </div>
                )}
                
                {node.retry_count !== undefined && node.retry_count > 0 && (
                  <div style={{ fontSize: 12, color: '#faad14', marginTop: 4 }}>
                    重试次数: {node.retry_count}
                  </div>
                )}
                
                {node.error && (
                  <div style={{ 
                    fontSize: 13, 
                    marginTop: 12,
                    padding: '12px 16px',
                    background: '#fff1f0',
                    border: '1px solid #ffccc7',
                    borderRadius: 6
                  }}>
                    <div style={{ fontWeight: 'bold', marginBottom: 6, color: '#cf1322' }}>
                      ❌ 错误信息:
                    </div>
                    <div style={{ 
                      color: '#ff4d4f',
                      wordBreak: 'break-word',
                      whiteSpace: 'pre-wrap',
                      lineHeight: '1.6',
                      fontFamily: 'Consolas, Monaco, monospace',
                      fontSize: 12,
                      background: '#fff',
                      padding: '8px 12px',
                      borderRadius: 4
                    }}>
                      {node.error}
                    </div>
                  </div>
                )}
              </Timeline.Item>
              );
            })}
          </Timeline>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            暂无执行轨迹数据
          </div>
        )}
      </Card>

      {/* 元数据信息 - 优化布局 */}
      {workflowData?.workflow_metadata && (
        <Card 
          title="📋 工作流元数据" 
          style={{ marginTop: 16 }}
          bodyStyle={{ padding: '16px 24px' }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <div style={{ 
                padding: '16px', 
                background: '#fafafa', 
                borderRadius: 8,
                textAlign: 'center',
                border: '1px solid #f0f0f0'
              }}>
                <div style={{ fontSize: 12, color: '#999', marginBottom: 8 }}>总重试次数</div>
                <div style={{ fontSize: 28, fontWeight: 'bold', color: '#1890ff' }}>
                  {workflowData.workflow_metadata.retry_count || 0}
                </div>
              </div>
            </Col>
            <Col span={8}>
              <div style={{ 
                padding: '16px', 
                background: '#fafafa', 
                borderRadius: 8,
                border: '1px solid #f0f0f0'
              }}>
                <div style={{ fontSize: 12, color: '#999', marginBottom: 8 }}>开始时间</div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>
                  {workflowData.workflow_metadata.start_time ? 
                    new Date(workflowData.workflow_metadata.start_time).toLocaleString('zh-CN', {
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit'
                    }) : '-'}
                </div>
              </div>
            </Col>
            <Col span={8}>
              <div style={{ 
                padding: '16px', 
                background: '#fafafa', 
                borderRadius: 8,
                border: '1px solid #f0f0f0'
              }}>
                <div style={{ fontSize: 12, color: '#999', marginBottom: 8 }}>结束时间</div>
                <div style={{ fontSize: 14, fontWeight: 500, color: '#333' }}>
                  {workflowData.workflow_metadata.end_time ? 
                    new Date(workflowData.workflow_metadata.end_time).toLocaleString('zh-CN', {
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit'
                    }) : '-'}
                </div>
              </div>
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
};

export default WorkflowVisualization;
