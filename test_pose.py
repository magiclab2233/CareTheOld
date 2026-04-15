import cv2
import mediapipe as mp
import sys

def test_pose_estimation():
    print("=" * 60)
    print("🧪 人体姿态估计测试")
    print("=" * 60)
    
    # 1. 测试MediaPipe初始化
    print("\n1️⃣ 测试MediaPipe姿态估计...")
    try:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("   ✅ MediaPipe初始化成功")
    except Exception as e:
        print(f"   ❌ MediaPipe初始化失败: {e}")
        sys.exit(1)
    
    # 2. 测试摄像头
    print("\n2️⃣ 测试摄像头访问...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("   ❌ 无法打开摄像头")
        sys.exit(1)
    print("   ✅ 摄像头打开成功")
    
    # 3. 读取画面并检测
    print("\n3️⃣ 读取画面并进行姿态检测...")
    ret, frame = cap.read()
    if not ret:
        print("   ❌ 无法读取摄像头画面")
        cap.release()
        sys.exit(1)
    print(f"   ✅ 画面读取成功 - 尺寸: {frame.shape}")
    
    # 转换颜色空间
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 进行姿态估计
    print("\n4️⃣ 处理姿态估计...")
    results = pose.process(frame_rgb)
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        visible_count = sum(1 for lm in landmarks if lm.visibility > 0.5)
        print(f"   ✅ 检测到人体姿态!")
        print(f"   📊 可见关键点数量: {visible_count}/33")
        
        # 显示一些关键点信息
        print("\n5️⃣ 关键点信息:")
        keypoints = [
            (0, "鼻子"), (11, "右肩"), (12, "左手腕"),
            (23, "右髋"), (24, "左髋"), (25, "右膝"), (26, "左膝"),
            (27, "右脚踝"), (28, "左脚踝")
        ]
        
        for idx, name in keypoints:
            if idx < len(landmarks):
                lm = landmarks[idx]
                print(f"   {name} (#{idx}): 可信度={lm.visibility:.2f}, 坐标=({lm.x:.2f}, {lm.y:.2f})")
    else:
        print("   ⚠️ 未检测到人体姿态")
        print("   💡 提示: 确保摄像头前有人体可见")
    
    # 清理资源
    cap.release()
    pose.close()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
    print("\n🎯 完整功能说明:")
    print("   运行 'python pose_estimation.py' 打开实时姿态估计窗口")
    print("   - 绿色圆点: 人体关键点")
    print("   - 蓝色线条: 关键点连接")
    print("   - 按 'q' 键退出")
    print()

if __name__ == "__main__":
    test_pose_estimation()
