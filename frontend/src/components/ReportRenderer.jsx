import React from 'react';
import { Card, Typography, Divider, Row, Col, Table, Tag, Progress } from 'antd';
import {
  PieChart, Pie, Cell, BarChart, Bar, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const { Title, Paragraph, Text } = Typography;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

/**
 * 增强的AI报告渲染器
 * 支持结构化展示、表格、图表
 */
const ReportRenderer = ({ content }) => {
  if (!content) {
    return <Text type="secondary">暂无报告内容</Text>;
  }

  // 渲染Markdown文本（简化版，支持加粗）
  const renderMarkdown = (text) => {
    if (!text) return null;
    
    // 简单处理加粗
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return <span key={index}>{part}</span>;
    });
  };

  // 渲染健康评分雷达图
  const renderHealthScoreRadar = () => {
    if (!content.chart_data?.health_score_radar) return null;

    return (
      <Card title="健康评分雷达图" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={content.chart_data.health_score_radar}>
            <PolarGrid />
            <PolarAngleAxis dataKey="dimension" />
            <PolarRadiusAxis angle={90} domain={[0, 25]} />
            <Radar name="得分" dataKey="score" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </Card>
    );
  };

  // 渲染资产配置饼图
  const renderAssetAllocationPie = () => {
    if (!content.chart_data?.asset_allocation_pie) return null;

    return (
      <Card title="资产配置分布" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={content.chart_data.asset_allocation_pie}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {content.chart_data.asset_allocation_pie.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Card>
    );
  };

  // 渲染固定资产分类柱状图
  const renderFixedAssetCategories = () => {
    if (!content.chart_data?.fixed_asset_categories) return null;

    return (
      <Card title="固定资产分类分布" style={{ marginTop: 16 }}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={content.chart_data.fixed_asset_categories}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
            <Legend />
            <Bar dataKey="value" fill="#8884d8" name="资产价值" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    );
  };

  // 渲染虚拟资产利用率表格
  const renderVirtualAssetTable = () => {
    if (!content.chart_data?.virtual_asset_utilization) return null;

    const columns = [
      {
        title: '分类',
        dataIndex: 'category',
        key: 'category',
      },
      {
        title: '利用率',
        dataIndex: 'utilization',
        key: 'utilization',
        render: (val) => (
          <div>
            <Progress 
              percent={val} 
              status={val > 70 ? 'success' : val > 40 ? 'normal' : 'exception'}
              size="small"
            />
          </div>
        ),
      },
      {
        title: '浪费率',
        dataIndex: 'waste',
        key: 'waste',
        render: (val) => (
          <Tag color={val > 30 ? 'red' : val > 10 ? 'orange' : 'green'}>
            {val.toFixed(1)}%
          </Tag>
        ),
      },
    ];

    return (
      <Card title="虚拟资产利用率分析" style={{ marginTop: 16 }}>
        <Table 
          dataSource={content.chart_data.virtual_asset_utilization} 
          columns={columns}
          pagination={false}
          size="small"
          rowKey="category"
        />
      </Card>
    );
  };

  return (
    <div>
      {/* 执行摘要 */}
      {content.executive_summary && (
        <Card title="📋 执行摘要" style={{ marginBottom: 16 }}>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.8 }}>
            {renderMarkdown(content.executive_summary)}
          </Paragraph>
        </Card>
      )}

      {/* 关键洞察 */}
      {content.key_insights && content.key_insights.length > 0 && (
        <Card title="💡 关键洞察" style={{ marginBottom: 16 }}>
          <ul style={{ marginLeft: 20 }}>
            {content.key_insights.map((insight, index) => (
              <li key={index} style={{ marginBottom: 12, fontSize: 14 }}>
                {renderMarkdown(insight)}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* 图表区域 */}
      <Row gutter={16}>
        <Col span={12}>
          {renderAssetAllocationPie()}
        </Col>
        <Col span={12}>
          {renderHealthScoreRadar()}
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          {renderFixedAssetCategories()}
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          {renderVirtualAssetTable()}
        </Col>
      </Row>

      {/* 固定资产分析 */}
      {content.fixed_asset_analysis && (
        <Card title="🏠 固定资产分析" style={{ marginTop: 16 }}>
          {Object.entries(content.fixed_asset_analysis).map(([key, value]) => (
            <div key={key} style={{ marginBottom: 16 }}>
              <Title level={5}>
                {key === 'overall_health' ? '整体健康度' :
                 key === 'value_trends' ? '价值趋势' :
                 key === 'depreciation_analysis' ? '折旧分析' :
                 key === 'category_insights' ? '分类洞察' :
                 key === 'usage_efficiency' ? '使用效率' : key}
              </Title>
              <Paragraph style={{ fontSize: 14 }}>{renderMarkdown(value)}</Paragraph>
            </div>
          ))}
        </Card>
      )}

      {/* 虚拟资产分析 */}
      {content.virtual_asset_analysis && (
        <Card title="💎 虚拟资产分析" style={{ marginTop: 16 }}>
          {Object.entries(content.virtual_asset_analysis).map(([key, value]) => (
            <div key={key} style={{ marginBottom: 16 }}>
              <Title level={5}>
                {key === 'usage_status' ? '使用状况' :
                 key === 'waste_assessment' ? '浪费评估' :
                 key === 'category_insights' ? '分类洞察' :
                 key === 'expiring_alerts' ? '过期预警' :
                 key === 'roi_analysis' ? 'ROI分析' : key}
              </Title>
              <Paragraph style={{ fontSize: 14 }}>{renderMarkdown(value)}</Paragraph>
            </div>
          ))}
        </Card>
      )}

      {/* 健康评分 */}
      {content.health_score && (
        <Card title="📊 健康评分" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Card>
                <Paragraph style={{ textAlign: 'center', fontSize: 32, fontWeight: 'bold', color: '#1890ff', margin: 0 }}>
                  {content.health_score.overall_score}
                </Paragraph>
                <Paragraph style={{ textAlign: 'center', margin: 0 }}>综合得分</Paragraph>
              </Card>
            </Col>
            <Col span={18}>
              {content.health_score.score_breakdown && (
                <div>
                  {Object.entries(content.health_score.score_breakdown).map(([key, value]) => (
                    <Paragraph key={key} style={{ fontSize: 14 }}>
                      <strong>{key}:</strong> {renderMarkdown(value)}
                    </Paragraph>
                  ))}
                </div>
              )}
            </Col>
          </Row>
          {content.health_score.score_trend && (
            <Paragraph style={{ marginTop: 16, fontSize: 14 }}>
              <strong>评分趋势：</strong>{renderMarkdown(content.health_score.score_trend)}
            </Paragraph>
          )}
        </Card>
      )}

      {/* 可执行建议 */}
      {content.actionable_recommendations && content.actionable_recommendations.length > 0 && (
        <Card title="✅ 可执行建议" style={{ marginTop: 16 }}>
          <ul style={{ marginLeft: 20 }}>
            {content.actionable_recommendations.map((rec, index) => (
              <li key={index} style={{ marginBottom: 16, fontSize: 14 }}>
                {renderMarkdown(rec)}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* 风险预警 */}
      {content.risk_alerts && content.risk_alerts.length > 0 && (
        <Card title="⚠️ 风险预警" style={{ marginTop: 16 }} headStyle={{ backgroundColor: '#fff1f0' }}>
          {content.risk_alerts.map((alert, index) => (
            <div key={index} style={{ marginBottom: 12, padding: 12, backgroundColor: '#fff7e6', borderLeft: '3px solid #fa8c16' }}>
              <Text style={{ fontSize: 14 }}>{renderMarkdown(alert)}</Text>
            </div>
          ))}
        </Card>
      )}

      {/* 下周重点 */}
      {content.next_week_focus && content.next_week_focus.length > 0 && (
        <Card title="🎯 下周重点关注" style={{ marginTop: 16 }}>
          <ul style={{ marginLeft: 20 }}>
            {content.next_week_focus.map((focus, index) => (
              <li key={index} style={{ marginBottom: 12, fontSize: 14 }}>
                {renderMarkdown(focus)}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
};

export default ReportRenderer;
