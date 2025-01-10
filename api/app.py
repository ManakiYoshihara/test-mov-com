from flask import Flask, request
from google.cloud import storage
import os
import sys
import json

# モジュール検索パスにプロジェクトルートを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main  # 動画処理ロジック

# Vercel環境でJSONキーを一時ファイルに保存
def setup_google_credentials():
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("環境変数 'GOOGLE_APPLICATION_CREDENTIALS_JSON' が設定されていません。")
    
    key_file_path = "/tmp/service-account-key.json"
    with open(key_file_path, "w") as f:
        f.write(credentials_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

# Flaskアプリケーション設定
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "../static")  # 明示的にstaticフォルダを指定
)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# GCSバケット設定
BUCKET_NAME = "laf-video"  # GCSのバケット名
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")  # ローカルアップロード用フォルダ
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_to_gcs(file_stream, bucket_name, destination_blob_name):
    """
    GCSにファイルをアップロードする関数
    :param file_stream: アップロードされたファイルオブジェクト
    :param bucket_name: GCSのバケット名
    :param destination_blob_name: GCS内の保存先ファイル名
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file_stream)
    print(f"Uploaded {destination_blob_name} to bucket {bucket_name}.")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # 環境変数を設定
            setup_google_credentials()
            
            # ファイルをアップロード
            thumbnail = request.files['thumbnail']
            question = request.files['question']
            main_video = request.files['main']

            # GCSにファイルを保存
            upload_to_gcs(thumbnail.stream, BUCKET_NAME, 'uploads/thumbnail.png')
            upload_to_gcs(question.stream, BUCKET_NAME, 'uploads/question.png')
            upload_to_gcs(main_video.stream, BUCKET_NAME, 'uploads/main.mp4')

            # ローカルディレクトリに一時保存（オプション）
            thumbnail_path = os.path.join(UPLOAD_FOLDER, 'thumbnail.png')
            question_path = os.path.join(UPLOAD_FOLDER, 'question.png')
            main_video_path = os.path.join(UPLOAD_FOLDER, 'main.mp4')
            thumbnail.save(thumbnail_path)
            question.save(question_path)
            main_video.save(main_video_path)

            # 動画処理を呼び出し
            main.main()

            return "処理が完了しました！"
        except Exception as e:
            return f"エラーが発生しました: {e}", 500
    return '''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>ファイルアップロード</title>
    </head>
    <body>
        <h1>動画編集用ファイルアップロード</h1>
        <form method="POST" enctype="multipart/form-data">
            <label for="thumbnail">サムネイル画像:</label>
            <input type="file" name="thumbnail" required><br><br>

            <label for="question">質問画像:</label>
            <input type="file" name="question" required><br><br>

            <label for="main">メイン動画:</label>
            <input type="file" name="main" required><br><br>

            <button type="submit">アップロードして処理を開始</button>
        </form>
    </body>
    </html>
    '''

# Vercelがエントリポイントとして認識するためのコード
if __name__ != "__main__":
    app = app
else:
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
