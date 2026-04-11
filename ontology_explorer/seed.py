"""Seed script: generate ontology definition and instance data for 4 business domains."""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from pathlib import Path

from .core.models import (
    ActionParameter,
    ActionType,
    InterfaceProperty,
    InterfaceType,
    LinkType,
    LinkTypeSide,
    ObjectType,
    OntologyDefinition,
    PropertyType,
)
from .core.store import OntologyStore


# ── Helpers ────────────────────────────────────────────────────────────────

def _id(prefix: str, n: int, width: int = 3) -> str:
    return f"{prefix}{str(n).zfill(width)}"


def _rand_date(start_year: int = 2023, end_year: int = 2025) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    d = start + timedelta(days=random.randint(0, delta.days))
    return d.strftime("%Y-%m-%d")


def _rand_timestamp(start_year: int = 2023, end_year: int = 2025) -> str:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31, 23, 59, 59)
    delta = (end - start).total_seconds()
    d = start + timedelta(seconds=random.randint(0, int(delta)))
    return d.strftime("%Y-%m-%dT%H:%M:%S")


def _rand_str(n: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


# ── Domain data pools ─────────────────────────────────────────────────────

SUPPLIERS = [
    ("华联供应链", "CN"), ("GlobalSource Inc.", "US"), ("EuroParts GmbH", "DE"),
    ("東京精密工業", "JP"), ("Samsung Materials", "KR"), ("Tata Components", "IN"),
    ("Acme Supply Co.", "US"), ("华南电子科技", "CN"), ("Bosch Logistics", "DE"),
    ("LG Materials", "KR"), ("Foxconn Supply", "CN"), ("Intel Components", "US"),
    ("Toyota Parts", "JP"), ("Hitachi Materials", "JP"), ("Hyundai Supply", "KR"),
    ("联想供应链", "CN"), ("Dell Logistics", "US"), ("Siemens Parts", "DE"),
    ("松下电子部品", "JP"), ("SK Materials", "KR"),
]

PRODUCT_CATEGORIES = ["电子元器件", "机械零件", "原材料", "包装材料", "办公用品"]
PRODUCT_NAMES = [
    "LED显示屏模组", "伺服电机", "碳纤维板材", "铝合金外壳", "USB-C连接器",
    "锂电池组", "散热风扇", "光纤线缆", "压力传感器", "控制芯片",
    "电源模块", "密封垫圈", "液压阀", "精密轴承", "导热硅脂",
]

COUNTRIES = ["CN", "US", "DE", "JP", "KR", "IN", "GB", "FR"]
WAREHOUSE_CITIES = [
    ("上海仓", "上海市浦东新区"), ("深圳仓", "深圳市南山区"), ("东京仓", "東京都品川区"),
    ("纽约仓", "New York, NY"), ("法兰克福仓", "Frankfurt am Main"), ("首尔仓", "서울시 강남구"),
]

CUSTOMER_NAMES = [
    "张伟", "李娜", "王芳", "John Smith", "Emily Johnson", "Michael Brown",
    "Sarah Davis", "Robert Wilson", "Maria Garcia", "David Martinez",
    "田中太郎", "佐藤花子", "김민수", "이수진", "محمد أحمد",
    "Marie Dupont", "Hans Mueller", "Raj Patel", "Anna Kowalski", "Carlos Silva",
]

MEDICATION_NAMES = [
    "阿莫西林胶囊", "布洛芬缓释片", "头孢克洛分散片", "氯雷他定片",
    "奥美拉唑肠溶胶囊", "二甲双胍缓释片", "阿托伐他汀钙片", "硝苯地平控释片",
    "Ibuprofen", "Amoxicillin", "Metformin", "Atorvastatin", "Lisinopril",
    "Omeprazole", "Levothyroxine", "Amlodipine", "Metoprolol", "Losartan",
]

ICD_CODES = [
    ("J06.9", "急性上呼吸道感染"), ("K21.0", "胃食管反流病"), ("E11.9", "2型糖尿病"),
    ("I10", "原发性高血压"), ("M54.5", "下背痛"), ("J45.909", "支气管哮喘"),
    ("K58.9", "肠易激综合征"), ("G43.909", "偏头痛"), ("L30.9", "皮炎"),
    ("N39.0", "尿路感染"),
]

ECOM_CATEGORIES = ["电子产品", "服装鞋帽", "食品饮料", "家居用品", "美妆个护", "图书音像"]
ECOM_PRODUCTS = [
    "无线蓝牙耳机", "智能手环", "纯棉T恤", "运动跑鞋", "有机绿茶",
    "不锈钢保温杯", "竹纤维毛巾", "洗面奶", "畅销小说", "蓝牙音箱",
    "平板保护壳", "速干运动裤", "坚果礼盒", "香薰蜡烛", "面膜套装",
]

MERCHANT_NAMES = [
    "数码旗舰馆", "时尚衣橱", "品味零食铺", "温馨家居坊", "美丽研究所",
    "TechZone", "StyleHub", "BookWorm", "GadgetPro", "FitGear",
]

DIAGNOSES = [
    ("J06.9", "急性上呼吸道感染", "发热、咽痛、咳嗽3天"),
    ("K21.0", "胃食管反流病", "反酸、烧心，餐后加重"),
    ("E11.9", "2型糖尿病", "空腹血糖升高，口渴多饮"),
    ("I10", "原发性高血压", "血压升高1年余"),
    ("M54.5", "下背痛", "腰部酸痛，久坐加重"),
    ("J45.909", "支气管哮喘", "反复喘息、气促"),
    ("K58.9", "肠易激综合征", "腹痛、腹泻交替"),
    ("G43.909", "偏头痛", "反复发作性头痛"),
]


# ── Ontology definition builder ────────────────────────────────────────────

def _build_supply_chain_types() -> tuple[list[ObjectType], list[LinkType], list[ActionType]]:
    objects = [
        ObjectType(
            api_name="Supplier",
            display_name="供应商",
            plural_display_name="供应商列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="供应链中的供应商实体",
            icon="people",
            icon_color="#F2994A",
            domain="supply_chain",
            properties=[
                PropertyType("id", "供应商ID", "string"),
                PropertyType("name", "供应商名称", "string", indexed_for_search=True),
                PropertyType("country", "国家", "string"),
                PropertyType("rating", "评分", "decimal"),
                PropertyType("contact_email", "联系邮箱", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="ScProduct",
            display_name="产品",
            plural_display_name="产品列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="供应链中的产品",
            icon="box",
            icon_color="#2D9CDB",
            domain="supply_chain",
            properties=[
                PropertyType("id", "产品ID", "string"),
                PropertyType("name", "产品名称", "string", indexed_for_search=True),
                PropertyType("category", "类别", "string"),
                PropertyType("unit_price", "单价", "decimal"),
                PropertyType("weight", "重量(kg)", "decimal"),
                PropertyType("supplier_id", "供应商ID", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Warehouse",
            display_name="仓库",
            plural_display_name="仓库列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="仓储设施",
            icon="office",
            icon_color="#27AE60",
            domain="supply_chain",
            properties=[
                PropertyType("id", "仓库ID", "string"),
                PropertyType("name", "仓库名称", "string", indexed_for_search=True),
                PropertyType("location", "位置", "string"),
                PropertyType("capacity", "容量", "integer"),
                PropertyType("latitude", "纬度", "decimal"),
                PropertyType("longitude", "经度", "decimal"),
                PropertyType("address", "地址", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable", "GeoLocated"],
        ),
        ObjectType(
            api_name="PurchaseOrder",
            display_name="采购单",
            plural_display_name="采购单列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="采购订单",
            icon="document",
            icon_color="#EB5757",
            domain="supply_chain",
            properties=[
                PropertyType("id", "采购单ID", "string"),
                PropertyType("supplier_id", "供应商ID", "string"),
                PropertyType("total_amount", "总金额", "decimal"),
                PropertyType("status", "状态", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Shipment",
            display_name="发货单",
            plural_display_name="发货单列表",
            primary_key_property_api_name="id",
            title_property_api_name="tracking_number",
            description="物流发货记录",
            icon="truck",
            icon_color="#9B51E0",
            domain="supply_chain",
            properties=[
                PropertyType("id", "发货单ID", "string"),
                PropertyType("purchase_order_id", "采购单ID", "string"),
                PropertyType("warehouse_id", "仓库ID", "string"),
                PropertyType("tracking_number", "追踪号", "string", indexed_for_search=True),
                PropertyType("status", "状态", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
    ]

    links = [
        LinkType(
            api_name="supplier_products",
            cardinality="OneToMany",
            source=LinkTypeSide("Supplier", "products", "产品", "产品列表"),
            target=LinkTypeSide("ScProduct", "supplier", "供应商"),
            foreign_key_property="supplier_id",
        ),
        LinkType(
            api_name="supplier_purchase_orders",
            cardinality="OneToMany",
            source=LinkTypeSide("Supplier", "purchase_orders", "采购单", "采购单列表"),
            target=LinkTypeSide("PurchaseOrder", "supplier", "供应商"),
            foreign_key_property="supplier_id",
        ),
        LinkType(
            api_name="warehouse_shipments",
            cardinality="OneToMany",
            source=LinkTypeSide("Warehouse", "shipments", "发货单", "发货单列表"),
            target=LinkTypeSide("Shipment", "warehouse", "仓库"),
            foreign_key_property="warehouse_id",
        ),
        LinkType(
            api_name="purchase_order_shipments",
            cardinality="OneToMany",
            source=LinkTypeSide("PurchaseOrder", "shipments", "发货单", "发货单列表"),
            target=LinkTypeSide("Shipment", "purchase_order", "采购单"),
            foreign_key_property="purchase_order_id",
        ),
    ]

    actions = [
        ActionType(
            api_name="createPurchaseOrder",
            display_name="创建采购单",
            description="创建新的采购订单",
            target_object_type="PurchaseOrder",
            domain="supply_chain",
            parameters=[
                ActionParameter("supplier_id", "供应商ID", "string", required=True),
                ActionParameter("items", "采购明细", "string", required=True),
            ],
        ),
        ActionType(
            api_name="updateShipmentStatus",
            display_name="更新发货状态",
            description="更新发货单的物流状态",
            target_object_type="Shipment",
            domain="supply_chain",
            parameters=[
                ActionParameter("shipment_id", "发货单ID", "string", required=True),
                ActionParameter("status", "新状态", "string", required=True),
            ],
        ),
    ]

    return objects, links, actions


def _build_finance_types() -> tuple[list[ObjectType], list[LinkType], list[ActionType]]:
    objects = [
        ObjectType(
            api_name="FiCustomer",
            display_name="客户",
            plural_display_name="客户列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="金融服务客户",
            icon="person",
            icon_color="#2F80ED",
            domain="finance",
            properties=[
                PropertyType("id", "客户ID", "string"),
                PropertyType("name", "客户姓名", "string", indexed_for_search=True),
                PropertyType("tier", "客户等级", "string"),
                PropertyType("risk_level", "风险等级", "string"),
                PropertyType("kyc_status", "KYC状态", "string"),
                PropertyType("created_at", "开户时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Account",
            display_name="账户",
            plural_display_name="账户列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="银行账户",
            icon="bank-account",
            icon_color="#27AE60",
            domain="finance",
            properties=[
                PropertyType("id", "账户ID", "string"),
                PropertyType("customer_id", "客户ID", "string"),
                PropertyType("type", "账户类型", "string"),
                PropertyType("balance", "余额", "decimal"),
                PropertyType("currency", "币种", "string"),
                PropertyType("opened_at", "开户日期", "date"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Transaction",
            display_name="交易",
            plural_display_name="交易列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="资金交易记录",
            icon="exchange",
            icon_color="#F2994A",
            domain="finance",
            properties=[
                PropertyType("id", "交易ID", "string"),
                PropertyType("from_account", "转出账户", "string"),
                PropertyType("to_account", "转入账户", "string"),
                PropertyType("amount", "金额", "decimal"),
                PropertyType("type", "交易类型", "string"),
                PropertyType("timestamp", "交易时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="FiProduct",
            display_name="金融产品",
            plural_display_name="金融产品列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="理财产品、贷款等金融产品",
            icon="layers",
            icon_color="#9B51E0",
            domain="finance",
            properties=[
                PropertyType("id", "产品ID", "string"),
                PropertyType("name", "产品名称", "string", indexed_for_search=True),
                PropertyType("category", "产品类别", "string"),
                PropertyType("interest_rate", "利率", "decimal"),
                PropertyType("min_investment", "最低投资额", "decimal"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
    ]

    links = [
        LinkType(
            api_name="customer_accounts",
            cardinality="OneToMany",
            source=LinkTypeSide("FiCustomer", "accounts", "账户", "账户列表"),
            target=LinkTypeSide("Account", "customer", "客户"),
            foreign_key_property="customer_id",
        ),
        LinkType(
            api_name="account_transactions_out",
            cardinality="OneToMany",
            source=LinkTypeSide("Account", "outgoing_transactions", "转出交易", "转出交易列表"),
            target=LinkTypeSide("Transaction", "from_account_ref", "转出账户"),
            foreign_key_property="from_account",
        ),
        LinkType(
            api_name="account_transactions_in",
            cardinality="OneToMany",
            source=LinkTypeSide("Account", "incoming_transactions", "转入交易", "转入交易列表"),
            target=LinkTypeSide("Transaction", "to_account_ref", "转入账户"),
            foreign_key_property="to_account",
        ),
    ]

    actions = [
        ActionType(
            api_name="processTransaction",
            display_name="处理交易",
            description="发起一笔资金转账交易",
            target_object_type="Transaction",
            domain="finance",
            parameters=[
                ActionParameter("from_account", "转出账户", "string", required=True),
                ActionParameter("to_account", "转入账户", "string", required=True),
                ActionParameter("amount", "金额", "decimal", required=True),
                ActionParameter("type", "交易类型", "string", required=True),
            ],
        ),
    ]

    return objects, links, actions


def _build_healthcare_types() -> tuple[list[ObjectType], list[LinkType], list[ActionType]]:
    objects = [
        ObjectType(
            api_name="Patient",
            display_name="患者",
            plural_display_name="患者列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="患者基本信息",
            icon="person",
            icon_color="#EB5757",
            domain="healthcare",
            properties=[
                PropertyType("id", "患者ID", "string"),
                PropertyType("name", "姓名", "string", indexed_for_search=True),
                PropertyType("dob", "出生日期", "date"),
                PropertyType("blood_type", "血型", "string"),
                PropertyType("insurance_id", "保险ID", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Provider",
            display_name="医疗机构",
            plural_display_name="医疗机构列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="医院、诊所等医疗机构",
            icon="office",
            icon_color="#2D9CDB",
            domain="healthcare",
            properties=[
                PropertyType("id", "机构ID", "string"),
                PropertyType("name", "机构名称", "string", indexed_for_search=True),
                PropertyType("type", "机构类型", "string"),
                PropertyType("location", "位置", "string"),
                PropertyType("accreditation", "认证等级", "string"),
                PropertyType("latitude", "纬度", "decimal"),
                PropertyType("longitude", "经度", "decimal"),
                PropertyType("address", "地址", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable", "GeoLocated"],
        ),
        ObjectType(
            api_name="Diagnosis",
            display_name="诊断",
            plural_display_name="诊断列表",
            primary_key_property_api_name="id",
            title_property_api_name="description",
            description="患者诊断记录",
            icon="clipboard",
            icon_color="#F2994A",
            domain="healthcare",
            properties=[
                PropertyType("id", "诊断ID", "string"),
                PropertyType("patient_id", "患者ID", "string"),
                PropertyType("provider_id", "机构ID", "string"),
                PropertyType("icd_code", "ICD编码", "string"),
                PropertyType("description", "诊断描述", "string", indexed_for_search=True),
                PropertyType("date", "诊断日期", "date"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Medication",
            display_name="药物",
            plural_display_name="药物列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="药物信息",
            icon="pill",
            icon_color="#27AE60",
            domain="healthcare",
            properties=[
                PropertyType("id", "药物ID", "string"),
                PropertyType("name", "药物名称", "string", indexed_for_search=True),
                PropertyType("dosage_form", "剂型", "string"),
                PropertyType("manufacturer", "生产厂家", "string"),
                PropertyType("ndc_code", "NDC编码", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Encounter",
            display_name="就诊记录",
            plural_display_name="就诊记录列表",
            primary_key_property_api_name="id",
            title_property_api_name="chief_complaint",
            description="患者就诊记录",
            icon="pulse",
            icon_color="#9B51E0",
            domain="healthcare",
            properties=[
                PropertyType("id", "就诊ID", "string"),
                PropertyType("patient_id", "患者ID", "string"),
                PropertyType("provider_id", "机构ID", "string"),
                PropertyType("type", "就诊类型", "string"),
                PropertyType("date", "就诊日期", "date"),
                PropertyType("chief_complaint", "主诉", "string", indexed_for_search=True),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
    ]

    links = [
        LinkType(
            api_name="patient_diagnoses",
            cardinality="OneToMany",
            source=LinkTypeSide("Patient", "diagnoses", "诊断", "诊断列表"),
            target=LinkTypeSide("Diagnosis", "patient", "患者"),
            foreign_key_property="patient_id",
        ),
        LinkType(
            api_name="patient_encounters",
            cardinality="OneToMany",
            source=LinkTypeSide("Patient", "encounters", "就诊记录", "就诊记录列表"),
            target=LinkTypeSide("Encounter", "patient", "患者"),
            foreign_key_property="patient_id",
        ),
        LinkType(
            api_name="provider_diagnoses",
            cardinality="OneToMany",
            source=LinkTypeSide("Provider", "diagnoses", "诊断", "诊断列表"),
            target=LinkTypeSide("Diagnosis", "provider", "医疗机构"),
            foreign_key_property="provider_id",
        ),
        LinkType(
            api_name="provider_encounters",
            cardinality="OneToMany",
            source=LinkTypeSide("Provider", "encounters", "就诊记录", "就诊记录列表"),
            target=LinkTypeSide("Encounter", "provider", "医疗机构"),
            foreign_key_property="provider_id",
        ),
    ]

    actions = [
        ActionType(
            api_name="recordDiagnosis",
            display_name="记录诊断",
            description="为患者记录一条诊断信息",
            target_object_type="Diagnosis",
            domain="healthcare",
            parameters=[
                ActionParameter("patient_id", "患者ID", "string", required=True),
                ActionParameter("provider_id", "机构ID", "string", required=True),
                ActionParameter("icd_code", "ICD编码", "string", required=True),
                ActionParameter("description", "诊断描述", "string", required=True),
            ],
        ),
    ]

    return objects, links, actions


def _build_ecommerce_types() -> tuple[list[ObjectType], list[LinkType], list[ActionType]]:
    objects = [
        ObjectType(
            api_name="EcomUser",
            display_name="用户",
            plural_display_name="用户列表",
            primary_key_property_api_name="id",
            title_property_api_name="username",
            description="电商平台用户",
            icon="person",
            icon_color="#2F80ED",
            domain="ecommerce",
            properties=[
                PropertyType("id", "用户ID", "string"),
                PropertyType("username", "用户名", "string", indexed_for_search=True),
                PropertyType("email", "邮箱", "string"),
                PropertyType("tier", "会员等级", "string"),
                PropertyType("registered_at", "注册时间", "timestamp"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Merchant",
            display_name="商家",
            plural_display_name="商家列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="平台商家/店铺",
            icon="shop",
            icon_color="#F2994A",
            domain="ecommerce",
            properties=[
                PropertyType("id", "商家ID", "string"),
                PropertyType("name", "商家名称", "string", indexed_for_search=True),
                PropertyType("category", "主营类目", "string"),
                PropertyType("rating", "评分", "decimal"),
                PropertyType("verified", "是否认证", "boolean"),
                PropertyType("latitude", "纬度", "decimal"),
                PropertyType("longitude", "经度", "decimal"),
                PropertyType("address", "地址", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable", "GeoLocated"],
        ),
        ObjectType(
            api_name="EcomProduct",
            display_name="商品",
            plural_display_name="商品列表",
            primary_key_property_api_name="id",
            title_property_api_name="name",
            description="平台上架商品",
            icon="box",
            icon_color="#27AE60",
            domain="ecommerce",
            properties=[
                PropertyType("id", "商品ID", "string"),
                PropertyType("merchant_id", "商家ID", "string"),
                PropertyType("name", "商品名称", "string", indexed_for_search=True),
                PropertyType("price", "价格", "decimal"),
                PropertyType("category", "类目", "string"),
                PropertyType("stock", "库存", "integer"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="EcomOrder",
            display_name="订单",
            plural_display_name="订单列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="用户订单",
            icon="shopping-cart",
            icon_color="#EB5757",
            domain="ecommerce",
            properties=[
                PropertyType("id", "订单ID", "string"),
                PropertyType("user_id", "用户ID", "string"),
                PropertyType("product_id", "商品ID", "string"),
                PropertyType("quantity", "数量", "integer"),
                PropertyType("total", "总金额", "decimal"),
                PropertyType("status", "订单状态", "string"),
                PropertyType("payment_method", "支付方式", "string"),
                PropertyType("created_at", "下单时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Review",
            display_name="评价",
            plural_display_name="评价列表",
            primary_key_property_api_name="id",
            title_property_api_name="content",
            description="商品评价",
            icon="comment",
            icon_color="#9B51E0",
            domain="ecommerce",
            properties=[
                PropertyType("id", "评价ID", "string"),
                PropertyType("user_id", "用户ID", "string"),
                PropertyType("product_id", "商品ID", "string"),
                PropertyType("rating", "评分", "integer"),
                PropertyType("content", "评价内容", "string", indexed_for_search=True),
                PropertyType("created_at", "评价时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
    ]

    links = [
        LinkType(
            api_name="user_orders",
            cardinality="OneToMany",
            source=LinkTypeSide("EcomUser", "orders", "订单", "订单列表"),
            target=LinkTypeSide("EcomOrder", "user", "用户"),
            foreign_key_property="user_id",
        ),
        LinkType(
            api_name="merchant_products",
            cardinality="OneToMany",
            source=LinkTypeSide("Merchant", "products", "商品", "商品列表"),
            target=LinkTypeSide("EcomProduct", "merchant", "商家"),
            foreign_key_property="merchant_id",
        ),
        LinkType(
            api_name="product_orders",
            cardinality="OneToMany",
            source=LinkTypeSide("EcomProduct", "orders", "订单", "订单列表"),
            target=LinkTypeSide("EcomOrder", "product", "商品"),
            foreign_key_property="product_id",
        ),
        LinkType(
            api_name="product_reviews",
            cardinality="OneToMany",
            source=LinkTypeSide("EcomProduct", "reviews", "评价", "评价列表"),
            target=LinkTypeSide("Review", "product", "商品"),
            foreign_key_property="product_id",
        ),
        LinkType(
            api_name="user_reviews",
            cardinality="OneToMany",
            source=LinkTypeSide("EcomUser", "reviews", "评价", "评价列表"),
            target=LinkTypeSide("Review", "user", "用户"),
            foreign_key_property="user_id",
        ),
    ]

    actions = [
        ActionType(
            api_name="placeOrder",
            display_name="下单",
            description="用户下单购买商品",
            target_object_type="EcomOrder",
            domain="ecommerce",
            parameters=[
                ActionParameter("user_id", "用户ID", "string", required=True),
                ActionParameter("product_id", "商品ID", "string", required=True),
                ActionParameter("quantity", "数量", "integer", required=True),
                ActionParameter("payment_method", "支付方式", "string", required=True),
            ],
        ),
        ActionType(
            api_name="submitReview",
            display_name="提交评价",
            description="用户对商品提交评价",
            target_object_type="Review",
            domain="ecommerce",
            parameters=[
                ActionParameter("user_id", "用户ID", "string", required=True),
                ActionParameter("product_id", "商品ID", "string", required=True),
                ActionParameter("rating", "评分", "integer", required=True),
                ActionParameter("content", "评价内容", "string", required=True),
            ],
        ),
    ]

    return objects, links, actions


def _build_interface_types() -> list[InterfaceType]:
    return [
        InterfaceType(
            api_name="Auditable",
            display_name="可审计",
            description="包含审计字段的接口，所有核心业务对象均实现此接口",
            properties=[
                InterfaceProperty("created_at", "创建时间", "timestamp"),
            ],
        ),
        InterfaceType(
            api_name="GeoLocated",
            display_name="地理定位",
            description="包含地理位置信息的接口",
            properties=[
                InterfaceProperty("latitude", "纬度", "decimal"),
                InterfaceProperty("longitude", "经度", "decimal"),
                InterfaceProperty("address", "地址", "string"),
            ],
        ),
    ]


# ── Instance data generators ──────────────────────────────────────────────

def _gen_supply_chain_instances() -> dict[str, list[dict]]:
    suppliers = []
    for i, (name, country) in enumerate(SUPPLIERS, 1):
        suppliers.append({
            "id": _id("SUP", i),
            "name": name,
            "country": country,
            "rating": round(random.uniform(3.0, 5.0), 1),
            "contact_email": f"contact@{_rand_str(5)}.com",
            "created_at": _rand_timestamp(),
        })

    products = []
    for i, name in enumerate(PRODUCT_NAMES, 1):
        products.append({
            "id": _id("PRD", i),
            "name": name,
            "category": random.choice(PRODUCT_CATEGORIES),
            "unit_price": round(random.uniform(10, 5000), 2),
            "weight": round(random.uniform(0.01, 50), 2),
            "supplier_id": random.choice(suppliers)["id"],
            "created_at": _rand_timestamp(),
        })

    warehouses = []
    for i, (name, loc) in enumerate(WAREHOUSE_CITIES, 1):
        warehouses.append({
            "id": _id("WH", i),
            "name": name,
            "location": loc,
            "capacity": random.randint(1000, 50000),
            "latitude": round(random.uniform(22, 52), 4),
            "longitude": round(random.uniform(-122, 140), 4),
            "address": loc,
            "created_at": _rand_timestamp(),
        })

    purchase_orders = []
    statuses = ["pending", "approved", "shipped", "delivered", "cancelled"]
    for i in range(1, 51):
        purchase_orders.append({
            "id": _id("PO", i),
            "supplier_id": random.choice(suppliers)["id"],
            "total_amount": round(random.uniform(1000, 100000), 2),
            "status": random.choice(statuses),
            "created_at": _rand_timestamp(),
        })

    shipments = []
    for i, po in enumerate(purchase_orders, 1):
        for j in range(random.randint(1, 3)):
            shipments.append({
                "id": _id("SHP", len(shipments) + 1),
                "purchase_order_id": po["id"],
                "warehouse_id": random.choice(warehouses)["id"],
                "tracking_number": f"TN{_rand_str(10).upper()}",
                "status": random.choice(["pending", "in_transit", "delivered"]),
                "created_at": _rand_timestamp(),
            })

    return {
        "Supplier": suppliers,
        "ScProduct": products,
        "Warehouse": warehouses,
        "PurchaseOrder": purchase_orders,
        "Shipment": shipments,
    }


def _gen_finance_instances() -> dict[str, list[dict]]:
    customers = []
    for i, name in enumerate(CUSTOMER_NAMES, 1):
        customers.append({
            "id": _id("CUS", i),
            "name": name,
            "tier": random.choice(["普通", "银卡", "金卡", "白金", "钻石"]),
            "risk_level": random.choice(["低", "中", "高"]),
            "kyc_status": random.choice(["已认证", "待认证", "认证中"]),
            "created_at": _rand_timestamp(),
        })

    accounts = []
    acc_types = ["储蓄账户", "活期账户", "定期账户", "理财账户"]
    currencies = ["CNY", "USD", "EUR", "JPY"]
    for i, cust in enumerate(customers):
        for j in range(random.randint(1, 3)):
            accounts.append({
                "id": _id("ACC", len(accounts) + 1),
                "customer_id": cust["id"],
                "type": random.choice(acc_types),
                "balance": round(random.uniform(100, 1000000), 2),
                "currency": random.choice(currencies),
                "opened_at": _rand_date(),
                "created_at": _rand_timestamp(),
            })

    transactions = []
    tx_types = ["转账", "消费", "存款", "取款", "工资", "理财收益"]
    for i in range(1, 101):
        from_acc = random.choice(accounts)
        to_acc = random.choice([a for a in accounts if a["id"] != from_acc["id"]])
        transactions.append({
            "id": _id("TXN", i),
            "from_account": from_acc["id"],
            "to_account": to_acc["id"],
            "amount": round(random.uniform(1, 50000), 2),
            "type": random.choice(tx_types),
            "timestamp": _rand_timestamp(),
        })

    products = []
    fi_products = [
        ("稳健理财A", "理财产品", 3.5, 1000),
        ("进取理财B", "理财产品", 6.2, 10000),
        ("个人消费贷", "贷款", 4.35, 0),
        ("住房贷款", "贷款", 3.85, 0),
        ("定期存款", "存款", 2.75, 50),
        ("大额存单", "存款", 3.35, 200000),
    ]
    for i, (name, cat, rate, min_inv) in enumerate(fi_products, 1):
        products.append({
            "id": _id("FPR", i),
            "name": name,
            "category": cat,
            "interest_rate": rate,
            "min_investment": min_inv,
            "created_at": _rand_timestamp(),
        })

    return {
        "FiCustomer": customers,
        "Account": accounts,
        "Transaction": transactions,
        "FiProduct": products,
    }


def _gen_healthcare_instances() -> dict[str, list[dict]]:
    patients = []
    for i, name in enumerate(CUSTOMER_NAMES[:15], 1):
        patients.append({
            "id": _id("PAT", i),
            "name": name,
            "dob": _rand_date(1950, 2005),
            "blood_type": random.choice(["A", "B", "O", "AB"]) + random.choice(["+", "-"]),
            "insurance_id": _id("INS", random.randint(10000, 99999), 5),
            "created_at": _rand_timestamp(),
        })

    providers = []
    provider_data = [
        ("协和医院", "三甲医院", "北京", "三级甲等"),
        ("华西医院", "三甲医院", "成都", "三级甲等"),
        ("Mayo Clinic", "综合医院", "Rochester, MN", "JCI认证"),
        ("东京大学医学部附属病院", "教学医院", "東京", "JCI认证"),
        ("社区卫生服务中心", "社区诊所", "上海", "基本医疗"),
    ]
    for i, (name, typ, loc, acc) in enumerate(provider_data, 1):
        providers.append({
            "id": _id("PRV", i),
            "name": name,
            "type": typ,
            "location": loc,
            "accreditation": acc,
            "latitude": round(random.uniform(22, 52), 4),
            "longitude": round(random.uniform(-122, 140), 4),
            "address": loc,
            "created_at": _rand_timestamp(),
        })

    diagnoses = []
    for i in range(1, 61):
        icd, desc, detail = random.choice(DIAGNOSES)
        diagnoses.append({
            "id": _id("DIA", i),
            "patient_id": random.choice(patients)["id"],
            "provider_id": random.choice(providers)["id"],
            "icd_code": icd,
            "description": f"{desc} - {detail}",
            "date": _rand_date(),
            "created_at": _rand_timestamp(),
        })

    medications = []
    for i, name in enumerate(MEDICATION_NAMES[:12], 1):
        forms = ["片剂", "胶囊", "注射液", "口服液", "颗粒"]
        manufacturers = ["辉瑞制药", "恒瑞医药", "阿斯利康", "诺华制药", "拜耳医药"]
        medications.append({
            "id": _id("MED", i),
            "name": name,
            "dosage_form": random.choice(forms),
            "manufacturer": random.choice(manufacturers),
            "ndc_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}-{random.randint(10, 99)}",
            "created_at": _rand_timestamp(),
        })

    encounters = []
    encounter_types = ["门诊", "急诊", "住院", "复查", "体检"]
    complaints = ["头痛发热", "咳嗽咽痛", "腹痛腹泻", "腰背疼痛", "胸闷气短", "皮肤过敏", "失眠焦虑"]
    for i in range(1, 81):
        encounters.append({
            "id": _id("ENC", i),
            "patient_id": random.choice(patients)["id"],
            "provider_id": random.choice(providers)["id"],
            "type": random.choice(encounter_types),
            "date": _rand_date(),
            "chief_complaint": random.choice(complaints),
            "created_at": _rand_timestamp(),
        })

    return {
        "Patient": patients,
        "Provider": providers,
        "Diagnosis": diagnoses,
        "Medication": medications,
        "Encounter": encounters,
    }


def _gen_ecommerce_instances() -> dict[str, list[dict]]:
    users = []
    for i in range(1, 26):
        name = random.choice(CUSTOMER_NAMES)
        users.append({
            "id": _id("USR", i),
            "username": f"{_rand_str(4)}_{name.split()[0].lower()}",
            "email": f"{_rand_str(6)}@{_rand_str(4)}.com",
            "tier": random.choice(["普通会员", "银牌会员", "金牌会员", "钻石会员"]),
            "registered_at": _rand_timestamp(),
            "created_at": _rand_timestamp(),
        })

    merchants = []
    for i, name in enumerate(MERCHANT_NAMES, 1):
        merchants.append({
            "id": _id("MCH", i),
            "name": name,
            "category": random.choice(ECOM_CATEGORIES),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "verified": random.choice([True, True, True, False]),
            "latitude": round(random.uniform(22, 42), 4),
            "longitude": round(random.uniform(100, 125), 4),
            "address": f"商业街{random.randint(1, 100)}号",
            "created_at": _rand_timestamp(),
        })

    products = []
    for i, name in enumerate(ECOM_PRODUCTS, 1):
        mch = random.choice(merchants)
        products.append({
            "id": _id("EPR", i),
            "merchant_id": mch["id"],
            "name": name,
            "price": round(random.uniform(9.9, 2999), 2),
            "category": random.choice(ECOM_CATEGORIES),
            "stock": random.randint(0, 1000),
            "created_at": _rand_timestamp(),
        })

    orders = []
    order_statuses = ["待支付", "已支付", "已发货", "已完成", "已取消", "退款中"]
    pay_methods = ["支付宝", "微信支付", "银行卡", "信用卡", "花呗"]
    for i in range(1, 81):
        prod = random.choice(products)
        qty = random.randint(1, 5)
        orders.append({
            "id": _id("ORD", i),
            "user_id": random.choice(users)["id"],
            "product_id": prod["id"],
            "quantity": qty,
            "total": round(prod["price"] * qty, 2),
            "status": random.choice(order_statuses),
            "payment_method": random.choice(pay_methods),
            "created_at": _rand_timestamp(),
        })

    reviews = []
    review_contents = [
        "质量很好，物超所值", "物流很快，包装完好", "性价比高，会回购",
        "一般般，不太满意", "非常满意，五星好评", "和描述一致，不错",
        "手感很好，颜色正", "做工精细，推荐购买", "收到了，还没用",
        "味道不错，新鲜", "穿着很舒服", "屏幕清晰，音质好",
    ]
    for i in range(1, 61):
        reviews.append({
            "id": _id("REV", i),
            "user_id": random.choice(users)["id"],
            "product_id": random.choice(products)["id"],
            "rating": random.randint(1, 5),
            "content": random.choice(review_contents),
            "created_at": _rand_timestamp(),
        })

    return {
        "EcomUser": users,
        "Merchant": merchants,
        "EcomProduct": products,
        "EcomOrder": orders,
        "Review": reviews,
    }


# ── Main entry point ───────────────────────────────────────────────────────

def seed(data_dir: Path | None = None) -> OntologyDefinition:
    """Generate all ontology definitions and instance data."""
    random.seed(42)  # Reproducible data

    sc_objects, sc_links, sc_actions = _build_supply_chain_types()
    fi_objects, fi_links, fi_actions = _build_finance_types()
    hc_objects, hc_links, hc_actions = _build_healthcare_types()
    ec_objects, ec_links, ec_actions = _build_ecommerce_types()

    ontology = OntologyDefinition(
        object_types=sc_objects + fi_objects + hc_objects + ec_objects,
        link_types=sc_links + fi_links + hc_links + ec_links,
        interface_types=_build_interface_types(),
        action_types=sc_actions + fi_actions + hc_actions + ec_actions,
    )

    store = OntologyStore(data_dir)
    store.save_ontology(ontology)

    store.save_instances("supply_chain", _gen_supply_chain_instances())
    store.save_instances("finance", _gen_finance_instances())
    store.save_instances("healthcare", _gen_healthcare_instances())
    store.save_instances("ecommerce", _gen_ecommerce_instances())

    return ontology


if __name__ == "__main__":
    ontology = seed()
    print(f"Seeded ontology with:")
    print(f"  {len(ontology.object_types)} object types")
    print(f"  {len(ontology.link_types)} link types")
    print(f"  {len(ontology.interface_types)} interface types")
    print(f"  {len(ontology.action_types)} action types")

    store = OntologyStore()
    all_instances = store.load_all_instances()
    total = sum(len(v) for v in all_instances.values())
    print(f"  {total} total instances across {len(all_instances)} types")
