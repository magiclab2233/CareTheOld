import cv2
import mediapipe as mp
import numpy as np
import joblib
import os
import time
import winsound
import threading
from PIL import Image, ImageDraw, ImageFont
from paho.mqtt import client as mqtt

MQTT_ENABLED = False
mqtt_client = None
MQTT_TOPIC = None

MQTT_CONFIG = {
    "broker": "iot.dfrobot.com.cn",
    "port": 1883,
    "topic": "1zAmJ1Hvg",
    "username": "HgKzJJHvR",
    "password": "HTQuCLHvg"
}

def mqtt_publish(topic, message):
    """发布MQTT消息（保留消息，新订阅者也能收到）"""
    global mqtt_client, MQTT_ENABLED
    if not MQTT_ENABLED or mqtt_client is None:
        return False
    try:
        mqtt_client.publish(topic, message, retain=True)
        print(f"   📡 MQTT已发布: {topic} -> {message}")
        return True
    except Exception as e:
        print(f"   MQTT发布失败: {e}")
        return False

def mqtt_connect(broker_host, broker_port, topic, username=None, password=None):
    """连接MQTT"""
    global mqtt_client, MQTT_ENABLED, MQTT_TOPIC
    MQTT_TOPIC = topic
    try:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="fall_detection_pc")
        if username and password:
            mqtt_client.username_pw_set(username, password)
        mqtt_client.connect(broker_host, broker_port, 60)
        mqtt_client.loop_start()
        MQTT_ENABLED = True
        print(f"   ✅ MQTT已连接: {broker_host}:{broker_port}")
        print(f"   📡 主题: {topic}")
        return True
    except Exception as e:
        print(f"   ❌ MQTT连接失败: {e}")
        return False

def play_alarm_sound():
    """在后台线程中播放警报声"""
    for _ in range(10):
        winsound.Beep(800, 500)
        time.sleep(0.1)
        winsound.Beep(1000, 500)
        time.sleep(0.1)

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

