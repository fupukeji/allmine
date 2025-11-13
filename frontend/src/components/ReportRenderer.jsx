import React from 'react';
import { Card, Typography, Divider, Row, Col, Table, Tag, Progress } from 'antd';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  PieChart, Pie, Cell, BarChart, Bar, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, LineChart, Line
} from 'recharts';

const { Title, Paragraph, Text } = Typography;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

/**
 * 增强的AI报告渲染器
 * 支持结构化展示、表格、图表和Markdown格式
 */
const ReportRenderer = ({ content }) => {
  if (!content) {
    return <Text type="secondary">暂无报告内容</Text>;
  }

  // 处理新的Markdown+图表数据格式
  if (content.report_type === 'markdown' && typeof content.content === 'string') {
    const markdownContent = content.content;
    const chartData = content.chart_data;
    
    // 调试信息
    console.log('[ReportRenderer] Markdown模式');
    console.log('[ReportRenderer] 图表数据:', chartData);
    console.log('[ReportRenderer] 图表类型:', chartData ? Object.keys(chartData) : '无');
    
    return (
      <div style={{ 
        padding: '24px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        minHeight: '400px'
      }}>
        {/* Markdown内容 */}
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            // 自定义样式
            h1: ({node, ...props}) => <Title level={1} {...props} style={{ marginTop: 24, marginBottom: 16 }} />,
            h2: ({node, ...props}) => <Title level={2} {...props} style={{ marginTop: 20, marginBottom: 12, borderBottom: '2px solid #f0f0f0', paddingBottom: 8 }} />,
            h3: ({node, ...props}) => <Title level={3} {...props} style={{ marginTop: 16, marginBottom: 8 }} />,
            h4: ({node, ...props}) => <Title level={4} {...props} style={{ marginTop: 12, marginBottom: 6 }} />,
            p: ({node, ...props}) => <Paragraph {...props} style={{ fontSize: 15, lineHeight: 1.8, marginBottom: 16 }} />,
            ul: ({node, ...props}) => <ul {...props} style={{ marginLeft: 24, marginBottom: 16 }} />,
            ol: ({node, ...props}) => <ol {...props} style={{ marginLeft: 24, marginBottom: 16 }} />,
            li: ({node, ...props}) => <li {...props} style={{ marginBottom: 8, fontSize: 14, lineHeight: 1.6 }} />,
            blockquote: ({node, ...props}) => (
              <div {...props} style={{ 
                borderLeft: '4px solid #1890ff',
                paddingLeft: 16,
                marginLeft: 0,
                marginBottom: 16,
                backgroundColor: '#f0f5ff',
                padding: 12,
                borderRadius: 4
              }} />
            ),
            table: ({node, ...props}) => (
              <Table 
                {...props} 
                style={{ marginBottom: 16 }}
                size="small"
                bordered
              />
            ),
            hr: ({node, ...props}) => <Divider {...props} style={{ margin: '24px 0' }} />,
            code: ({node, inline, ...props}) => (
              inline ? 
                <code {...props} style={{ 
                  backgroundColor: '#f5f5f5',
                  padding: '2px 6px',
                  borderRadius: 3,
                  fontSize: 13,
                  fontFamily: 'Monaco, Consolas, monospace'
                }} /> :
                <pre {...props} style={{ 
                  backgroundColor: '#f5f5f5',
                  padding: 16,
                  borderRadius: 4,
                  overflow: 'auto',
                  fontSize: 13,
                  fontFamily: 'Monaco, Consolas, monospace'
                }} />
            ),
          }}
        >
          {markdownContent}
        </ReactMarkdown>
        
        {/* 图表区域 */}
        {chartData && (
          <>
            <Divider style={{ margin: '32px 0' }}>📊 数据可视化</Divider>
            
            {/* 第一行: 资产配置 + 健康评分 */}
            <Row gutter={16}>
              <Col span={12}>
                {chartData.asset_allocation_pie && chartData.asset_allocation_pie.length > 0 && (
                  <Card title="🧩 资产配置分布" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={chartData.asset_allocation_pie}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {chartData.asset_allocation_pie.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </Card>
                )}
              </Col>
              <Col span={12}>
                {chartData.health_score_radar && chartData.health_score_radar.length > 0 && (
                  <Card title="🏥 健康评分雷达图" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <RadarChart data={chartData.health_score_radar}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="dimension" />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar name="得分" dataKey="score" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                        <Tooltip />
                        <Legend />
                      </RadarChart>
                    </ResponsiveContainer>
                  </Card>
                )}
              </Col>
            </Row>

            {/* 第二行: 趋势图表(如果有对比数据) */}
            {chartData.asset_value_trend && chartData.asset_value_trend.length > 0 && (
              <Row gutter={16}>
                <Col span={12}>
                  <Card title="📈 资产价值趋势" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={chartData.asset_value_trend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="period" />
                        <YAxis />
                        <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
                        <Legend />
                        <Line type="monotone" dataKey="固定资产" stroke="#8884d8" strokeWidth={2} />
                        <Line type="monotone" dataKey="虚拟资产" stroke="#82ca9d" strokeWidth={2} />
                        <Line type="monotone" dataKey="总资产" stroke="#ffc658" strokeWidth={3} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col span={12}>
                  {chartData.utilization_comparison && (
                    <Card title="⚡ 利用率对比" style={{ marginBottom: 16 }}>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData.utilization_comparison}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period" />
                          <YAxis />
                          <Tooltip formatter={(value) => `${value}%`} />
                          <Legend />
                          <Bar dataKey="利用率" fill="#52c41a" />
                          <Bar dataKey="浪费率" fill="#ff4d4f" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Card>
                  )}
                </Col>
              </Row>
            )}

            {/* 第三行: 固定资产分析 */}
            <Row gutter={16}>
              <Col span={12}>
                {chartData.fixed_asset_categories && chartData.fixed_asset_categories.length > 0 && (
                  <Card title="🏠 固定资产分类分布" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={chartData.fixed_asset_categories}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category" />
                        <YAxis />
                        <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
                        <Legend />
                        <Bar dataKey="value" fill="#1890ff" name="当前价值" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                )}
              </Col>
              <Col span={12}>
                {chartData.fixed_asset_status_pie && chartData.fixed_asset_status_pie.length > 0 && (
                  <Card title="📊 固定资产状态分布" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={chartData.fixed_asset_status_pie}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}项`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {chartData.fixed_asset_status_pie.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </Card>
                )}
              </Col>
            </Row>

            {/* 第四行: 虚拟资产分析 */}
            <Row gutter={16}>
              <Col span={12}>
                {chartData.virtual_asset_status && chartData.virtual_asset_status.length > 0 && (
                  <Card title="💎 虚拟资产状态分布" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={chartData.virtual_asset_status}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}个`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {chartData.virtual_asset_status.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </Card>
                )}
              </Col>
              <Col span={12}>
                {chartData.virtual_asset_utilization && chartData.virtual_asset_utilization.length > 0 && (
                  <Card title="📊 虚拟资产利用率分析" style={{ marginBottom: 16 }}>
                    <Table 
                      dataSource={chartData.virtual_asset_utilization} 
                      columns={[
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
                      ]}
                      pagination={false}
                      size="small"
                      rowKey="category"
                    />
                  </Card>
                )}
              </Col>
            </Row>

            {/* 第五行: 收入分析 */}
            {chartData.income_structure_pie && chartData.income_structure_pie.length > 0 && (
              <Row gutter={16}>
                <Col span={12}>
                  <Card title="💵 收入结构分布" style={{ marginBottom: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={chartData.income_structure_pie}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ source, percent }) => `${source}: ${(percent * 100).toFixed(1)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="amount"
                          nameKey="source"
                        >
                          {chartData.income_structure_pie.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col span={12}>
                  {chartData.income_comparison && (
                    <Card title="💰 收入对比" style={{ marginBottom: 16 }}>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData.income_comparison}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="period" />
                          <YAxis />
                          <Tooltip formatter={(value) => `¥${value.toLocaleString()}`} />
                          <Legend />
                          <Bar dataKey="income" fill="#52c41a" name="收入" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Card>
                  )}
                </Col>
              </Row>
            )}
          </>
        )}
      </div>
    );
  }
  
  // 兼容旧的纯字符串Markdown格式
  if (typeof content === 'string') {
    return (
      <div style={{ 
        padding: '24px',
        backgroundColor: '#fff',
        borderRadius: '8px',
        minHeight: '400px'
      }}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            // 自定义样式
            h1: ({node, ...props}) => <Title level={1} {...props} style={{ marginTop: 24, marginBottom: 16 }} />,
            h2: ({node, ...props}) => <Title level={2} {...props} style={{ marginTop: 20, marginBottom: 12, borderBottom: '2px solid #f0f0f0', paddingBottom: 8 }} />,
            h3: ({node, ...props}) => <Title level={3} {...props} style={{ marginTop: 16, marginBottom: 8 }} />,
            h4: ({node, ...props}) => <Title level={4} {...props} style={{ marginTop: 12, marginBottom: 6 }} />,
            p: ({node, ...props}) => <Paragraph {...props} style={{ fontSize: 15, lineHeight: 1.8, marginBottom: 16 }} />,
            ul: ({node, ...props}) => <ul {...props} style={{ marginLeft: 24, marginBottom: 16 }} />,
            ol: ({node, ...props}) => <ol {...props} style={{ marginLeft: 24, marginBottom: 16 }} />,
            li: ({node, ...props}) => <li {...props} style={{ marginBottom: 8, fontSize: 14, lineHeight: 1.6 }} />,
            blockquote: ({node, ...props}) => (
              <div {...props} style={{ 
                borderLeft: '4px solid #1890ff',
                paddingLeft: 16,
                marginLeft: 0,
                marginBottom: 16,
                backgroundColor: '#f0f5ff',
                padding: 12,
                borderRadius: 4
              }} />
            ),
            table: ({node, ...props}) => (
              <Table 
                {...props} 
                style={{ marginBottom: 16 }}
                size="small"
                bordered
              />
            ),
            hr: ({node, ...props}) => <Divider {...props} style={{ margin: '24px 0' }} />,
            code: ({node, inline, ...props}) => (
              inline ? 
                <code {...props} style={{ 
                  backgroundColor: '#f5f5f5',
                  padding: '2px 6px',
                  borderRadius: 3,
                  fontSize: 13,
                  fontFamily: 'Monaco, Consolas, monospace'
                }} /> :
                <pre {...props} style={{ 
                  backgroundColor: '#f5f5f5',
                  padding: 16,
                  borderRadius: 4,
                  overflow: 'auto',
                  fontSize: 13,
                  fontFamily: 'Monaco, Consolas, monospace'
                }} />
            ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  }

  // 渲染Markdown文本（简化版，支持加粗）
  const renderMarkdown = (text) => {
    if (!text) return null;
    
    // 确保是字符串类型
    const textStr = typeof text === 'object' ? JSON.stringify(text, null, 2) : String(text);
    
    // 简单处理加粗
    const parts = textStr.split(/(\*\*.*?\*\*)/g);
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
      {/* 执行摘要 - 周报/月报 */}
      {content.executive_summary && (
        <Card title="📋 执行摘要" style={{ marginBottom: 16 }}>
          {/* 如果executive_summary是对象，提取content字段 */}
          {typeof content.executive_summary === 'object' && content.executive_summary.content ? (
            <>
              {content.executive_summary.highlight && (
                <div style={{ 
                  padding: '12px 16px', 
                  backgroundColor: '#fff1f0', 
                  borderLeft: '4px solid #ff4d4f',
                  marginBottom: 16,
                  borderRadius: 4
                }}>
                  <Text strong style={{ fontSize: 15, color: '#cf1322' }}>
                    {content.executive_summary.highlight}
                  </Text>
                </div>
              )}
              <Paragraph style={{ fontSize: 15, lineHeight: 1.8 }}>
                {renderMarkdown(content.executive_summary.content)}
              </Paragraph>
            </>
          ) : (
            <Paragraph style={{ fontSize: 15, lineHeight: 1.8 }}>
              {renderMarkdown(content.executive_summary)}
            </Paragraph>
          )}
        </Card>
      )}
      
      {/* 时间段总结 - 自定义报告/年报 */}
      {content.period_summary && !content.executive_summary && (
        <Card title="📋 时间段总结" style={{ marginBottom: 16 }}>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.8 }}>
            {renderMarkdown(content.period_summary)}
          </Paragraph>
        </Card>
      )}

      {/* 关键结论 - 周报/月报 */}
      {content.key_conclusions && content.key_conclusions.length > 0 && (
        <Card title="💡 关键结论" style={{ marginBottom: 16 }}>
          {content.key_conclusions.map((conclusion, index) => {
            // 如果是对象格式（新结构）
            if (typeof conclusion === 'object' && conclusion.title) {
              const typeColor = 
                conclusion.type === 'critical' ? '#ff4d4f' :
                conclusion.type === 'warning' ? '#fa8c16' :
                conclusion.type === 'opportunity' ? '#52c41a' : '#1890ff';
              
              return (
                <div key={index} style={{ 
                  marginBottom: 16, 
                  padding: 16,
                  backgroundColor: conclusion.type === 'critical' ? '#fff1f0' : 
                                   conclusion.type === 'warning' ? '#fff7e6' : '#f6ffed',
                  borderLeft: `4px solid ${typeColor}`,
                  borderRadius: 4
                }}>
                  <Title level={5} style={{ color: typeColor, marginTop: 0 }}>
                    {conclusion.title}
                  </Title>
                  <Paragraph style={{ fontSize: 14, marginBottom: 8 }}>
                    {renderMarkdown(conclusion.content)}
                  </Paragraph>
                  {conclusion.action && (
                    <Paragraph style={{ fontSize: 14, color: '#595959', marginBottom: 0 }}>
                      <strong>建议行动：</strong>{renderMarkdown(conclusion.action)}
                    </Paragraph>
                  )}
                </div>
              );
            }
            // 兼容旧格式（字符串）
            return (
              <li key={index} style={{ marginBottom: 12, fontSize: 14 }}>
                {renderMarkdown(conclusion)}
              </li>
            );
          })}
        </Card>
      )}

      {/* 关键洞察 - 兼容旧版本 */}
      {content.key_insights && content.key_insights.length > 0 && !content.key_conclusions && (
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
      
      {/* 关键发现 - 自定义报告/年报 */}
      {content.key_findings && content.key_findings.length > 0 && (
        <Card title="💡 关键发现" style={{ marginBottom: 16 }}>
          <ul style={{ marginLeft: 20 }}>
            {content.key_findings.map((finding, index) => (
              <li key={index} style={{ marginBottom: 12, fontSize: 14 }}>
                {renderMarkdown(finding)}
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
          {typeof content.fixed_asset_analysis === 'string' ? (
            <Paragraph style={{ fontSize: 14 }}>{renderMarkdown(content.fixed_asset_analysis)}</Paragraph>
          ) : (
            <>
              {/* summary */}
              {content.fixed_asset_analysis.summary && (
                <Paragraph style={{ fontSize: 15, fontWeight: 500, marginBottom: 16, color: '#1890ff' }}>
                  {renderMarkdown(content.fixed_asset_analysis.summary)}
                </Paragraph>
              )}
              
              {/* health_status */}
              {content.fixed_asset_analysis.health_status && (
                <div style={{ marginBottom: 16, padding: 12, backgroundColor: '#f0f5ff', borderRadius: 4 }}>
                  <Text strong>健康状态：</Text>
                  <Tag color="blue" style={{ marginLeft: 8 }}>
                    {content.fixed_asset_analysis.health_status.rating} ({content.fixed_asset_analysis.health_status.score}分)
                  </Tag>
                  <Tag color="green">
                    {content.fixed_asset_analysis.health_status.trend}
                  </Tag>
                </div>
              )}
              
              {/* category_breakdown */}
              {content.fixed_asset_analysis.category_breakdown && content.fixed_asset_analysis.category_breakdown.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <Title level={5}>分类明细</Title>
                  {content.fixed_asset_analysis.category_breakdown.map((cat, idx) => (
                    <div key={idx} style={{ marginBottom: 12, padding: 12, backgroundColor: '#fafafa', borderRadius: 4 }}>
                      <Text strong>{cat.name || cat.category}</Text>
                      <div style={{ marginTop: 8 }}>
                        {renderMarkdown(typeof cat.insight === 'string' ? cat.insight : JSON.stringify(cat, null, 2))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* key_insights */}
              {content.fixed_asset_analysis.key_insights && content.fixed_asset_analysis.key_insights.length > 0 && (
                <div>
                  <Title level={5}>关键洞察</Title>
                  <ul style={{ marginLeft: 20 }}>
                    {content.fixed_asset_analysis.key_insights.map((insight, idx) => (
                      <li key={idx} style={{ marginBottom: 8, fontSize: 14 }}>
                        {renderMarkdown(insight)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* 兼容旧格式 */}
              {!content.fixed_asset_analysis.summary && 
               !content.fixed_asset_analysis.key_insights &&
               Object.keys(content.fixed_asset_analysis).length > 0 && (
                Object.entries(content.fixed_asset_analysis).map(([key, value]) => (
                  <div key={key} style={{ marginBottom: 16 }}>
                    <Title level={5}>
                      {key === 'overall_health' ? '整体健康度' :
                       key === 'value_trends' ? '价值趋势' :
                       key === 'depreciation_analysis' ? '折旧分析' :
                       key === 'category_insights' ? '分类洞察' :
                       key === 'usage_efficiency' ? '使用效率' :
                       key === 'usage_effectiveness' ? '使用效果' : key}
                    </Title>
                    <Paragraph style={{ fontSize: 14 }}>{renderMarkdown(typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value))}</Paragraph>
                  </div>
                ))
              )}
            </>
          )}
        </Card>
      )}

      {/* 虚拟资产分析 */}
      {content.virtual_asset_analysis && (
        <Card title="💎 虚拟资产分析" style={{ marginTop: 16 }}>
          {typeof content.virtual_asset_analysis === 'string' ? (
            <Paragraph style={{ fontSize: 14 }}>{renderMarkdown(content.virtual_asset_analysis)}</Paragraph>
          ) : (
            <>
              {/* summary */}
              {content.virtual_asset_analysis.summary && (
                <Paragraph style={{ fontSize: 15, fontWeight: 500, marginBottom: 16, color: '#52c41a' }}>
                  {renderMarkdown(content.virtual_asset_analysis.summary)}
                </Paragraph>
              )}
              
              {/* utilization_details / efficiency_status */}
              {(content.virtual_asset_analysis.utilization_details || content.virtual_asset_analysis.efficiency_status) && (
                <div style={{ marginBottom: 16, padding: 12, backgroundColor: '#f6ffed', borderRadius: 4 }}>
                  <Text strong>利用情况：</Text>
                  {content.virtual_asset_analysis.utilization_details && (
                    <div style={{ marginTop: 8 }}>
                      {renderMarkdown(JSON.stringify(content.virtual_asset_analysis.utilization_details, null, 2))}
                    </div>
                  )}
                  {content.virtual_asset_analysis.efficiency_status && (
                    <div style={{ marginTop: 8 }}>
                      <Tag color="green">
                        利用率: {content.virtual_asset_analysis.efficiency_status.utilization_rate}%
                      </Tag>
                      <Tag color="orange">
                        浪费率: {content.virtual_asset_analysis.efficiency_status.waste_rate}%
                      </Tag>
                      <Tag>
                        {content.virtual_asset_analysis.efficiency_status.rating}
                      </Tag>
                    </div>
                  )}
                </div>
              )}
              
              {/* category_breakdown */}
              {content.virtual_asset_analysis.category_breakdown && content.virtual_asset_analysis.category_breakdown.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <Title level={5}>分类明细</Title>
                  {content.virtual_asset_analysis.category_breakdown.map((cat, idx) => (
                    <div key={idx} style={{ marginBottom: 12, padding: 12, backgroundColor: '#fafafa', borderRadius: 4 }}>
                      <Text strong>{cat.name || cat.category}</Text>
                      <div style={{ marginTop: 8 }}>
                        {renderMarkdown(typeof cat.insight === 'string' ? cat.insight : JSON.stringify(cat, null, 2))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* expiring_alerts */}
              {content.virtual_asset_analysis.expiring_alerts && content.virtual_asset_analysis.expiring_alerts.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <Title level={5}>⚠️ 过期预警</Title>
                  {content.virtual_asset_analysis.expiring_alerts.map((alert, idx) => (
                    <div key={idx} style={{ 
                      marginBottom: 8, 
                      padding: 12, 
                      backgroundColor: '#fff7e6', 
                      borderLeft: '3px solid #fa8c16',
                      borderRadius: 4
                    }}>
                      {renderMarkdown(typeof alert === 'object' ? JSON.stringify(alert, null, 2) : alert)}
                    </div>
                  ))}
                </div>
              )}
              
              {/* key_insights */}
              {content.virtual_asset_analysis.key_insights && content.virtual_asset_analysis.key_insights.length > 0 && (
                <div>
                  <Title level={5}>关键洞察</Title>
                  <ul style={{ marginLeft: 20 }}>
                    {content.virtual_asset_analysis.key_insights.map((insight, idx) => (
                      <li key={idx} style={{ marginBottom: 8, fontSize: 14 }}>
                        {renderMarkdown(insight)}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* 兼容旧格式 */}
              {!content.virtual_asset_analysis.summary && 
               !content.virtual_asset_analysis.key_insights &&
               Object.keys(content.virtual_asset_analysis).length > 0 && (
                Object.entries(content.virtual_asset_analysis).map(([key, value]) => (
                  <div key={key} style={{ marginBottom: 16 }}>
                    <Title level={5}>
                      {key === 'usage_status' ? '使用状况' :
                       key === 'waste_assessment' ? '浪费评估' :
                       key === 'category_insights' ? '分类洞察' :
                       key === 'expiring_alerts' ? '过期预警' :
                       key === 'roi_analysis' ? 'ROI分析' :
                       key === 'usage_effectiveness' ? '使用效果' :
                       key === 'waste_analysis' ? '浪费分析' : key}
                    </Title>
                    <Paragraph style={{ fontSize: 14 }}>{renderMarkdown(typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value))}</Paragraph>
                  </div>
                ))
              )}
            </>
          )}
        </Card>
      )}
      
      {/* 综合洞察 - 自定义报告/年报 */}
      {content.comprehensive_insights && (
        <Card title="🔍 综合洞察" style={{ marginTop: 16 }}>
          <Paragraph style={{ fontSize: 14, lineHeight: 1.8 }}>
            {renderMarkdown(content.comprehensive_insights)}
          </Paragraph>
        </Card>
      )}
      
      {/* 趋势分析 - 自定义报告/年报 */}
      {content.trends && (
        <Card title="📈 趋势分析" style={{ marginTop: 16 }}>
          <Paragraph style={{ fontSize: 14, lineHeight: 1.8 }}>
            {renderMarkdown(content.trends)}
          </Paragraph>
        </Card>
      )}
      
      {/* 收入分析 - 自定义报告/年报 */}
      {content.income_analysis && typeof content.income_analysis === 'string' && (
        <Card title="💰 收入分析" style={{ marginTop: 16 }}>
          <Paragraph style={{ fontSize: 14, lineHeight: 1.8 }}>
            {renderMarkdown(content.income_analysis)}
          </Paragraph>
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
          {content.actionable_recommendations.map((rec, index) => {
            // 如果是对象格式（新结构）
            if (typeof rec === 'object' && rec.title) {
              const priorityColor = 
                rec.priority === '高' ? '#ff4d4f' :
                rec.priority === '中' ? '#fa8c16' : '#52c41a';
              
              return (
                <div key={index} style={{ 
                  marginBottom: 16, 
                  padding: 16,
                  backgroundColor: '#fafafa',
                  borderLeft: `4px solid ${priorityColor}`,
                  borderRadius: 4
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Title level={5} style={{ margin: 0 }}>
                      {rec.title}
                    </Title>
                    <Tag color={priorityColor}>{rec.priority}优先级</Tag>
                  </div>
                  {rec.category && <Text type="secondary">分类：{rec.category}</Text>}
                  {rec.problem && (
                    <Paragraph style={{ marginTop: 8, marginBottom: 8 }}>
                      <strong>问题：</strong>{renderMarkdown(rec.problem)}
                    </Paragraph>
                  )}
                  {rec.solution && (
                    <Paragraph style={{ marginBottom: 8 }}>
                      <strong>解决方案：</strong>{renderMarkdown(rec.solution)}
                    </Paragraph>
                  )}
                  {rec.timeline && (
                    <Text style={{ fontSize: 12, color: '#595959' }}>
                      ⛰️ 时间表：{rec.timeline}
                    </Text>
                  )}
                  {rec.expected_result && (
                    <Paragraph style={{ marginTop: 8, color: '#52c41a', marginBottom: 0 }}>
                      <strong>🎯 预期效果：</strong>{renderMarkdown(rec.expected_result)}
                    </Paragraph>
                  )}
                </div>
              );
            }
            // 兼容旧格式（字符串）
            return (
              <li key={index} style={{ marginBottom: 16, fontSize: 14 }}>
                {renderMarkdown(rec)}
              </li>
            );
          })}
        </Card>
      )}
      
      {/* 风险评估 - 自定义报告/年报 */}
      {content.risk_assessment && (
        <Card title="⚠️ 风险评估" style={{ marginTop: 16 }} styles={{ header: { backgroundColor: '#fff1f0' } }}>
          {content.risk_assessment.risk_level && (
            <Paragraph style={{ fontSize: 14 }}>
              <strong>风险等级：</strong>
              <Tag color={content.risk_assessment.risk_level === 'high' ? 'red' : content.risk_assessment.risk_level === 'medium' ? 'orange' : 'green'}>
                {content.risk_assessment.risk_level === 'high' ? '高' : content.risk_assessment.risk_level === 'medium' ? '中' : '低'}
              </Tag>
            </Paragraph>
          )}
          {content.risk_assessment.key_risks && content.risk_assessment.key_risks.length > 0 && (
            <div>
              <Title level={5}>关键风险：</Title>
              <ul style={{ marginLeft: 20 }}>
                {content.risk_assessment.key_risks.map((risk, index) => (
                  <li key={index} style={{ marginBottom: 8, fontSize: 14, color: '#ff4d4f' }}>
                    {renderMarkdown(risk)}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {content.risk_assessment.opportunities && content.risk_assessment.opportunities.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Title level={5}>机会点：</Title>
              <ul style={{ marginLeft: 20 }}>
                {content.risk_assessment.opportunities.map((opp, index) => (
                  <li key={index} style={{ marginBottom: 8, fontSize: 14, color: '#52c41a' }}>
                    {renderMarkdown(opp)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      )}
      
      {/* 结论 - 自定义报告/年报 */}
      {content.conclusion && (
        <Card title="🎯 总结" style={{ marginTop: 16 }}>
          <Paragraph style={{ fontSize: 15, lineHeight: 1.8 }}>
            {renderMarkdown(content.conclusion)}
          </Paragraph>
        </Card>
      )}

      {/* 风险预警 */}
      {content.risk_alerts && content.risk_alerts.length > 0 && (
        <Card title="⚠️ 风险预警" style={{ marginTop: 16 }} styles={{ header: { backgroundColor: '#fff1f0' } }}>
          {content.risk_alerts.map((alert, index) => {
            // 如果是对象格式（新结构）
            if (typeof alert === 'object' && alert.risk_type) {
              const severityColor = 
                alert.severity === '高' ? '#ff4d4f' :
                alert.severity === '中' ? '#fa8c16' : '#faad14';
              const urgencyTag = 
                alert.urgency === '紧急' ? 'red' :
                alert.urgency === '重要' ? 'orange' : 'default';
              
              return (
                <div key={index} style={{ 
                  marginBottom: 16, 
                  padding: 16, 
                  backgroundColor: '#fff7e6', 
                  borderLeft: `4px solid ${severityColor}`,
                  borderRadius: 4
                }}>
                  <div style={{ marginBottom: 12 }}>
                    <Tag color={severityColor} style={{ marginRight: 8 }}>
                      {alert.severity}严重度
                    </Tag>
                    <Tag color={urgencyTag}>{alert.urgency}</Tag>
                    <Text strong style={{ marginLeft: 8, fontSize: 15 }}>
                      {alert.risk_type}
                    </Text>
                  </div>
                  {alert.description && (
                    <Paragraph style={{ marginBottom: 8 }}>
                      <strong>📌 风险描述：</strong>{renderMarkdown(alert.description)}
                    </Paragraph>
                  )}
                  {(alert.probability || alert.impact) && (
                    <div style={{ marginBottom: 8, padding: 8, backgroundColor: '#fff', borderRadius: 4 }}>
                      {alert.probability && <Text>🎲 发生概率：{alert.probability} </Text>}
                      {alert.impact && <Text style={{ marginLeft: 16 }}>💥 影响：{alert.impact}</Text>}
                    </div>
                  )}
                  {alert.trigger_conditions && (
                    <Paragraph style={{ fontSize: 12, color: '#cf1322', marginBottom: 8 }}>
                      ⚡ 触发条件：{alert.trigger_conditions}
                    </Paragraph>
                  )}
                  {alert.mitigation && (
                    <Paragraph style={{ marginBottom: 0, color: '#52c41a' }}>
                      <strong>🛡️ 缓解措施：</strong>{renderMarkdown(alert.mitigation)}
                    </Paragraph>
                  )}
                </div>
              );
            }
            // 兼容旧格式（字符串）
            return (
              <div key={index} style={{ marginBottom: 12, padding: 12, backgroundColor: '#fff7e6', borderLeft: '3px solid #fa8c16' }}>
                <Text style={{ fontSize: 14 }}>{renderMarkdown(alert)}</Text>
              </div>
            );
          })}
        </Card>
      )}

      {/* 下周重点/下期重点 */}
      {(content.next_week_focus || content.next_period_focus) && (
        <Card title="🎯 下期重点关注" style={{ marginTop: 16 }}>
          {(content.next_period_focus || content.next_week_focus).map((focus, index) => {
            // 如果是对象格式（新结构）
            if (typeof focus === 'object' && focus.task) {
              const priorityColor = 
                focus.priority === '高' ? '#ff4d4f' :
                focus.priority === '中' ? '#fa8c16' : '#52c41a';
              
              return (
                <div key={index} style={{ 
                  marginBottom: 16, 
                  padding: 16,
                  backgroundColor: '#f0f5ff',
                  borderLeft: `4px solid ${priorityColor}`,
                  borderRadius: 4
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Title level={5} style={{ margin: 0 }}>
                      {focus.task}
                    </Title>
                    {focus.priority && <Tag color={priorityColor}>{focus.priority}</Tag>}
                  </div>
                  {focus.target && (
                    <Paragraph style={{ marginBottom: 8 }}>
                      <strong>🎯 目标：</strong>{renderMarkdown(focus.target)}
                    </Paragraph>
                  )}
                  {focus.deadline && (
                    <Text style={{ fontSize: 12, color: '#595959', marginRight: 16 }}>
                      ⏰ 期限：{focus.deadline}
                    </Text>
                  )}
                  {focus.expected_impact && (
                    <Paragraph style={{ marginTop: 8, color: '#1890ff', marginBottom: 0 }}>
                      <strong>💡 预期影响：</strong>{renderMarkdown(focus.expected_impact)}
                    </Paragraph>
                  )}
                  {focus.dependencies && (
                    <Paragraph style={{ fontSize: 12, color: '#8c8c8c', marginTop: 8, marginBottom: 0 }}>
                      🔗 前置条件：{focus.dependencies}
                    </Paragraph>
                  )}
                </div>
              );
            }
            // 兼容旧格式（字符串）
            return (
              <li key={index} style={{ marginBottom: 12, fontSize: 14 }}>
                {renderMarkdown(focus)}
              </li>
            );
          })}
        </Card>
      )}
    </div>
  );
};

export default ReportRenderer;
