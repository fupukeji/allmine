/**
 * 虚拟资产表单弹窗组件
 * 用于添加和编辑虚拟资产（随风而逝的资产）
 */

import { useState, useEffect } from 'react'
import { Form, Input, Button, Popup, Toast, Picker } from 'antd-mobile'
import dayjs from 'dayjs'
import { createProject, updateProject } from '../services/projects'
import { getCategories } from '../services/categories'

const VirtualAssetForm = ({ visible, onClose, onSuccess, initialData = null }) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [startDate, setStartDate] = useState(null)
  const [endDate, setEndDate] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState([])
  const [categoryOptions, setCategoryOptions] = useState([[]])

  // 加载分类列表
  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const res = await getCategories({ asset_type: 'virtual' })  // 只加载虚拟资产分类
      if (res.code === 200 && res.data) {
        const options = res.data.map(cat => ({
          label: cat.name,
          value: cat.id
        }))
        setCategoryOptions([options])
        // 设置默认选中第一个
        if (options.length > 0 && selectedCategory.length === 0) {
          setSelectedCategory([options[0].value])
        }
      }
    } catch (error) {
      console.error('加载分类失败:', error)
    }
  }

  useEffect(() => {
    if (visible && initialData) {
      // 编辑模式，填充表单
      const startTime = initialData.start_time ? new Date(initialData.start_time) : null
      const endTime = initialData.end_time ? new Date(initialData.end_time) : null
      
      setStartDate(startTime)
      setEndDate(endTime)
      // 使用category_id
      if (initialData.category_id) {
        setSelectedCategory([initialData.category_id])
      }
      
      form.setFieldsValue({
        name: initialData.name,
        total_amount: initialData.total_amount,
        description: initialData.description,
        account_username: initialData.account_username || '',
        account_password: initialData.account_password || ''
      })
    } else if (visible) {
      // 新增模式，重置表单
      form.resetFields()
      setStartDate(null)
      setEndDate(null)
      // 默认选第一个分类
      if (categoryOptions[0]?.length > 0) {
        setSelectedCategory([categoryOptions[0][0].value])
      }
    }
  }, [visible, initialData, form, categoryOptions])

  const handleSubmit = async () => {
    try {
      // 验证日期
      if (!startDate) {
        Toast.show({
          icon: 'fail',
          content: '请选择开始日期'
        })
        return
      }
      
      if (!endDate) {
        Toast.show({
          icon: 'fail',
          content: '请选择结束日期'
        })
        return
      }
      
      const values = await form.validateFields()
      setLoading(true)

      // 格式化日期
      const categoryId = selectedCategory[0]
      const categoryLabel = categoryOptions[0]?.find(c => c.value === categoryId)?.label || ''

      const data = {
        name: values.name,
        total_amount: parseFloat(values.total_amount),
        start_time: dayjs(startDate).format('YYYY-MM-DD'),
        end_time: dayjs(endDate).format('YYYY-MM-DD'),
        description: values.description || '',
        account_username: values.account_username || '',
        account_password: values.account_password || '',
        category_name: categoryLabel,
        category_id: categoryId
      }

      let res
      if (initialData) {
        // 编辑
        res = await updateProject(initialData.id, data)
      } else {
        // 新增
        res = await createProject(data)
      }

      if (res.code === 200) {
        Toast.show({
          icon: 'success',
          content: initialData ? '更新成功' : '添加成功'
        })
        form.resetFields()
        onSuccess()
        onClose()
      } else {
        Toast.show({
          icon: 'fail',
          content: res.message || '操作失败'
        })
      }
    } catch (error) {
      console.error('提交失败:', error)
      if (error.errorFields) {
        Toast.show({
          icon: 'fail',
          content: '请填写完整信息'
        })
      } else {
        Toast.show({
          icon: 'fail',
          content: '操作失败'
        })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Popup
      visible={visible}
      onMaskClick={onClose}
      bodyStyle={{
        borderTopLeftRadius: '16px',
        borderTopRightRadius: '16px',
        height: '80vh',
        display: 'flex',
        flexDirection: 'column',
        padding: '0'
      }}
    >
      {/* 固定头部 */}
      <div style={{ padding: '20px 20px 12px', flexShrink: 0 }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
          {initialData ? '编辑虚拟资产' : '添加虚拟资产'}
        </h3>
        <p style={{ margin: '8px 0 0', fontSize: '14px', color: '#999' }}>
          管理那些随时间流逝的资产，如会员、订阅服务等
        </p>
      </div>

      {/* 可滚动表单区域 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '0 20px' }}>
        <Form
          form={form}
          layout="horizontal"
        >
        <Form.Item
          name="name"
          label="资产名称"
          rules={[{ required: true, message: '请输入资产名称' }]}
        >
          <Input placeholder="例如：网易云音乐会员" />
        </Form.Item>

        <Form.Item
          label="资产类型"
          onClick={(e, pickerRef) => {
            // 阻止事件冒泡
          }}
        >
          {categoryOptions[0]?.length > 0 ? (
            <Picker
              columns={categoryOptions}
              value={selectedCategory}
              onConfirm={setSelectedCategory}
            >
              {(items, { open }) => (
                <div 
                  onClick={open}
                  style={{ 
                    padding: '8px 0', 
                    color: selectedCategory[0] ? '#333' : '#999',
                    cursor: 'pointer'
                  }}
                >
                  {categoryOptions[0].find(c => c.value === selectedCategory[0])?.label || '请选择资产类型'}
                </div>
              )}
            </Picker>
          ) : (
            <div style={{ padding: '8px 0', color: '#999' }}>
              加载中...
            </div>
          )}
        </Form.Item>

        <Form.Item
          name="total_amount"
          label="总金额"
          rules={[
            { required: true, message: '请输入总金额' },
            {
              pattern: /^\d+(\.\d{1,2})?$/,
              message: '请输入有效的金额'
            }
          ]}
        >
          <Input type="number" placeholder="0.00" />
        </Form.Item>

        <Form.Item
          label="开始日期"
        >
          <Input
            type="date"
            value={startDate ? dayjs(startDate).format('YYYY-MM-DD') : ''}
            onChange={val => {
              if (val) {
                setStartDate(new Date(val))
              }
            }}
            placeholder="请选择开始日期"
          />
        </Form.Item>

        <Form.Item
          label="结束日期"
        >
          <Input
            type="date"
            value={endDate ? dayjs(endDate).format('YYYY-MM-DD') : ''}
            onChange={val => {
              if (val) {
                setEndDate(new Date(val))
              }
            }}
            placeholder="请选择结束日期"
          />
        </Form.Item>

        <Form.Item
          name="description"
          label="备注"
        >
          <Input placeholder="选填，补充说明" />
        </Form.Item>

        <Form.Item
          name="account_username"
          label="账号"
        >
          <Input placeholder="选填，登录用户名" />
        </Form.Item>

        <Form.Item
          name="account_password"
          label="密码"
        >
          <Input placeholder="选填，登录密码" type="password" />
        </Form.Item>
        </Form>
      </div>

      {/* 固定底部按钮 */}
      <div style={{ padding: '12px 20px 20px', flexShrink: 0, borderTop: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Button block onClick={onClose}>
            取消
          </Button>
          <Button block type="submit" color="primary" loading={loading} onClick={handleSubmit}>
            {initialData ? '更新' : '添加'}
          </Button>
        </div>
      </div>
    </Popup>
  )
}

export default VirtualAssetForm
