# Ontology Explorer — 对话使用指南

本技能让 AI Agent 通过 `otlg` CLI 查询平台本体数据，覆盖供应链、金融、医疗、电商四大业务域。

## 前提条件

`otlg` 命令需已安装并可在 PATH 中访问。验证方式：

```bash
otlg --help
```

如未安装，参考项目 `scripts/INSTALL.md` 中的安装指引。

## 对话示例

### 场景 1: 探索有哪些业务域

**你说：** "帮我看看平台支持哪些业务域"

**Agent 会执行：**
```bash
otlg domains
otlg types
```

返回 4 个域（供应链、金融、医疗、电商）和所有对象类型的列表。

---

### 场景 2: 查看某个类型的详细结构

**你说：** "Supplier 有哪些属性？跟哪些类型有关联？"

**Agent 会执行：**
```bash
otlg type Supplier
```

返回 Supplier 的完整定义：11 个属性、关联的产品/采购单/合同链接、实例数量。

---

### 场景 3: 查询具体数据

**你说：** "帮我查几个供应商的数据看看"

**Agent 会执行：**
```bash
otlg instances Supplier --limit 5
```

返回 5 个供应商实例，包含名称、国家、评分、注册资本等详细信息。

**你也可以筛选：**
- "中国的供应商" → `otlg instances Supplier --filter country=CN`
- "状态是待支付的订单" → `otlg instances EcomOrder --filter status=待支付`
- "工资类交易" → `otlg instances Transaction --filter type=工资`

---

### 场景 4: 分析业务关系

**你说：** "SUP001 这个供应商关联了哪些数据？"

**Agent 会执行：**
```bash
otlg links-of Supplier SUP001
```

返回该供应商关联的产品、采购单、合同等所有关联实体。

**跨类型关系查询：**
- "Patient PAT001 有哪些诊断和就诊记录？" → `otlg links-of Patient PAT001`
- "用户 USR005 下过哪些订单？" → `otlg links-of EcomUser USR005`

---

### 场景 5: 数据统计分析

**你说：** "交易总金额是多少？"

**Agent 会执行：**
```bash
otlg aggregate Transaction amount --func sum
```

**更多统计场景：**
- "产品平均单价" → `otlg aggregate ScProduct unit_price --func avg`
- "订单最多的状态是哪个" → 先查询 `otlg instances EcomOrder` 再统计
- "贷款最大金额" → `otlg aggregate Loan principal --func max`
- "有多少笔交易" → `otlg aggregate Transaction amount --func count`

---

### 场景 6: 关键词搜索

**你说：** "帮我搜一下有没有糖尿病相关的诊断"

**Agent 会执行：**
```bash
otlg search Diagnosis "糖尿病"
```

返回所有描述中包含"糖尿病"的诊断记录。

**更多搜索场景：**
- "蓝牙相关的商品" → `otlg search EcomProduct "蓝牙"`
- "华联供应商" → `otlg search Supplier "华联"`
- "张某的患者" → `otlg search Patient "张"`

---

### 场景 7: 查看新增类型

**你说：** "金融域有哪些类型？信用卡和贷款的数据看一下"

**Agent 会执行：**
```bash
otlg types --domain finance
otlg type CreditCard
otlg instances CreditCard --limit 3
otlg type Loan
otlg instances Loan --limit 3
```

---

## 可用域概览

| 域 | 类型数 | 说明 |
|---|--------|------|
| supply_chain | 7 | Supplier, ScProduct, Warehouse, PurchaseOrder, Shipment, Contract, Inventory |
| finance | 6 | FiCustomer, Account, Transaction, FiProduct, CreditCard, Loan |
| healthcare | 7 | Patient, Provider, Diagnosis, Medication, Encounter, LabResult, InsuranceClaim |
| ecommerce | 6 | EcomUser, Merchant, EcomProduct, EcomOrder, Review, Coupon |

总计 26 个对象类型、26 个关系链接、10 个操作类型、约 1500 个实例。

## 输出格式

所有命令输出 JSON 到 stdout。Agent 会直接读取 JSON 并以自然语言向你汇报结果。