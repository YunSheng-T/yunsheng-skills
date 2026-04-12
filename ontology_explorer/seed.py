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
from .core.store import JsonOntologyStore


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

# ── 供应商数据: (名称, 国家, 评分基数, 注册资本万元, 主营类别) ──────────────
SUPPLIERS = [
    ("华联供应链",       "CN", 4.6, 5000, "原材料,包装材料"),
    ("GlobalSource Inc.", "US", 4.3, 8000, "电子元器件,机械零件"),
    ("EuroParts GmbH",    "DE", 4.5, 6000, "机械零件,精密部件"),
    ("東京精密工業",      "JP", 4.8, 12000, "电子元器件,精密部件"),
    ("Samsung Materials", "KR", 4.7, 15000, "电子元器件"),
    ("Tata Components",   "IN", 4.0, 3000, "原材料,机械零件"),
    ("Acme Supply Co.",   "US", 3.9, 2000, "办公用品,包装材料"),
    ("华南电子科技",      "CN", 4.2, 4500, "电子元器件"),
    ("Bosch Logistics",   "DE", 4.6, 10000, "机械零件,电子元器件"),
    ("LG Materials",      "KR", 4.4, 9000, "电子元器件,原材料"),
    ("Foxconn Supply",    "CN", 4.5, 20000, "电子元器件"),
    ("Intel Components",  "US", 4.7, 18000, "电子元器件"),
    ("Toyota Parts",      "JP", 4.6, 16000, "机械零件"),
    ("Hitachi Materials", "JP", 4.3, 11000, "电子元器件,原材料"),
    ("Hyundai Supply",    "KR", 4.1, 7000, "机械零件,原材料"),
    ("联想供应链",        "CN", 4.4, 8500, "电子元器件,办公用品"),
    ("Dell Logistics",    "US", 4.2, 7500, "电子元器件,办公用品"),
    ("Siemens Parts",     "DE", 4.5, 13000, "电子元器件,机械零件"),
    ("松下电子部品",      "JP", 4.4, 9500, "电子元器件"),
    ("SK Materials",      "KR", 4.3, 6500, "原材料,电子元器件"),
]

PRODUCT_CATEGORIES = ["电子元器件", "机械零件", "原材料", "包装材料", "办公用品"]

# (名称, 类别, 价格范围, 重量范围kg, 品牌, 产地)
PRODUCTS_DATA = [
    ("LED显示屏模组 P3.0",   "电子元器件", (380, 2800),  (0.5, 3.0),   "华星光电", "深圳"),
    ("伺服电机 750W",        "机械零件",   (1200, 4500), (3.0, 8.0),   "安川电机", "上海"),
    ("碳纤维板材 T300",      "原材料",     (150, 800),   (0.5, 5.0),   "东丽",     "东京"),
    ("铝合金外壳 6061",      "原材料",     (30, 200),    (0.1, 2.0),   "忠旺铝业", "辽阳"),
    ("USB-C连接器 24Pin",    "电子元器件", (2.5, 15),    (0.003, 0.02),"Molex",    "上海"),
    ("锂电池组 18650",       "电子元器件", (80, 450),    (0.3, 1.5),   "宁德时代", "宁德"),
    ("散热风扇 120mm",       "电子元器件", (15, 120),    (0.08, 0.3),  "Delta",    "东莞"),
    ("光纤线缆 LC-LC 10m",   "电子元器件", (25, 180),    (0.05, 0.5),  "康宁",     "上海"),
    ("压力传感器 PT100",     "电子元器件", (200, 1500),  (0.05, 0.3),  "Honeywell","深圳"),
    ("控制芯片 STM32F4",     "电子元器件", (8, 65),      (0.001, 0.01),"ST",       "深圳"),
    ("电源模块 5V/3A",       "电子元器件", (25, 150),    (0.02, 0.15), "明纬",     "东莞"),
    ("密封垫圈 NBR 50mm",    "机械零件",   (1.5, 12),    (0.005, 0.05),"NOK",      "东京"),
    ("液压阀 DN25",          "机械零件",   (350, 2500),  (1.0, 5.0),   "力士乐",   "上海"),
    ("精密轴承 6205-2RS",    "机械零件",   (12, 85),     (0.1, 0.5),   "SKF",      "上海"),
    ("导热硅脂 TG-50",       "原材料",     (8, 45),      (0.005, 0.05),"信越化学", "东京"),
    ("PCB电路板 双层",       "电子元器件", (5, 80),      (0.01, 0.1),  "鹏鼎控股", "深圳"),
    ("工业传感器 温湿度",    "电子元器件", (120, 600),   (0.05, 0.2),  "Sensirion","深圳"),
    ("减速齿轮箱 RV40E",    "机械零件",   (800, 3500),  (2.0, 6.0),   "Nabtesco", "上海"),
    ("不锈钢螺丝 M6*20",    "机械零件",   (0.1, 0.8),   (0.005, 0.02),"晋亿实业", "嘉兴"),
    ("环氧树脂 AB胶",       "原材料",     (15, 80),     (0.2, 1.0),   "3M",       "上海"),
    ("气缸 SDA32*30",       "机械零件",   (60, 350),    (0.2, 1.0),   "SMC",      "上海"),
    ("变频器 2.2kW",        "电子元器件", (650, 3200),  (1.5, 4.0),   "ABB",      "北京"),
    ("光耦隔离器 TLP281",    "电子元器件", (1.5, 8),     (0.001, 0.005),"东芝",    "深圳"),
    ("铝合金散热器 200mm",   "电子元器件", (35, 200),    (0.2, 1.5),   "Aavid",    "东莞"),
    ("防静电包装袋",         "包装材料",   (0.5, 5),     (0.01, 0.05), "杜邦",     "上海"),
]

COUNTRIES = ["CN", "US", "DE", "JP", "KR", "IN", "GB", "FR"]

# (名称, 地址, 经纬度, 类型, 负责人)
WAREHOUSE_DATA = [
    ("上海仓", "上海市浦东新区张江高科技园区碧波路888号", 31.2045, 121.5889, "普通仓", "李建国"),
    ("深圳仓", "深圳市南山区科技园南区深南大道9966号", 22.5311, 113.9456, "普通仓", "王小明"),
    ("东京冷链仓", "東京都品川区大崎2-11-1", 35.6197, 139.7287, "冷链仓", "山田太郎"),
    ("纽约仓", "New York, NY 10001, 350 5th Ave", 40.7484, -73.9857, "普通仓", "John Miller"),
    ("法兰克福仓", "Frankfurt am Main, Hanauer Landstr. 150", 50.1109, 8.6821, "危险品仓", "Hans Weber"),
    ("首尔仓", "서울시 강남구 테헤란로 152", 37.5013, 127.0395, "冷链仓", "박지훈"),
]

# 客户: (姓名, 等级, 风险等级, 职业, 年收入万, 开户年)
CUSTOMER_PROFILES = [
    ("张伟",       "钻石", "低",  "企业高管",    120, 2018),
    ("李娜",       "金卡", "低",  "医生",        50,  2020),
    ("王芳",       "银卡", "中",  "教师",        20,  2021),
    ("John Smith", "白金", "低",  "Engineer",    85,  2019),
    ("Emily Johnson","普通","中", "Designer",    35,  2022),
    ("Michael Brown","金卡","低", "Manager",     60,  2020),
    ("Sarah Davis", "银卡", "中", "Nurse",       25,  2021),
    ("Robert Wilson","钻石","低", "CEO",         200, 2017),
    ("Maria Garcia","普通", "高", "Freelancer",  15,  2023),
    ("David Martinez","金卡","低","Accountant",  45,  2019),
    ("田中太郎",    "白金", "低",  "エンジニア",  90,  2018),
    ("佐藤花子",    "金卡", "低",  "医師",        55,  2020),
    ("김민수",      "银卡", "中",  "개발자",      30,  2021),
    ("이수진",      "普通", "低",  "간호사",      22,  2022),
    ("محمد أحمد",   "白金", "低",  "مدير",        75,  2019),
    ("Marie Dupont","金卡", "低",  "Avocate",     55,  2020),
    ("Hans Mueller","钻石", "低",  "Direktor",   150,  2017),
    ("Raj Patel",   "普通", "高",  "Trader",      18,  2023),
    ("Anna Kowalski","银卡","中",  "Lekarka",     28,  2021),
    ("Carlos Silva","金卡", "低",  "Engenheiro",  48,  2019),
]

