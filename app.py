import os
import json
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret_key"

# OpenAI client for AI advisor (requires OPENAI_API_KEY in environment)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Feature flag: you can turn this off for clients without AI
ENABLE_AI_ADVISOR = True

# ---------- TRANSLATIONS ----------

TEXTS = {
    "en": {
        # Global / layout
        "site_title": "SkyLane Shop – Demo Export Store",
        "brand_name": "SkyLane Shop",
        "nav_home": "Home",
        "nav_products": "Products",
        "nav_cart": "Basket",
        "nav_login": "Login",
        "nav_account": "My Account",
        "nav_logout": "Logout",
        "footer_text": (
            "Demo export shop website – showing product list, basket, account and checkout. "
            "Use this as an example for clients who want an online store."
        ),

        # Index
        "home_title": "SkyLane Shop – Demo Export Store",
        "home_heading": "SkyLane Demo Store",
        "home_tagline": (
            "Example of an export-oriented online store with shopping basket and account area."
        ),
        "home_btn_details": "Details",
        "home_btn_add": "Add",

        # Homepage expansion (more front-page content)
        "home_hero_kicker": "B2B / Export storefront template",
        "home_hero_title": "Demo Export Storefront",
        "home_hero_sub": "A bilingual, buyer-friendly demo shop that shows how products can be presented to international customers.",
        "home_cta_browse": "Browse products",
        "home_cta_ai": "Ask AI advisor",
        "home_cta_cart": "View basket",
        "home_badge_mobile": "Mobile-ready",
        "home_badge_bilingual": "EN/CN",
        "home_badge_export": "Export-friendly",
        "home_badge_demo": "Demo",

        "home_quick_title": "At a glance",
        "home_quick_sub": "Key highlights buyers notice first.",
        "home_quick_item1_title": "Clear listings",
        "home_quick_item1_desc": "Images, short benefits, and price display.",
        "home_quick_item2_title": "Basket flow",
        "home_quick_item2_desc": "Add, update quantities, and checkout request.",
        "home_quick_item3_title": "Account area",
        "home_quick_item3_desc": "Demo login and order history placeholders.",
        "home_quick_item4_title": "AI advisor (optional)",
        "home_quick_item4_desc": "Recommends 2–3 items from your catalog.",

        "home_includes_kicker": "Homepage content",
        "home_includes_title": "What this demo includes",
        "home_includes_sub": "More front-page content so the shop feels complete and client-ready.",

        "home_feature1_title": "Bilingual storefront",
        "home_feature1_desc": "Language toggle so buyers understand your offer quickly.",
        "home_feature2_title": "Buyer-ready product cards",
        "home_feature2_desc": "Short descriptions and pricing, with a clean product detail page.",
        "home_feature3_title": "Basket + checkout request",
        "home_feature3_desc": "A simple checkout flow that can be connected to real payments later.",
        "home_feature4_title": "AI product advisor",
        "home_feature4_desc": "Helps buyers pick a small bundle based on their use case.",
        "home_note_under_features": "This is a demo: replace policies, freight terms, and payment options with your real setup.",

        "home_steps_kicker": "Demo checkout",
        "home_steps_title": "How ordering works (demo flow)",
        "home_step1_title": "Choose products",
        "home_step1_desc": "Browse items, open details, and add quantities to the basket.",
        "home_step2_title": "Submit request",
        "home_step2_desc": "Checkout collects contact details and shipping address (demo).",
        "home_step3_title": "Confirm terms",
        "home_step3_desc": "In a real store: confirm MOQ, lead time, freight, and payment method.",
        "home_step4_title": "Ship & support",
        "home_step4_desc": "Share tracking and provide after-sales support.",

        "home_service_kicker": "Export operations",
        "home_service_title": "Export-friendly service notes",
        "home_service_sub": "Common details exporters add to improve buyer confidence.",
        "home_service_b1": "Show MOQ, lead time, and key specs per SKU.",
        "home_service_b2": "Add shipping terms (EXW/FOB/CIF) and packaging options.",
        "home_service_b3": "Integrate payment options (bank transfer, PayPal, Stripe, local payment).",
        "home_service_b4": "Add compliance documents, warranty, and return policy pages if needed.",

        "home_featured_kicker": "Quick selection",
        "home_featured_title": "Featured picks",
        "home_featured_link": "View all",

        "home_all_kicker": "Full catalog",
        "home_all_title": "All demo products",
        "home_all_hint": "Use Details to see the full description.",

        "home_social_kicker": "Social proof",
        "home_social_title": "What buyers like about this layout",
        "home_social_label1": "International buyer",
        "home_social_quote1": "Clean layout—easy to understand key benefits quickly.",
        "home_social_meta1": "Demo feedback",
        "home_social_label2": "Purchasing",
        "home_social_quote2": "I can shortlist items fast and submit a clear request.",
        "home_social_meta2": "Demo feedback",
        "home_social_label3": "Distributor",
        "home_social_quote3": "Bilingual pages reduce back-and-forth and speed up decisions.",
        "home_social_meta3": "Demo feedback",

        "home_faq_kicker": "Questions",
        "home_faq_title": "FAQ",
        "home_faq_q1": "Can I replace the demo products with my own?",
        "home_faq_a1": "Yes. Update the product list (or connect a database) and replace images in static/img.",
        "home_faq_q2": "Is this a real checkout?",
        "home_faq_a2": "Not in the demo. It submits an order request only. Payment and order storage can be added.",
        "home_faq_q3": "Can you add categories, search, and filters?",
        "home_faq_a3": "Yes. Add tags/collections and a search bar; connect a database for large catalogs.",
        "home_faq_q4": "Can I disable the AI advisor?",
        "home_faq_a4": "Yes. Turn off ENABLE_AI_ADVISOR in app.py (and hide the card if you want).",

        "home_cta2_kicker": "Next step",
        "home_cta2_title": "Want this store for your business?",
        "home_cta2_desc": "Branding, product import, payment integration, and deployment can be built on top of this demo.",
        "home_cta2_btn": "Browse products",

        # Product detail
        "product_qty_label": "Quantity",
        "product_add_btn": "Add to basket",
        "product_view_cart": "View basket",

        # Cart
        "cart_title": "Your Basket – SkyLane Shop",
        "cart_heading": "Your Basket",
        "cart_empty": "Your basket is currently empty.",
        "cart_continue": "Continue shopping",
        "cart_th_product": "Product",
        "cart_th_qty": "Quantity",
        "cart_th_price": "Price",
        "cart_th_line_total": "Line total",
        "cart_update_btn": "Update",
        "cart_update_hint": "Set to 0 to remove.",
        "cart_clear_btn": "Clear basket",
        "cart_total_label": "Total:",
        "cart_checkout_btn": "Proceed to checkout",

        # Checkout
        "checkout_title": "Checkout – SkyLane Shop",
        "checkout_heading": "Checkout",
        "checkout_fullname_label": "Full name",
        "checkout_fullname_placeholder": "Your name",
        "checkout_email_label": "Email",
        "checkout_email_placeholder": "you@example.com",
        "checkout_address_label": "Shipping address",
        "checkout_address_placeholder": "Address, city, postal code, country",
        "checkout_note_label": "Order notes (optional)",
        "checkout_note_placeholder": "Any extra information",
        "checkout_submit_btn": "Submit order request (demo)",
        "checkout_summary_title": "Order summary",
        "checkout_summary_demo_note": (
            "This is a demo. In a real project, this part would connect to "
            "PayPal / Stripe / bank transfer instructions or other payment options."
        ),

        # Login
        "login_title": "Login – SkyLane Shop",
        "login_heading": "Login (demo)",
        "login_intro": (
            "For this demo, we only ask for a name. In a real shop, you would have "
            "a full registration system."
        ),
        "login_name_label": "Your name",
        "login_btn": "Login",

        # Account
        "account_title": "My Account – SkyLane Shop",
        "account_heading": "My Account",
        "account_hello": "Hello, {user}.",
        "account_intro": (
            "This is a demo account area. In a real shop, this page would show "
            "your order history, addresses, etc."
        ),
        "account_recent_title": "Recent orders (demo)",
        "account_th_order": "Order #",
        "account_th_date": "Date",
        "account_th_status": "Status",
        "account_th_total": "Total",
        "account_status_delivered": "Delivered",
        "account_status_pending": "Pending (demo)",

        # Flash / messages
        "flash_product_not_found": "Product not found.",
        "flash_cart_added": "Added {product_name} to your basket.",
        "flash_cart_updated": "Basket updated.",
        "flash_cart_cleared": "Basket cleared.",
        "flash_cart_empty": "Your basket is empty.",
        "flash_order_submitted": "Thank you, your order request has been submitted (demo).",
        "flash_login_missing_name": "Please enter a name.",
        "flash_login_welcome": "Welcome, {username}! (demo login)",
        "flash_logged_out": "You have been logged out.",
        "flash_login_required": "Please log in to view your account.",
    },

    "zh": {
        # Global / layout
        "site_title": "SkyLane 商店 – 出口示例商城",
        "brand_name": "SkyLane 商店",
        "nav_home": "首页",
        "nav_products": "产品",
        "nav_cart": "购物篮",
        "nav_login": "登录",
        "nav_account": "我的账户",
        "nav_logout": "退出登录",
        "footer_text": (
            "演示出口类商城网站，包含产品列表、购物篮、账户和结算页面。"
            "可作为客户在线商店的示例。"
        ),

        # Index
        "home_title": "SkyLane 商店 – 出口示例商城",
        "home_heading": "SkyLane 示例商店",
        "home_tagline": "面向出口业务的在线商店示例，带购物篮和账户页面。",
        "home_btn_details": "详情",
        "home_btn_add": "加入",

        # 首页内容扩展（让首页信息更完整）
        "home_hero_kicker": "B2B / 外贸出海商城模板",
        "home_hero_title": "出口示例商城",
        "home_hero_sub": "双语、买家友好的示例商店，用于展示产品如何面向海外客户呈现。",
        "home_cta_browse": "浏览产品",
        "home_cta_ai": "询问 AI 推荐",
        "home_cta_cart": "查看购物篮",
        "home_badge_mobile": "移动端友好",
        "home_badge_bilingual": "中英双语",
        "home_badge_export": "适合外贸",
        "home_badge_demo": "演示",

        "home_quick_title": "快速概览",
        "home_quick_sub": "买家第一眼最关心的亮点。",
        "home_quick_item1_title": "清晰展示",
        "home_quick_item1_desc": "图片、要点、价格一目了然。",
        "home_quick_item2_title": "购物篮流程",
        "home_quick_item2_desc": "加入、修改数量、提交询盘/订单请求。",
        "home_quick_item3_title": "账户页面",
        "home_quick_item3_desc": "演示登录与订单记录占位。",
        "home_quick_item4_title": "AI 推荐（可选）",
        "home_quick_item4_desc": "根据需求从目录中推荐 2–3 款。",

        "home_includes_kicker": "首页内容",
        "home_includes_title": "本示例包含什么",
        "home_includes_sub": "增加首页信息量，让示例更像真实可用的商城。",

        "home_feature1_title": "双语店铺",
        "home_feature1_desc": "支持中英切换，减少沟通成本。",
        "home_feature2_title": "买家友好展示",
        "home_feature2_desc": "简洁卡片 + 详情页，便于快速了解产品。",
        "home_feature3_title": "购物篮 + 结算请求",
        "home_feature3_desc": "演示版结算流程，后续可对接真实支付。",
        "home_feature4_title": "AI 商品推荐",
        "home_feature4_desc": "根据场景建议一个小组合，帮助买家下决策。",
        "home_note_under_features": "本项目为演示：请将运费条款、支付方式与政策说明替换为您的真实信息。",

        "home_steps_kicker": "演示结算",
        "home_steps_title": "下单流程（示例）",
        "home_step1_title": "选择产品",
        "home_step1_desc": "浏览产品、查看详情并加入购物篮。",
        "home_step2_title": "提交请求",
        "home_step2_desc": "结算页收集联系信息与收货地址（演示）。",
        "home_step3_title": "确认条款",
        "home_step3_desc": "真实项目中：确认 MOQ、交期、运费与支付方式。",
        "home_step4_title": "发货售后",
        "home_step4_desc": "提供追踪号并进行售后支持。",

        "home_service_kicker": "外贸运营",
        "home_service_title": "外贸友好提示",
        "home_service_sub": "常见让买家更放心的展示信息。",
        "home_service_b1": "每个 SKU 可展示 MOQ、交期与关键参数。",
        "home_service_b2": "可增加 EXW/FOB/CIF 等贸易条款与包装选项。",
        "home_service_b3": "可对接银行转账、PayPal、Stripe、... 等支付。",
        "home_service_b4": "按需增加合规文件、保修与退换货政策页面。",

        "home_featured_kicker": "快速挑选",
        "home_featured_title": "精选示例",
        "home_featured_link": "查看全部",

        "home_all_kicker": "产品目录",
        "home_all_title": "全部示例产品",
        "home_all_hint": "点击“详情”查看更多描述。",

        "home_social_kicker": "口碑展示",
        "home_social_title": "买家喜欢的地方",
        "home_social_label1": "海外买家",
        "home_social_quote1": "页面干净，产品要点很快就能看明白。",
        "home_social_meta1": "演示反馈",
        "home_social_label2": "采购",
        "home_social_quote2": "快速筛选并提交清晰的请求，非常方便。",
        "home_social_meta2": "演示反馈",
        "home_social_label3": "渠道商",
        "home_social_quote3": "双语信息减少来回确认，决策更快。",
        "home_social_meta3": "演示反馈",

        "home_faq_kicker": "常见问题",
        "home_faq_title": "FAQ",
        "home_faq_q1": "可以把示例产品替换为我的产品吗？",
        "home_faq_a1": "可以。更新产品列表（或连接数据库），并替换 static/img 里的图片即可。",
        "home_faq_q2": "这是真实支付结算吗？",
        "home_faq_a2": "演示版仅提交订单请求。真实支付与订单保存可在项目中实现。",
        "home_faq_q3": "能加分类、搜索和筛选吗？",
        "home_faq_a3": "可以。增加标签/分类与搜索栏；目录较大时建议接入数据库。",
        "home_faq_q4": "可以关闭 AI 推荐吗？",
        "home_faq_a4": "可以。在 app.py 里关闭 ENABLE_AI_ADVISOR（并按需隐藏卡片）。",

        "home_cta2_kicker": "下一步",
        "home_cta2_title": "想把它变成你的正式商城？",
        "home_cta2_desc": "在此示例基础上，可定制品牌、导入产品、对接支付并部署上线。",
        "home_cta2_btn": "浏览产品",

        # Product detail
        "product_qty_label": "数量",
        "product_add_btn": "加入购物篮",
        "product_view_cart": "查看购物篮",

        # Cart
        "cart_title": "购物篮 – SkyLane 商店",
        "cart_heading": "您的购物篮",
        "cart_empty": "您的购物篮目前是空的。",
        "cart_continue": "继续购物",
        "cart_th_product": "产品",
        "cart_th_qty": "数量",
        "cart_th_price": "单价",
        "cart_th_line_total": "小计",
        "cart_update_btn": "更新",
        "cart_update_hint": "数量设为 0 即可删除。",
        "cart_clear_btn": "清空购物篮",
        "cart_total_label": "合计：",
        "cart_checkout_btn": "前往结算",

        # Checkout
        "checkout_title": "结算 – SkyLane 商店",
        "checkout_heading": "结算",
        "checkout_fullname_label": "姓名",
        "checkout_fullname_placeholder": "请输入您的姓名",
        "checkout_email_label": "邮箱",
        "checkout_email_placeholder": "you@example.com",
        "checkout_address_label": "收货地址",
        "checkout_address_placeholder": "地址、城市、邮编、国家",
        "checkout_note_label": "订单备注（可选）",
        "checkout_note_placeholder": "其他说明",
        "checkout_submit_btn": "提交订单请求（演示）",
        "checkout_summary_title": "订单摘要",
        "checkout_summary_demo_note": (
            "本页面仅为演示。实际项目中，此处会连接到 PayPal / Stripe / 银行转账等支付方式。"
        ),

        # Login
        "login_title": "登录 – SkyLane 商店",
        "login_heading": "登录（演示）",
        "login_intro": (
            "在本演示中，只需要输入名字。真实商店中会有完整的注册与登录系统。"
        ),
        "login_name_label": "您的名字",
        "login_btn": "登录",

        # Account
        "account_title": "我的账户 – SkyLane 商店",
        "account_heading": "我的账户",
        "account_hello": "您好，{user}。",
        "account_intro": "这是演示账户页面。实际商店中，这里会显示您的订单记录、收货地址等信息。",
        "account_recent_title": "最近订单（示例）",
        "account_th_order": "订单号",
        "account_th_date": "日期",
        "account_th_status": "状态",
        "account_th_total": "总计",
        "account_status_delivered": "已送达",
        "account_status_pending": "待处理（示例）",

        # Flash / messages
        "flash_product_not_found": "未找到该产品。",
        "flash_cart_added": "已将 {product_name} 加入购物篮。",
        "flash_cart_updated": "购物篮已更新。",
        "flash_cart_cleared": "购物篮已清空。",
        "flash_cart_empty": "您的购物篮是空的。",
        "flash_order_submitted": "感谢您的下单请求（演示）。",
        "flash_login_missing_name": "请输入名字。",
        "flash_login_welcome": "欢迎，{username}！（演示登录）",
        "flash_logged_out": "您已退出登录。",
        "flash_login_required": "请先登录再查看账户信息。",
    }
}


