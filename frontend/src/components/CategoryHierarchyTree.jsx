import React from 'react';
import { Card, Tree, Tag, Badge, Tooltip, Empty } from 'antd';
import { 
  FolderOutlined, 
  FolderOpenOutlined,
  FireOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';

const CategoryHierarchyTree = ({ categoryHierarchy }) => {
  if (!categoryHierarchy?.length) {
    return (
      <Card title="📂 分类层级结构">
        <Empty description="暂无分类数据" />
      </Card>
    );
  }

  // 构建树形结构
  const buildTree = (categories) => {
    const categoryMap = new Map();
    const roots = [];

    // 先创建所有节点
    categories.forEach(cat => {
      categoryMap.set(cat.id, {
        ...cat,
        children: []
      });
    });

    // 建立父子关系
    categories.forEach(cat => {
      const node = categoryMap.get(cat.id);
      if (cat.parent_id) {
        const parent = categoryMap.get(cat.parent_id);
        parent?.children.push(node);
      } else {
        roots.push(node);
      }
    });

    // 按project_count降序排序
    const sortByActivity = (nodes) => {
      nodes.sort((a, b) => b.project_count - a.project_count);
      nodes.forEach(node => {
        if (node.children?.length) {
          sortByActivity(node.children);
        }
      });
    };

    sortByActivity(roots);
    return roots;
  };

  // 转换为Ant Design Tree需要的格式
  const convertToTreeData = (nodes) => {
    return nodes.map(node => ({
      key: node.id,
      title: (
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 14, fontWeight: node.level === 0 ? 600 : 400 }}>
            {node.name}
          </span>
          <Badge count={node.project_count} 
                 showZero 
                 style={{ 
                   backgroundColor: node.project_count > 0 ? '#1890ff' : '#d9d9d9' 
                 }} 
          />
          {node.project_count > 5 && (
            <Tooltip title="活跃分类">
              <FireOutlined style={{ color: '#ff4d4f', fontSize: 12 }} />
            </Tooltip>
          )}
          <Tag color="blue" style={{ fontSize: 11, padding: '0 4px', margin: 0 }}>
            L{node.level}
          </Tag>
        </div>
      ),
      icon: node.children?.length > 0 ? <FolderOpenOutlined /> : <FolderOutlined />,
      children: node.children?.length > 0 ? convertToTreeData(node.children) : undefined
    }));
  };

  const treeData = convertToTreeData(buildTree(categoryHierarchy));

  // 计算统计信息
  const maxLevel = Math.max(...categoryHierarchy.map(c => c.level));
  const topCategories = categoryHierarchy.filter(c => c.level === 0);
  const activeCategories = categoryHierarchy.filter(c => c.project_count > 0);
  const mostActive = [...categoryHierarchy]
    .sort((a, b) => b.project_count - a.project_count)
    .slice(0, 3);

  return (
    <Card 
      title={
        <span>
          📂 分类层级结构
          <Tooltip title="显示完整的分类路径和活跃度">
            <InfoCircleOutlined style={{ marginLeft: 8, fontSize: 14, color: '#999' }} />
          </Tooltip>
        </span>
      }
      extra={
        <div style={{ fontSize: 12, color: '#999' }}>
          共{categoryHierarchy.length}个分类，{maxLevel + 1}层深度
        </div>
      }
      style={{ marginBottom: 24 }}
    >
      {/* 统计概览 */}
      <div style={{ 
        marginBottom: 16, 
        padding: 12, 
        background: '#f5f5f5', 
        borderRadius: 4 
      }}>
        <div style={{ display: 'flex', gap: 24, fontSize: 13 }}>
          <div>
            📊 顶级分类：<strong>{topCategories.length}</strong>
          </div>
          <div>
            ✅ 活跃分类：<strong>{activeCategories.length}</strong>
          </div>
          <div>
            🔥 最活跃：
            {mostActive.map((cat, idx) => (
              <Tag key={cat.id} color={idx === 0 ? 'red' : idx === 1 ? 'orange' : 'gold'} 
                   style={{ marginLeft: 4, fontSize: 11 }}>
                {cat.name} ({cat.project_count})
              </Tag>
            ))}
          </div>
        </div>
      </div>

      {/* 树形结构 */}
      <Tree
        showIcon
        defaultExpandAll
        treeData={treeData}
        style={{ background: '#fff' }}
      />

      {/* 图例说明 */}
      <div style={{ 
        marginTop: 16, 
        padding: 12, 
        background: '#f0f5ff', 
        borderRadius: 4,
        fontSize: 12,
        color: '#666'
      }}>
        <strong>图例：</strong>
        <span style={{ marginLeft: 12 }}>
          <Badge count={0} style={{ backgroundColor: '#d9d9d9', marginRight: 4 }} /> 项目数量
        </span>
        <span style={{ marginLeft: 12 }}>
          <FireOutlined style={{ color: '#ff4d4f', marginRight: 4 }} /> 活跃分类（&gt;5项）
        </span>
        <span style={{ marginLeft: 12 }}>
          <Tag color="blue" style={{ fontSize: 11 }}>L0</Tag> 层级深度
        </span>
      </div>
    </Card>
  );
};

export default CategoryHierarchyTree;
