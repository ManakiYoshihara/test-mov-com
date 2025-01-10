# Pythonの軽量イメージ
FROM python:3.12.8-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存ライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# Flaskアプリの起動
CMD ["python", "api/app.py"]
