/**
 * 资产费用管理组件
 */
import { useState, useEffect } from 'react'
import { Popup, NavBar, List, Button, Form, Input, Picker, Toast, Dialog, Empty, Tag } from 'antd-mobile'
import { AddOutline, DeleteOutline } from 'antd-mobile-icons'
import { getExpenses, createExpense, deleteExpense, getExpenseTypes } from '../services/expenses'
import dayjs from 'dayjs'
import './AssetExpenseManager.css'

// 默认费用类型
const DEFAULT_EXPENSE_TYPES = [
  { value: 'maintenance', label: '维护费' },
  { value: 'repair', label: '维修费' },
  { value: 'insurance', label: '保险费' },
  { value: 'tax', label: '税费' },
  { value: 'other', label: '其他' }
]

// 周期选项
const RECURRING_PERIODS = [
  [
    { value: 'monthly', label: '每月' },
    { value: 'quarterly', label: '每季度' },
    { value: 'yearly', label: '每年' }
  ]
]

const AssetExpenseManager = ({ visible, onClose, asset }) => {
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [expenseTypes, setExpenseTypes] = useState(DEFAULT_EXPENSE_TYPES)
  const [totalAmount, setTotalAmount] = useState(0)
  const [form] = Form.useForm()

  useEffect(() => {
    if (visible && asset) {
      loadExpenses()
      loadExpenseTypes()
    }
  }, [visible, asset])

  const loadExpenses = async () => {
    if (!asset) return
    try {
      setLoading(true)
      const res = await getExpenses(asset.id)
      if (res.code === 200 && res.data) {
        setExpenses(res.data.items || [])
        setTotalAmount(res.data.total_amount || 0)
      }
    } catch (error) {
      console.error('加载费用失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadExpenseTypes = async () => {
    if (!asset) return
    try {
      const res = await getExpenseTypes(asset.category_name)
      if (res.code === 200 && res.data) {
        setExpenseTypes(res.data)
      }
    } catch (error) {
      console.error('加载费用类型失败:', error)
    }
  }

  const handleAdd = async () => {
    try {
      const values = await form.validateFields()
      
      const data = {
        expense_type: values.expense_type?.[0] || 'other',
        expense_name: values.expense_name,
        amount: parseFloat(values.amount),
        expense_date: values.expense_date || dayjs().format('YYYY-MM-DD'),
        is_recurring: values.is_recurring || false,
        recurring_period: values.recurring_period?.[0],
        description: values.description
      }
      
      const res = await createExpense(asset.id, data)
      if (res.code === 200) {
        Toast.show({ icon: 'success', content: '添加成功' })
        setShowAddForm(false)
        form.resetFields()
        loadExpenses()
      } else {
        Toast.show({ icon: 'fail', content: res.message || '添加失败' })
      }
    } catch (error) {
      console.error('添加费用失败:', error)
    }
  }

  const handleDelete = (expense) => {
    Dialog.confirm({
      content: `确认删除「${expense.expense_name}」吗？`,
      onConfirm: async () => {
        try {
          const res = await deleteExpense(expense.id)
          if (res.code === 200) {
            Toast.show({ icon: 'success', content: '删除成功' })
            loadExpenses()
          }
        } catch (error) {
          Toast.show({ icon: 'fail', content: '删除失败' })
        }
      }
    })
  }

  const getExpenseTypeLabel = (type) => {
    const found = expenseTypes.find(t => t.value === type)
    return found ? found.label : type
  }

  return (
    <Popup
      visible={visible}
      onMaskClick={onClose}
      position="right"
      bodyStyle={{ width: '100vw', height: '100vh', overflow: 'auto' }}
    >
      <div className="expense-manager">
        <NavBar onBack={onClose} right={
          <Button size="small" color="primary" onClick={() => setShowAddForm(true)}>
            <AddOutline /> 添加
          </Button>
        }>
          费用管理
        </NavBar>

        {/* 费用统计 */}
        <div className="expense-summary">
          <div className="asset-name">{asset?.name}</div>
          <div className="total-expense">
            <span className="label">累计费用</span>
            <span className="value">￥{totalAmount.toLocaleString()}</span>
          </div>
        </div>

        {/* 费用列表 */}
        <div className="expense-list">
          {expenses.length === 0 ? (
            <Empty description="暂无费用记录" />
          ) : (
            <List>
              {expenses.map(expense => (
                <List.Item
                  key={expense.id}
                  prefix={
                    <Tag color="primary" fill="outline">
                      {getExpenseTypeLabel(expense.expense_type)}
                    </Tag>
                  }
                  extra={
                    <div className="expense-actions">
                      <span className="expense-amount">￥{expense.amount}</span>
                      <DeleteOutline 
                        className="delete-btn"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(expense)
                        }}
                      />
                    </div>
                  }
                  description={
                    <div className="expense-info">
                      <span>{dayjs(expense.expense_date).format('YYYY-MM-DD')}</span>
                      {expense.is_recurring && (
                        <Tag color="warning" fill="outline" style={{ marginLeft: 8 }}>
                          {expense.recurring_period === 'monthly' ? '月付' : 
                           expense.recurring_period === 'quarterly' ? '季付' : '年付'}
                        </Tag>
                      )}
                    </div>
                  }
                >
                  {expense.expense_name}
                </List.Item>
              ))}
            </List>
          )}
        </div>

        {/* 添加费用表单 */}
        <Popup
          visible={showAddForm}
          onMaskClick={() => setShowAddForm(false)}
          position="bottom"
          bodyStyle={{ borderRadius: '16px 16px 0 0', maxHeight: '80vh', overflow: 'auto' }}
        >
          <div className="add-expense-form">
            <div className="form-header">
              <h3>添加费用</h3>
            </div>
            <Form form={form} layout="horizontal" initialValues={{ expense_date: dayjs().format('YYYY-MM-DD') }}>
              <Form.Item
                name="expense_type"
                label="费用类型"
                trigger="onConfirm"
                onClick={(e, pickerRef) => pickerRef.current?.open()}
              >
                <Picker columns={[expenseTypes]}>
                  {(value) => value?.[0] ? getExpenseTypeLabel(value[0]) : '请选择'}
                </Picker>
              </Form.Item>
              
              <Form.Item
                name="expense_name"
                label="费用名称"
                rules={[{ required: true, message: '请输入费用名称' }]}
              >
                <Input placeholder="如：2024年车险" />
              </Form.Item>
              
              <Form.Item
                name="amount"
                label="金额"
                rules={[{ required: true, message: '请输入金额' }]}
              >
                <Input type="number" placeholder="请输入金额" />
              </Form.Item>
              
              <Form.Item name="expense_date" label="日期">
                <Input type="date" />
              </Form.Item>
              
              <Form.Item name="description" label="备注">
                <Input placeholder="选填" />
              </Form.Item>
            </Form>
            
            <div className="form-actions">
              <Button block onClick={() => setShowAddForm(false)}>取消</Button>
              <Button block color="primary" onClick={handleAdd}>确认添加</Button>
            </div>
          </div>
        </Popup>
      </div>
    </Popup>
  )
}

export default AssetExpenseManager
