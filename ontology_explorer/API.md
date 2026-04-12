# Ontology Explorer REST API 规范

本文档定义了 `otlg --backend rest` 模式下，API 服务端需要实现的接口规范。

## 认证

所有请求通过 `Authorization` Header 传递 API Key（可选）：

```
Authorization: Bearer <api_key>
```

`api_key` 通过以下方式之一配置：
- CLI 参数：`--api-key <key>`
- 环境变量：`OTLG_API_KEY`
- 配置文件：`~/.otlg/config.json` 中的 `api_key` 字段

## 资源层级关系

```
Domain (业务域)
  ├── ObjectType (对象类型)
  │    ├── PropertyType (属性)   — 嵌入在 type 定义中
  │    └── Instance (实例)       — /types/{type}/instances
  └── ActionType (操作类型)      — /domains/{domain}/actions

LinkType (链接)    — 顶层资源，连接两个 ObjectType
InterfaceType (接口) — 顶层资源，跨域共享
```

## 端点概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/domains` | 列出所有业务域 |
| GET | `/domains/{domain}/types` | 列出某域下的对象类型 |
| GET | `/domains/{domain}/actions` | 列出某域下的操作类型 |
| GET | `/types` | 列出所有对象类型（跨域） |
| GET | `/types/{type}` | 获取单个类型的完整定义 |
| GET | `/types/{type}/instances` | 分页获取实例列表 |
| GET | `/types/{type}/instances/{pk}` | 获取单个实例 |
| GET | `/types/{type}/search?q=` | 搜索实例 |
| GET | `/types/{type}/aggregate/{field}?func=` | 聚合计算 |
| GET | `/links` | 列出所有链接类型 |
| GET | `/links?source={type}` | 按类型过滤链接 |
| GET | `/interfaces` | 列出所有接口类型 |

---

## 1. GET /domains

列出所有业务域。

### 响应

`200 OK`

```json
[
  { "apiName": "supply_chain", "displayName": "Supply Chain" },
  { "apiName": "finance", "displayName": "Finance" },
  { "apiName": "healthcare", "displayName": "Healthcare" },
  { "apiName": "ecommerce", "displayName": "Ecommerce" }
]
```

**CLI 映射：** `otlg domains`

---

## 2. GET /domains/{domain}/types

列出某域下的所有对象类型摘要。

### 路径参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `domain` | 域 apiName | `supply_chain`, `finance` |

### 响应

`200 OK`

```json
[
  {
    "apiName": "Supplier",
    "displayName": "供应商",
    "pluralDisplayName": "供应商列表",
    "description": "供应链中的供应商实体",
    "domain": "supply_chain",
    "status": "active",
    "propertyCount": 11
  },
  {
    "apiName": "ScProduct",
    "displayName": "产品",
    "pluralDisplayName": "产品列表",
    "description": "供应链中的产品",
    "domain": "supply_chain",
    "status": "active",
    "propertyCount": 12
  }
]
```

### 错误

`404 Not Found` — 域不存在。

**CLI 映射：** `otlg types --domain supply_chain`

---

## 3. GET /domains/{domain}/actions

列出某域下的所有操作类型。

### 路径参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `domain` | 域 apiName | `finance` |

### 响应

`200 OK`

```json
[
  {
    "apiName": "processTransaction",
    "displayName": "处理交易",
    "description": "发起一笔资金转账交易",
    "parameters": [
      {
        "apiName": "from_account",
        "displayName": "转出账户",
        "type": "string",
        "description": "",
        "required": true
      }
    ],
    "targetObjectType": "Transaction",
    "domain": "finance",
    "status": "active"
  }
]
```

**CLI 映射：** `otlg actions --domain finance`

---

## 4. GET /types

列出所有对象类型（跨域）。

### 响应

`200 OK`

```json
[
  {
    "apiName": "Supplier",
    "displayName": "供应商",
    "pluralDisplayName": "供应商列表",
    "description": "供应链中的供应商实体",
    "domain": "supply_chain",
    "status": "active",
    "propertyCount": 11
  },
  {
    "apiName": "FiCustomer",
    "displayName": "客户",
    "pluralDisplayName": "客户列表",
    "description": "金融服务客户",
    "domain": "finance",
    "status": "active",
    "propertyCount": 10
  }
]
```

**CLI 映射：** `otlg types`

---

## 5. GET /types/{type}

获取单个对象类型的完整定义，包含属性列表、关联链接、实例数量。

### 路径参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `type` | 对象类型 apiName | `Supplier` |

### 响应

