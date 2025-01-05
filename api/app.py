from flask import Flask, request
import os
import sys

# モジュール検索パスにプロジェクトルートを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main  # 動画処理ロジック

# Flaskアプリケーション設定
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "../static")  # 明示的にstaticフォルダを指定
)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# アップロードフォルダの設定
UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")  # staticフォルダ内のuploadsを指定
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ファイルをアップロード
        thumbnail = request.files['thumbnail']
        question = request.files['question']
        main_video = request.files['main']

        # ファイルを保存
        thumbnail.save(os.path.join(UPLOAD_FOLDER, 'thumbnail.png'))
        question.save(os.path.join(UPLOAD_FOLDER, 'question.png'))
        main_video.save(os.path.join(UPLOAD_FOLDER, 'main.mp4'))

        # 動画処理を呼び出し
        main.process_video()

        return "処理が完了しました！"
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
    app.run(host="0.0.0.0", port=5000, debug=True)
