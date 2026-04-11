# Ontology Explorer — 架构与概念说明

## 一、Skill 处理逻辑

### 1.1 Skill 发现与加载

```
Claude Code 启动
  ↓
扫描 .claude/skills/*/SKILL.md
  ↓
读取 YAML frontmatter 中的 name + description
  ↓
注入到系统提示词中（轻量级元数据）
  ↓
用户提问时，Claude 匹配 description → 自动触发
  ↓
通过 Skill 工具加载完整 SKILL.md 内容
  ↓
按照 Skill 指导执行 CLI 命令
```

### 1.2 交互流程

```
用户自然语言提问
  ↓
Claude 匹配 ontology-explorer skill（基于 description）
  ↓
根据 SKILL.md 中的 Exploration Workflow 决定执行哪些命令
  ↓
通过 Bash 工具执行 otlg CLI 命令
  ↓
解析 JSON 输出，用自然语言回答用户
```

### 1.3 Skill 文件结构

```
.claude/skills/ontology-explorer/
├── SKILL.md           # 主文件（必需）：frontmatter + 指导内容
└── ARCHITECTURE.md    # 本文件：架构说明（辅助文档）
```

**SKILL.md 组成：**

```
---
name: ontology-explorer                    # 技能名称（≤64字符）
description: Use when exploring...         # 触发条件描述（≤1024字符）
---
# 正文内容（Markdown）
├── Prerequisites         # 前置条件
├── CLI Command Reference # 命令速查表
├── Exploration Workflow  # 探索工作流
├── Common Query Patterns # 常见查询模式
├── Available Domains     # 领域一览
├── Output Format         # 输出格式说明
└── Rules                 # 使用规则
```

---

## 二、本体（Ontology）概念模型

### 2.1 核心概念总览

```
┌─────────────────────────────────────────────────────┐
│                  Ontology Definition                │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Object Type  │  │  Link Type   │                 │
│  │  （对象类型）  │  │ （关系类型）  │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                         │
│  ┌──────┴───────┐  ┌──────┴───────┐                 │
│  │  Property    │  │  Cardinality │                 │
│  │  （属性）     │  │ （基数）      │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Interface    │  │  Action Type │                 │
│  │  （接口）     │  │ （操作类型）  │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                     │
│  ┌──────────────────────────────────┐               │
│  │        Instance Data             │               │
│  │        （实例数据）                │               │
│  └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 2.2 Object Type（对象类型）

**定义：** 业务实体的结构化描述，类似数据库中的"表"或编程中的"类"。

**核心字段：**

| 字段 | 含义 | 示例 |
|------|------|------|
| `apiName` | API 标识符（唯一） | `Supplier` |
| `displayName` | 人类可读名称 | 供应商 |
| `primaryKeyPropertyApiName` | 主键属性 | `id` |
| `titlePropertyApiName` | 显示标题的属性 | `name` |
| `properties` | 属性列表 | 见下方 |
| `domain` | 所属业务领域 | `supply_chain` |
| `implementsInterfaces` | 实现的接口 | `["Auditable"]` |

**本项目中的 19 个对象类型：**

```
supply_chain          finance              healthcare           ecommerce
─────────────         ───────              ──────────           ─────────
Supplier              FiCustomer           Patient              EcomUser
ScProduct             Account              Provider             Merchant
Warehouse             Transaction          Diagnosis            EcomProduct
PurchaseOrder         FiProduct            Medication           EcomOrder
Shipment                                 Encounter            Review
```

### 2.3 Property（属性）

**定义：** 对象类型的数据字段，类似数据库中的"列"。

**支持的数据类型：**

| 类型 | 说明 | 示例 |
|------|------|------|
| `string` | 文本 | `name`, `country` |
| `integer` | 整数 | `stock`, `capacity` |
| `decimal` | 小数 | `unit_price`, `balance` |
| `boolean` | 布尔 | `verified` |
| `date` | 日期 | `dob`, `opened_at` |
| `timestamp` | 时间戳 | `created_at` |

**关键属性标记：**

- `indexedForSearch: true` — 支持全文搜索（如 `name`、`description`）
- `array: true` — 数组类型

### 2.4 Link Type（关系类型）

**定义：** 描述两个对象类型之间的关联关系，类似数据库中的"外键"或"关联表"。

**三种基数模式：**

```
OneToMany（一对多）           ManyToMany（多对多）         OneToOne（一对一）
─────────────────           ──────────────────          ──────────────────
Supplier ──1:N──→ Product   Student ←N:M→ Course       User ──1:1──→ Profile
  一个供应商有多个产品          学生选修多门课程              一个用户对应一个档案
  Product.supplier_id         通过中间表关联               一对一映射
  是外键字段