`200 OK`

```json
{
  "apiName": "Supplier",
  "displayName": "供应商",
  "pluralDisplayName": "供应商列表",
  "primaryKeyPropertyApiName": "id",
  "titlePropertyApiName": "name",
  "properties": [
    {
      "apiName": "id",
      "displayName": "供应商ID",
      "type": "string",
      "description": "",
      "indexedForSearch": false,
      "array": false
    },
    {
      "apiName": "name",
      "displayName": "供应商名称",
      "type": "string",
      "description": "",
      "indexedForSearch": true,
      "array": false
    }
  ],
  "description": "供应链中的供应商实体",
  "icon": {
    "locator": "people",
    "color": "#F2994A"
  },
  "status": "active",
  "domain": "supply_chain",
  "implementsInterfaces": ["Auditable"],
  "links": [
    {
      "apiName": "supplier_products",
      "direction": "outgoing",
      "cardinality": "OneToMany",
      "relatedObject": "ScProduct",
      "relatedDisplayName": "产品",
      "foreignKeyProperty": "supplier_id"
    },
    {
      "apiName": "supplier_products",
      "direction": "incoming",
      "cardinality": "OneToMany",
      "relatedObject": "ScProduct",
      "relatedDisplayName": "供应商"
    }
  ],
  "instanceCount": 20
}
```

**links 说明：** `direction=outgoing` 表示从当前类型出发的链接（目标通过 foreignKeyProperty 关联）；`direction=incoming` 表示指向当前类型的链接。

### 错误

`404 Not Found` — 类型不存在。

**CLI 映射：** `otlg type Supplier`

---

## 6. GET /types/{type}/instances

分页获取指定类型的实例列表。

> 生产数据量可能很大（百万级），必须支持分页。

### 路径参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `type` | 对象类型 apiName | `Supplier`, `Transaction` |

### 查询参数

| 参数 | 类型 | 默认值 | 说明 | 示例 |
|------|------|--------|------|------|
| `limit` | int | 50 | 最大返回数量（上限 500） | `?limit=100` |
| `offset` | int | 0 | 偏移量 | `?offset=200` |
| `filter` | string | - | 过滤条件 `key=value`，可重复 | `?filter country=CN` |

### 响应

`200 OK`

```json
{
  "typeApiName": "Supplier",
  "total": 20,
  "limit": 50,
  "offset": 0,
  "instances": [
    {
      "id": "SUP001",
      "name": "华联供应链",
      "country": "CN",
      "rating": 4.6,
      "contact_email": "procurement@华联.com",
      "status": "正常"
    }
  ]
}
```

实例属性 key 使用 **snake_case**（与 PropertyType.apiName 一致）。

### 错误

`404 Not Found` — 类型不存在。

**CLI 映射：** `otlg instances Supplier --limit 10 --filter country=CN`

---

## 7. GET /types/{type}/instances/{pk}

获取单个实例（按主键）。

### 路径参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `type` | 对象类型 apiName | `Supplier` |
| `pk` | 主键值 | `SUP001` |

### 响应

`200 OK`

```json
{
  "id": "SUP001",
  "name": "华联供应链",
  "country": "CN",
  "rating": 4.6,
  "contact_email": "procurement@华联.com",
  "contact_phone": "+86-15746317213",
  "address": "CN business district #7",
  "business_scope": "原材料,包装材料",
  "registered_capital": 5000,
  "status": "正常",
  "created_at": "2022-01-30T20:27:37"
}
```

### 错误

`404 Not Found` — 类型或实例不存在。

**CLI 映射：** `otlg instance Supplier SUP001`

---

## 8. GET /types/{type}/search?q={query}

在指定类型的可搜索字段（`indexedForSearch: true`）中全文搜索。

### 路径参数

| 参数 | 说明 |
|------|------|
| `type` | 对象类型 apiName |

### 查询参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `q` | 是 | 搜索关键词 |

### 响应

`200 OK`

```json
[
  {
    "id": "DIA002",
    "patient_id": "PAT007",
    "icd_code": "E11.9",
    "description": "2型糖尿病 - 空腹血糖升高，口渴多饮",
    "severity": "轻度"
  }
]
```

**CLI 映射：** `otlg search Diagnosis "糖尿病"`

---

## 9. GET /types/{type}/aggregate/{field}?func={fn}

对数值字段进行聚合计算。

### 路径参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `type` | 对象类型 apiName | `Transaction` |
| `field` | 聚合字段名 | `amount` |

### 查询参数

