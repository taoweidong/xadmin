# 部门和菜单管理API设计文档

## 1. 概述

本文档详细描述了部门和菜单管理模块的API接口设计，包括标准的RESTful接口规范，用于对外提供部门和菜单数据的增删改查操作。设计与Django项目保持一致，确保前后端兼容性。设计与Django项目保持一致，确保前后端兼容性。

## 2. 技术架构

### 2.1 技术栈
- 后端框架: FastAPI
- 数据库: SQLAlchemy ORM
- 认证机制: JWT Token
- 响应格式: 统一JSON格式

### 2.2 设计原则
- 遵循RESTful API设计规范
- 使用标准HTTP方法(GET, POST, PUT, DELETE)
- 统一响应格式(code, detail, data)
- 支持分页、排序、搜索等通用功能

## 3. 数据模型

### 3.1 部门模型(DeptInfo)
| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| pk | UUID | 是 | 主键ID |
| name | String(128) | 是 | 部门名称 |
| code | String(128) | 是 | 部门编码 |
| parent | Object | 否 | 父部门 |
| is_active | Boolean | 是 | 是否启用 |
| rank | Integer | 是 | 排序 |
| mode_type | Integer | 否 | 模式类型 |
| auto_bind | Boolean | 是 | 自动绑定 |
| description | String(256) | 否 | 部门描述 |
| created_time | DateTime | 是 | 创建时间 |
| updated_time | DateTime | 是 | 更新时间 |

### 3.2 菜单模型(Menu)
| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| pk | UUID | 是 | 主键ID |
| name | String(128) | 是 | 组件名称或权限代码 |
| rank | Integer | 是 | 排序 |
| path | String(255) | 是 | 路由路径或API路径 |
| component | String(255) | 否 | 组件路径 |
| menu_type | Integer | 是 | 菜单类型(0-目录,1-菜单,2-权限) |
| is_active | Boolean | 是 | 是否启用 |
| method | String | 否 | HTTP方法(GET,POST,PUT,DELETE,PATCH) |
| meta | Object | 是 | 菜单元数据 |
| parent | Object | 否 | 父菜单 |
| model | Array | 否 | 关联模型 |
| created_time | DateTime | 是 | 创建时间 |
| updated_time | DateTime | 是 | 更新时间 |

## 4. API接口设计

### 4.1 部门管理API

#### 4.1.1 获取部门列表
- **接口地址**: `GET /api/system/dept`
- **功能描述**: 获取部门列表，支持分页、搜索、排序
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | page | Integer | 否 | 页码，默认1 |
  | size | Integer | 否 | 每页大小，默认20 |
  | ordering | String | 否 | 排序字段 |
  | search | String | 否 | 搜索关键词 |
  | is_active | Boolean | 否 | 是否启用 |
  | code | String | 否 | 部门编码 |
  | mode_type | Integer | 否 | 模式类型 |
  | auto_bind | Boolean | 否 | 自动绑定 |
  | name | String | 否 | 部门名称 |
  | description | String | 否 | 部门描述 |
  | pk | UUID | 否 | 部门ID |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "success",
  "data": {
    "results": [
      {
        "pk": "550e8400-e29b-41d4-a716-446655440000",
        "name": "技术部",
        "code": "TECH",
        "parent": null,
        "is_active": true,
        "rank": 1,
        "mode_type": 1,
        "auto_bind": false,
        "description": "技术开发部门",
        "created_time": "2023-01-01T00:00:00",
        "updated_time": "2023-01-01T00:00:00",
        "user_count": 10
      }
    ],
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 4.1.2 创建部门
- **接口地址**: `POST /api/system/dept`
- **功能描述**: 创建新部门
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | name | String | 是 | 部门名称 |
  | code | String | 是 | 部门编码 |
  | parent | Object | 否 | 父部门 |
  | description | String | 否 | 部门描述 |
  | is_active | Boolean | 否 | 是否启用，默认true |
  | rank | Integer | 否 | 排序，默认99 |
  | mode_type | Integer | 否 | 模式类型 |
  | auto_bind | Boolean | 否 | 自动绑定，默认false |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "部门创建成功",
  "data": {
    "pk": "550e8400-e29b-41d4-a716-446655440000",
    "name": "技术部",
    "code": "TECH",
    "parent": null,
    "is_active": true,
    "rank": 1,
    "mode_type": 1,
    "auto_bind": false,
    "description": "技术开发部门",
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00",
    "user_count": 0
  }
}
```

#### 4.1.3 获取部门详情
- **接口地址**: `GET /api/system/dept/{dept_id}`
- **功能描述**: 获取指定部门的详细信息
- **路径参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | dept_id | UUID | 是 | 部门ID |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "success",
  "data": {
    "pk": "550e8400-e29b-41d4-a716-446655440000",
    "name": "技术部",
    "code": "TECH",
    "parent": null,
    "is_active": true,
    "rank": 1,
    "mode_type": 1,
    "auto_bind": false,
    "description": "技术开发部门",
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00",
    "user_count": 10
  }
}
```

