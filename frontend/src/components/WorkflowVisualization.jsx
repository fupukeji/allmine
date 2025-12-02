import React, { useState, useEffect } from 'react';
import { Card, Steps, Tag, Timeline, Spin, Alert } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  LoadingOutlined
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

  // 节点名称映射
  const nodeNameMap = {
    'init_task': '初始化任务',
    'collect_data': '数据采集',
    'compress_data': '数据压缩',
    'agent_decide_comparison': 'Agent决策',
    'query_previous_data': '查询上期数据',
    'ai_preanalysis': 'AI定性分析',  // 更新名称
    'generate_report': '生成报告',
    'evaluate_quality': '质量评估',
    'save_report': '保存报告',
    'handle_retry': '重试处理',
    'handle_failure': '失败处理'
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
      
      {/* 失败提示 */}
      {workflowData?.status === 'failed' && (
        <Alert
          message="报告生成失败"
          description="请查看下方执行轨迹了解失败原因"
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 执行进度条 */}
      <Card title="📊 工作流执行进度" style={{ marginBottom: 16 }}>
        <Steps current={currentStep} status={workflowData?.status === 'failed' ? 'error' : 'process'}>
          <Step title="初始化" description="准备任务" />
          <Step title="数据采集" description="收集资产数据" />
          <Step title="数据处理" description="压缩与分析" />
          <Step title="报告生成" description="AI生成报告" />
          <Step title="质量评估" description="评估报告质量" />
          <Step title="完成" description="保存报告" />
        </Steps>
      </Card>

      {/* 执行轨迹时间线 */}
      <Card title="🔍 执行轨迹详情">
        {executionPath.length > 0 ? (
          <Timeline>
            {executionPath.map((node, index) => (
              <Timeline.Item
                key={index}
                dot={getNodeStatusIcon(node)}
                color={node.status === 'completed' ? 'green' : 
                       node.status === 'failed' ? 'red' : 'blue'}
              >
                <div style={{ marginBottom: 8 }}>
                  <span style={{ fontWeight: 'bold' }}>
                    {nodeNameMap[node.node] || node.node}
                  </span>
                  <Tag
                    color={getNodeStatusColor(node)}
                    style={{ marginLeft: 8 }}
                  >
                    {node.status === 'completed' ? '已完成' :
                     node.status === 'failed' ? '失败' :
                     node.status === 'skipped' ? '跳过' : '执行中'}
                  </Tag>
                </div>
                
                {node.timestamp && (
                  <div style={{ fontSize: 12, color: '#666' }}>
                    执行时间: {formatTime(node.timestamp)}
                  </div>
                )}
                
                {/* 显示节点额外信息 */}
                {node.data_summary && (
                  <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                    固定资产: {node.data_summary.fixed_assets_count}项 | 
                    虚拟资产: {node.data_summary.virtual_assets_count}项
                  </div>
                )}
                
                {/* 【新增】定性分析结果展示 */}
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
                  <div style={{ fontSize: 12, color: '#ff4d4f', marginTop: 4 }}>
                    错误: {node.error}
                  </div>
                )}
              </Timeline.Item>
            ))}
          </Timeline>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            暂无执行轨迹数据
          </div>
        )}
      </Card>

      {/* 元数据信息 */}
      {workflowData?.workflow_metadata && (
        <Card title="📋 工作流元数据" style={{ marginTop: 16 }}>
          <div>
            <p><strong>总重试次数:</strong> {workflowData.workflow_metadata.retry_count || 0}</p>
            {workflowData.workflow_metadata.start_time && (
              <p><strong>开始时间:</strong> {new Date(workflowData.workflow_metadata.start_time).toLocaleString('zh-CN')}</p>
            )}
            {workflowData.workflow_metadata.end_time && (
              <p><strong>结束时间:</strong> {new Date(workflowData.workflow_metadata.end_time).toLocaleString('zh-CN')}</p>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default WorkflowVisualization;
