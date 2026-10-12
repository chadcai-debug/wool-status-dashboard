#!/usr/bin/env python3
"""Wool system status dashboard - lightweight, for Render free tier."""
import os
import sqlite3
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>羊毛系统状态</title>
<style>
body {{ font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
.stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
.stat .num {{ font-size: 2em; font-weight: bold; color: #2563eb; }}
.stat .label {{ color: #666; font-size: 0.9em; }}
.updated {{ color: #999; font-size: 0.85em; margin-top: 20px; }}
.ok {{ color: #16a34a; font-weight: bold; }}
</style></head>
<body>
<h1>🐑 Render 保活测试</h1>
<p class="ok">● 服务在线</p>
<p>这是一个轻量测试页，用于验证 Render 免费档 + 心跳保活是否可靠。</p>
<div class="stat"><div class="num">512MB</div><div class="label">内存</div></div>
<div class="stat"><div class="num">0.1</div><div class="label">vCPU</div></div>
<div class="stat"><div class="num">750h/月</div><div class="label">额度</div></div>
<div class="updated">更新于 {now} UTC · 心跳每 10 分钟</div>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        html = HTML_TEMPLATE.format(now=now)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on port {port}", flush=True)
    server.serve_forever()
