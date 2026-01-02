FROM python:3.9-slim
WORKDIR /app
COPY . .

# SSL 검증을 우회하고 PyPI 서버를 신뢰할 수 있는 호스트로 등록
RUN pip install --no-cache-dir --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org -r requirements.txt

EXPOSE 5000
CMD ["python", "main_web.py"]