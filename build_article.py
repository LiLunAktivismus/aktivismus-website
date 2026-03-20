import os
import json
from datetime import datetime

# 1. 接收数据并增加防弹机制 (处理手动运行没数据的情况)
payload_str = os.environ.get('CLIENT_PAYLOAD', '{}')

try:
    payload = json.loads(payload_str)
    # 当手动运行时，toJson(null) 会变成字符串 "null"，解析后是 None
    if payload is None: 
        payload = {}
except Exception:
    payload = {}

# 如果取不到数据，就使用默认的测试数据
title = payload.get('title') or 'System Test Article'
content = payload.get('content') or 'This is an automated test to check if the pipeline is working.'
image_url = payload.get('image_url') or 'https://via.placeholder.com/800x400'
slug = payload.get('slug') or f"test-article-{int(datetime.now().timestamp())}"
date_str = datetime.now().strftime('%B %d, %Y')

# 将换行符转换为简单的 <p> 标签
# 修改后的代码：
formatted_content = content

# 2. 生成单独的文章 HTML 页面
article_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} | Aktivismus Insights</title>
    <link rel="stylesheet" href="/navigation.css">
</head>
<body style="background:#131313; color:#fff; font-family:sans-serif;">
    <div style="max-width:800px; margin: 150px auto; padding: 0 5%;">
        <img src="{image_url}" style="width:100%; border-radius:12px; margin-bottom:30px;">
        <h1 style="color:#00EEFF; font-size: 3rem;">{title}</h1>
        <p style="color:#888;">Published on {date_str}</p>
        <div style="line-height: 1.8; font-size: 1.1rem; margin-top:40px;">
            {formatted_content}
        </div>
    </div>
</body>
</html>
"""

# 保存文章到 insights 文件夹
os.makedirs('insights', exist_ok=True)
file_path = f"insights/{slug}.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(article_html)

# 3. 自动更新 insights-hub.html 的列表页
hub_path = "insights-hub.html"
if os.path.exists(hub_path):
    with open(hub_path, "r", encoding="utf-8") as f:
        hub_content = f.read()

    new_card = f"""
    <a href="/{file_path}" class="insight-card">
        <div class="card-meta"><span>NEW UPDATE</span><span>{date_str}</span></div>
        <div class="card-img-placeholder" style="background-image:url('{image_url}'); background-size:cover; background-position:center;"></div>
        <h3>{title}</h3>
        <p>{content[:100]}...</p>
        <div class="read-more">Read More →</div>
    </a>
    """
    
    if '<main class="insights-grid">' in hub_content:
        hub_content = hub_content.replace(
            '<main class="insights-grid">', 
            f'<main class="insights-grid">\n{new_card}'
        )
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(hub_content)

print(f"Success! Generated {file_path}")
