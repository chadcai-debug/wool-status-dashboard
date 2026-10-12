#!/usr/bin/env python3
"""Wool system status dashboard - lightweight, for Render free tier."""
import sqlite3
import json
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

WOOL_DB = "/opt/render/project/src/wool.db"  # Will be set via env or fallback

HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>羊毛系统状态</title>
<style>
body {{ font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
.stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
.stat .num {{ font-size: 2em; font-weight: bold; color: #2563eb; }}
.stat .label {{ color: #666; font-size: 0.9em; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
th {{ background: #f5f5f5; }}
.updated {{ color: #999; font-size: 0.85em; margin-top: 20px; }}
</style></head>
<body>
<h1>🐑 羊毛系统状态</h1>
<div>
<div class="stat"><div class="num">{claimed}</div><div class="label">已领取</div></div>
<div class="stat"><div class="num">{pending}</div><div class="label">待处理</div></div>
<div class="stat"><div class="num">{human}</div><div class="label">需人工</div></div>
</div>
<h2>最近领取</h2>
<table><tr><th>ID</th><th>厂商</th><th>时间</th></tr>{rows}</table>
<div class="updated">更新于 {now} UTC</div>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        
        # Main dashboard
        try:
            # Try to read from env-specified DB or local copy
            import os
            db_path = os.environ.get("WOOL_DB", "wool.db")
            db = sqlite3.connect(db_path)
            
            claimed = db.execute("SELECT COUNT(*) FROM offers WHERE status='claimed'").fetchone()[0]
            pending = db.execute("SELECT COUNT(*) FROM offers WHERE status='pending'").fetchone()[0]
            human = db.execute("SELECT COUNT(*) FROM offers WHERE status='pending' AND lane='human'").fetchone()[0]
            
            recent = db.execute("""
                SELECT id, vendor, claimed_at FROM offers 
                WHERE status='claimed' AND claimed_at IS NOT NULL
                ORDER BY claimed_at DESC LIMIT 10
            """).fetchall()
            
            rows = "".join(
                f"<tr><td>#{r[0]}</td><td>{r[1]}</td><td>{r[2][:16] if r[2] else '-'}</td></tr>"
                for r in recent
            )
            
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            html = HTML_TEMPLATE.format(
                claimed=claimed, pending=pending, human=human,
                rows=rows, now=now
            )
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())
    
    def log_message(self, format, *args):
        pass  # Quiet

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on port {port}")
    server.serve_forever()