# ---------- PRODUCTS (with CN text too) ----------

PRODUCTS = [
    {
        "id": 1,
        "slug": "wireless-headphones",
        "name": "Wireless Headphones X1",
        "name_zh": "无线耳机 X1",
        "price": 59.90,
        "currency": "USD",
        "short": "Comfortable wireless headphones with noise reduction.",
        "short_zh": "舒适的无线耳机，带降噪功能。",
        "description": (
            "Comfortable wireless headphones with 30 hours of battery, "
            "lightweight design and soft ear cushions. A good demo product "
            "to show how your shop can present technical items."
        ),
        "description_zh": (
            "舒适的无线耳机，续航约 30 小时，重量轻，耳罩柔软。"
            "适合作为展示技术类产品的示例。"
        ),
        "image": "prod_headphones.jpg"
    },
    {
        "id": 2,
        "slug": "urban-backpack",
        "name": "Urban Commuter Backpack",
        "name_zh": "城市通勤背包",
        "price": 42.50,
        "currency": "USD",
        "short": "Water-repellent backpack for daily use and travel.",
        "short_zh": "适合日常使用和旅行的防泼水背包。",
        "description": (
            "Minimalist backpack with padded laptop compartment (up to 15.6''), "
            "hidden pocket and water-repellent fabric. Great for showing fashion / soft goods."
        ),
        "description_zh": (
            "极简风格背包，带有 15.6 英寸笔记本保护隔层、隐形口袋和防泼水面料。"
            "非常适合展示时尚 / 软包类产品。"
        ),
        "image": "prod_backpack.jpg"
    },
    {
        "id": 3,
        "slug": "desk-lamp",
        "name": "LED Desk Lamp Pro",
        "name_zh": "LED 专业台灯",
        "price": 34.20,
        "currency": "USD",
        "short": "Adjustable LED desk lamp with three color modes.",
        "short_zh": "带三种色温模式的可调节 LED 台灯。",
        "description": (
            "Adjustable LED lamp with brightness control, three color temperatures and USB charging. "
            "Used here as an example of home & office product."
        ),
        "description_zh": (
            "可调节亮度的 LED 台灯，三档色温，并带 USB 充电接口。"
            "可作为家居 / 办公产品示例。"
        ),
        "image": "prod_lamp.jpg"
    },
    {
        "id": 4,
        "slug": "fast-charge-power-bank-20000",
        "name": "Fast-Charge Power Bank 20,000mAh",
        "name_zh": "20,000mAh 快充移动电源",
        "price": 29.90,
        "currency": "USD",
        "short": "High-capacity power bank with fast charging support.",
        "short_zh": "大容量移动电源，支持快充。",
        "description": (
            "A 20,000mAh power bank with fast-charging support, dual output ports, "
            "and a compact form factor. Ideal demo item for electronics accessory listings."
        ),
        "description_zh": (
            "20,000mAh 大容量移动电源，支持快充，双输出接口，体积紧凑便携。"
            "适合用于展示数码配件类商品。"
        ),
        "image": "prod_powerbank.jpg"
    },
    {
        "id": 5,
        "slug": "smart-speaker-mini",
        "name": "Smart Speaker Mini",
        "name_zh": "智能音箱 Mini",
        "price": 34.90,
        "currency": "USD",
        "short": "Compact speaker with clear sound and voice assistant support.",
        "short_zh": "小巧音箱，音质清晰，支持语音助手。",
        "description": (
            "A compact smart speaker with clear vocals, room-filling sound, and simple setup. "
            "Useful as a demo product for smart home and audio categories."
        ),
        "description_zh": (
            "小巧智能音箱，人声清晰，覆盖空间更广，安装设置简单。"
            "适合作为智能家居与音频类产品展示示例。"
        ),
        "image": "prod_speaker.jpg"
    },
    {
        "id": 6,
        "slug": "stainless-steel-water-bottle",
        "name": "Stainless Steel Water Bottle 750ml",
        "name_zh": "750ml 不锈钢保温水瓶",
        "price": 18.90,
        "currency": "USD",
        "short": "Insulated bottle that keeps drinks hot or cold for hours.",
        "short_zh": "保温保冷多小时的不锈钢水瓶。",
        "description": (
            "A 750ml stainless steel insulated bottle with leak-proof lid and easy-carry handle. "
            "A strong demo item for outdoor, fitness, and everyday essentials."
        ),
        "description_zh": (
            "750ml 不锈钢保温水瓶，防漏瓶盖，便携提手设计。"
            "适合用于展示户外、健身与日用必需品类商品。"
        ),
        "image": "prod_bottle.jpg"
    },
    {
        "id": 7,
        "slug": "eco-yoga-mat",
        "name": "Eco Yoga Mat",
        "name_zh": "环保防滑瑜伽垫",
        "price": 21.90,
        "currency": "USD",
        "short": "Non-slip yoga mat with comfortable cushioning.",
        "short_zh": "防滑瑜伽垫，回弹舒适。",
        "description": (
            "An eco-friendly yoga mat with textured grip, comfortable thickness, "
            "and easy-roll design. Great for showcasing sports and wellness products."
        ),
        "description_zh": (
            "环保材质瑜伽垫，纹理防滑抓地力强，厚度舒适，易卷收纳。"
            "适合展示运动与健康类产品。"
        ),
        "image": "prod_yoga_mat.jpg"
    },
    {
        "id": 8,
        "slug": "electric-toothbrush-s2",
        "name": "Electric Toothbrush S2",
        "name_zh": "电动牙刷 S2",
        "price": 27.90,
        "currency": "USD",
        "short": "Multi-mode toothbrush with gentle and deep-clean settings.",
        "short_zh": "多模式清洁，兼顾温和与深度护理。",
        "description": (
            "An electric toothbrush with multiple cleaning modes, timer guidance, "
            "and a sleek charging base. A clean demo item for personal care categories."
        ),
        "description_zh": (
            "多模式电动牙刷，带计时提醒与引导，配套充电底座，外观简洁。"
            "适合作为个护类商品的展示示例。"
        ),
        "image": "prod_toothbrush.jpg"
    },
    {
        "id": 9,
        "slug": "mechanical-keyboard-tkl",
        "name": "Mechanical Keyboard TKL",
        "name_zh": "机械键盘 TKL",
        "price": 49.90,
        "currency": "USD",
        "short": "Compact mechanical keyboard with satisfying tactile feel.",
        "short_zh": "紧凑布局，手感清脆舒适。",
        "description": (
            "A tenkeyless mechanical keyboard designed for productivity and gaming, "
            "with durable keycaps and responsive switches. Ideal for showcasing PC accessories."
        ),
        "description_zh": (
            "87 键紧凑机械键盘，兼顾办公与游戏体验，键帽耐用，触发响应灵敏。"
            "适合用于展示电脑外设类产品。"
        ),
        "image": "prod_keyboard.jpg"
    },
    {
        "id": 10,
        "slug": "portable-blender-go",
        "name": "Portable Blender Go",
        "name_zh": "便携随行搅拌杯",
        "price": 32.90,
        "currency": "USD",
        "short": "Portable blender for smoothies at home or on the go.",
        "short_zh": "随行搅拌杯，轻松做果昔与奶昔。",
        "description": (
            "A portable blender with rechargeable battery, easy-clean cup design, "
            "and strong blending performance for smoothies. Great demo item for kitchen gadgets."
        ),
        "description_zh": (
            "充电式便携搅拌杯，杯体易清洗，搅拌动力充足，适合制作果昔饮品。"
            "适合作为厨房小电器类产品的示例。"
        ),
        "image": "prod_blender.jpg"
    },
    {
        "id": 11,
        "slug": "universal-travel-adapter",
        "name": "Universal Travel Adapter",
        "name_zh": "全球通用旅行转换插头",
        "price": 19.90,
        "currency": "USD",
        "short": "All-in-one travel adapter for multiple plug standards.",
        "short_zh": "一体式旅行转换插头，覆盖多国插头标准。",
        "description": (
            "An all-in-one travel adapter covering multiple plug standards, "
            "with compact design and built-in safety features. Ideal for showcasing travel essentials."
        ),
        "description_zh": (
            "一体式旅行转换插头，覆盖多国插头标准，体积小巧，具备安全防护设计。"
            "适合作为出行必备类产品的展示示例。"
        ),
        "image": "prod_travel_adapter.jpg"
    },
]


