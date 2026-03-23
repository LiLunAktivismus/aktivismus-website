import os
import json
import requests
from datetime import datetime
import re 

# 1. 接收飞书传来的基础数据
payload_str = os.environ.get('CLIENT_PAYLOAD', '{}')

try:
    payload = json.loads(payload_str)
    if payload is None: 
        payload = {}
except Exception:
    payload = {}

title = payload.get('title') or 'System Test Article'
content = payload.get('content') or 'This is an automated test to check if the pipeline is working.'
tag = payload.get('tag') or 'INDUSTRY INSIGHT'
date_str = datetime.now().strftime('%B %d, %Y')
image_raw = payload.get('image_url', '')

# Slug清洗逻辑
raw_slug = payload.get('slug') or title
# 1. 强力剔除可能存在的 HTML 转义序列 (如 &quot; &#39; &amp;)
clean_slug = re.sub(r'&[a-z0-9#]+;', '', raw_slug.lower())
# 2. 兜底逻辑：无情抹杀除小写字母、数字、横线以外的所有残余符号（如引号实体的残余）
slug = re.sub(r'[^a-z0-9\-]', '', clean_slug)

# 提取纯文本摘要，用于卡片预览
snippet = content.replace("<br><br>", " ").replace("&quot;", '"').replace("\\\\", "\\")[:120] + "..."

# ==========================================
# 🚀 核心修复：飞书私有链接下载器
# ==========================================
local_image_path = "https://via.placeholder.com/800x400" 
APP_ID = os.environ.get('FEISHU_APP_ID')
APP_SECRET = os.environ.get('FEISHU_APP_SECRET')

if APP_ID and APP_SECRET and image_raw:
    try:
        # 1. 从长链接中提取 File Token
        # 你的链接中，Token 通常在 /download/all/ 之后，下一个斜杠之前
        file_token = ""
        if "download/all/" in image_raw:
            file_token = image_raw.split("download/all/")[1].split("/")[0]
        else:
            # 如果传过来的是纯 Token，则直接使用
            file_token = image_raw.strip()

        if file_token:
            print(f"🔄 Attempting to download file_token: {file_token}")

            # 2. 获取 Tenant Access Token (拿钥匙)
            auth_res = requests.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": APP_ID, "app_secret": APP_SECRET}
            ).json()
            
            if auth_res.get("code") == 0:
                tenant_token = auth_res["tenant_access_token"]
                
                # 3. 使用标准 API 下载文件流
                # 注意：不要直接请求你那个长链接，要请求飞书的 OpenAPI 接口
                download_url = f"https://open.feishu.cn/open-apis/drive/v1/medias/{file_token}/download"
                img_res = requests.get(
                    download_url, 
                    headers={"Authorization": f"Bearer {tenant_token}"}
                )
                
                if img_res.status_code == 200:
                    os.makedirs('assets/images', exist_ok=True)
                    # 使用 slug 命名图片，确保唯一性
                    save_path = f"assets/images/{slug}.png"
                    with open(save_path, "wb") as f:
                        f.write(img_res.content)
                    
                    local_image_path = f"/{save_path}"
                    print(f"✅ Image downloaded: {local_image_path}")
                else:
                    print(f"❌ API Download failed. Status: {img_res.status_code}")
    except Exception as e:
        print(f"⚠️ Image processing error: {e}")

# ==========================================
# 2. 生成单篇文章 HTML (读取模板并替换)
# ==========================================
with open("article-template.html", "r", encoding="utf-8") as template_file:
    template_html = template_file.read()

final_html = template_html.replace("{{TITLE}}", title)
final_html = final_html.replace("{{TAG}}", tag)
final_html = final_html.replace("{{DATE}}", date_str)
# 注意：这里插入的是刚刚下载到本地的图片路径
final_html = final_html.replace("{{IMAGE}}", local_image_path) 
final_html = final_html.replace("{{CONTENT}}", content)

os.makedirs('insights', exist_ok=True)
file_path = f"insights/{slug}.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(final_html)

# ==========================================
# 3. 自动更新 insights.html 的列表页 (彻底抛弃隐形暗号的防弹版)
# ==========================================
hub_path = "insights.html"
if os.path.exists(hub_path):
    with open(hub_path, "r", encoding="utf-8") as f:
        hub_content = f.read()

    new_card = f"""
        <a href="/{file_path}" class="insight-card auto-card">
            <div class="card-meta"><span>{tag}</span><span>{date_str}</span></div>
            <div class="card-img-placeholder" style="background-image: url('{local_image_path}'); background-size: cover; background-position: center; border: none;"></div>
            <h3>{title}</h3>
            <p>{snippet}</p>
            <div class="read-more">Read More →</div>
        </a>"""
    
    # 👇 核心改变：直接用网页里天然存在的原生 HTML 标签作为定位器！
    target_tag = '<section class="insights-grid auto-section" id="auto-article-grid">'
    
    if target_tag in hub_content:
        # 找到这个大门后，把它替换为【大门本身 + 换行 + 新卡片】
        hub_content = hub_content.replace(target_tag, f'{target_tag}\n{new_card}', 1)
        with open(hub_path, "w", encoding="utf-8") as f:
            f.write(hub_content)

print(f"✅ Success! Published {file_path}")
