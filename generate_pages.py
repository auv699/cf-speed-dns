#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
from html import escape

CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
CF_ZONE_ID = os.environ.get("CF_ZONE_ID")
CF_DNS_NAME = os.environ.get("CF_DNS_NAME")

HEADERS = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json",
}

def get_dns_ips():
    url = (
        f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records"
        f"?type=A&name={CF_DNS_NAME}"
    )

    resp = requests.get(url, headers=HEADERS, timeout=30)
    data = resp.json()

    if not data.get("success"):
        raise RuntimeError(f"Cloudflare API error: {data}")

    records = data.get("result", [])
    ips = [
        record["content"]
        for record in records
        if record.get("type") == "A" and record.get("content")
    ]

    if not ips:
        raise RuntimeError("No A records found")

    return ips

def write_files(ips):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ip_csv = ",".join(ips)

    with open("ipTop.html", "w", encoding="utf-8") as f:
        f.write(ip_csv)

    with open("ipTop10.html", "w", encoding="utf-8") as f:
        f.write(ip_csv)

    rows = ""

    for index, ip in enumerate(ips, start=1):
        safe_ip = escape(ip)

        rows += f"""
            <tr>
                <td>{index}</td>
                <td>
                    <a href="https://zh-hans.ipshu.com/ipv4/{safe_ip}" target="_blank">
                        {safe_ip}
                    </a>
                </td>
                <td>{now}</td>
            </tr>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloudflare 优选 IP</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 30px;
            background: #f7f7f7;
            color: #111;
        }}

        h1, p {{
            text-align: center;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            margin-top: 20px;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }}

        th {{
            background: #f0f0f0;
        }}

        a {{
            color: #0070f3;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <h1>Cloudflare 优选 IP</h1>
    <p>更新时间：{now}</p>

    <table>
        <thead>
            <tr>
                <th>序号</th>
                <th>IP 地址</th>
                <th>更新时间</th>
            </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
    </table>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    if not all([CF_API_TOKEN, CF_ZONE_ID, CF_DNS_NAME]):
        raise RuntimeError("Missing CF_API_TOKEN / CF_ZONE_ID / CF_DNS_NAME")

    ips = get_dns_ips()
    write_files(ips)

    print(f"Generated pages with {len(ips)} IPs")

if __name__ == "__main__":
    main()