# ---------- Helpers ----------

def get_lang(default="en"):
    lang = request.args.get("lang", default)
    return "zh" if lang and lang.lower() in ("zh", "cn", "zh-cn") else "en"



def tr(key: str, **kwargs) -> str:
    """Translate helper for flash messages, etc."""
    lang = get_lang()
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def get_cart():
    """Return cart dict from session (product_id -> qty)."""
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart


def find_product_by_id(pid: int):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return None


def find_product_by_slug(slug: str):
    for p in PRODUCTS:
        if p["slug"] == slug:
            return p
    return None


def get_cart_items_and_total():
    cart = get_cart()
    items = []
    total = 0.0
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        product = find_product_by_id(pid)
        if not product:
            continue
        line_total = product["price"] * qty
        total += line_total
        items.append({
            "product": product,
            "qty": qty,
            "line_total": line_total
        })
    return items, total


# ---- Auth (very simple demo, no DB) ----
def current_user():
    """Return username from session or None."""
    return session.get("user")


@app.context_processor
def inject_globals():
    """Make language, text dict, user and cart count available in templates."""
    cart = get_cart()
    total_qty = sum(cart.values())
    lang = get_lang()
    t = TEXTS[lang]
    return {
        "current_user": current_user(),
        "cart_count": total_qty,
        "lang": lang,
        "t": t,
    }


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/product/<slug>")
def product_detail(slug):
    product = find_product_by_slug(slug)
    if not product:
        flash(tr("flash_product_not_found"), "danger")
        return redirect(url_for("index"))
    return render_template("product_detail.html", product=product)


