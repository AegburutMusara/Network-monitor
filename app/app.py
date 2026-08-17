# Network Monitor app
# Flask application for checking connectivity to external hosts using ping
# and storing uptime statistics in Redis.

import os
import subprocess
import time

from flask import Flask, render_template_string
import redis

app = Flask(__name__)

# ดึงค่า config ของ Redis จาก environment variable ที่ Docker Compose ส่งให้
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# เชื่อมต่อ Redis และตรวจสอบว่า service พร้อมใช้งานหรือไม่
# หากยังไม่พร้อม ให้ retry หลายรอบก่อนยกเลิก
redis_client = None
for attempt in range(10):
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        redis_client.ping()
        break
    except redis.exceptions.ConnectionError:
        time.sleep(1)

if redis_client is None:
    raise RuntimeError("Could not connect to Redis server.")

# รายการ host ที่ต้องการตรวจสอบความพร้อมใช้งานแบบ ICMP ping
TARGETS = ["8.8.8.8", "1.1.1.1", "google.com"]


def check_target(host):
    """Send a single ICMP ping to target and return True if reachable."""
    cmd = ["ping", "-c", "1", "-W", "1", host]
    response = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return response.returncode == 0


@app.route("/")
def dashboard():
    """Build the dashboard page and update Redis counters for each target."""
    results = []

    for target in TARGETS:
        is_online = check_target(target)
        status_text = "ONLINE" if is_online else "OFFLINE"

        # บันทึกจำนวนการตรวจสอบทั้งหมด และจำนวนที่สำเร็จลง Redis
        redis_client.incr(f"total_checks:{target}")
        if is_online:
            redis_client.incr(f"success_checks:{target}")

        total = int(redis_client.get(f"total_checks:{target}") or 1)
        success = int(redis_client.get(f"success_checks:{target}") or 0)
        uptime_pct = round((success / total) * 100, 1)

        results.append({
            "target": target,
            "status": status_text,
            "is_online": is_online,
            "uptime": uptime_pct,
            "total_checks": total,
        })

    # HTML template สำหรับแสดงสถานะเครือข่ายแบบง่ายและสวยงาม
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Health Monitor</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 30px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #1a1a1a;
                text-align: center;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .target-name {
                font-size: 1.2rem;
                font-weight: bold;
                color: #333;
            }
            .status-badge {
                padding: 6px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9rem;
            }
            .online {
                background-color: #d4edda;
                color: #155724;
            }
            .offline {
                background-color: #f8d7da;
                color: #721c24;
            }
            .uptime {
                font-size: 0.95rem;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Network Health Monitor</h1>
            {% for item in results %}
            <div class="card">
                <div>
                    <div class="target-name">{{ item.target }}</div>
                    <div class="uptime">Uptime: {{ item.uptime }}% (Checked {{ item.total_checks }} times)</div>
                </div>
                <div>
                    <span class="status-badge {{ 'online' if item.is_online else 'offline' }}">
                        {{ item.status }}
                    </span>
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results)


if __name__ == "__main__":
    # เมื่อรันไฟล์นี้โดยตรง ให้เปิด Flask app บนพอร์ต 5000 และรับการเชื่อมต่อจากทุก interface
    app.run(host="0.0.0.0", port=5000)