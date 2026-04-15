import cv2
import mediapipe as mp

with open('result.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("🧪 人体姿态估计测试\n")
    f.write("=" * 60 + "\n\n")
    
    try:
        f.write("1️⃣ 初始化MediaPipe...\n")
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        f.write("   ✅ MediaPipe初始化成功\n\n")
        
        f.write("2️⃣ 打开摄像头...\n")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            f.write("   ✅ 摄像头打开成功\n\n")
        else:
            f.write("   ❌ 无法打开摄像头\n")
            exit(1)
        
        f.write("3️⃣ 读取画面...\n")
        ret, frame = cap.read()
        if ret:
            f.write(f"   ✅ 画面读取成功 - 尺寸: {frame.shape}\n\n")
        else:
            f.write("   ❌ 无法读取画面\n")
            exit(1)
        
        f.write("4️⃣ 进行姿态检测...\n")
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            visible_count = sum(1 for lm in landmarks if lm.visibility > 0.5)
            f.write(f"   ✅ 检测到人体姿态!\n")
            f.write(f"   📊 可见关键点: {visible_count}/33\n\n")
            
            f.write("5️⃣ 关键点信息:\n")
            keypoints = [
                (0, "鼻子"), (11, "右肩"), (12, "左肩"),
                (13, "右手肘"), (14, "左手肘"), (15, "右手腕"), (16, "左手腕"),
                (23, "右髋"), (24, "左髋"), (25, "右膝"), (26, "左膝"),
                (27, "右脚踝"), (28, "左脚踝")
            ]
            
            for idx, name in keypoints:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    f.write(f"   {name}: 可信度={lm.visibility:.2f}\n")
        else:
            f.write("   ⚠️ 未检测到人体姿态\n")
            f.write("   💡 提示: 确保摄像头前有人体可见\n\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("✅ 测试完成!\n")
        f.write("=" * 60 + "\n")
        
    except Exception as e:
        f.write(f"\n❌ 错误: {e}\n")
    finally:
        if 'cap' in locals():
            cap.release()
        if 'pose' in locals():
            pose.close()