| 参数 | 必填 | 说明 | 取值 |
|------|------|------|------|
| `func` | 是 | 聚合函数 | `count`, `sum`, `avg`, `min`, `max` |

### 响应

`200 OK`

```json
{
  "typeApiName": "Transaction",
  "field": "amount",
  "function": "sum",
  "totalInstances": 150,
  "nonNullValues": 150,
  "value": 5285125.15
}
```

**CLI 映射：** `otlg aggregate Transaction amount --func sum`

---

## 10. GET /links

列出所有链接类型。

### 查询参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `source` | string | 按源或目标类型过滤 | `?source=Supplier` |

### 响应

`200 OK`

```json
[
  {
    "apiName": "supplier_products",
    "cardinality": "OneToMany",
    "source": {
      "objectApiName": "Supplier",
      "apiName": "products",
      "displayName": "产品",
      "pluralDisplayName": "产品列表"
    },
    "target": {
      "objectApiName": "ScProduct",
      "apiName": "supplier",
      "displayName": "供应商",
      "pluralDisplayName": ""
    },
    "foreignKeyProperty": "supplier_id",
    "status": "active"
  }
]
```

**cardinality 取值**: `OneToMany`, `ManyToMany`, `OneToOne`

**CLI 映射：** `otlg links` / `otlg links --source Supplier`

---

## 11. GET /interfaces

列出所有接口类型。

### 响应

`200 OK`

```json
[
  {
    "apiName": "Auditable",
    "displayName": "可审计",
    "description": "包含审计字段的接口，所有核心业务对象均实现此接口",
    "properties": [
      {
        "apiName": "created_at",
        "displayName": "创建时间",
        "type": "timestamp"
      }
    ],
    "extendsInterfaces": [],
    "status": "active"
  },
  {
    "apiName": "GeoLocated",
    "displayName": "地理定位",
    "description": "包含地理位置信息的接口",
    "properties": [
      { "apiName": "latitude", "displayName": "纬度", "type": "decimal" },
      { "apiName": "longitude", "displayName": "经度", "type": "decimal" },
      { "apiName": "address", "displayName": "地址", "type": "string" }
    ],
    "extendsInterfaces": [],
    "status": "active"
  }
]
```

**CLI 映射：** `otlg interfaces`

---

## 错误响应格式

所有错误响应统一格式：

```json
{
  "error": "error_code",
  "message": "Human-readable error message"
}
```

| HTTP 状态码 | error | 说明 |
|-------------|-------|------|
| 400 | `bad_request` | 请求参数错误 |
| 401 | `unauthorized` | API Key 缺失或无效 |
| 404 | `not_found` | 资源不存在 |
| 429 | `rate_limited` | 请求频率超限 |
| 500 | `internal_error` | 服务端错误 |

---

## PropertyType Schema

```json
{
  "apiName": "name",
  "displayName": "供应商名称",
  "type": "string",
  "description": "",
  "indexedForSearch": true,
  "array": false
}
```

**type 取值**: `string`, `integer`, `decimal`, `boolean`, `timestamp`, `date`

---

## 数据格式约定

- 时间戳：`YYYY-MM-DDTHH:MM:SS`（ISO 8601，不带时区）
- 日期：`YYYY-MM-DD`
- 金额：保留 2 位小数的数字
- 布尔值：JSON `true` / `false`
- 空值：JSON `null`

---

## 附录：CLI 命令 → API 端点完整映射

| CLI 命令 | API 端点 |
|----------|----------|
| `otlg domains` | `GET /domains` |
| `otlg types` | `GET /types` |
| `otlg types --domain finance` | `GET /domains/finance/types` |
| `otlg type Supplier` | `GET /types/Supplier` |
| `otlg links` | `GET /links` |
| `otlg links --source Supplier` | `GET /links?source=Supplier` |
| `otlg interfaces` | `GET /interfaces` |
| `otlg actions` | `GET /domains` → 遍历各域 `GET /domains/{d}/actions` |
| `otlg actions --domain finance` | `GET /domains/finance/actions` |
| `otlg instances Supplier --limit 10` | `GET /types/Supplier/instances?limit=10` |
| `otlg instance Supplier SUP001` | `GET /types/Supplier/instances/SUP001` |
| `otlg search Patient "张"` | `GET /types/Patient/search?q=张` |
| `otlg aggregate Tx amount --func sum` | `GET /types/Transaction/aggregate/amount?func=sum` |
| `otlg links-of Supplier SUP001` | `GET /links?source=Supplier` + 遍历出链接调用 `GET /types/{target}/instances/{pk}` |
