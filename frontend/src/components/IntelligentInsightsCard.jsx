import React, { useState } from 'react';
import { Card, Row, Col, Progress, Tag, Statistic, Tooltip, Modal, Descriptions } from 'antd';
import { 
  HeartOutlined, 
  ThunderboltOutlined, 
  DollarOutlined, 
  BarChartOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';

const IntelligentInsightsCard = ({ insights }) => {
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState(null);

  if (!insights) return null;

  const getColor = (score) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    if (score >= 40) return '#ff7a45';
    return '#f5222d';
  };

  const getRating = (score) => {
    if (score >= 80) return { text: '优秀', color: 'success' };
    if (score >= 60) return { text: '良好', color: 'warning' };
    if (score >= 40) return { text: '需关注', color: 'error' };
    return { text: '紧急', color: 'error' };
  };

  const metrics = [
    {
      key: 'fixed_asset_health',
      title: '固定资产健康度',
      icon: <HeartOutlined />,
      value: insights.fixed_asset_health || 0,
      description: '综合评估固定资产的整体状况（折旧率、收入率、使用率）',
      tips: [
        '80-100分：资产保值好、收益高、利用充分',
        '60-79分：正常运营状态',
        '40-59分：折旧过快或收益偏低',
        '0-39分：严重贬值或大量闲置'
      ]
    },
    {
      key: 'virtual_asset_efficiency',
      title: '虚拟资产效率',
      icon: <ThunderboltOutlined />,
      value: insights.virtual_asset_efficiency || 0,
      description: '评估虚拟资产（会员、课程等）的利用效率',
      tips: [
        '80-100分：利用率>80%，浪费<10%',
        '60-79分：利用率60-80%',
        '40-59分：利用率<60%或浪费>20%',
        '0-39分：大量过期未使用'
      ]
    },
    {
      key: 'income_quality',
      title: '收入质量',
      icon: <DollarOutlined />,
      value: insights.income_quality || 0,
      description: '评估资产的收益能力（ROI）',
      tips: [
        '80-100分：ROI≥8%',
        '60-79分：ROI 6-8%',
        '40-59分：ROI 4-6%',
        '0-39分：ROI<4%'
      ]
    },
    {
      key: 'allocation_balance',
      title: '资产配置均衡度',
      icon: <BarChartOutlined />,
      value: insights.allocation_balance || 0,
      description: '评估固定资产与虚拟资产的配置合理性',
      tips: [
        '80-100分：接近理想比例（固定60-80%，虚拟20-40%）',
        '60-79分：轻微偏离理想配置',
        '40-59分：明显偏离',
        '0-39分：极端配置，严重失衡'
      ]
    }
  ];

  const showDetail = (metric) => {
    setSelectedMetric(metric);
    setDetailVisible(true);
  };

  return (
    <>
      <Card 
        title={
          <span>
            🧠 智能健康诊断
            <Tooltip title="基于多维度数据分析的资产健康评分">
              <InfoCircleOutlined style={{ marginLeft: 8, fontSize: 14, color: '#999' }} />
            </Tooltip>
          </span>
        }
        style={{ marginBottom: 24 }}
        styles={{ body: { padding: '24px' } }}
      >
        <Row gutter={[24, 24]}>
          {metrics.map((metric) => {
            const rating = getRating(metric.value);
            return (
              <Col xs={12} sm={12} md={6} key={metric.key}>
                <div 
                  style={{ textAlign: 'center', cursor: 'pointer' }}
                  onClick={() => showDetail(metric)}
                >
                  <Progress
                    type="circle"
                    percent={metric.value}
                    strokeColor={{
                      '0%': getColor(metric.value),
                      '100%': getColor(metric.value)
                    }}
                    format={(percent) => (
                      <div>
                        <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                          {percent?.toFixed(0)}
                        </div>
                        <div style={{ fontSize: 12, color: '#999' }}>分</div>
                      </div>
                    )}
                    width={120}
                  />
                  <div style={{ marginTop: 12 }}>
                    <div style={{ fontSize: 16, marginBottom: 4 }}>
                      {metric.icon} {metric.title}
                    </div>
                    <Tag color={rating.color}>{rating.text}</Tag>
                  </div>
                </div>
              </Col>
            );
          })}
        </Row>

        {/* 整体健康状态 */}
        <div style={{ 
          marginTop: 24, 
          padding: 16, 
          background: '#f0f5ff', 
          borderRadius: 8,
          borderLeft: '4px solid #1890ff'
        }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic 
                title="综合健康指数" 
                value={((insights.fixed_asset_health + insights.virtual_asset_efficiency + 
                         insights.income_quality + insights.allocation_balance) / 4).toFixed(1)}
                suffix="/ 100"
                valueStyle={{ color: getColor((insights.fixed_asset_health + insights.virtual_asset_efficiency + 
                                               insights.income_quality + insights.allocation_balance) / 4) }}
              />
            </Col>
            <Col span={18}>
              <div style={{ fontSize: 14, color: '#666', lineHeight: 1.8 }}>
                {insights.fixed_asset_health < 60 && (
                  <div>🔴 <strong>固定资产健康度偏低</strong>，建议关注折旧、收入和使用情况</div>
                )}
                {insights.virtual_asset_efficiency < 60 && (
                  <div>🔴 <strong>虚拟资产效率偏低</strong>，存在较高浪费，建议优化续费策略</div>
                )}
                {insights.income_quality < 60 && (
                  <div>🟡 <strong>收入质量有待提升</strong>，ROI偏低，建议调整资产结构</div>
                )}
                {insights.allocation_balance < 60 && (
                  <div>🟡 <strong>资产配置需优化</strong>，理想比例为固定60-80%，虚拟20-40%</div>
                )}
                {insights.fixed_asset_health >= 60 && insights.virtual_asset_efficiency >= 60 && 
                 insights.income_quality >= 60 && insights.allocation_balance >= 60 && (
                  <div>✅ <strong>整体健康状况良好</strong>，继续保持当前资产管理策略</div>
                )}
              </div>
            </Col>
          </Row>
        </div>
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title={selectedMetric?.title}
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={600}
      >
        {selectedMetric && (
          <div>
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Progress
                type="circle"
                percent={selectedMetric.value}
                strokeColor={{
                  '0%': getColor(selectedMetric.value),
                  '100%': getColor(selectedMetric.value)
                }}
                width={150}
              />
              <div style={{ marginTop: 16 }}>
                <Tag color={getRating(selectedMetric.value).color} style={{ fontSize: 16, padding: '4px 16px' }}>
                  {getRating(selectedMetric.value).text}
                </Tag>
              </div>
            </div>

            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="指标说明">
                {selectedMetric.description}
              </Descriptions.Item>
              <Descriptions.Item label="评分标准">
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {selectedMetric.tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </Descriptions.Item>
            </Descriptions>

            {selectedMetric.value < 60 && (
              <div style={{ 
                marginTop: 16, 
                padding: 12, 
                background: '#fff7e6', 
                border: '1px solid #ffd591',
                borderRadius: 4 
              }}>
                <strong>💡 优化建议：</strong>
                <div style={{ marginTop: 8 }}>
                  {selectedMetric.key === 'fixed_asset_health' && (
                    <>
                      • 检查折旧率是否过快（&gt;50%需关注）<br/>
                      • 评估收入是否足够（目标ROI≥8%）<br/>
                      • 激活闲置资产，提高使用率
                    </>
                  )}
                  {selectedMetric.key === 'virtual_asset_efficiency' && (
                    <>
                      • 分析哪个分类浪费最严重<br/>
                      • 停止重复购买，优选单一平台<br/>
                      • 设置过期提醒（建议7天前）
                    </>
                  )}
                  {selectedMetric.key === 'income_quality' && (
                    <>
                      • 评估当前ROI是否合理<br/>
                      • 优先投资高收益资产<br/>
                      • 处置低收益或零收益资产
                    </>
                  )}
                  {selectedMetric.key === 'allocation_balance' && (
                    <>
                      • 理想配置：固定资产60-80%，虚拟资产20-40%<br/>
                      • 固定资产过多：流动性不足<br/>
                      • 虚拟资产过多：稳定性欠缺
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </>
  );
};

export default IntelligentInsightsCard;
