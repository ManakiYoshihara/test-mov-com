import os
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip

def add_overlay(video, overlay_path, position, resize_width=None):
    # videoがパスの場合、VideoFileClipに変換
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
    # Paths
    upload_dir = 'static/uploads'
    output_dir = 'static/outputs'
    material_dir = "material"
    thumbnail_path = os.path.join(upload_dir, 'thumbnail.png')
    question_path = os.path.join(upload_dir, 'question.png')
    main_video_path = os.path.join(upload_dir, 'main.mp4')
    base_image_path = os.path.join(material_dir, "base.jpg")

    # Process op1.mp4
    op1 = add_overlay(os.path.join(material_dir, "op1.mp4"), thumbnail_path, position=(120, 1380), resize_width=1920)

    # Process op2.mp4
    op2 = add_overlay(os.path.join(material_dir, "op2.mp4"), thumbnail_path, position=(0, 34), resize_width=2160)
    op2_question = ImageClip(question_path).resize(width=2160)
    op2_question = op2_question.set_position((0, 1312)).set_duration(op2.duration)
    op2 = CompositeVideoClip([op2, op2_question])

    # Process op4.mp4
    op4 = add_overlay(os.path.join(material_dir, "op4.mp4"), thumbnail_path, position=(120, 1380), resize_width=1920)

    # Process main.mp4
    main_video = overlay_on_base(main_video_path, base_image_path, output_duration=150, output_resolution=(2160, 3840))
    main = add_overlay(main_video, thumbnail_path, position=(0, 0), resize_width=2160)

    # Load ed.mp4
    ed = VideoFileClip(os.path.join(material_dir, "ed.mp4")).set_fps(24)
    op3 = VideoFileClip(os.path.join(material_dir, "op3.mp4")).set_fps(24)

    # Concatenate all clips
    final_video = concatenate_videoclips([op1, op2, op3, op4, main, ed])

    # Export
    output_path = os.path.join(output_dir, "output.mp4")
    final_video.write_videofile(output_path, fps=24, codec="libx264")

if __name__ == "__main__":
    main()