def draw_button(img, text, x, y, w, h, color, hover_color, is_hover, font_size=30):
    """绘制按钮"""
    current_color = hover_color if is_hover else color
    
    cv2.rectangle(img, (x, y), (x + w, y + h), current_color, -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
    
    text_size = cv2.getTextSize("A", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = x + (w - text_size[0] * len(text) * 0.5) // 2 - 20
    text_y = y + (h + text_size[1]) // 2 - 15
    
    img = put_chinese_text(img, text, (text_x, text_y), font_size, (255, 255, 255))
    
    return img

def select_camera_gui():
    """GUI摄像头选择界面"""
    print("\n🔍 检测可用摄像头...")
    available_cameras = []
    camera_sizes = {}
    
    for i in range(5):
        try:
            temp_cap = cv2.VideoCapture(i)
            if temp_cap.isOpened():
                ret, frame = temp_cap.read()
                if ret:
                    available_cameras.append(i)
                    h, w = frame.shape[:2]
                    camera_sizes[i] = f"{w}x{h}"
                    print(f"   ✅ 摄像头 {i}: {w}x{h}")
                temp_cap.release()
        except:
            continue
    
    if not available_cameras:
        print("   ❌ 未检测到可用摄像头")
        return 0
    
    if len(available_cameras) == 1:
        print(f"\n   使用摄像头 {available_cameras[0]}")
        return available_cameras[0]
    
    window_name = "Select Camera"
    window_w, window_h = 800, 500
    
    canvas = np.zeros((window_h, window_w, 3), dtype=np.uint8)
    canvas[:] = (30, 30, 30)
    
    selected_camera = None
    buttons = []
    mouse_pos = [0, 0]
    
    button_w, button_h = 220, 80
    start_x = (window_w - (len(available_cameras) * (button_w + 50))) // 2
    start_y = 250
    
    for i, cam_idx in enumerate(available_cameras):
        x = start_x + i * (button_w + 50)
        y = start_y
        buttons.append({
            'x': x, 'y': y, 'w': button_w, 'h': button_h,
            'cam_idx': cam_idx, 'text': f"摄像头 {cam_idx} ({camera_sizes.get(cam_idx, 'Unknown')})"
        })
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal selected_camera
        mouse_pos[0] = x
        mouse_pos[1] = y
        if event == cv2.EVENT_LBUTTONDOWN:
            for btn in buttons:
                if btn['x'] <= x <= btn['x'] + btn['w'] and btn['y'] <= y <= btn['y'] + btn['h']:
                    selected_camera = btn['cam_idx']
    
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    while True:
        display = canvas.copy()
        
        display = put_chinese_text(display, "请选择摄像头", (window_w // 2 - 100, 150), 40, (255, 255, 255))
        
        for btn in buttons:
            is_hover = (btn['x'] <= mouse_pos[0] <= btn['x'] + btn['w'] and 
                       btn['y'] <= mouse_pos[1] <= btn['y'] + btn['h'])
            
            color = (0, 150, 0) if is_hover else (0, 100, 0)
            hover_color = (0, 180, 0)
            
            display = draw_button(display, btn['text'], btn['x'], btn['y'],
                                 btn['w'], btn['h'], color, hover_color, is_hover)
        
        display = put_chinese_text(display, "点击下方按钮选择摄像头", (window_w // 2 - 120, 420), 25, (200, 200, 200))
        
        cv2.imshow(window_name, display)
        
        if selected_camera is not None:
            cv2.destroyWindow(window_name)
            return selected_camera
        
        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            cv2.destroyWindow(window_name)
            return available_cameras[0]

def extract_features(landmarks, image_width, image_height):
    """从人体关键点提取特征"""
    features = []
    
    if landmarks is None:
        return None
    
    keypoints = {}
    for i in range(len(landmarks)):
        lm = landmarks[i]
        keypoints[i] = (lm.x, lm.y, lm.visibility)
    
    if sum(kp[2] for kp in keypoints.values()) < 10:
        return None
    
    for i in range(33):
        x, y, vis = keypoints.get(i, (0, 0, 0))
        features.extend([x, y, vis])
    
    def distance(p1, p2):
        x1, y1, _ = p1
        x2, y2, _ = p2
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def angle(p1, p2, p3):
        x1, y1, _ = p1
        x2, y2, _ = p2
        x3, y3, _ = p3
        
        v1 = np.array([x1 - x2, y1 - y2])
        v2 = np.array([x3 - x2, y3 - y2])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1, 1)
        return np.arccos(cos_angle) * 180 / np.pi
    
    nose = keypoints.get(0, (0, 0, 0))
    left_shoulder = keypoints.get(11, (0, 0, 0))
    right_shoulder = keypoints.get(12, (0, 0, 0))
    left_hip = keypoints.get(23, (0, 0, 0))
    right_hip = keypoints.get(24, (0, 0, 0))
    left_knee = keypoints.get(25, (0, 0, 0))
    right_knee = keypoints.get(26, (0, 0, 0))
    left_ankle = keypoints.get(27, (0, 0, 0))
    right_ankle = keypoints.get(28, (0, 0, 0))
    left_wrist = keypoints.get(15, (0, 0, 0))
    right_wrist = keypoints.get(16, (0, 0, 0))
    
    body_height = distance(left_shoulder, left_hip)
    leg_length = (distance(left_hip, left_knee) + distance(right_hip, right_knee)) / 2
    torso_length = distance(left_shoulder, left_hip)
    
    shoulder_width = distance(left_shoulder, right_shoulder)
    hip_width = distance(left_hip, right_hip)
    
    left_arm_length = distance(left_shoulder, left_wrist)
    right_arm_length = distance(right_shoulder, right_wrist)
    avg_arm_length = (left_arm_length + right_arm_length) / 2
    
    left_leg_length = distance(left_hip, left_ankle)
    right_leg_length = distance(right_hip, right_ankle)
    avg_leg_length = (left_leg_length + right_leg_length) / 2
    
    left_elbow_angle = angle(left_shoulder, keypoints.get(13, (0,0,0)), left_wrist)
    right_elbow_angle = angle(right_shoulder, keypoints.get(14, (0,0,0)), right_wrist)
    left_knee_angle = angle(left_hip, left_knee, left_ankle)
    right_knee_angle = angle(right_hip, right_knee, right_ankle)
    
    left_shoulder_angle = angle(left_hip, left_shoulder, keypoints.get(13, (0,0,0)))
    right_shoulder_angle = angle(right_hip, right_shoulder, keypoints.get(14, (0,0,0)))
    
    body_tilt_angle = angle(left_shoulder, nose, right_shoulder)
    hip_tilt_angle = angle(left_shoulder, left_hip, right_hip)
    
    if body_height > 0:
        features.extend([
            leg_length / body_height,
            torso_length / body_height,
            shoulder_width / body_height,
            hip_width / body_height,
            avg_arm_length / body_height,
            avg_leg_length / body_height,
        ])
    else:
        features.extend([0] * 6)
    
    features.extend([
        left_elbow_angle,
        right_elbow_angle,
        left_knee_angle,
        right_knee_angle,
        left_shoulder_angle,
        right_shoulder_angle,
        body_tilt_angle,
        hip_tilt_angle,
    ])
    
    nose_y = nose[1]
    ankle_avg_y = (left_ankle[1] + right_ankle[1]) / 2
    features.append(nose_y - ankle_avg_y)
    
    left_wrist_y = left_wrist[1]
    right_wrist_y = right_wrist[1]
    features.append(left_wrist_y - nose_y)
    features.append(right_wrist_y - nose_y)
    
    features.append(avg_arm_length / (avg_leg_length + 1e-6))
    features.append(leg_length / (torso_length + 1e-6))
    
    return features[:100]

def main():
    print("=" * 60)
    print("🎯 实时摔倒检测系统")
    print("=" * 60)
    
    model_path = "fall_detection_model.pkl"
    if not os.path.exists(model_path):
        print(f"\n❌ 错误: 模型文件 '{model_path}' 不存在")
        print("   请先运行 'python train_fall_model.py' 训练模型")
        return
    
    print("\n📦 加载模型...")
    model = joblib.load(model_path)
    print("   ✅ 模型加载成功")

    mqtt_connect(
        MQTT_CONFIG['broker'],
        MQTT_CONFIG['port'],
        MQTT_CONFIG['topic'],
        MQTT_CONFIG['username'],
        MQTT_CONFIG['password']
    )
    
    camera_index = select_camera_gui()
    print(f"\n   已选择摄像头: {camera_index}")
    
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    print("\n📷 打开摄像头...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("   ❌ 无法打开摄像头")
        return
    
    print("   ✅ 摄像头已连接")
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"   分辨率: {frame_width}x{frame_height}")
    
    print("\n" + "-" * 60)
    print("💡 使用说明:")
    print("   - 站在摄像头前，系统会自动检测您的姿态")
    print("   - 绿色边框: 正常状态")
    print("   - 红色边框: 摔倒检测")
    print("   - 按 'q' 键退出程序")
    print("-" * 60)
    
    fall_count = 0
    normal_count = 0
    frame_count = 0
    fall_start_time = None
    alarm_triggered = False
    last_normal_mqtt_time = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ 无法获取画面")
            break
        
        frame = cv2.flip(frame, 1)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        h, w, c = frame.shape
        
        skeleton = np.zeros((h, w, 3), dtype=np.uint8)
        skeleton[:] = (0, 0, 0)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=5),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )
            
            skeleton = np.zeros((h, w, 3), dtype=np.uint8)
            skeleton[:] = (0, 0, 0)
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    skeleton,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=5),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
                )
            
            skeleton = put_chinese_text(skeleton, "人体关键点", (w // 2 - 60, 30), 25, (0, 255, 0))
            cv2.rectangle(skeleton, (0, 0), (w, h), (0, 255, 0), 4)
            
            if results.pose_landmarks:
                features = extract_features(results.pose_landmarks.landmark, w, h)
            else:
                features = None
            
            if features is not None and len(features) == 100:
                features = np.array(features).reshape(1, -1)
                prediction = model.predict(features)[0]
                probability = model.predict_proba(features)[0]
                
                frame_count += 1
                
                if prediction == 1:
                    fall_count += 1
                    status = "⚠️ 摔倒!"
                    status_color = (0, 0, 255)
                    confidence = probability[1] * 100
                    
                    if fall_start_time is None:
                        fall_start_time = time.time()
                        alarm_triggered = False
                    
                    fall_duration = time.time() - fall_start_time
                    
                    if fall_duration >= 5 and not alarm_triggered:
                        alarm_triggered = True
                        if MQTT_TOPIC:
                            mqtt_publish(MQTT_TOPIC, "Fall")
                        threading.Thread(target=play_alarm_sound, daemon=True).start()
                    
                    if fall_duration >= 5:
                        status = "🚨 警报! 摔倒超过5秒!"
                        status_color = (0, 0, 255)
                        frame = put_chinese_text(frame, f"摔倒持续: {fall_duration:.1f}秒", (20, 150), 30, (0, 0, 255))
                        skeleton = put_chinese_text(skeleton, f"摔倒持续: {fall_duration:.1f}秒", (20, 150), 30, (0, 0, 255))
                    else:
                        frame = put_chinese_text(frame, f"摔倒持续: {fall_duration:.1f}秒", (20, 150), 30, (255, 165, 0))
                        skeleton = put_chinese_text(skeleton, f"摔倒持续: {fall_duration:.1f}秒", (20, 150), 30, (255, 165, 0))
                else:
                    normal_count += 1
                    status = "✅ 正常"
                    status_color = (0, 255, 0)
                    confidence = probability[0] * 100
                    fall_start_time = None
                    alarm_triggered = False
                    
                    current_time = time.time()
                    if MQTT_TOPIC and (current_time - last_normal_mqtt_time >= 60):
                        last_normal_mqtt_time = current_time
                        mqtt_publish(MQTT_TOPIC, "Normal")
                
                frame = put_chinese_text(frame, status, (20, 50), 40, status_color)
                skeleton = put_chinese_text(skeleton, status, (20, 50), 40, status_color)
                
                frame = put_chinese_text(frame, f"置信度: {confidence:.1f}%", (20, 100), 30, status_color)
                skeleton = put_chinese_text(skeleton, f"置信度: {confidence:.1f}%", (20, 100), 30, status_color)
            else:
                frame_count += 1
                status = "检测中..."
                status_color = (255, 255, 0)
                fall_start_time = None
                alarm_triggered = False
                frame = put_chinese_text(frame, status, (20, 50), 40, status_color)
            
            cv2.rectangle(frame, (0, 0), (w, h), status_color, 8)
            cv2.rectangle(skeleton, (0, 0), (w, h), status_color, 8)
            
            frame = put_chinese_text(frame, f"正常: {normal_count} | 摔倒: {fall_count}", (20, h - 30), 25, (255, 255, 255))
            skeleton = put_chinese_text(skeleton, f"正常: {normal_count} | 摔倒: {fall_count}", (20, h - 30), 25, (255, 255, 255))
        else:
            skeleton = put_chinese_text(skeleton, "未检测到人体", (w // 2 - 70, h // 2), 30, (100, 100, 100))
            cv2.rectangle(skeleton, (0, 0), (w, h), (100, 100, 100), 4)
            
            frame_count += 1
            status = "检测中..."
            status_color = (255, 255, 0)
            fall_start_time = None
            alarm_triggered = False
            frame = put_chinese_text(frame, status, (20, 50), 40, status_color)
            
            cv2.rectangle(frame, (0, 0), (w, h), status_color, 8)
            
            frame = put_chinese_text(frame, f"正常: {normal_count} | 摔倒: {fall_count}", (20, h - 30), 25, (255, 255, 255))
        
        combined = np.hstack((frame, skeleton))
        
        combined = put_chinese_text(combined, "按 'q' 退出", (w * 2 - 200, 30), 20, (255, 255, 255))
        
        cv2.imshow("Fall Detection", combined)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    pose.close()
    
    print("\n" + "=" * 60)
    print("📊 检测统计:")
    print(f"   总帧数: {frame_count}")
    print(f"   正常帧数: {normal_count}")
    print(f"   摔倒帧数: {fall_count}")
    print(f"   摔倒比例: {fall_count/frame_count*100:.1f}%" if frame_count > 0 else "   N/A")
    print("=" * 60)
    print("👋 程序已退出")

if __name__ == "__main__":
    main()
