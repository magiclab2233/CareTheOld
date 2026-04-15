import cv2
import mediapipe as mp
import os
import glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def check_image_sizes():
    print("=" * 60)
    print("🔍 检查 fall 文件夹中的图片尺寸")
    print("=" * 60)
    
    fall_images = glob.glob("fall/*.jpg")[:10]
    
    if not fall_images:
        print("❌ 没有找到 fall 文件夹中的图片")
        return 640, 480
    
    sizes = {}
    for img_path in fall_images[:5]:
        img = cv2.imread(img_path)
        if img is not None:
            h, w = img.shape[:2]
            size_key = f"{w}x{h}"
            sizes[size_key] = sizes.get(size_key, 0) + 1
    
    print("\n📊 图片尺寸统计:")
    for size, count in sizes.items():
        print(f"   {size}: {count} 张")
    
    most_common = max(sizes, key=sizes.get)
    w, h = map(int, most_common.split('x'))
    print(f"\n✅ 最常见尺寸: {w}x{h}")
    
    return w, h

def put_chinese_text(img, text, position, font_size, color):
    """在图像上显示中文文字"""
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    
    font = None
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, font_size)
            break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
    
    draw.text(position, text, font=font, fill=(color[2], color[1], color[0]))
    
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def capture_samples():
    print("=" * 60)
    print("📷 拍摄摔倒样本图片")
    print("=" * 60)
    
    w, h = check_image_sizes()
    if w is None:
        w, h = 640, 480
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    print(f"\n📐 目标尺寸: {w}x{h}")
    print("\n🔍 检测可用摄像头...")
    
    cap = None
    camera_index = 0
    
    available_cameras = []
    
    for i in range(5):
        temp_cap = cv2.VideoCapture(i)
        if temp_cap.isOpened():
            ret, frame = temp_cap.read()
            if ret:
                available_cameras.append(i)
                print(f"   ✅ 摄像头 {i}: 可用 ({frame.shape[1]}x{frame.shape[0]})")
            temp_cap.release()
    
    if not available_cameras:
        print("   ❌ 未检测到可用摄像头")
        return
    
    if len(available_cameras) == 1:
        camera_index = available_cameras[0]
        print(f"\n   使用摄像头 {camera_index}")
    else:
        print(f"\n   检测到 {len(available_cameras)} 个摄像头:")
        for i, idx in enumerate(available_cameras):
            print(f"     {i+1}. 摄像头索引 {idx}")
        
        try:
            choice = int(input("\n   请选择摄像头 (输入数字): "))
            if 1 <= choice <= len(available_cameras):
                camera_index = available_cameras[choice - 1]
            else:
                camera_index = 0
        except:
            camera_index = 0
    
    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    print(f"   ✅ 摄像头已连接 (索引: {camera_index})")
    print("\n💡 使用说明:")
    print("   - 站在摄像头前，摆出摔倒姿势")
    print("   - 按 's' 键拍照并保存")
    print("   - 按 'q' 键退出")
    print("-" * 60)
    
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 无法获取画面")
            break
        
        frame = cv2.flip(frame, 1)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(
                    color=(0, 255, 0), thickness=3, circle_radius=5
                ),
                mp.solutions.drawing_utils.DrawingSpec(
                    color=(255, 0, 0), thickness=2, circle_radius=2
                )
            )
            frame = put_chinese_text(frame, "✅ 检测到人体姿态", (20, 50), 30, (0, 255, 0))
        else:
            frame = put_chinese_text(frame, "🔍 未检测到人体", (20, 50), 30, (0, 0, 255))
        
        frame = put_chinese_text(frame, f"已保存: {saved_count} 张", (20, h - 40), 25, (255, 255, 255))
        frame = put_chinese_text(frame, "按 's' 拍照 | 'q' 退出", (20, h - 15), 20, (255, 255, 255))
        
        cv2.imshow("Capture Samples", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n👋 退出程序")
            break
        elif key == ord('s'):
            if results.pose_landmarks:
                timestamp = len(glob.glob("fall/*.jpg"))
                filename = f"fall/frame_video_capture_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                saved_count += 1
                print(f"✅ 已保存: {filename}")
            else:
                print("⚠️ 未检测到人体姿态，无法保存")
    
    cap.release()
    cv2.destroyAllWindows()
    pose.close()
    
    print(f"\n📊 总结:")
    print(f"   总共保存: {saved_count} 张图片")
    print(f"   保存位置: fall/ 文件夹")
    print("=" * 60)

if __name__ == "__main__":
    capture_samples()
