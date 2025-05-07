# convert_readme.py
import markdown
import os

# 파일 읽기
with open("README.md", "r", encoding="utf-8") as f:
    md_text = f.read()

# 마크다운 → HTML 변환 (표 지원 포함)
html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

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
      max-width: 900px;
      margin: 40px auto;
      padding: 20px;
      line-height: 1.6;
      background-color: #fdfdfd;
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
      font-family: monospace;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 20px 0;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }}
    th {{
      background-color: #f2f2f2;
    }}
    a {{
      color: #0366d6;
      text-decoration: none;
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

print("✅ README.md converted to templates/readme.html with table support")