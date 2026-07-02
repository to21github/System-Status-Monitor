"""Home Assistant 系统状态监控 — Flask 主应用。

提供仪表盘页面和 REST API（/api/stats、/api/health）。
通过 HA Ingress 在侧边栏中展示。"""

import json
import os
from flask import Flask, jsonify, render_template
import collector
import health

app = Flask(__name__)

# ---- 安全配置 ----
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
app.logger.info("系统状态监控启动完成 (pid=%d)", os.getpid())

# ---- 业务配置（从 HA 加载项 options.json 读取）----
def _read_options():
    try:
        with open("/data/options.json") as f:
            return json.load(f)
    except Exception:
        return {}

_options = _read_options()
REFRESH_INTERVAL = int(_options.get("refresh_interval", 30))

@app.route("/")
def dashboard():
    """仪表盘主页"""
    return render_template("index.html", refresh_interval=REFRESH_INTERVAL)


@app.route("/api/stats")
def api_stats():
    """返回系统指标 JSON"""
    try:
        stats = collector.collect()
        return jsonify({"ok": True, "data": stats})
    except Exception as e:
        app.logger.error(f"采集系统指标失败: {e}")
        return jsonify({"ok": False, "error": "内部采集错误"}), 500


@app.route("/api/health")
def api_health():
    """返回健康评分 JSON"""
    try:
        stats = collector.collect()
        ha = collector.collect_ha_status()
        score = health.calculate(stats, ha)
        return jsonify({
            "ok": True,
            "data": {
                "score": score,
                "ha": ha,
            },
        })
    except Exception as e:
        app.logger.error(f"健康评分计算失败: {e}")
        return jsonify({"ok": False, "error": "健康评分计算错误"}), 500


# ---- 启动入口 ----
if __name__ == "__main__":
    port = int(os.environ.get("INGRESS_PORT", 8099))
    app.run(host="0.0.0.0", port=port, debug=False)