#### 4.1.4 更新部门
- **接口地址**: `PUT /api/system/dept/{dept_id}`
- **功能描述**: 更新指定部门的信息
- **路径参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | dept_id | UUID | 是 | 部门ID |

- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | name | String | 否 | 部门名称 |
  | parent | Object | 否 | 父部门 |
  | description | String | 否 | 部门描述 |
  | is_active | Boolean | 否 | 是否启用 |
  | rank | Integer | 否 | 排序 |
  | mode_type | Integer | 否 | 模式类型 |
  | auto_bind | Boolean | 否 | 自动绑定 |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "部门更新成功",
  "data": {
    "pk": "550e8400-e29b-41d4-a716-446655440000",
    "name": "技术研发部",
    "code": "TECH",
    "parent": null,
    "is_active": true,
    "rank": 1,
    "mode_type": 1,
    "auto_bind": false,
    "description": "技术研发部门",
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-02T00:00:00",
    "user_count": 10
  }
}
```

#### 4.1.5 删除部门
- **接口地址**: `DELETE /api/system/dept/{dept_id}`
- **功能描述**: 删除指定部门
- **路径参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | dept_id | UUID | 是 | 部门ID |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "部门删除成功",
  "data": null
}
```

#### 4.1.6 批量删除部门
- **接口地址**: `POST /api/system/dept/batch-delete`
- **功能描述**: 批量删除部门
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | pks | Array[UUID] | 是 | 部门ID列表 |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "部门批量删除成功",
  "data": null
}
```

### 4.2 菜单管理API

#### 4.2.1 获取菜单列表
- **接口地址**: `GET /api/system/menu`
- **功能描述**: 获取菜单列表，支持分页、搜索、排序
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | page | Integer | 否 | 页码，默认1 |
  | size | Integer | 否 | 每页大小，默认20 |
  | ordering | String | 否 | 排序字段 |
  | search | String | 否 | 搜索关键词 |
  | name | String | 否 | 菜单名称 |
  | component | String | 否 | 组件路径 |
  | title | String | 否 | 菜单标题 |
  | path | String | 否 | 路由路径 |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "success",
  "data": {
    "results": [
      {
        "pk": "550e8400-e29b-41d4-a716-446655440000",
        "name": "System",
        "rank": 1,
        "path": "/system",
        "component": "",
        "menu_type": 0,
        "is_active": true,
        "method": null,
        "meta": {
          "pk": "550e8400-e29b-41d4-a716-446655440001",
          "title": "系统管理",
          "icon": "el-icon-setting",
          "is_show_menu": true,
          "is_keepalive": false
        },
        "parent": null,
        "model": [],
        "created_time": "2023-01-01T00:00:00",
        "updated_time": "2023-01-01T00:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1
  }
}
```

