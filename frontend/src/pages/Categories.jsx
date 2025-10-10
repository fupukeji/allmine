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
  Col
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
  deleteCategory 
} from '../services/categories'

const { Title } = Typography

const Categories = () => {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingCategory, setEditingCategory] = useState(null)
  const [selectedColor, setSelectedColor] = useState('#1890ff') // 新增颜色状态
  const [form] = Form.useForm()

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    setLoading(true)
    try {
      const response = await getCategories()
      if (response.code === 200) {
        setCategories(response.data)
      }
    } catch (error) {
      console.error('获取分类列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingCategory(null)
    setSelectedColor('#1890ff') // 重置颜色选择
    setModalVisible(true)
    form.resetFields()
  }

  const handleEdit = (category) => {
    setEditingCategory(category)
    setSelectedColor(category.color || '#1890ff') // 设置当前颜色
    setModalVisible(true)
    form.setFieldsValue(category)
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
    setSelectedColor('#1890ff') // 重置颜色选择
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
          {text}
        </Space>
      ),
    },
    {
      title: '颜色',
      dataIndex: 'color',
      key: 'color',
      render: (color) => (
        <Tag color={color}>{color}</Tag>
      ),
    },
    {
      title: '图标',
      dataIndex: 'icon',
      key: 'icon',
    },
    {
      title: '项目数量',
      dataIndex: 'project_count',
      key: 'project_count',
      render: (count) => `${count} 个`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleDateString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
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
              danger
              icon={<DeleteOutlined />}
              disabled={record.project_count > 0}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const colorOptions = [
    '#1890ff', '#52c41a', '#faad14', '#f5222d', 
    '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'
  ]

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
        <Col>
          <Title level={2}>分类管理</Title>
        </Col>
        <Col>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={handleAdd}
          >
            添加分类
          </Button>
        </Col>
      </Row>

      <Table
        dataSource={categories}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />

      <Modal
        title={editingCategory ? '编辑分类' : '添加分类'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            color: '#1890ff',
            icon: 'folder'
          }}
        >
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