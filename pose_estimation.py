import cv2
import mediapipe as mp
import time

def main():
    # 初始化MediaPipe姿态估计
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    print("程序已启动，按 'q' 键退出")
    print("正在识别人体姿态关键点...")

    # 获取摄像头帧率
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"摄像头帧率: {fps} FPS")

    while True:
        # 读取摄像头画面
        ret, frame = cap.read()
        
        if not ret:
            print("无法获取画面")
            break

        # 镜像翻转画面（水平翻转）
        frame = cv2.flip(frame, 1)

        # 转换颜色空间 (BGR to RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理画面进行姿态估计
        results = pose.process(frame_rgb)
        
        # 绘制人体关键点和连接线
        if results.pose_landmarks:
            # 绘制关键点
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=(0, 255, 0),  # 绿色关键点
                    thickness=3,
                    circle_radius=5
                ),
                mp_drawing.DrawingSpec(
                    color=(255, 0, 0),  # 蓝色连接线
                    thickness=2,
                    circle_radius=2
                )
            )
            
            # 获取并显示关键点坐标
            h, w, c = frame.shape
            landmarks = results.pose_landmarks.landmark
            
            # 绘制关键点编号
            keypoint_names = [
                '鼻子', '左眼外', '左眼内', '右眼内', '右眼外',
                '左耳', '右耳', '左肩', '右肩', '左肘', '右肘',
                '左手腕', '右手腕', '左髋', '右髋', '左膝', '右膝',
                '左脚踝', '右脚踝'
            ]
            
            for i, (name, landmark) in enumerate(zip(keypoint_names, landmarks[:19])):
                if landmark.visibility > 0.5:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                    cv2.putText(frame, str(i), (x + 10, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 在画面上显示信息
        cv2.putText(frame, 'Press Q to exit', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, 'Pose Estimation', (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 显示画面
        cv2.imshow('Camera - Pose Estimation', frame)

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
    pose.close()
    print("程序已退出")

if __name__ == "__main__":
    main()
