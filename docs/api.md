# API 接口文档

## 概述

时间价值计算器 RESTful API 文档，所有 API 均返回 JSON 格式数据。

**基础URL**: `http://localhost:5000/api`

**认证方式**: Bearer Token (JWT)

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息"
}
```

## 认证接口

### 用户注册
- **URL**: `/auth/register`
- **方法**: `POST`
- **描述**: 用户注册

**请求参数**:
```json
{
  "username": "用户名",
  "email": "邮箱地址",
  "password": "密码"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
  }
}
```

### 用户登录
- **URL**: `/auth/login`
- **方法**: `POST`
- **描述**: 用户登录

**请求参数**:
```json
{
  "username": "用户名或邮箱",
  "password": "密码"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 获取用户信息
- **URL**: `/auth/profile`
- **方法**: `GET`
- **描述**: 获取当前用户信息
- **认证**: 必需

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
  }
}
```

### 更新用户信息
- **URL**: `/auth/profile`
- **方法**: `PUT`
- **描述**: 更新用户信息
- **认证**: 必需

**请求参数**:
```json
{
  "email": "新邮箱",
  "password": "新密码"
}
```

### 验证Token
- **URL**: `/auth/check-token`
- **方法**: `GET`
- **描述**: 验证Token有效性
- **认证**: 必需

## 分类管理接口

### 获取分类列表
- **URL**: `/categories`
- **方法**: `GET`
- **描述**: 获取用户的所有分类
- **认证**: 必需

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "运动健身",
      "color": "#52c41a",
      "icon": "trophy",
      "created_at": "2024-01-01T00:00:00",
      "project_count": 2
    }
  ]
}
```

### 创建分类
- **URL**: `/categories`
- **方法**: `POST`
- **描述**: 创建新分类
- **认证**: 必需

**请求参数**:
```json
{
  "name": "分类名称",
  "color": "#1890ff",
  "icon": "folder"
}
```

### 更新分类
- **URL**: `/categories/{category_id}`
- **方法**: `PUT`
- **描述**: 更新指定分类
- **认证**: 必需

**请求参数**:
```json
{
  "name": "新分类名称",
  "color": "#52c41a",
  "icon": "star"
}
```

### 删除分类
- **URL**: `/categories/{category_id}`
- **方法**: `DELETE`
- **描述**: 删除指定分类（需确保没有关联项目）
- **认证**: 必需

### 获取分类详情
- **URL**: `/categories/{category_id}`
- **方法**: `GET`
- **描述**: 获取分类详情及其项目列表
- **认证**: 必需

## 项目管理接口

### 获取项目列表
- **URL**: `/projects`
- **方法**: `GET`
- **描述**: 获取用户的项目列表
- **认证**: 必需

**查询参数**:
- `category_id`: 分类ID（可选）
- `status`: 项目状态 (`not_started`, `active`, `expired`)（可选）
- `sort_by`: 排序字段 (`created_at`, `remaining_value`, `progress`)（可选）
- `order`: 排序方式 (`asc`, `desc`)（可选）

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "健身房年卡",
      "total_amount": 1980.00,
      "start_time": "2024-01-01T00:00:00",
      "end_time": "2025-01-01T00:00:00",
      "purpose": "健身锻炼",
      "category_id": 1,
      "category_name": "运动健身",
      "unit_cost": 5.42,
      "used_cost": 980.25,
      "remaining_value": 999.75,
      "progress": 49.5,
      "status": "active",
      "total_days": 365.0,
      "used_days": 181.0
    }
  ]
}
```

### 创建项目
- **URL**: `/projects`
- **方法**: `POST`
- **描述**: 创建新项目
- **认证**: 必需

**请求参数**:
```json
{
  "name": "项目名称",
  "category_id": 1,
  "total_amount": 1980.00,
  "start_time": "2024-01-01 00:00:00",
  "end_time": "2025-01-01 00:00:00",
  "purchase_time": "2023-12-15 10:00:00",
  "purpose": "购买目的"
}
```

### 获取项目详情
- **URL**: `/projects/{project_id}`
- **方法**: `GET`
- **描述**: 获取指定项目详情
- **认证**: 必需

### 更新项目
- **URL**: `/projects/{project_id}`
- **方法**: `PUT`
- **描述**: 更新指定项目
- **认证**: 必需

**请求参数**（同创建项目，所有字段可选）:
```json
{
  "name": "新项目名称",
  "total_amount": 2000.00
}
```

### 删除项目
- **URL**: `/projects/{project_id}`
- **方法**: `DELETE`
- **描述**: 删除指定项目
- **认证**: 必需

### 批量删除项目
- **URL**: `/projects/batch-delete`
- **方法**: `POST`
- **描述**: 批量删除项目
- **认证**: 必需

**请求参数**:
```json
{
  "project_ids": [1, 2, 3]
}
```

### 计算项目价值
- **URL**: `/projects/{project_id}/calculate`
- **方法**: `GET`
- **描述**: 计算指定项目的实时价值
- **认证**: 必需

**查询参数**:
- `base_time`: 自定义计算基准时间（可选，格式：YYYY-MM-DD HH:mm:ss）

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "unit_cost": 5.42,
    "used_cost": 980.25,
    "remaining_value": 999.75,
    "progress": 49.5,
    "total_days": 365.0,
    "used_days": 181.0,
    "status": "active"
  }
}
```

### 获取统计数据
- **URL**: `/statistics`
- **方法**: `GET`
- **描述**: 获取用户的统计数据
- **认证**: 必需

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total_projects": 5,
    "total_amount": 9800.00,
    "total_used_cost": 4500.75,
    "total_remaining_value": 5299.25,
    "status_distribution": {
      "not_started": 1,
      "active": 3,
      "expired": 1
    }
  }
}
```

## 错误代码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 使用示例

### 完整工作流程

1. **用户注册**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "123456"
  }'
```

2. **用户登录**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456"
  }'
```

3. **创建分类**
```bash
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "健身运动",
    "color": "#52c41a",
    "icon": "trophy"
  }'
```

4. **创建项目**
```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "健身房年卡",
    "category_id": 1,
    "total_amount": 1980.00,
    "start_time": "2024-01-01 00:00:00",
    "end_time": "2025-01-01 00:00:00",
    "purpose": "健身锻炼"
  }'
```

5. **获取项目价值计算**
```bash
curl -X GET "http://localhost:5000/api/projects/1/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```