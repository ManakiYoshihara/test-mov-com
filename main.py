import os
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip
from google.cloud import storage

# GCSの設定
BUCKET_NAME = 'laf-video'  # GCSバケット名
LOCAL_MATERIAL_DIR = 'material'   # ローカル素材ファイルディレクトリ
LOCAL_UPLOAD_DIR = 'static/uploads'
LOCAL_OUTPUT_DIR = 'static/outputs'

# 必要なフォルダを作成
os.makedirs(LOCAL_MATERIAL_DIR, exist_ok=True)
os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """
    GCSからファイルをダウンロードする関数
    :param bucket_name: GCSのバケット名
    :param source_blob_name: GCS内のファイルパス
    :param destination_file_name: ローカルに保存するファイルパス
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}.")

def download_material_files():
    """
    GCSから必要な素材ファイルをすべてダウンロードする
    """
    files_to_download = [
        ("op1.mp4", os.path.join(LOCAL_MATERIAL_DIR, "op1.mp4")),
        ("op2.mp4", os.path.join(LOCAL_MATERIAL_DIR, "op2.mp4")),
        ("op3.mp4", os.path.join(LOCAL_MATERIAL_DIR, "op3.mp4")),
        ("op4.mp4", os.path.join(LOCAL_MATERIAL_DIR, "op4.mp4")),
        ("ed.mp4", os.path.join(LOCAL_MATERIAL_DIR, "ed.mp4")),
        ("base.jpg", os.path.join(LOCAL_MATERIAL_DIR, "base.jpg"))
    ]
    for gcs_path, local_path in files_to_download:
        download_from_gcs(BUCKET_NAME, gcs_path, local_path)

def add_overlay(video, overlay_path, position, resize_width=None):
    if isinstance(video, str):
        video = VideoFileClip(video).set_fps(24)
    overlay = ImageClip(overlay_path)
    if resize_width:
        overlay = overlay.resize(width=resize_width)
    overlay = overlay.set_position(position).set_duration(video.duration)
    return CompositeVideoClip([video, overlay])

def overlay_on_base(video_path, base_image_path, output_duration, output_resolution):
    base = ImageClip(base_image_path).set_duration(output_duration).resize(output_resolution)
    video = VideoFileClip(video_path).subclip(0, output_duration).set_fps(24)
    video = video.set_position(("center", "center"))
    return CompositeVideoClip([base, video])

def main():
    # 素材ファイルをGCSからダウンロード
    download_material_files()

    # Paths
    thumbnail_path = os.path.join(LOCAL_UPLOAD_DIR, 'thumbnail.png')
    question_path = os.path.join(LOCAL_UPLOAD_DIR, 'question.png')
    main_video_path = os.path.join(LOCAL_UPLOAD_DIR, 'main.mp4')
    base_image_path = os.path.join(LOCAL_MATERIAL_DIR, "base.jpg")

    # Process op1.mp4
    op1 = add_overlay(os.path.join(LOCAL_MATERIAL_DIR, "op1.mp4"), thumbnail_path, position=(120, 1380), resize_width=1920)

    # Process op2.mp4
    op2 = add_overlay(os.path.join(LOCAL_MATERIAL_DIR, "op2.mp4"), thumbnail_path, position=(0, 34), resize_width=2160)
    op2_question = ImageClip(question_path).resize(width=2160)
    op2_question = op2_question.set_position((0, 1312)).set_duration(op2.duration)
    op2 = CompositeVideoClip([op2, op2_question])

    # Process op4.mp4
    op4 = add_overlay(os.path.join(LOCAL_MATERIAL_DIR, "op4.mp4"), thumbnail_path, position=(120, 1380), resize_width=1920)

    # Process main.mp4
    main_video = overlay_on_base(main_video_path, base_image_path, output_duration=150, output_resolution=(2160, 3840))
    main = add_overlay(main_video, thumbnail_path, position=(0, 0), resize_width=2160)

    # Load ed.mp4
    ed = VideoFileClip(os.path.join(LOCAL_MATERIAL_DIR, "ed.mp4")).set_fps(24)
    op3 = VideoFileClip(os.path.join(LOCAL_MATERIAL_DIR, "op3.mp4")).set_fps(24)

    # Concatenate all clips
    final_video = concatenate_videoclips([op1, op2, op3, op4, main, ed])

    # Export
    output_path = os.path.join(LOCAL_OUTPUT_DIR, "output.mp4")
    final_video.write_videofile(output_path, fps=24, codec="libx264")

if __name__ == "__main__":
    main()
