import React, { useState, useEffect, useCallback } from 'react'
import { 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  message, 
  Popconfirm, 
  Typography, 
  Space,
  Tag,
  Row,
  Col,
  Badge,
  TreeSelect,
  InputNumber,
  Tooltip
} from 'antd'
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  FolderOutlined
} from '@ant-design/icons'
import { 
  getCategories, 
  createCategory, 
  updateCategory, 
  deleteCategory,
  initializeCategories
} from '../services/categories'

const { Title, Text } = Typography
const { TextArea } = Input

const Categories = () => {
  const [categories, setCategories] = useState([])
  const [treeData, setTreeData] = useState([]) // 树形数据
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [selectedColor, setSelectedColor] = useState('#1890ff')
  const [selectedParentId, setSelectedParentId] = useState(null) // 选中的父分类
  const [expandedRowKeys, setExpandedRowKeys] = useState([]) // 展开的行
  const [form] = Form.useForm()

  useEffect(() => {
    fetchCategories()
  }, [])

  const buildTree = (flatData) => {
    const map = {}
    const tree = []
    
    flatData.forEach(item => {
      map[item.id] = { ...item, children: [] }
    })
    
    flatData.forEach(item => {
      const node = map[item.id]
      if (item.parent_id && map[item.parent_id]) {
        map[item.parent_id].children.push(node)
      } else {
        tree.push(node)
      }
    })
    
    const cleanEmptyChildren = (nodes) => {
      nodes.forEach(node => {
        if (node.children?.length > 0) {
          cleanEmptyChildren(node.children)
        } else {
          delete node.children
        }
      })
    }
    cleanEmptyChildren(tree)
    
    return tree
  }

  const buildTreeSelectData = (categories, level = 0) => {
    return categories.map(cat => ({
      value: cat.id,
      title: (
        <Space>
          <FolderOutlined style={{ color: cat.color }} />
          {cat.name}
        </Space>
      ),
      disabled: level >= 2,
      children: cat.children?.length > 0 
        ? buildTreeSelectData(cat.children, level + 1) 
        : undefined
    }))
  }

  const fetchCategories = async () => {
    setLoading(true)
    try {
      const response = await getCategories()
      if (response.code === 200) {
        setCategories(response.data)
        const tree = buildTree(response.data)
        setTreeData(tree)
        
        const expandKeys = []
        const collectExpandKeys = (nodes) => {
          nodes.forEach(node => {
            if (node.children?.length > 0) {
              expandKeys.push(node.id)
              collectExpandKeys(node.children)
            }
          })
        }
        collectExpandKeys(tree)
        setExpandedRowKeys(expandKeys)
      }
    } catch (error) {
      console.error('获取分类列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = (parentId = null) => {
    setEditingCategory(null)
    setSelectedColor('#1890ff')
    setSelectedParentId(parentId)
    setModalVisible(true)
    form.resetFields()
    if (parentId) {
      form.setFieldsValue({ parent_id: parentId })
    }
  }

  const handleEdit = (category) => {
    setEditingCategory(category)
    setSelectedColor(category.color || '#1890ff')
    setSelectedParentId(category.parent_id)
    setModalVisible(true)
    form.setFieldsValue({
      ...category,
      parent_id: category.parent_id || undefined
    })
  }

  const handleDelete = async (categoryId) => {
    try {
      const response = await deleteCategory(categoryId)
      if (response.code === 200) {
        message.success('删除成功')
        fetchCategories()
      }
    } catch (error) {
      console.error('删除分类失败:', error)
    }
  }

  const handleInitialize = async () => {
    Modal.confirm({
      title: '初始化默认分类',
      content: (
        <div>
          <p>将添加预设的两级分类体系：</p>
          <ul style={{ paddingLeft: 20 }}>
            <li>8个一级分类（固定资产、金融资产等）</li>
            <li>38个二级分类（房产、车辆、股票等）</li>
          </ul>
          <Text type="success" style={{ display: 'block', marginTop: 12 }}>
            ✔️ 新分类将与现有分类并存，不会删除现有数据
          </Text>
          <Text type="warning" style={{ display: 'block', marginTop: 8 }}>
            ⚠️ 同名分类将自动跳过
          </Text>
        </div>
      ),
      okText: '确认初始化',
      cancelText: '取消',
      width: 500,
      onOk: async () => {
        try {
          setLoading(true)
          const response = await initializeCategories({ force: true })
          if (response.code === 200) {
            message.success('默认分类初始化成功')
          } else {
            message.info(response.message || '初始化完成')
          }
          fetchCategories()
        } catch (error) {
          message.error(error.response?.data?.message || '初始化失败')
        } finally {
          setLoading(false)
        }
      }
    })
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingCategory) {
        // 更新分类
        const response = await updateCategory(editingCategory.id, values)
        if (response.code === 200) {
          message.success('更新成功')
          setModalVisible(false)
          fetchCategories()
        }
      } else {
        // 创建分类
        const response = await createCategory(values)
        if (response.code === 200) {
          message.success('创建成功')
          setModalVisible(false)
          fetchCategories()
        }
      }
    } catch (error) {
      console.error('操作失败:', error)
    }
  }

  const handleModalCancel = () => {
    setModalVisible(false)
    setEditingCategory(null)
    setSelectedColor('#1890ff')
    setSelectedParentId(null)
    form.resetFields()
  }

  const columns = [
    {
      title: '分类名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <FolderOutlined style={{ color: record.color }} />
          <Text>{text}</Text>
          {record.description && (
            <Tooltip title={record.description}>
              <Tag color="cyan" style={{ fontSize: 11 }}>
                {record.description.substring(0, 10)}{record.description.length > 10 ? '...' : ''}
              </Tag>
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: '颜色',
      dataIndex: 'color',
      key: 'color',
      width: 120,
      render: (color) => (
        <Tag color={color}>{color}</Tag>
      ),
    },
    {
      title: '图标',
      dataIndex: 'icon',
      key: 'icon',
      width: 100,
    },
    {
      title: '项目数量',
      dataIndex: 'project_count',
      key: 'project_count',
      width: 100,
      render: (count) => (
        <Badge 
          count={count} 
          showZero 
          style={{ backgroundColor: count > 0 ? '#52c41a' : '#d9d9d9' }}
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (time) => new Date(time).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => {
        const getLevel = (cat) => {
          if (!cat.parent_id) return 0
          const parent = categories.find(c => c.id === cat.parent_id)
          return parent ? getLevel(parent) + 1 : 0
        }
        const level = getLevel(record)
        
        return (
          <Space size="small">
            {level < 2 && (
              <Tooltip title="添加子分类">
                <Button
                  type="link"
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={() => handleAdd(record.id)}
                >
                  子级
                </Button>
              </Tooltip>
            )}
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              编辑
            </Button>
            <Popconfirm
              title="确定删除这个分类吗？"
              description={record.project_count > 0 ? `该分类下还有${record.project_count}个项目` : '删除后无法恢复'}
              onConfirm={() => handleDelete(record.id)}
              okText="确定"
              cancelText="取消"
              disabled={record.project_count > 0}
            >
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                disabled={record.project_count > 0}
              >
                删除
              </Button>
            </Popconfirm>
          </Space>
        )
      },
    },
  ]

  const colorOptions = [
    '#1890ff', '#52c41a', '#faad14', '#f5222d', 
    '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'
  ]

  return (
    <div style={{ padding: '24px', background: '#f5f7fa', minHeight: 'calc(100vh - 64px)' }}>
      {/* 页面头部 */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '20px',
        padding: '32px',
        marginBottom: '24px',
        boxShadow: '0 20px 60px rgba(102, 126, 234, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* 浮动装饰 */}
        <div style={{ 
          position: 'absolute', 
          top: '-80px', 
          right: '-80px', 
          width: '250px', 
          height: '250px', 
          background: 'rgba(255,255,255,0.1)', 
          borderRadius: '50%',
          animation: 'float 6s ease-in-out infinite'
        }} />
        <div style={{ 
          position: 'absolute', 
          bottom: '-60px', 
          left: '-60px', 
          width: '200px', 
          height: '200px', 
          background: 'rgba(255,255,255,0.08)', 
          borderRadius: '50%',
          animation: 'float 8s ease-in-out infinite'
        }} />
        
        <Row justify="space-between" align="middle" style={{ position: 'relative', zIndex: 1 }}>
          <Col>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                width: '60px',
                height: '60px',
                background: 'rgba(255,255,255,0.2)',
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '16px',
                backdropFilter: 'blur(10px)'
              }}>
                <FolderOutlined style={{ fontSize: '32px', color: 'white' }} />
              </div>
              <div>
                <Title level={2} style={{ color: 'white', margin: 0, fontWeight: 'bold' }}>
                  分类管理
                </Title>
                {categories.length > 0 && (
                  <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px', marginTop: '4px' }}>
                    共 {categories.length} 个分类，支持多级层级结构
                  </div>
                )}
              </div>
            </div>
          </Col>
          <Col>
            <Space>
              <Button 
                onClick={handleInitialize}
                loading={loading}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  color: 'white',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '10px',
                  fontWeight: 500
                }}
              >
                初始化默认分类
              </Button>
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => handleAdd()}
                style={{
                  background: 'white',
                  color: '#667eea',
                  border: 'none',
                  borderRadius: '10px',
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(255,255,255,0.3)'
                }}
              >
                添加分类
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 树形表格展示 */}
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '24px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
      }}>
        <Table
          dataSource={treeData}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={false}
          expandable={{
            expandedRowKeys: expandedRowKeys,
            onExpandedRowsChange: (keys) => setExpandedRowKeys(keys),
            childrenColumnName: 'children'
          }}
        />
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(20px); }
        }
      `}</style>

      <Modal
        title={editingCategory ? '编辑分类' : '添加分类'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            color: '#1890ff',
            icon: 'folder',
            sort_order: 0
          }}
        >
          <Form.Item
            label="父级分类"
            name="parent_id"
            help="选择父级可创建层级结构，最多2级"
          >
            <TreeSelect
              placeholder="不选择则为顶级分类"
              allowClear
              treeDefaultExpandAll
              treeData={buildTreeSelectData(treeData)}
              onChange={(value) => setSelectedParentId(value)}
            />
          </Form.Item>

          <Form.Item
            label="分类名称"
            name="name"
            rules={[
              { required: true, message: '请输入分类名称!' },
              { max: 50, message: '分类名称不能超过50个字符!' }
            ]}
          >
            <Input placeholder="请输入分类名称" />
          </Form.Item>

          <Form.Item
            label="分类描述"
            name="description"
          >
            <TextArea 
              placeholder="选填，用于说明该分类的用途" 
              rows={3}
              maxLength={200}
              showCount
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="颜色"
                name="color"
                rules={[{ required: true, message: '请选择颜色!' }]}
              >
                <div>
                  <Row gutter={8}>
                    {colorOptions.map(color => (
                      <Col key={color}>
                        <div
                          style={{
                            width: '32px',
                            height: '32px',
                            backgroundColor: color,
                            borderRadius: '4px',
                            cursor: 'pointer',
                            border: selectedColor === color ? '3px solid #000' : '1px solid #d9d9d9',
                            marginBottom: '8px',
                            transition: 'border 0.2s ease'
                          }}
                          onClick={() => {
                            setSelectedColor(color)
                            form.setFieldsValue({ color })
                          }}
                        />
                      </Col>
                    ))}
                  </Row>
                  <Input 
                    value={selectedColor} 
                    onChange={(e) => {
                      const newColor = e.target.value
                      setSelectedColor(newColor)
                      form.setFieldsValue({ color: newColor })
                    }}
                    placeholder="或输入自定义颜色代码"
                  />
                </div>
              </Form.Item>
            </Col>
            
            <Col span={12}>
              <Form.Item
                label="排序顺序"
                name="sort_order"
                help="数字越小越靠前"
              >
                <InputNumber 
                  min={0} 
                  max={9999} 
                  style={{ width: '100%' }}
                  placeholder="0"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="图标"
            name="icon"
            rules={[{ required: true, message: '请输入图标名称!' }]}
          >
            <Input placeholder="请输入图标名称（如: folder, tag, star）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Categories