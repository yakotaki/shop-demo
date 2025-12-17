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
]


# ---------- Helpers ----------

def get_lang():
    """Get language from ?lang=xx or session; default en."""
    lang_param = request.args.get("lang")
    if lang_param in TEXTS:
        session["lang"] = lang_param
    if "lang" not in session:
        session["lang"] = "en"
    return session["lang"]


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