@app.route("/add-to-cart/<int:pid>", methods=["POST"])
def add_to_cart(pid):
    product = find_product_by_id(pid)
    if not product:
        flash(tr("flash_product_not_found"), "danger")
        return redirect(url_for("index"))

    cart = get_cart()
    qty = cart.get(str(pid), 0)
    qty_to_add = int(request.form.get("qty", 1))
    cart[str(pid)] = qty + max(qty_to_add, 1)
    save_cart(cart)
    flash(tr("flash_cart_added", product_name=product["name_zh"] if get_lang() == "zh" else product["name"]), "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart")
def cart_view():
    items, total = get_cart_items_and_total()
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/update/<int:pid>", methods=["POST"])
def cart_update(pid):
    cart = get_cart()
    key = str(pid)
    if key in cart:
        new_qty = int(request.form.get("qty", 1))
        if new_qty <= 0:
            cart.pop(key)
        else:
            cart[key] = new_qty
        save_cart(cart)
        flash(tr("flash_cart_updated"), "info")
    return redirect(url_for("cart_view"))


@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    save_cart({})
    flash(tr("flash_cart_cleared"), "info")
    return redirect(url_for("cart_view"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total = get_cart_items_and_total()
    if not items:
        flash(tr("flash_cart_empty"), "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        # Here you would integrate real payment + save order to DB.
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        note = request.form.get("note")
        # demo: ignore form data

        save_cart({})
        flash(tr("flash_order_submitted"), "success")
        return redirect(url_for("index"))

    return render_template("checkout.html", items=items, total=total)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash(tr("flash_login_missing_name"), "warning")
            return redirect(url_for("login"))
        session["user"] = username
        flash(tr("flash_login_welcome", username=username), "success")
        return redirect(url_for("account"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash(tr("flash_logged_out"), "info")
    return redirect(url_for("index"))


@app.route("/account")
def account():
    user = current_user()
    if not user:
        flash(tr("flash_login_required"), "warning")
        return redirect(url_for("login"))

    demo_orders = [
        {
            "id": 1001,
            "date": "2025-01-10",
            "status_key": "delivered",
            "total": 92.40
        },
        {
            "id": 1002,
            "date": "2025-01-18",
            "status_key": "pending",
            "total": 59.90
        }
    ]
    return render_template("account.html", user=user, orders=demo_orders)

@app.route("/api/ai-product-advisor", methods=["POST"])
def api_ai_product_advisor():
    """
    AI product recommender / bundle advisor.

    Expects JSON:
    {
      "query": "I run a small workshop, need headset for calls...",
      "lang": "en" | "zh"
    }

    Returns JSON:
    {
      "recommendations": [
        {
          "product_id": 1,
          "product_name": "...",
          "product_name_zh": "...",
          "price": 59.9,
          "currency": "USD",
          "reason": "...",
          "url": "/product/wireless-headphones"
        },
        ...
      ]
    }
    """
    if not ENABLE_AI_ADVISOR:
        return jsonify({"error": "AI advisor is disabled"}), 403

    if os.environ.get("OPENAI_API_KEY") is None:
        return jsonify({"error": "OPENAI_API_KEY is not set on the server"}), 500

    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    lang = (data.get("lang") or get_lang() or "en").lower()
    lang = "zh" if lang in ("zh", "cn", "zh-cn") else "en"

    if not query:
        return jsonify({"error": "Missing query"}), 400

    products_text = build_products_prompt(lang)

    if lang == "zh":
        user_prompt = f"""
用户描述的使用场景如下：
{query}

下面是可选产品列表（每一行一个产品）：
{products_text}

请你扮演一名熟悉出口电商的产品顾问，根据用户场景从列表中推荐 2–3 款产品（可以考虑凑成一个简单“组合”）。

要求：
- 只在上面列表中的产品里选择；
- 对每个推荐说明简短理由（不超过 3 句话）；
- 尝试覆盖不同用途或价位（如果合适）。

请严格按照以下 JSON 格式返回（不要包含其它文字或解释）：
{{
  "recommendations": [
    {{
      "product_id": <int>,
      "reason": "<Chinese explanation>"
    }},
    ...
  ]
}}
"""
    else:
        user_prompt = f"""
The buyer describes their situation as:
{query}

Here is the available product list (one per line):
{products_text}

You are an export-focused product advisor.
Recommend 2–3 products (possibly as a small bundle) from the list ABOVE only.

Requirements:
- Only pick products that actually exist in the list.
- For each recommendation, provide a short reason (max 3 sentences).
- Try to cover different use cases or price points if it makes sense.

Return STRICT JSON ONLY, with no extra commentary, using this exact format:
{{
  "recommendations": [
    {{
      "product_id": <int>,
      "reason": "<English explanation>"
    }},
    ...
  ]
}}
"""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful product advisor. "
                "Always and only respond with valid JSON that can be parsed by a program."
            )
        },
        {"role": "user", "content": user_prompt},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",  # adjust if you prefer another model
            messages=messages,
            max_tokens=500,
            temperature=0.4,
        )
        raw = completion.choices[0].message.content

        try:
            parsed = json.loads(raw)
        except Exception:
            # Fallback: not proper JSON, wrap entire reply into a single recommendation
            parsed = {
                "recommendations": [
                    {"product_id": PRODUCTS[0]["id"], "reason": raw.strip()}
                ]
            }

        recs = parsed.get("recommendations", [])
        enriched = []

        for rec in recs:
            pid = rec.get("product_id")
            if not isinstance(pid, int):
                continue
            product = find_product_by_id(pid)
            if not product:
                continue

            enriched.append({
                "product_id": pid,
                "product_name": product["name"],
                "product_name_zh": product["name_zh"],
                "price": product["price"],
                "currency": product["currency"],
                "reason": rec.get("reason", ""),
                "url": url_for("product_detail", slug=product["slug"])
            })

        if not enriched:
            # If model output was useless, at least suggest top-1 product
            p = PRODUCTS[0]
            enriched.append({
                "product_id": p["id"],
                "product_name": p["name"],
                "product_name_zh": p["name_zh"],
                "price": p["price"],
                "currency": p["currency"],
                "reason": "AI could not parse a good recommendation, so we suggest starting from this popular demo product.",
                "url": url_for("product_detail", slug=p["slug"])
            })

        return jsonify({"recommendations": enriched})

    except Exception as e:
        return jsonify({"error": "AI advisor request failed", "detail": str(e)}), 500


def build_products_prompt(lang: str) -> str:
    """
    Build a compact text listing all products for the AI model.
    """
    lines = []
    use_zh = (lang == "zh")
    for p in PRODUCTS:
        name = p["name_zh"] if use_zh else p["name"]
        short = p["short_zh"] if use_zh else p["short"]
        line = (
            f"ID: {p['id']}, "
            f"Name: {name}, "
            f"Price: {p['price']} {p['currency']}, "
            f"Short: {short}"
        )
        lines.append(line)
    return "\n".join(lines)



if __name__ == "__main__":
    app.run(debug=True)
