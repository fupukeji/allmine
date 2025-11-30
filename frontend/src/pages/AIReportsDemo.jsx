import React, { useState } from 'react';
import { Card, Button, Space } from 'antd';
import IntelligentInsightsCard from '../components/IntelligentInsightsCard';
import CategoryHierarchyTree from '../components/CategoryHierarchyTree';

// 模拟数据用于演示
const mockInsights = {
  fixed_asset_health: 85.0,
  virtual_asset_efficiency: 72.5,
  income_quality: 65.0,
  allocation_balance: 92.0,
  category_hierarchy: [
    {
      id: 1,
      name: '投资',
      parent_id: null,
      level: 0,
      full_path: '投资',
      project_count: 15
    },
    {
      id: 2,
      name: '股票',
      parent_id: 1,
      level: 1,
      full_path: '投资 > 股票',
      project_count: 10
    },
    {
      id: 3,
      name: 'A股',
      parent_id: 2,
      level: 2,
      full_path: '投资 > 股票 > A股',
      project_count: 8
    },
    {
      id: 4,
      name: '港股',
      parent_id: 2,
      level: 2,
      full_path: '投资 > 股票 > 港股',
      project_count: 2
    },
    {
      id: 5,
      name: '基金',
      parent_id: 1,
      level: 1,
      full_path: '投资 > 基金',
      project_count: 5
    },
    {
      id: 6,
      name: '消费',
      parent_id: null,
      level: 0,
      full_path: '消费',
      project_count: 8
    },
    {
      id: 7,
      name: '会员',
      parent_id: 6,
      level: 1,
      full_path: '消费 > 会员',
      project_count: 6
    },
    {
      id: 8,
      name: '视频会员',
      parent_id: 7,
      level: 2,
      full_path: '消费 > 会员 > 视频会员',
      project_count: 4
    },
    {
      id: 9,
      name: '资产',
      parent_id: null,
      level: 0,
      full_path: '资产',
      project_count: 3
    },
    {
      id: 10,
      name: '房产',
      parent_id: 9,
      level: 1,
      full_path: '资产 > 房产',
      project_count: 3
    }
  ]
};

const mockInsightsLow = {
  fixed_asset_health: 45.0,
  virtual_asset_efficiency: 38.0,
  income_quality: 52.0,
  allocation_balance: 48.0,
  category_hierarchy: mockInsights.category_hierarchy
};

const AIReportsDemo = () => {
  const [currentInsights, setCurrentInsights] = useState(mockInsights);

  return (
    <div style={{ padding: 24 }}>
      <Card title="🎨 智能报告前端展示 - 演示页面" style={{ marginBottom: 24 }}>
        <Space>
          <Button 
            type="primary" 
            onClick={() => setCurrentInsights(mockInsights)}
          >
            查看优秀案例（健康度85分）
          </Button>
          <Button 
            onClick={() => setCurrentInsights(mockInsightsLow)}
          >
            查看问题案例（健康度45分）
          </Button>
        </Space>
      </Card>

      <IntelligentInsightsCard insights={currentInsights} />
      
      <CategoryHierarchyTree categoryHierarchy={currentInsights.category_hierarchy} />
    </div>
  );
};

export default AIReportsDemo;