```

**Link Type 结构：**

```json
{
  "apiName": "supplier_products",
  "cardinality": "OneToMany",
  "source": {
    "objectApiName": "Supplier",
    "apiName": "products",
    "displayName": "产品"
  },
  "target": {
    "objectApiName": "ScProduct",
    "apiName": "supplier",
    "displayName": "供应商"
  },
  "foreignKeyProperty": "supplier_id"
}
```

**本项目中的 16 个关系：**

```
supply_chain                          finance
────────────                          ───────
Supplier ──1:N──→ ScProduct           FiCustomer ──1:N──→ Account
Supplier ──1:N──→ PurchaseOrder       Account ──1:N──→ Transaction (out)
Warehouse ──1:N──→ Shipment           Account ──1:N──→ Transaction (in)
PurchaseOrder ──1:N──→ Shipment

healthcare                            ecommerce
──────────                            ─────────
Patient ──1:N──→ Diagnosis            EcomUser ──1:N──→ EcomOrder
Patient ──1:N──→ Encounter            Merchant ──1:N──→ EcomProduct
Provider ──1:N──→ Diagnosis           EcomProduct ──1:N──→ EcomOrder
Provider ──1:N──→ Encounter           EcomProduct ──1:N──→ Review
                                      EcomUser ──1:N──→ Review
```

### 2.5 Interface Type（接口类型）

**定义：** 一组共享属性的抽象，多个对象类型可以"实现"同一个接口，实现属性复用。

**类比：** 类似编程中的 interface/trait，或数据库设计中的"公共字段模式"。

**本项目中的接口：**

```
Auditable（可审计）
├── created_at: timestamp
└── 被所有 19 个对象类型实现

GeoLocated（地理定位）
├── latitude: decimal
├── longitude: decimal
├── address: string
└── 被 Warehouse, Provider, Merchant 实现
```

### 2.6 Action Type（操作类型）

**定义：** 可对对象执行的操作，类似 API 的"端点"或编程中的"方法"。

| Action | 目标类型 | 领域 | 说明 |
|--------|---------|------|------|
| `createPurchaseOrder` | PurchaseOrder | supply_chain | 创建采购单 |
| `updateShipmentStatus` | Shipment | supply_chain | 更新发货状态 |
| `processTransaction` | Transaction | finance | 发起交易 |
| `recordDiagnosis` | Diagnosis | healthcare | 记录诊断 |
| `placeOrder` | EcomOrder | ecommerce | 用户下单 |
| `submitReview` | Review | ecommerce | 提交评价 |

每个 Action 包含 `parameters`（参数列表），定义了执行操作所需的输入。

---

## 三、查询能力矩阵

```
                    元数据（Metadata）        实例数据（Instances）
                    ─────────────────        ────────────────────
浏览/列表            otlg types               otlg instances
                    otlg links               otlg search
                    otlg interfaces
                    otlg actions
                    otlg domains

查看详情            otlg type <name>         otlg instance <type> <pk>

统计/聚合            —                        otlg aggregate <type> <field> --func

关系遍历            otlg links --source      otlg links-of <type> <pk>

过滤                otlg types --domain      otlg instances --filter key=value
```

---

## 四、数据存储结构

```
ontology_explorer/data/
├── ontology.json                    # 本体定义（所有类型的 schema）
│   ├── objectTypes: [...]           #   19 个对象类型定义
│   ├── linkTypes: [...]             #   16 个关系类型定义
│   ├── interfaceTypes: [...]        #    2 个接口类型定义
│   └── actionTypes: [...]           #    6 个操作类型定义
└── instances/
    ├── supply_chain.json            #   5 种类型共 ~120 条实例
    ├── finance.json                 #   4 种类型共 ~160 条实例
    ├── healthcare.json              #   5 种类型共 ~175 条实例
    └── ecommerce.json               #   5 种类型共 ~170 条实例
                                     #   总计 728 条实例
```

数据由 `seed.py` 生成（`random.seed(42)` 保证可重复），通过 `OntologyStore` 类读写。