# 姓名列表，用于医疗和电商域
CUSTOMER_NAMES = [p[0] for p in CUSTOMER_PROFILES]

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

# (名称, 类别, 价格范围, 品牌)
ECOM_PRODUCTS_DATA = [
    ("AirPods Pro 2 无线蓝牙耳机", "电子产品", (799, 1899), "Apple"),
    ("小米手环8 NFC版",          "电子产品", (199, 349),   "小米"),
    ("优衣库 AIRism棉质T恤",     "服装鞋帽", (79, 149),    "优衣库"),
    ("Nike Air Zoom Pegasus 40",  "服装鞋帽", (599, 899),   "Nike"),
    ("西湖龙井明前特级 250g",     "食品饮料", (168, 398),   "西湖牌"),
    ("膳魔师不锈钢保温杯 500ml",  "家居用品", (158, 298),   "THERMOS"),
    ("竹之韵竹纤维浴巾",          "家居用品", (49, 129),    "竹之韵"),
    ("芙丽芳丝氨基酸洗面奶",      "美妆个护", (98, 159),    "freeplus"),
    ("《三体》全集精装版",         "图书音像", (89, 168),    "重庆出版社"),
    ("JBL Charge 5 蓝牙音箱",    "电子产品", (899, 1499),  "JBL"),
    ("iPad Air 保护壳 磁吸款",    "电子产品", (68, 198),    "ESR"),
    ("Under Armour 速干运动裤",  "服装鞋帽", (249, 499),   "UA"),
    ("三只松鼠坚果礼盒 1.66kg",   "食品饮料", (98, 188),    "三只松鼠"),
    ("祖玛珑香薰蜡烛 英国梨",     "美妆个护", (350, 580),   "Jo Malone"),
    ("SK-II 前男友面膜 10片装",  "美妆个护", (690, 1090),  "SK-II"),
    ("Sony WH-1000XM5 降噪耳机", "电子产品", (1999, 2699),"Sony"),
    ("Lululemon Align瑜伽裤",    "服装鞋帽", (650, 850),   "Lululemon"),
    ("茅台飞天 53度 500ml",       "食品饮料", (1499, 2999),"茅台"),
    ("戴森 V15 Detect 吸尘器",    "家居用品", (3990, 5490),"Dyson"),
    ("兰蔻小黑瓶精华 50ml",       "美妆个护", (760, 1080), "兰蔻"),
    ("LEGO 哈利波特城堡",         "玩具",     (599, 2999), "LEGO"),
    ("小米电视6 65英寸 OLED",     "电子产品", (4999, 7999),"小米"),
    ("阿迪达斯 Ultraboost 23",   "服装鞋帽", (899, 1299), "adidas"),
    ("茅台王子酒 53度 500ml",     "食品饮料", (268, 398),  "茅台"),
    ("戴森 Airwrap 卷发棒",       "美妆个护", (3190, 3990),"Dyson"),
    ("Switch OLED 游戏机",        "电子产品", (2199, 2599),"Nintendo"),
    ("北面 1996 Retro 羽绒服",   "服装鞋帽", (1998, 2998),"The North Face"),
    ("好想你红枣礼盒 2kg",        "食品饮料", (128, 258),  "好想你"),
    ("飞利浦电动牙刷 HX9352",    "美妆个护", (399, 699),  "Philips"),
    ("Kindle Paperwhite 5",       "电子产品", (999, 1399), "Amazon"),
]

MERCHANT_NAMES = [
    "数码旗舰馆", "时尚衣橱", "品味零食铺", "温馨家居坊", "美丽研究所",
    "TechZone", "StyleHub", "BookWorm", "GadgetPro", "FitGear",
]

# (ICD码, 名称, 详情, 是否慢性病, 对应药物关键词)
DIAGNOSES = [
    ("J06.9",   "急性上呼吸道感染", "发热、咽痛、咳嗽3天",         False, "阿莫西林|头孢"),
    ("K21.0",   "胃食管反流病",     "反酸、烧心，餐后加重",        True,  "奥美拉唑"),
    ("E11.9",   "2型糖尿病",        "空腹血糖升高，口渴多饮",       True,  "二甲双胍|Metformin"),
    ("I10",     "原发性高血压",     "血压升高1年余",               True,  "硝苯地平|Amlodipine|Losartan"),
    ("M54.5",   "下背痛",           "腰部酸痛，久坐加重",          False, "布洛芬|Ibuprofen"),
    ("J45.909", "支气管哮喘",       "反复喘息、气促",              True,  ""),
    ("K58.9",   "肠易激综合征",     "腹痛、腹泻交替",              True,  ""),
    ("G43.909", "偏头痛",           "反复发作性头痛",              True,  ""),
    ("L30.9",   "皮炎",             "皮肤红疹、瘙痒",              False, "氯雷他定"),
    ("N39.0",   "尿路感染",         "尿频、尿急、尿痛",            False, "头孢"),
]

# 检验项目池: (名称, 单位, 参考范围, 正常值范围)
LAB_TESTS = [
    ("空腹血糖",     "mmol/L",  "3.9-6.1",    (4.0, 6.0)),
    ("糖化血红蛋白", "%",       "4.0-6.0",    (4.5, 6.0)),
    ("总胆固醇",     "mmol/L",  "2.8-5.17",   (3.0, 5.5)),
    ("甘油三酯",     "mmol/L",  "0.56-1.7",   (0.6, 2.0)),
    ("收缩压",       "mmHg",    "90-140",     (110, 135)),
    ("舒张压",       "mmHg",    "60-90",      (70, 85)),
    ("白细胞计数",   "10^9/L",  "4.0-10.0",   (4.5, 9.5)),
    ("血红蛋白",     "g/L",     "120-160",    (125, 165)),
    ("血小板计数",   "10^9/L",  "100-300",    (120, 280)),
    ("谷丙转氨酶",   "U/L",     "0-40",       (10, 38)),
    ("肌酐",         "μmol/L",  "44-133",     (50, 110)),
    ("尿酸",         "μmol/L",  "208-428",    (210, 420)),
    ("C反应蛋白",    "mg/L",    "0-10",       (0.5, 8)),
    ("血沉",         "mm/h",    "0-20",       (2, 18)),
]

ECOM_USER_CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆",
                    "Tokyo", "Seoul", "New York", "London", "Paris"]

ECOM_ADDRESSES = [
    "北京市朝阳区建国路89号华贸中心", "上海市黄浦区南京东路123号",
    "广州市天河区天河路385号", "深圳市南山区深南大道10000号",
    "杭州市西湖区文三路478号", "成都市锦江区春熙路168号",
    "武汉市洪山区珞喻路1037号", "南京市鼓楼区中山路321号",
    "西安市雁塔区高新路88号", "重庆市渝中区解放碑步行街66号",
]

