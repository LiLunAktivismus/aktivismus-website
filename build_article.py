import os
import json
from datetime import datetime

# 1. 接收飞书传来的数据，增加防弹机制
payload_str = os.environ.get('CLIENT_PAYLOAD', '{}')

try:
    payload = json.loads(payload_str)
    if payload is None: 
        payload = {}
except Exception:
    payload = {}

# 提取字段，如果为空则使用默认测试数据
title = payload.get('title') or 'System Test Article'
content = payload.get('content') or 'This is an automated test to check if the pipeline is working.'
image_url = payload.get('image_url') or 'https://via.placeholder.com/800x400'
slug = payload.get('slug') or f"test-article-{int(datetime.now().timestamp())}"
tag = payload.get('tag') or 'INDUSTRY INSIGHT'
date_str = datetime.now().strftime('%B %d, %Y')

# 清洗出纯文本摘要 (剥离飞书公式加上的 <br> 和转义符)，用于卡片预览
snippet = content.replace("<br><br>", " ").replace("&quot;", '"').replace("\\\\", "\\")[:120] + "..."

# 2. 生成单独的文章 HTML 页面 (读取模板并替换)
with open("article-template.html", "r", encoding="utf-8") as template_file:
    template_html = template_file.read()

final_html = template_html.replace("{{TITLE}}", title)
final_html = final_html.replace("{{TAG}}", tag)
final_html = final_html.replace("{{DATE}}", date_str)
final_html = final_html.replace("{{IMAGE}}", image_url)
final_html = final_html.replace("{{CONTENT}}", content)

# 保存文章到 insights 文件夹
os.makedirs('insights', exist_ok=True)
file_path = f"insights/{slug}.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(final_html)

# 3. 自动更新 insights.html 的列表页 (精准插入锚点)
hub_path = "insights.html"
if os.path.exists(hub_path):
    with open(hub_path, "r", encoding="utf-8") as f:
        hub_content = f.read()

    # 构建新卡片的 HTML
    new_card = f"""
        <a href="/{file_path}" class="insight-card auto-card">
            <div class="card-meta"><span>{tag}</span><span>{date_str}</span></div>
            <div class="card-img-placeholder" style="background-image:url('{image_url}'); background-size:cover; background-position:center;"></div>
            <h3>{title}</h3>
            <p>{snippet}</p>
            <div class="read-more">Read More →</div>
        </a>"""
    
    # 查找锚点并插入
    marker = ""
    if marker in hub_content:
        hub_content = hub_content.replace(
            marker, 
            f'{marker}\n{new_card}'
        )
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(hub_content)

print(f"Success! Generated {file_path} and updated insights.html")
