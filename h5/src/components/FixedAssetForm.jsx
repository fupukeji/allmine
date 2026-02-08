/**
 * 固定资产表单组件
 * 用于添加和编辑固定资产
 */

import { useState, useEffect } from 'react'
import { Form, Input, Button, Popup, Toast, Picker, Stepper } from 'antd-mobile'
import dayjs from 'dayjs'
import { createAsset, updateAsset } from '../services/assets'
import { getCategories } from '../services/categories'

const FixedAssetForm = ({ visible, onClose, onSuccess, initialData = null }) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [categoryOptions, setCategoryOptions] = useState([[]])
  const [selectedCategory, setSelectedCategory] = useState([])
  const [purchaseDate, setPurchaseDate] = useState(null)
  const [depreciationStartDate, setDepreciationStartDate] = useState(null)
  const [selectedStatus, setSelectedStatus] = useState(['in_use'])
  const [selectedMethod, setSelectedMethod] = useState(['straight_line'])

  // 状态选项
  const statusOptions = [
    [
      { label: '使用中', value: 'in_use' },
      { label: '闲置', value: 'idle' },
      { label: '维修中', value: 'maintenance' },
      { label: '已处置', value: 'disposed' }
    ]
  ]

  // 折旧方法选项
  const depreciationMethodOptions = [
    [
      { label: '直线法', value: 'straight_line' }
    ]
  ]

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    if (visible && initialData) {
      // 编辑模式，填充表单
      const purchaseTime = initialData.purchase_date ? new Date(initialData.purchase_date) : null
      const depreciationTime = initialData.depreciation_start_date ? new Date(initialData.depreciation_start_date) : null
      
      setPurchaseDate(purchaseTime)
      setDepreciationStartDate(depreciationTime)
      
      // 设置分类
      if (initialData.category_id) {
        setSelectedCategory([initialData.category_id])
      }
      // 设置状态
      setSelectedStatus([initialData.status || 'in_use'])
      setSelectedMethod([initialData.depreciation_method || 'straight_line'])
      
      form.setFieldsValue({
        name: initialData.name,
        description: initialData.description,
        original_value: initialData.original_value,
        useful_life_years: initialData.useful_life_years || 5,
        residual_rate: initialData.residual_rate || 5,
        location: initialData.location,
        responsible_person: initialData.responsible_person
      })
    } else if (visible) {
      // 新增模式，重置表单
      form.resetFields()
      setPurchaseDate(null)
      setDepreciationStartDate(null)
      setSelectedStatus(['in_use'])
      setSelectedMethod(['straight_line'])
      // 默认选第一个分类
      if (categoryOptions[0]?.length > 0) {
        setSelectedCategory([categoryOptions[0][0].value])
      }
    }
  }, [visible, initialData, form, categoryOptions])

  const loadCategories = async () => {
    try {
      const res = await getCategories({ asset_type: 'fixed' })  // 只加载固定资产分类
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

  const handleSubmit = async () => {
    try {
      // 验证日期
      if (!purchaseDate) {
        Toast.show({
          icon: 'fail',
          content: '请选择购买日期'
        })
        return
      }
      
      if (!depreciationStartDate) {
        Toast.show({
          icon: 'fail',
          content: '请选择折旧开始日期'
        })
        return
      }
      
      const values = await form.validateFields()
      setLoading(true)

      // 验证分类
      if (!selectedCategory[0]) {
        Toast.show({ icon: 'fail', content: '请选择资产分类' })
        setLoading(false)
        return
      }

      // 生成资产编号（如果是新增）
      let assetCode = initialData?.asset_code
      if (!assetCode) {
        assetCode = `FA${Date.now().toString().slice(-8)}`
      }

      const data = {
        asset_code: assetCode,
        name: values.name,
        description: values.description || '',
        category_id: selectedCategory[0],
        original_value: parseFloat(values.original_value),
        current_value: parseFloat(values.original_value), // 初始等于原值
        residual_rate: parseFloat(values.residual_rate),
        purchase_date: dayjs(purchaseDate).format('YYYY-MM-DD'),
        useful_life_years: parseInt(values.useful_life_years),
        depreciation_start_date: dayjs(depreciationStartDate).format('YYYY-MM-DD'),
        depreciation_method: selectedMethod[0],
        status: selectedStatus[0],
        location: values.location || '',
        responsible_person: values.responsible_person || ''
      }

      let res
      if (initialData) {
        // 更新
        res = await updateAsset(initialData.id, data)
      } else {
        // 新增
        res = await createAsset(data)
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
        height: '85vh',
        display: 'flex',
        flexDirection: 'column',
        padding: '0'
      }}
    >
      {/* 固定头部 */}
      <div style={{ padding: '20px 16px 12px', flexShrink: 0, textAlign: 'center' }}>
        <h2 style={{ margin: '0', fontSize: '20px', fontWeight: 'bold' }}>
          {initialData ? '编辑固定资产' : '添加固定资产'}
        </h2>
      </div>

      {/* 可滚动表单区域 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '0 16px' }}>
        <Form
          form={form}
          layout="horizontal"
          initialValues={{
            useful_life_years: 5,
            residual_rate: 5,
            status: 'in_use',
            depreciation_method: 'straight_line'
          }}
        >
          <Form.Item
            name="name"
            label="资产名称"
            rules={[{ required: true, message: '请输入资产名称' }]}
          >
            <Input placeholder="例如：MacBook Pro" />
          </Form.Item>

          <Form.Item
            label="资产分类"
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
                    {categoryOptions[0].find(c => c.value === selectedCategory[0])?.label || '请选择资产分类'}
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
            name="original_value"
            label="原值（元）"
            rules={[
              { required: true, message: '请输入原值' },
              {
                pattern: /^\d+(\.\d{1,2})?$/,
                message: '请输入有效的金额'
              }
            ]}
          >
            <Input type="number" placeholder="0.00" />
          </Form.Item>

          <Form.Item
            label="购买日期"
          >
            <Input
              type="date"
              value={purchaseDate ? dayjs(purchaseDate).format('YYYY-MM-DD') : ''}
              onChange={val => {
                if (val) {
                  setPurchaseDate(new Date(val))
                  // 如果折旧开始日期未设置，默认设置为购买日期
                  if (!depreciationStartDate) {
                    setDepreciationStartDate(new Date(val))
                  }
                }
              }}
              placeholder="请选择购买日期"
            />
          </Form.Item>

          <Form.Item
            name="useful_life_years"
            label="使用年限"
            rules={[{ required: true, message: '请输入使用年限' }]}
          >
            <Stepper min={1} max={50} />
          </Form.Item>

          <Form.Item
            label="折旧开始日期"
          >
            <Input
              type="date"
              value={depreciationStartDate ? dayjs(depreciationStartDate).format('YYYY-MM-DD') : ''}
              onChange={val => {
                if (val) {
                  setDepreciationStartDate(new Date(val))
                }
              }}
              placeholder="请选择折旧开始日期"
            />
          </Form.Item>

          <Form.Item
            name="residual_rate"
            label="残值率（%）"
          >
            <Stepper min={0} max={100} step={0.5} digits={1} />
          </Form.Item>

          <Form.Item
            label="折旧方法"
          >
            <Picker
              columns={depreciationMethodOptions}
              value={selectedMethod}
              onConfirm={setSelectedMethod}
            >
              {(items, { open }) => (
                <div onClick={open} style={{ padding: '8px 0', cursor: 'pointer' }}>
                  {selectedMethod[0] === 'straight_line' ? '直线法' : '请选择'}
                </div>
              )}
            </Picker>
          </Form.Item>

          <Form.Item
            label="使用状态"
          >
            <Picker
              columns={statusOptions}
              value={selectedStatus}
              onConfirm={setSelectedStatus}
            >
              {(items, { open }) => (
                <div onClick={open} style={{ padding: '8px 0', cursor: 'pointer' }}>
                  {{
                    'in_use': '使用中',
                    'idle': '闲置',
                    'maintenance': '维修中',
                    'disposed': '已处置'
                  }[selectedStatus[0]] || '请选择'}
                </div>
              )}
            </Picker>
          </Form.Item>

          <Form.Item
            name="location"
            label="所在位置"
          >
            <Input placeholder="例如：北京办公室" />
          </Form.Item>

          <Form.Item
            name="responsible_person"
            label="责任人"
          >
            <Input placeholder="例如：张三" />
          </Form.Item>

          <Form.Item
            name="description"
            label="备注说明"
          >
            <Input placeholder="选填，补充说明" />
          </Form.Item>
        </Form>
      </div>

      {/* 固定底部按钮 */}
      <div style={{ padding: '12px 16px 20px', flexShrink: 0, borderTop: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Button block onClick={onClose}>取消</Button>
          <Button block type="submit" color="primary" loading={loading} onClick={handleSubmit}>
            {initialData ? '更新' : '添加'}
          </Button>
        </div>
      </div>
    </Popup>
  )
}

export default FixedAssetForm