#### 4.2.2 创建菜单
- **接口地址**: `POST /api/system/menu`
- **功能描述**: 创建新菜单
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | name | String | 是 | 组件名称或权限代码 |
  | path | String | 是 | 路由路径或API路径 |
  | component | String | 否 | 组件路径 |
  | menu_type | Integer | 否 | 菜单类型(0-目录,1-菜单,2-权限) |
  | is_active | Boolean | 否 | 是否启用，默认true |
  | method | String | 否 | HTTP方法(GET,POST,PUT,DELETE,PATCH) |
  | meta | Object | 是 | 菜单元数据 |
  | parent | Object | 否 | 父菜单 |
  | model | Array | 否 | 关联模型 |
  | rank | Integer | 否 | 排序，默认9999 |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "菜单创建成功",
  "data": {
    "pk": "550e8400-e29b-41d4-a716-446655440000",
    "name": "System",
    "rank": 1,
    "path": "/system",
    "component": "",
    "menu_type": 0,
    "is_active": true,
    "method": null,
    "meta": {
      "pk": "550e8400-e29b-41d4-a716-446655440001",
      "title": "系统管理",
      "icon": "el-icon-setting",
      "is_show_menu": true,
      "is_keepalive": false
    },
    "parent": null,
    "model": [],
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00"
  }
}
```

#### 4.2.3 获取菜单详情
- **接口地址**: `GET /api/system/menu/{menu_id}`
- **功能描述**: 获取指定菜单的详细信息
- **路径参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | menu_id | UUID | 是 | 菜单ID |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "success",
  "data": {
    "pk": "550e8400-e29b-41d4-a716-446655440000",
    "name": "System",
    "rank": 1,
    "path": "/system",
    "component": "",
    "menu_type": 0,
    "is_active": true,
    "method": null,
    "meta": {
      "pk": "550e8400-e29b-41d4-a716-446655440001",
      "title": "系统管理",
      "icon": "el-icon-setting",
      "is_show_menu": true,
      "is_keepalive": false
    },
    "parent": null,
    "model": [],
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00"
  }
}
```

#### 4.2.4 更新菜单
- **接口地址**: `PUT /api/system/menu/{menu_id}`
- **功能描述**: 更新指定菜单的信息
- **路径参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | menu_id | UUID | 是 | 菜单ID |

- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | name | String | 否 | 组件名称或权限代码 |
  | path | String | 否 | 路由路径或API路径 |
  | component | String | 否 | 组件路径 |
  | menu_type | Integer | 否 | 菜单类型(0-目录,1-菜单,2-权限) |
  | is_active | Boolean | 否 | 是否启用 |
  | method | String | 否 | HTTP方法(GET,POST,PUT,DELETE,PATCH) |
  | meta | Object | 否 | 菜单元数据 |
  | parent | Object | 否 | 父菜单 |
  | model | Array | 否 | 关联模型 |
  | rank | Integer | 否 | 排序 |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "菜单更新成功",
  "data": {
    "pk": "550e8400-e29b-41d4-a716-446655440000",
    "name": "System",
    "rank": 1,
    "path": "/system",
    "component": "",
    "menu_type": 0,
    "is_active": true,
    "method": null,
    "meta": {
      "pk": "550e8400-e29b-41d4-a716-446655440001",
      "title": "系统管理",
      "icon": "el-icon-setting",
      "is_show_menu": true,
      "is_keepalive": false
    },
    "parent": null,
    "model": [],
    "created_time": "2023-01-01T00:00:00",
    "updated_time": "2023-01-01T00:00:00"
  }
}
```

#### 4.2.5 删除菜单
- **接口地址**: `DELETE /api/system/menu/{menu_id}`
- **功能描述**: 删除指定菜单
- **路径参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | menu_id | UUID | 是 | 菜单ID |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "菜单删除成功",
  "data": null
}
```

#### 4.2.6 批量删除菜单
- **接口地址**: `POST /api/system/menu/batch-delete`
- **功能描述**: 批量删除菜单
- **请求参数**:
  | 参数名 | 类型 | 必填 | 描述 |
  |--------|------|------|------|
  | pks | Array[UUID] | 是 | 菜单ID列表 |

- **响应示例**:
```json
{
  "code": 1000,
  "detail": "菜单批量删除成功",
  "data": null
}
```

## 5. 权限控制

所有API接口均需要相应的权限验证:
- 部门管理接口需要`dept:read`、`dept:create`、`dept:update`、`dept:delete`等权限
- 菜单管理接口需要`menu:read`、`menu:create`、`menu:update`、`menu:delete`等权限

## 6. 错误处理

系统使用统一的错误响应格式:
```json
{
  "code": 4000,
  "detail": "错误描述信息",
  "data": null
}
```

常见错误码:
- 1000: 成功
- 4000: 请求参数错误
- 4001: 数据已存在
- 4004: 数据不存在
- 4003: 权限不足
- 5000: 服务器内部错误

## 7. 注意事项

1. 所有时间字段均使用ISO8601格式
2. 删除操作为软删除，不会真正从数据库中移除数据
3. 部门删除前需要确保没有关联的用户和子部门
4. 菜单删除前需要确保没有关联的角色权限
5. 接口调用需要携带有效的JWT Token