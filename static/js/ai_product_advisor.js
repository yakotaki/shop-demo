window.SkyLaneAdvisor = (function () {
    let state = {
        lang: "en",
        busy: false
    };

    function init(config) {
        state.lang = (config && config.lang) || "en";

        const input = document.getElementById("aiAdvisorInput");
        if (input) {
            input.addEventListener("keydown", function (e) {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    ask();
                }
            });
        }
    }

    function setStatus(text) {
        const el = document.getElementById("aiAdvisorStatus");
        if (el) {
            el.textContent = text;
        }
    }

    function clearResults() {
        const box = document.getElementById("aiAdvisorResults");
        if (box) {
            box.innerHTML = "";
            box.style.display = "none";
        }
    }

    function renderResults(recs) {
        const box = document.getElementById("aiAdvisorResults");
        if (!box) return;

        box.innerHTML = "";
        if (!recs || !recs.length) {
            box.style.display = "none";
            return;
        }

        recs.forEach(function (r) {
            const item = document.createElement("div");
            item.className = "border rounded-3 p-2 mb-2 small bg-light";

            const title = document.createElement("div");
            title.className = "fw-semibold mb-1";

            const name =
                state.lang === "zh"
                    ? (r.product_name_zh || r.product_name)
                    : r.product_name;

            title.textContent =
                name + " – " + r.price.toFixed(2) + " " + r.currency;

            const reason = document.createElement("div");
            reason.className = "text-muted mb-1";
            reason.textContent = r.reason || "";

            const linkWrap = document.createElement("div");
            const link = document.createElement("a");
            link.href = r.url;
            link.className = "btn btn-sm btn-outline-primary rounded-pill";
            link.target = "_self";
            link.textContent =
                state.lang === "zh" ? "查看详情" : "View details";

            linkWrap.appendChild(link);

            item.appendChild(title);
            item.appendChild(reason);
            item.appendChild(linkWrap);

            box.appendChild(item);
        });

        box.style.display = "block";
    }

    async function ask() {
        if (state.busy) return false;

        const input = document.getElementById("aiAdvisorInput");
        const button = document.getElementById("aiAdvisorButton");
        if (!input || !button) return false;

        const text = input.value.trim();
        if (!text) {
            if (state.lang === "zh") {
                setStatus("请先简单描述一下您的使用场景或需求。");
            } else {
                setStatus("Please briefly describe your use case or what you need.");
            }
            return false;
        }

        state.busy = true;
        button.disabled = true;
        clearResults();

        if (state.lang === "zh") {
            setStatus("AI 正在分析您的需求并匹配商品，请稍候...");
        } else {
            setStatus("AI is analysing your needs and matching products...");
        }

        try {
            const resp = await fetch("/api/ai-product-advisor", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: text,
                    lang: state.lang
                })
            });

            const data = await resp.json();
            state.busy = false;
            button.disabled = false;

            if (data.error) {
                if (state.lang === "zh") {
                    setStatus("推荐失败：" + data.error);
                } else {
                    setStatus("Recommendation failed: " + data.error);
                }
                return false;
            }

            renderResults(data.recommendations || []);

            if (state.lang === "zh") {
                setStatus("已生成推荐，可点击查看产品详情。");
            } else {
                setStatus("Recommendations ready. Click to view product details.");
            }
        } catch (e) {
            state.busy = false;
            button.disabled = false;
            if (state.lang === "zh") {
                setStatus("网络或服务器错误，请稍后重试。");
            } else {
                setStatus("Network or server error, please try again later.");
            }
        }

        return false;
    }

    return {
        init,
        ask
    };
})();