# 评价内容池: (评分, 内容列表)
REVIEW_POOLS = {
    5: [
        "质量非常好，和描述完全一致，包装精美，物流也很快，非常满意的一次购物体验！",
        "用了一个月了，效果超出预期，物超所值，已经推荐给朋友了。",
        "做工精细，手感很好，颜色很正，五星好评！",
        "收到后就试用了，效果立竿见影，果断回购。",
        "颜值超高，功能强大，这个价位买到真的很划算。",
    ],
    4: [
        "整体不错，就是物流稍微慢了一点，产品本身很好用。",
        "质量可以，性价比高，就是包装可以再改进一下。",
        "用了几天感觉还行，基本符合预期。",
        "和图片一致，还不错，给个好评。",
        "功能齐全，操作简单，日常使用足够了。",
    ],
    3: [
        "一般般吧，中规中矩，没有特别惊喜的地方。",
        "质量还行，但是和期望值有差距。",
        "能用，但做工有些粗糙，细节还需要改进。",
        "凑合，用着还行，但不会再回购了。",
        "一般，没有想象中好，但也说不上差。",
    ],
    2: [
        "质量不太好，用了没多久就出问题了，不太满意。",
        "和描述差距较大，有点失望。",
        "做工粗糙，颜色和图片不一致。",
        "收到就有瑕疵，联系客服处理比较慢。",
    ],
    1: [
        "非常差！质量太差了，用了两天就坏了，要求退款！",
        "和图片严重不符，完全不值这个价格，差评！",
        "破损严重，包装简陋，快递暴力运输，卖家也不负责。",
    ],
}


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
                PropertyType("contact_phone", "联系电话", "string"),
                PropertyType("address", "地址", "string"),
                PropertyType("business_scope", "经营范围", "string"),
                PropertyType("registered_capital", "注册资本(万元)", "decimal"),
                PropertyType("status", "状态", "string"),
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
                PropertyType("brand", "品牌", "string"),
                PropertyType("model", "型号", "string"),
                PropertyType("origin", "产地", "string"),
                PropertyType("min_order_qty", "最小订购量", "integer"),
                PropertyType("lead_time_days", "交期(天)", "integer"),
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
                PropertyType("warehouse_type", "仓库类型", "string"),
                PropertyType("manager", "负责人", "string"),
                PropertyType("phone", "联系电话", "string"),
                PropertyType("utilization_rate", "利用率", "decimal"),
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
                PropertyType("currency", "币种", "string"),
                PropertyType("priority", "优先级", "string"),
                PropertyType("payment_terms", "付款条件", "string"),
                PropertyType("expected_delivery", "预计交付日期", "date"),
                PropertyType("remark", "备注", "string"),
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
                PropertyType("carrier", "承运人", "string"),
                PropertyType("weight", "重量(kg)", "decimal"),
                PropertyType("shipping_method", "运输方式", "string"),
                PropertyType("estimated_arrival", "预计到达", "date"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Contract",
            display_name="合同",
            plural_display_name="合同列表",
            primary_key_property_api_name="id",
            title_property_api_name="title",
            description="供应商合同",
            icon="document",
            icon_color="#6C5CE7",
            domain="supply_chain",
            properties=[
                PropertyType("id", "合同ID", "string"),
                PropertyType("supplier_id", "供应商ID", "string"),
                PropertyType("contract_no", "合同编号", "string", indexed_for_search=True),
                PropertyType("title", "合同名称", "string", indexed_for_search=True),
                PropertyType("value", "合同金额", "decimal"),
                PropertyType("currency", "币种", "string"),
                PropertyType("start_date", "生效日期", "date"),
                PropertyType("end_date", "到期日期", "date"),
                PropertyType("status", "状态", "string"),
                PropertyType("signed_at", "签订日期", "date"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Inventory",
            display_name="库存",
            plural_display_name="库存列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="产品库存记录",
            icon="layers",
            icon_color="#00B894",
            domain="supply_chain",
            properties=[
                PropertyType("id", "库存ID", "string"),
                PropertyType("product_id", "产品ID", "string"),
                PropertyType("warehouse_id", "仓库ID", "string"),
                PropertyType("quantity", "总数量", "integer"),
                PropertyType("reserved_qty", "已预留", "integer"),
                PropertyType("available_qty", "可用数量", "integer"),
                PropertyType("last_checked", "最后盘点", "date"),
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
        LinkType(
            api_name="supplier_contracts",
            cardinality="OneToMany",
            source=LinkTypeSide("Supplier", "contracts", "合同", "合同列表"),
            target=LinkTypeSide("Contract", "supplier", "供应商"),
            foreign_key_property="supplier_id",
        ),
        LinkType(
            api_name="product_inventory",
            cardinality="OneToMany",
            source=LinkTypeSide("ScProduct", "inventory_records", "库存记录", "库存记录列表"),
            target=LinkTypeSide("Inventory", "product", "产品"),
            foreign_key_property="product_id",
        ),
        LinkType(
            api_name="warehouse_inventory",
            cardinality="OneToMany",
            source=LinkTypeSide("Warehouse", "inventory_records", "库存记录", "库存记录列表"),
            target=LinkTypeSide("Inventory", "warehouse", "仓库"),
            foreign_key_property="warehouse_id",
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
        ActionType(
            api_name="createContract",
            display_name="创建合同",
            description="与供应商创建新合同",
            target_object_type="Contract",
            domain="supply_chain",
            parameters=[
                ActionParameter("supplier_id", "供应商ID", "string", required=True),
                ActionParameter("title", "合同名称", "string", required=True),
                ActionParameter("value", "合同金额", "decimal", required=True),
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
                PropertyType("phone", "联系电话", "string"),
                PropertyType("occupation", "职业", "string"),
                PropertyType("annual_income", "年收入(万)", "decimal"),
                PropertyType("vip_since", "VIP起始年", "integer"),
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
                PropertyType("branch", "开户行", "string"),
                PropertyType("status", "状态", "string"),
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
                PropertyType("status", "状态", "string"),
                PropertyType("channel", "渠道", "string"),
                PropertyType("description", "描述", "string", indexed_for_search=True),
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
                PropertyType("risk_level", "风险等级", "string"),
                PropertyType("term_days", "期限(天)", "integer"),
                PropertyType("issuer", "发行方", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="CreditCard",
            display_name="信用卡",
            plural_display_name="信用卡列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="信用卡信息",
            icon="credit-card",
            icon_color="#E17055",
            domain="finance",
            properties=[
                PropertyType("id", "卡ID", "string"),
                PropertyType("customer_id", "客户ID", "string"),
                PropertyType("card_number", "卡号(脱敏)", "string"),
                PropertyType("card_type", "卡类型", "string"),
                PropertyType("credit_limit", "信用额度", "decimal"),
                PropertyType("used_amount", "已用额度", "decimal"),
                PropertyType("available_amount", "可用额度", "decimal"),
                PropertyType("billing_day", "账单日", "integer"),
                PropertyType("status", "状态", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Loan",
            display_name="贷款",
            plural_display_name="贷款列表",
            primary_key_property_api_name="id",
            title_property_api_name="id",
            description="贷款记录",
            icon="money",
            icon_color="#D63031",
            domain="finance",
            properties=[
                PropertyType("id", "贷款ID", "string"),
                PropertyType("customer_id", "客户ID", "string"),
                PropertyType("account_id", "关联账户", "string"),
                PropertyType("loan_type", "贷款类型", "string"),
                PropertyType("principal", "本金", "decimal"),
                PropertyType("interest_rate", "利率", "decimal"),
                PropertyType("term_months", "期限(月)", "integer"),
                PropertyType("monthly_payment", "月供", "decimal"),
                PropertyType("remaining_principal", "剩余本金", "decimal"),
                PropertyType("status", "状态", "string"),
                PropertyType("applied_at", "申请日期", "date"),
                PropertyType("approved_at", "批准日期", "date"),
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
        LinkType(
            api_name="customer_credit_cards",
            cardinality="OneToMany",
            source=LinkTypeSide("FiCustomer", "credit_cards", "信用卡", "信用卡列表"),
            target=LinkTypeSide("CreditCard", "customer", "客户"),
            foreign_key_property="customer_id",
        ),
        LinkType(
            api_name="customer_loans",
            cardinality="OneToMany",
            source=LinkTypeSide("FiCustomer", "loans", "贷款", "贷款列表"),
            target=LinkTypeSide("Loan", "customer", "客户"),
            foreign_key_property="customer_id",
        ),
        LinkType(
            api_name="account_loans",
            cardinality="OneToMany",
            source=LinkTypeSide("Account", "loans", "贷款", "贷款列表"),
            target=LinkTypeSide("Loan", "account", "账户"),
            foreign_key_property="account_id",
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
        ActionType(
            api_name="approveLoan",
            display_name="审批贷款",
            description="审批贷款申请",
            target_object_type="Loan",
            domain="finance",
            parameters=[
                ActionParameter("loan_id", "贷款ID", "string", required=True),
                ActionParameter("approved", "是否批准", "boolean", required=True),
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
                PropertyType("gender", "性别", "string"),
                PropertyType("blood_type", "血型", "string"),
                PropertyType("insurance_id", "保险ID", "string"),
                PropertyType("phone", "联系电话", "string"),
                PropertyType("emergency_contact", "紧急联系人", "string"),
                PropertyType("allergies", "过敏史", "string"),
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
                PropertyType("bed_count", "床位数", "integer"),
                PropertyType("doctor_count", "医生数", "integer"),
                PropertyType("phone", "联系电话", "string"),
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
                PropertyType("severity", "严重程度", "string"),
                PropertyType("doctor_name", "主治医生", "string"),
                PropertyType("date", "诊断日期", "date"),
                PropertyType("follow_up_date", "复诊日期", "date"),
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
                PropertyType("specification", "规格", "string"),
                PropertyType("unit_price", "单价", "decimal"),
                PropertyType("insurance_covered", "医保覆盖", "boolean"),
                PropertyType("side_effects", "副作用", "string"),
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
                PropertyType("doctor_name", "主治医生", "string"),
                PropertyType("cost", "费用", "decimal"),
                PropertyType("follow_up_required", "需复诊", "boolean"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="LabResult",
            display_name="检验结果",
            plural_display_name="检验结果列表",
            primary_key_property_api_name="id",
            title_property_api_name="test_name",
            description="检验化验结果",
            icon="clipboard",
            icon_color="#00CEC9",
            domain="healthcare",
            properties=[
                PropertyType("id", "检验ID", "string"),
                PropertyType("patient_id", "患者ID", "string"),
                PropertyType("encounter_id", "就诊ID", "string"),
                PropertyType("test_name", "检验项目", "string", indexed_for_search=True),
                PropertyType("result_value", "结果值", "decimal"),
                PropertyType("unit", "单位", "string"),
                PropertyType("reference_range", "参考范围", "string"),
                PropertyType("status", "状态", "string"),
                PropertyType("collected_at", "采样时间", "timestamp"),
                PropertyType("reported_at", "报告时间", "timestamp"),
                PropertyType("created_at", "创建时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="InsuranceClaim",
            display_name="医保理赔",
            plural_display_name="医保理赔列表",
            primary_key_property_api_name="id",
            title_property_api_name="claim_no",
            description="医保理赔记录",
            icon="shield",
            icon_color="#FDCB6E",
            domain="healthcare",
            properties=[
                PropertyType("id", "理赔ID", "string"),
                PropertyType("patient_id", "患者ID", "string"),
                PropertyType("encounter_id", "就诊ID", "string"),
                PropertyType("claim_no", "理赔编号", "string", indexed_for_search=True),
                PropertyType("total_amount", "总费用", "decimal"),
                PropertyType("approved_amount", "批准金额", "decimal"),
                PropertyType("self_pay_amount", "自费金额", "decimal"),
                PropertyType("status", "状态", "string"),
                PropertyType("submitted_at", "提交日期", "date"),
                PropertyType("processed_at", "处理日期", "date"),
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
        LinkType(
            api_name="patient_lab_results",
            cardinality="OneToMany",
            source=LinkTypeSide("Patient", "lab_results", "检验结果", "检验结果列表"),
            target=LinkTypeSide("LabResult", "patient", "患者"),
            foreign_key_property="patient_id",
        ),
        LinkType(
            api_name="encounter_lab_results",
            cardinality="OneToMany",
            source=LinkTypeSide("Encounter", "lab_results", "检验结果", "检验结果列表"),
            target=LinkTypeSide("LabResult", "encounter", "就诊记录"),
            foreign_key_property="encounter_id",
        ),
        LinkType(
            api_name="patient_claims",
            cardinality="OneToMany",
            source=LinkTypeSide("Patient", "claims", "理赔记录", "理赔记录列表"),
            target=LinkTypeSide("InsuranceClaim", "patient", "患者"),
            foreign_key_property="patient_id",
        ),
        LinkType(
            api_name="encounter_claims",
            cardinality="OneToMany",
            source=LinkTypeSide("Encounter", "claims", "理赔记录", "理赔记录列表"),
            target=LinkTypeSide("InsuranceClaim", "encounter", "就诊记录"),
            foreign_key_property="encounter_id",
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
        ActionType(
            api_name="submitLabOrder",
            display_name="提交检验申请",
            description="为患者提交检验申请",
            target_object_type="LabResult",
            domain="healthcare",
            parameters=[
                ActionParameter("patient_id", "患者ID", "string", required=True),
                ActionParameter("encounter_id", "就诊ID", "string", required=True),
                ActionParameter("test_name", "检验项目", "string", required=True),
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
                PropertyType("phone", "手机号", "string"),
                PropertyType("gender", "性别", "string"),
                PropertyType("age", "年龄", "integer"),
                PropertyType("city", "城市", "string"),
                PropertyType("tier", "会员等级", "string"),
                PropertyType("total_spent", "累计消费", "decimal"),
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
                PropertyType("phone", "联系电话", "string"),
                PropertyType("employee_count", "员工数", "integer"),
                PropertyType("monthly_sales", "月销量", "integer"),
                PropertyType("return_rate", "退货率", "decimal"),
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
                PropertyType("brand", "品牌", "string"),
                PropertyType("sales_count", "销量", "integer"),
                PropertyType("rating", "评分", "decimal"),
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
                PropertyType("shipping_address", "收货地址", "string"),
                PropertyType("coupon_amount", "优惠金额", "decimal"),
                PropertyType("remark", "备注", "string"),
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
                PropertyType("images", "有图", "boolean"),
                PropertyType("helpful_count", "有帮助数", "integer"),
                PropertyType("merchant_reply", "商家回复", "string"),
                PropertyType("created_at", "评价时间", "timestamp"),
            ],
            implements_interfaces=["Auditable"],
        ),
        ObjectType(
            api_name="Coupon",
            display_name="优惠券",
            plural_display_name="优惠券列表",
            primary_key_property_api_name="id",
            title_property_api_name="code",
            description="优惠券",
            icon="ticket",
            icon_color="#E84393",
            domain="ecommerce",
            properties=[
                PropertyType("id", "券ID", "string"),
                PropertyType("code", "券码", "string", indexed_for_search=True),
                PropertyType("type", "类型", "string"),
                PropertyType("discount_value", "折扣值", "decimal"),
                PropertyType("min_order_amount", "最低消费", "decimal"),
                PropertyType("max_discount", "最大折扣", "decimal"),
                PropertyType("valid_from", "生效日期", "date"),
                PropertyType("valid_to", "到期日期", "date"),
                PropertyType("usage_limit", "使用次数限制", "integer"),
                PropertyType("used_count", "已使用次数", "integer"),
                PropertyType("status", "状态", "string"),
                PropertyType("created_at", "创建时间", "timestamp"),
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
        ActionType(
            api_name="issueCoupon",
            display_name="发放优惠券",
            description="向用户发放优惠券",
            target_object_type="Coupon",
            domain="ecommerce",
            parameters=[
                ActionParameter("code", "券码", "string", required=True),
                ActionParameter("type", "类型", "string", required=True),
                ActionParameter("discount_value", "折扣值", "decimal", required=True),
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
    # ── 供应商: 使用真实数据，评分和注册资本来自数据池 ──────────────────
    suppliers = []
    for i, (name, country, rating, capital, scope) in enumerate(SUPPLIERS, 1):
        domain = name.split(".")[0].split(" ")[0].lower().replace("供应链", "").replace("科技", "")
        suppliers.append({
            "id": _id("SUP", i),
            "name": name,
            "country": country,
            "rating": rating,
            "contact_email": f"procurement@{domain}.com",
            "contact_phone": f"+{'86' if country == 'CN' else '1'}-{random.randint(13000000000, 19999999999) if country == 'CN' else random.randint(2000000000, 9999999999)}",
            "address": f"{country} business district #{random.randint(1, 200)}",
            "business_scope": scope,
            "registered_capital": capital,
            "status": random.choice(["正常"] * 9 + ["暂停"]),
            "created_at": _rand_timestamp(2020, 2024),
        })

    # ── 产品: 关联到对应类别的供应商，价格按类别合理分布 ──────────────────
    # 按经营范围把供应商分组
    scope_map: dict[str, list[dict]] = {}
    for s in suppliers:
        for cat in s["business_scope"].split(","):
            cat = cat.strip()
            scope_map.setdefault(cat, []).append(s)

    products = []
    for i, (name, category, price_range, weight_range, brand, origin) in enumerate(PRODUCTS_DATA, 1):
        # 优先从经营范围匹配的供应商中选择
        candidates = scope_map.get(category, suppliers)
        sup = random.choice(candidates)
        products.append({
            "id": _id("PRD", i),
            "name": name,
            "category": category,
            "unit_price": round(random.uniform(*price_range), 2),
            "weight": round(random.uniform(*weight_range), 3),
            "supplier_id": sup["id"],
            "brand": brand,
            "model": name.split(" ")[-1] if " " in name else f"V{random.randint(1, 5)}.0",
            "origin": origin,
            "min_order_qty": random.choice([1, 10, 50, 100, 500]),
            "lead_time_days": random.choice([3, 5, 7, 14, 21, 30]),
            "created_at": _rand_timestamp(2021, 2024),
        })

    # ── 仓库: 使用真实坐标 ───────────────────────────────────────────────
    warehouses = []
    for i, (name, addr, lat, lng, wh_type, manager) in enumerate(WAREHOUSE_DATA, 1):
        warehouses.append({
            "id": _id("WH", i),
            "name": name,
            "location": addr[:6],
            "capacity": random.choice([10000, 20000, 30000, 50000]),
            "latitude": lat,
            "longitude": lng,
            "address": addr,
            "warehouse_type": wh_type,
            "manager": manager,
            "phone": f"+{random.choice(['86', '81', '1', '49', '82'])}-{random.randint(1000000000, 9999999999)}",
            "utilization_rate": round(random.uniform(0.45, 0.92), 2),
            "created_at": _rand_timestamp(2020, 2023),
        })

    # ── 采购单: 金额基于实际产品价格 ──────────────────────────────────────
    purchase_orders = []
    sc_statuses = ["待审批", "已审批", "已发货", "已交付", "已取消"]
    priorities = ["紧急", "普通", "普通", "普通", "低"]
    payment_terms_list = ["预付30%", "月结30天", "月结60天", "货到付款", "季结"]
    currencies = ["CNY", "USD", "EUR", "JPY"]
    for i in range(1, 61):
        sup = random.choice(suppliers)
        # 模拟: 选几个产品算总价
        n_items = random.randint(1, 4)
        po_products = random.sample(products, min(n_items, len(products)))
        total = sum(round(p["unit_price"] * random.randint(p.get("min_order_qty", 1), p.get("min_order_qty", 1) * 5), 2) for p in po_products)
        status = random.choice(sc_statuses)
        created = _rand_timestamp(2023, 2025)
        purchase_orders.append({
            "id": _id("PO", i),
            "supplier_id": sup["id"],
            "total_amount": total,
            "status": status,
            "currency": random.choice(currencies) if sup["country"] != "CN" else "CNY",
            "priority": random.choice(priorities),
            "payment_terms": random.choice(payment_terms_list),
            "expected_delivery": _rand_date(2024, 2026),
            "remark": random.choice(["", "", "请加急处理", "需分批交货", "请提前通知", ""]),
            "created_at": created,
        })

    # ── 发货单: 与采购单关联 ──────────────────────────────────────────────
    carriers = ["顺丰速运", "中通快递", "德邦物流", "FedEx", "DHL", "UPS", "EMS"]
    ship_methods = ["陆运", "空运", "海运"]
    shipments = []
    for po in purchase_orders:
        n_ship = random.randint(1, 3)
        for j in range(n_ship):
            ship_status = random.choice(["待揽收", "运输中", "已签收", "已签收"])
            shipments.append({
                "id": _id("SHP", len(shipments) + 1),
                "purchase_order_id": po["id"],
                "warehouse_id": random.choice(warehouses)["id"],
                "tracking_number": f"{'SF' if '顺丰' in (car := random.choice(carriers)) else 'TN'}{_rand_str(10).upper()}",
                "status": ship_status,
                "carrier": car if 'car' in dir() else random.choice(carriers),
                "weight": round(random.uniform(0.5, 200), 1),
                "shipping_method": random.choice(ship_methods),
                "estimated_arrival": _rand_date(2024, 2026),
                "created_at": _rand_timestamp(2023, 2025),
            })
    # Fix carrier field for all shipments
    for s in shipments:
        if "car" not in dir() or s["carrier"] not in carriers:
            s["carrier"] = random.choice(carriers)

    # ── 合同 ─────────────────────────────────────────────────────────────
    contracts = []
    contract_statuses = ["生效中", "生效中", "已到期", "草稿", "已终止"]
    for i in range(1, 31):
        sup = random.choice(suppliers)
        value = round(sup["registered_capital"] * random.uniform(0.05, 0.4) * 10000, 2)
        start = _rand_date(2022, 2024)
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = start_dt + timedelta(days=random.choice([365, 730, 1095]))
        contracts.append({
            "id": _id("CTR", i),
            "supplier_id": sup["id"],
            "contract_no": f"SC-{random.randint(2022, 2025)}-{str(i).zfill(4)}",
            "title": f"{sup['name']}{'年度框架' if random.random() > 0.4 else '专项'}采购合同",
            "value": value,
            "currency": "CNY" if sup["country"] == "CN" else random.choice(["USD", "EUR"]),
            "start_date": start,
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "status": random.choice(contract_statuses),
            "signed_at": (start_dt - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
            "created_at": _rand_timestamp(2022, 2024),
        })

    # ── 库存: 每个产品在1-2个仓库有库存 ───────────────────────────────────
    inventory = []
    for prod in products:
        whs = random.sample(warehouses, random.randint(1, min(2, len(warehouses))))
        for wh in whs:
            qty = random.randint(50, 5000)
            reserved = random.randint(0, qty // 3)
            inventory.append({
                "id": _id("INV", len(inventory) + 1),
                "product_id": prod["id"],
                "warehouse_id": wh["id"],
                "quantity": qty,
                "reserved_qty": reserved,
                "available_qty": qty - reserved,
                "last_checked": _rand_date(2024, 2025),
                "created_at": _rand_timestamp(2021, 2024),
            })

    return {
        "Supplier": suppliers,
        "ScProduct": products,
        "Warehouse": warehouses,
        "PurchaseOrder": purchase_orders,
        "Shipment": shipments,
        "Contract": contracts,
        "Inventory": inventory,
    }


def _gen_finance_instances() -> dict[str, list[dict]]:
    # ── 客户: 使用预定义画像，等级与收入关联 ──────────────────────────────
    customers = []
    tier_balance_ranges = {"钻石": (500000, 5000000), "白金": (200000, 2000000), "金卡": (50000, 500000), "银卡": (10000, 100000), "普通": (1000, 50000)}
    tier_card_limits = {"钻石": (200000, 500000), "白金": (100000, 300000), "金卡": (30000, 100000), "银卡": (10000, 50000), "普通": (5000, 20000)}

    for i, (name, tier, risk, occ, income, vip_year) in enumerate(CUSTOMER_PROFILES, 1):
        customers.append({
            "id": _id("CUS", i),
            "name": name,
            "tier": tier,
            "risk_level": risk,
            "kyc_status": "已认证" if random.random() > 0.1 else random.choice(["待认证", "认证中"]),
            "phone": f"+{random.choice(['86', '1', '44', '81', '82', '49'])}-{random.randint(10000000000, 19999999999)}",
            "occupation": occ,
            "annual_income": income,
            "vip_since": vip_year if tier in ("白金", "钻石") else None,
            "created_at": f"{vip_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(8,18):02d}:{random.randint(0,59):02d}:00",
        })

    # ── 账户: 客户等级决定余额范围 ─────────────────────────────────────────
    accounts = []
    acc_types = ["储蓄账户", "活期账户", "定期账户", "理财账户"]
    branches = ["工商银行北京分行", "建设银行上海支行", "中国银行广州分行", "招商银行深圳分行",
                "Chase Bank NYC", "Deutsche Bank Frankfurt", "Mizuho Bank Tokyo"]
    for cust in customers:
        n_acc = {"钻石": 3, "白金": 3, "金卡": 2, "银卡": 2, "普通": 1}[cust["tier"]]
        bal_range = tier_balance_ranges[cust["tier"]]
        currency = "CNY" if "CN" in cust.get("phone", "86") else random.choice(["CNY", "USD", "EUR"])
        for j in range(n_acc):
            accounts.append({
                "id": _id("ACC", len(accounts) + 1),
                "customer_id": cust["id"],
                "type": random.choice(acc_types),
                "balance": round(random.uniform(*bal_range), 2),
                "currency": currency,
                "branch": random.choice(branches),
                "status": "正常",
                "opened_at": _rand_date(2018, 2024),
                "created_at": _rand_timestamp(2018, 2024),
            })

    # ── 交易: 按类型不同金额分布，VIP 客户交易更频繁 ───────────────────────
    transactions = []
    # 交易类型: (类型名, 金额范围, 描述模板, 渠道)
    tx_profiles = [
        ("工资",   (8000, 80000),  "2024年{m}月工资",       "网银"),
        ("消费",   (10, 5000),     "商场购物",              "手机银行"),
        ("消费",   (50, 3000),     "餐饮消费",              "手机银行"),
        ("转账",   (100, 100000),  "个人转账",              "手机银行"),
        ("存款",   (1000, 200000), "定期存款",              "柜台"),
        ("取款",   (100, 10000),   "ATM取款",              "ATM"),
        ("理财收益",(50, 5000),    "理财产品收益到账",       "网银"),
    ]
    channels = ["网银", "手机银行", "ATM", "柜台"]
    for i in range(1, 151):
        from_acc = random.choice(accounts)
        to_acc = random.choice([a for a in accounts if a["id"] != from_acc["id"]])
        profile = random.choice(tx_profiles)
        amount = round(random.uniform(*profile[1]), 2)
        desc = profile[2].format(m=random.randint(1, 12)) if "{m}" in profile[2] else profile[2]
        transactions.append({
            "id": _id("TXN", i),
            "from_account": from_acc["id"],
            "to_account": to_acc["id"],
            "amount": amount,
            "type": profile[0],
            "status": random.choices(["成功", "成功", "成功", "失败", "处理中"], weights=[85, 85, 85, 10, 5])[0],
            "channel": random.choice(channels),
            "description": desc,
            "timestamp": _rand_timestamp(2023, 2025),
        })

    # ── 金融产品: 增加风险等级、期限、发行方 ────────────────────────────────
    fi_products_data = [
        ("稳健理财A",   "理财产品", 3.5,  1000,   "低风险",  365,  "招商银行"),
        ("进取理财B",   "理财产品", 6.2,  10000,  "中风险",  730,  "招商银行"),
        ("激进理财C",   "理财产品", 12.5, 50000,  "高风险", 1095,  "中信证券"),
        ("个人消费贷",  "贷款",     4.35, 0,      "低风险",  360,  "工商银行"),
        ("住房贷款",    "贷款",     3.85, 0,      "低风险", 3600,  "建设银行"),
        ("经营贷",      "贷款",     4.75, 0,      "中风险", 1095,  "中国银行"),
        ("定期存款1年", "存款",     2.75, 50,     "低风险",  365,  "工商银行"),
        ("大额存单3年", "存款",     3.35, 200000, "低风险", 1095,  "建设银行"),
        ("结构性存款",  "存款",     4.15, 100000, "中风险",  180,  "招商银行"),
        ("外汇理财",    "理财产品", 5.8,  5000,   "高风险",  90,   "中国银行"),
    ]
    products = []
    for i, (name, cat, rate, min_inv, risk, term, issuer) in enumerate(fi_products_data, 1):
        products.append({
            "id": _id("FPR", i),
            "name": name,
            "category": cat,
            "interest_rate": rate,
            "min_investment": min_inv,
            "risk_level": risk,
            "term_days": term,
            "issuer": issuer,
            "created_at": _rand_timestamp(2021, 2024),
        })

    # ── 信用卡: 额度与客户等级匹配 ─────────────────────────────────────────
    credit_cards = []
    card_types = {"钻石": "白金卡", "白金": "白金卡", "金卡": "金卡", "银卡": "普卡", "普通": "普卡"}
    for cust in customers:
        if random.random() > 0.2:  # 80% 客户有信用卡
            limit_range = tier_card_limits[cust["tier"]]
            limit = round(random.uniform(*limit_range), -3)  # 取整到千
            used = round(random.uniform(0, limit * 0.7), 2)
            credit_cards.append({
                "id": _id("CC", len(credit_cards) + 1),
                "customer_id": cust["id"],
                "card_number": f"****-****-****-{random.randint(1000, 9999)}",
                "card_type": card_types[cust["tier"]],
                "credit_limit": limit,
                "used_amount": used,
                "available_amount": round(limit - used, 2),
                "billing_day": random.randint(1, 28),
                "status": "正常",
                "created_at": _rand_timestamp(2019, 2024),
            })

    # ── 贷款: 月供按等额本息公式计算 ───────────────────────────────────────
    loans = []
    loan_types = ["房贷", "车贷", "消费贷", "经营贷"]
    loan_statuses = ["还款中", "还款中", "已结清", "审批中", "逾期"]
    for i in range(1, 21):
        cust = random.choice(customers)
        cust_accounts = [a for a in accounts if a["customer_id"] == cust["id"]]
        loan_type = random.choice(loan_types)
        principal = round(random.uniform({"房贷": 500000, "车贷": 80000, "消费贷": 50000, "经营贷": 200000}[loan_type] * 0.5,
                                          {"房贷": 500000, "车贷": 80000, "消费贷": 50000, "经营贷": 200000}[loan_type] * 2), -3)
        rate = round(random.uniform(3.5, 6.5), 2) / 100
        term = random.choice([12, 24, 36, 60, 120, 240, 360])
        # 等额本息月供公式
        monthly = round(principal * rate / 12 * (1 + rate / 12) ** term / ((1 + rate / 12) ** term - 1), 2) if term > 0 else 0
        status = random.choice(loan_statuses)
        remaining = round(principal * random.uniform(0.1, 1.0), 2) if status == "还款中" else (0 if status == "已结清" else principal)
        loans.append({
            "id": _id("LOAN", i),
            "customer_id": cust["id"],
            "account_id": cust_accounts[0]["id"] if cust_accounts else None,
            "loan_type": loan_type,
            "principal": principal,
            "interest_rate": round(rate * 100, 2),
            "term_months": term,
            "monthly_payment": monthly,
            "remaining_principal": remaining,
            "status": status,
            "applied_at": _rand_date(2020, 2024),
            "approved_at": _rand_date(2020, 2024),
            "created_at": _rand_timestamp(2020, 2024),
        })

    return {
        "FiCustomer": customers,
        "Account": accounts,
        "Transaction": transactions,
        "FiProduct": products,
        "CreditCard": credit_cards,
        "Loan": loans,
    }


def _gen_healthcare_instances() -> dict[str, list[dict]]:
    # ── 患者: 有真实年龄分布，关联诊断类型 ────────────────────────────────
    patients = []
    genders = ["男", "女"]
    allergy_options = ["无", "青霉素过敏", "花粉过敏", "海鲜过敏", "磺胺类药物过敏", "尘螨过敏"]
    for i, name in enumerate(CUSTOMER_NAMES[:15], 1):
        dob = _rand_date(1950, 2005)
        birth_year = int(dob[:4])
        age = 2025 - birth_year
        patients.append({
            "id": _id("PAT", i),
            "name": name,
            "dob": dob,
            "gender": random.choice(genders),
            "blood_type": random.choice(["A", "B", "O", "AB"]) + random.choice(["+", "-"]),
            "insurance_id": _id("INS", random.randint(10000, 99999), 5),
            "phone": f"+{random.choice(['86', '1', '81', '82'])}-{random.randint(10000000000, 19999999999)}",
            "emergency_contact": random.choice(CUSTOMER_NAMES[:10]),
            "allergies": random.choice(allergy_options),
            "created_at": _rand_timestamp(2020, 2024),
        })

    # 患者按年龄分组
    young_patients = [p for p in patients if (2025 - int(p["dob"][:4])) < 40]
    old_patients = [p for p in patients if (2025 - int(p["dob"][:4])) >= 40]
    chronic_diagnoses = [d for d in DIAGNOSES if d[3]]  # 慢性病
    acute_diagnoses = [d for d in DIAGNOSES if not d[3]]  # 急性病

    # ── 医疗机构: 增加床位和医生数 ─────────────────────────────────────────
    providers = []
    provider_data = [
        ("协和医院",       "三甲医院", "北京",   "三级甲等", 2500, 3000),
        ("华西医院",       "三甲医院", "成都",   "三级甲等", 4300, 5000),
        ("Mayo Clinic",    "综合医院", "Rochester, MN", "JCI认证", 1200, 1500),
        ("东京大学医学部附属病院", "教学医院", "東京", "JCI认证", 1100, 1300),
        ("社区卫生服务中心浦东","社区诊所","上海", "基本医疗",   50,   30),
        ("北京大学第一医院","三甲医院","北京",  "三级甲等", 1800, 2200),
        ("Ruijin Hospital","三甲医院","上海",  "三级甲等", 2000, 2500),
        ("Samsung Medical","综合医院","首尔",  "JCI认证",  1900, 2300),
    ]
    doctors = ["李明", "王强", "张华", "刘芳", "陈伟", "赵丽", "周杰", "吴静",
               "Dr. Smith", "Dr. Johnson", "Dr. Brown", "田中先生", "김박사"]
    for i, (name, typ, loc, acc, beds, docs) in enumerate(provider_data, 1):
        providers.append({
            "id": _id("PRV", i),
            "name": name,
            "type": typ,
            "location": loc,
            "accreditation": acc,
            "latitude": round(random.uniform(22, 52), 4),
            "longitude": round(random.uniform(-122, 140), 4),
            "address": f"{loc} 医学中心",
            "bed_count": beds,
            "doctor_count": docs,
            "phone": f"+{random.choice(['86', '1', '81', '82'])}-{random.randint(10000000, 99999999)}",
            "created_at": _rand_timestamp(2018, 2023),
        })

    # ── 诊断: 年龄相关性，严重程度，主治医生 ──────────────────────────────
    diagnoses = []
    severities = ["轻度", "中度", "重度"]
    for i in range(1, 81):
        # 老年患者更多慢性病，年轻患者更多急性病
        if old_patients and (random.random() < 0.65):
            patient = random.choice(old_patients)
            icd, desc, detail, chronic, drug_kw = random.choice(chronic_diagnoses)
        else:
            pool = young_patients if young_patients else patients
            patient = random.choice(pool)
            icd, desc, detail, chronic, drug_kw = random.choice(acute_diagnoses)

        prov = random.choice(providers)
        diag_date = _rand_date(2023, 2025)
        diag_dt = datetime.strptime(diag_date, "%Y-%m-%d")
        follow_up = (diag_dt + timedelta(days=random.choice([7, 14, 30, 90]))).strftime("%Y-%m-%d")
        diagnoses.append({
            "id": _id("DIA", i),
            "patient_id": patient["id"],
            "provider_id": prov["id"],
            "icd_code": icd,
            "description": f"{desc} - {detail}",
            "severity": random.choice(severities) if chronic else random.choice(["轻度", "轻度", "中度"]),
            "doctor_name": random.choice(doctors),
            "date": diag_date,
            "follow_up_date": follow_up if random.random() > 0.3 else None,
            "created_at": _rand_timestamp(2023, 2025),
        })

    # ── 药物: 增加规格、单价、医保、副作用 ─────────────────────────────────
    medications = []
    med_details = [
        ("规格: 0.25g*24粒",  15.8,  True,  "偶见皮疹、胃肠不适"),
        ("规格: 0.3g*20片",   12.5,  True,  "偶见恶心、头晕"),
        ("规格: 0.25g*6片",   28.0,  True,  "过敏反应、腹泻"),
        ("规格: 10mg*6片",    22.0,  True,  "偶见嗜睡、口干"),
        ("规格: 20mg*14粒",   35.0,  True,  "头痛、腹泻"),
        ("规格: 0.5g*30片",   8.5,   True,  "胃肠不适、乳酸酸中毒"),
        ("规格: 10mg*7片",    42.0,  True,  "肌痛、肝酶升高"),
        ("规格: 30mg*7片",    38.0,  True,  "头痛、面部潮红"),
        ("规格: 200mg*30片",  25.0,  False, "胃肠道反应"),
        ("规格: 500mg*20粒",  18.0,  True,  "过敏反应"),
        ("规格: 500mg*20片",  12.0,  True,  "胃肠不适、乳酸酸中毒"),
        ("规格: 10mg*30片",   55.0,  True,  "肌痛、肝酶升高"),
        ("规格: 10mg*30片",   32.0,  True,  "干咳、血管性水肿"),
        ("规格: 20mg*14粒",   28.0,  True,  "头痛、腹泻"),
        ("规格: 25μg*100片",  68.0,  True,  "心悸、体重减轻"),
        ("规格: 5mg*30片",    35.0,  True,  "踝部水肿、头痛"),
        ("规格: 50mg*30片",   25.0,  True,  "疲劳、心动过缓"),
        ("规格: 50mg*30片",   45.0,  True,  "头晕、高血钾"),
    ]
    manufacturers = ["辉瑞制药", "恒瑞医药", "阿斯利康", "诺华制药", "拜耳医药",
                     "默沙东", "葛兰素史克", "赛诺菲"]
    dosage_forms = ["片剂", "胶囊", "注射液", "口服液", "颗粒", "缓释片", "肠溶胶囊"]
    for i, name in enumerate(MEDICATION_NAMES[:15], 1):
        detail = med_details[i - 1] if i - 1 < len(med_details) else ("规格: 标准装", 20.0, True, "详见说明书")
        medications.append({
            "id": _id("MED", i),
            "name": name,
            "dosage_form": random.choice(dosage_forms),
            "manufacturer": random.choice(manufacturers),
            "ndc_code": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}-{random.randint(10, 99)}",
            "specification": detail[0],
            "unit_price": detail[1],
            "insurance_covered": detail[2],
            "side_effects": detail[3],
            "created_at": _rand_timestamp(2020, 2024),
        })

    # ── 就诊: 关联患者和医生，费用与类型匹配 ──────────────────────────────
    encounters = []
    encounter_types = ["门诊", "门诊", "急诊", "住院", "复查", "体检"]
    complaint_pools = {
        "门诊": ["头痛发热", "咳嗽咽痛", "腹痛腹泻", "腰背疼痛", "皮肤红疹"],
        "急诊": ["剧烈腹痛", "高热不退", "胸闷气短", "外伤出血", "呼吸困难"],
        "住院": ["手术治疗", "系统治疗", "重症监护", "康复治疗"],
        "复查": ["定期复查", "术后复查", "指标监测", "用药调整"],
        "体检": ["年度体检", "入职体检", "入学体检"],
    }
    cost_ranges = {"门诊": (80, 500), "急诊": (300, 3000), "住院": (5000, 80000), "复查": (100, 800), "体检": (200, 1500)}
    for i in range(1, 101):
        patient = random.choice(patients)
        prov = random.choice(providers)
        enc_type = random.choice(encounter_types)
        complaints = complaint_pools.get(enc_type, ["不适就诊"])
        encounters.append({
            "id": _id("ENC", i),
            "patient_id": patient["id"],
            "provider_id": prov["id"],
            "type": enc_type,
            "date": _rand_date(2023, 2025),
            "chief_complaint": random.choice(complaints),
            "doctor_name": random.choice(doctors),
            "cost": round(random.uniform(*cost_ranges[enc_type]), 2),
            "follow_up_required": random.random() > 0.5,
            "created_at": _rand_timestamp(2023, 2025),
        })

    # ── 检验结果: 与就诊关联，慢性病患者数值偏高 ───────────────────────────
    lab_results = []
    for enc in encounters:
        n_tests = random.randint(2, 5)
        chosen_tests = random.sample(LAB_TESTS, min(n_tests, len(LAB_TESTS)))
        patient = next(p for p in patients if p["id"] == enc["patient_id"])
        is_diabetic = any(d["patient_id"] == patient["id"] and d["icd_code"] == "E11.9" for d in diagnoses)
        is_hypertensive = any(d["patient_id"] == patient["id"] and d["icd_code"] == "I10" for d in diagnoses)

        for test_name, unit, ref_range, normal_range in chosen_tests:
            lo, hi = normal_range
            # 慢性病患者特定指标偏高
            if is_diabetic and "血糖" in test_name:
                val = round(random.uniform(6.5, 15.0), 1)
                status = "异常"
            elif is_diabetic and "糖化" in test_name:
                val = round(random.uniform(6.5, 12.0), 1)
                status = "异常"
            elif is_hypertensive and "收缩压" in test_name:
                val = round(random.uniform(140, 180), 0)
                status = "异常"
            elif is_hypertensive and "舒张压" in test_name:
                val = round(random.uniform(90, 120), 0)
                status = "异常"
            else:
                val = round(random.uniform(lo * 0.9, hi * 1.1), 1)
                if val < lo * 0.8 or val > hi * 1.2:
                    status = "异常"
                elif val < lo or val > hi:
                    status = "临界"
                else:
                    status = "正常"

            enc_dt = datetime.strptime(enc["date"], "%Y-%m-%d")
            lab_results.append({
                "id": _id("LAB", len(lab_results) + 1),
                "patient_id": patient["id"],
                "encounter_id": enc["id"],
                "test_name": test_name,
                "result_value": val,
                "unit": unit,
                "reference_range": ref_range,
                "status": status,
                "collected_at": enc["date"] + f"T{random.randint(7,11):02d}:{random.randint(0,59):02d}:00",
                "reported_at": (enc_dt + timedelta(hours=random.randint(2, 24))).strftime("%Y-%m-%dT%H:%M:%S"),
                "created_at": _rand_timestamp(2023, 2025),
            })

    # ── 医保理赔: 与就诊关联 ──────────────────────────────────────────────
    claims = []
    claim_statuses = ["已批准", "已批准", "已支付", "待审核", "已拒绝"]
    for i, enc in enumerate(random.sample(encounters, min(40, len(encounters))), 1):
        total = enc["cost"] + round(random.uniform(0, enc["cost"] * 0.5), 2)
        approved = round(total * random.uniform(0.5, 0.85), 2)
        self_pay = round(total - approved, 2)
        proc_date = datetime.strptime(enc["date"], "%Y-%m-%d") + timedelta(days=random.randint(5, 30))
        claims.append({
            "id": _id("CLM", i),
            "patient_id": enc["patient_id"],
            "encounter_id": enc["id"],
            "claim_no": f"CLM{random.randint(2023, 2025)}{random.randint(100000, 999999)}",
            "total_amount": round(total, 2),
            "approved_amount": approved,
            "self_pay_amount": self_pay,
            "status": random.choice(claim_statuses),
            "submitted_at": (datetime.strptime(enc["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
            "processed_at": proc_date.strftime("%Y-%m-%d"),
            "created_at": _rand_timestamp(2023, 2025),
        })

    return {
        "Patient": patients,
        "Provider": providers,
        "Diagnosis": diagnoses,
        "Medication": medications,
        "Encounter": encounters,
        "LabResult": lab_results,
        "InsuranceClaim": claims,
    }


def _gen_ecommerce_instances() -> dict[str, list[dict]]:
    # ── 用户: 增加真实信息，等级与累计消费关联 ──────────────────────────────
    users = []
    tier_spent_ranges = {"钻石会员": (50000, 200000), "金牌会员": (10000, 50000), "银牌会员": (2000, 15000), "普通会员": (0, 5000)}
    for i in range(1, 31):
        name = random.choice(CUSTOMER_NAMES)
        tier = random.choices(["普通会员", "银牌会员", "金牌会员", "钻石会员"], weights=[40, 30, 20, 10])[0]
        spent_range = tier_spent_ranges[tier]
        users.append({
            "id": _id("USR", i),
            "username": f"{name.split()[0].lower()}_{random.randint(100, 9999)}",
            "email": f"{name.split()[0].lower()}{random.randint(10, 99)}@{'gmail.com' if random.random() > 0.5 else 'qq.com'}",
            "phone": f"1{random.choice(['3', '5', '7', '8', '9'])}{random.randint(100000000, 999999999)}",
            "gender": random.choice(["男", "女"]),
            "age": random.randint(18, 55),
            "city": random.choice(ECOM_USER_CITIES),
            "tier": tier,
            "total_spent": round(random.uniform(*spent_range), 2),
            "registered_at": _rand_timestamp(2020, 2024),
            "created_at": _rand_timestamp(2020, 2024),
        })

    # ── 商家: 增加真实数据 ──────────────────────────────────────────────────
    merchants = []
    mch_categories = ["电子产品", "服装鞋帽", "食品饮料", "家居用品", "美妆个护", "图书音像"]
    for i, name in enumerate(MERCHANT_NAMES, 1):
        cat = mch_categories[i - 1] if i - 1 < len(mch_categories) else random.choice(mch_categories)
        merchants.append({
            "id": _id("MCH", i),
            "name": name,
            "category": cat,
            "rating": round(random.uniform(4.0, 5.0), 1),
            "verified": random.choices([True, False], weights=[80, 20])[0],
            "latitude": round(random.uniform(22, 42), 4),
            "longitude": round(random.uniform(100, 125), 4),
            "address": random.choice(ECOM_ADDRESSES),
            "phone": f"1{random.choice(['3', '5', '7', '8'])}{random.randint(100000000, 999999999)}",
            "employee_count": random.choice([5, 15, 50, 200, 500]),
            "monthly_sales": random.randint(100, 50000),
            "return_rate": round(random.uniform(0.01, 0.08), 3),
            "created_at": _rand_timestamp(2020, 2023),
        })

    # ── 商品: 按类别合理定价，关联对应商家 ──────────────────────────────────
    products = []
    # 商家按主营类别分组
    mch_by_cat: dict[str, list[dict]] = {}
    for m in merchants:
        mch_by_cat.setdefault(m["category"], []).append(m)

    for i, (name, category, price_range, brand) in enumerate(ECOM_PRODUCTS_DATA, 1):
        candidates = mch_by_cat.get(category, merchants)
        mch = random.choice(candidates)
        price = round(random.uniform(*price_range), 2)
        products.append({
            "id": _id("EPR", i),
            "merchant_id": mch["id"],
            "name": name,
            "price": price,
            "category": category,
            "stock": random.randint(0, 2000),
            "brand": brand,
            "sales_count": random.randint(10, 50000),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "created_at": _rand_timestamp(2021, 2024),
        })

    # ── 订单: VIP 用户订单更多，状态有时间逻辑 ──────────────────────────────
    orders = []
    pay_methods = ["支付宝", "微信支付", "银行卡", "信用卡", "花呗"]
    # 状态序列: 已完成 > 已发货 > 已支付 > 待支付
    final_statuses = ["已完成", "已完成", "已完成", "已取消", "退款中"]
    progress_statuses = ["待支付", "已支付", "已发货", "已完成"]

    order_idx = 0
    for user in users:
        # VIP 用户订单更多
        n_orders = {"钻石会员": random.randint(8, 15), "金牌会员": random.randint(4, 8),
                     "银牌会员": random.randint(2, 5), "普通会员": random.randint(1, 3)}[user["tier"]]
        for _ in range(n_orders):
            order_idx += 1
            prod = random.choice(products)
            qty = random.randint(1, 3)
            coupon = round(random.uniform(0, prod["price"] * qty * 0.2), 2) if random.random() > 0.7 else 0
            status = random.choice(final_statuses)
            created = _rand_timestamp(2023, 2025)
            orders.append({
                "id": _id("ORD", order_idx),
                "user_id": user["id"],
                "product_id": prod["id"],
                "quantity": qty,
                "total": round(prod["price"] * qty - coupon, 2),
                "status": status,
                "payment_method": random.choice(pay_methods),
                "shipping_address": random.choice(ECOM_ADDRESSES),
                "coupon_amount": coupon,
                "remark": random.choice(["", "", "请尽快发货", "包装好一点", ""]),
                "created_at": created,
            })

    # ── 评价: 评分与内容一致，有图率与评分正相关 ────────────────────────────
    reviews = []
    for i in range(1, 81):
        rating = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
        content_pool = REVIEW_POOLS.get(rating, REVIEW_POOLS[3])
        prod = random.choice(products)
        user = random.choice(users)
        has_images = random.random() < (0.1 * rating)  # 高评分更可能有图
        reply = random.choice(["感谢您的支持！", "欢迎再次光临！",
                                "很抱歉给您带来不好的体验，我们会改进。",
                                ""]) if rating <= 3 or random.random() > 0.5 else ""
        reviews.append({
            "id": _id("REV", i),
            "user_id": user["id"],
            "product_id": prod["id"],
            "rating": rating,
            "content": random.choice(content_pool),
            "images": has_images,
            "helpful_count": random.randint(0, 50 * rating),
            "merchant_reply": reply,
            "created_at": _rand_timestamp(2023, 2025),
        })

    # ── 优惠券 ─────────────────────────────────────────────────────────────
    coupons = []
    coupon_types = ["满减", "折扣", "免运费"]
    for i in range(1, 16):
        ctype = random.choice(coupon_types)
        code = f"{'SAVE' if ctype == '满减' else 'PCT' if ctype == '折扣' else 'FREE'}{random.randint(1000, 9999)}"
        valid_from = _rand_date(2024, 2025)
        valid_from_dt = datetime.strptime(valid_from, "%Y-%m-%d")
        valid_to = (valid_from_dt + timedelta(days=random.choice([30, 60, 90, 180]))).strftime("%Y-%m-%d")
        coupons.append({
            "id": _id("CPN", i),
            "code": code,
            "type": ctype,
            "discount_value": round(random.uniform(5, 100), 2) if ctype == "满减" else round(random.uniform(0.5, 0.9), 2),
            "min_order_amount": round(random.choice([0, 50, 100, 200, 500]), 2),
            "max_discount": round(random.uniform(50, 300), 2) if ctype == "折扣" else None,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "usage_limit": random.choice([1, 3, 5, 10, -1]),
            "used_count": random.randint(0, 500),
            "status": random.choice(["有效", "有效", "已过期", "已用完"]),
            "created_at": _rand_timestamp(2024, 2025),
        })

    return {
        "EcomUser": users,
        "Merchant": merchants,
        "EcomProduct": products,
        "EcomOrder": orders,
        "Review": reviews,
        "Coupon": coupons,
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

    store = JsonOntologyStore(data_dir)
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

    store = JsonOntologyStore()
    all_instances = store.load_all_instances()
    total = sum(len(v) for v in all_instances.values())
    print(f"  {total} total instances across {len(all_instances)} types")
