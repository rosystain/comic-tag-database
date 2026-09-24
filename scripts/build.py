import os
import sys
import json
import requests

# 1. 仅依赖两个通用环境变量：上游数据源 URL 与鉴权 Token
UPSTREAM_API_URL = os.environ.get("UPSTREAM_API_URL")
UPSTREAM_API_TOKEN = os.environ.get("UPSTREAM_API_TOKEN")

if not UPSTREAM_API_URL:
    print("Error: Missing UPSTREAM_API_URL.", file=sys.stderr)
    sys.exit(1)

# 2. 构造通用请求头（如果上游配置了 Token 则携带 Bearer）
headers = {}
if UPSTREAM_API_TOKEN:
    headers["Authorization"] = f"Bearer {UPSTREAM_API_TOKEN}"

# 3. 发起请求
try:
    res = requests.get(UPSTREAM_API_URL, headers=headers, timeout=30)
    res.raise_for_status()
    payload = res.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching upstream data: {e}", file=sys.stderr)
    sys.exit(1)

# 4. 解析记录（兼容直接返回列表，或包裹在 records/data 字段内的格式）
records = payload.get("records", payload) if isinstance(payload, dict) else payload

clean_tags = []
for item in records:
    # 兼容直接平铺的字典，或带 fields 包装的结构
    fields = item.get("fields", item) if isinstance(item, dict) else {}
    
    clean_tags.append({
        "key": fields.get("key"),
        "display_zh": fields.get("display_zh"),
        "display_en": fields.get("display_en"),
        "category": fields.get("category"),
        "is_adult": bool(fields.get("is_adult", 0)),
        "description": fields.get("description", ""),
    })

# 5. 按 key 升序排序并输出
clean_tags.sort(key=lambda x: (x["key"] or ""))

os.makedirs("data", exist_ok=True)
with open("data/tags.json", "w", encoding="utf-8") as f:
    json.dump(clean_tags, f, ensure_ascii=False, indent=2)

print(f"Build complete. Processed {len(clean_tags)} tags.")