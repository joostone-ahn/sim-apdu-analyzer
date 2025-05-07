# convert_readme.py
import markdown
import os

# 파일 읽기
with open("README.md", "r", encoding="utf-8") as f:
    md_text = f.read()

# 마크다운 → HTML 변환
html = markdown.markdown(md_text)

# 전체 HTML 템플릿으로 감싸기
wrapped_html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>README</title>
  <style>
    body {{
      font-family: sans-serif;
      max-width: 800px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
    }}
    h1, h2, h3 {{
      border-bottom: 1px solid #ddd;
      padding-bottom: 0.3em;
    }}
    pre {{
      background: #f4f4f4;
      padding: 10px;
      overflow-x: auto;
    }}
    code {{
      background: #f0f0f0;
      padding: 2px 4px;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
  <a href="/" style="display:block;margin-bottom:20px;">← Back to Home</a>
  {html}
</body>
</html>
"""

# 저장 위치
os.makedirs("templates", exist_ok=True)
with open("templates/readme.html", "w", encoding="utf-8") as f:
    f.write(wrapped_html)

print("✅ README.md converted to templates/readme.html")