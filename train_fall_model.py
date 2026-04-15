import cv2
import mediapipe as mp
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import glob

def extract_features(landmarks, image_width, image_height):
    """从人体关键点提取特征"""
    if landmarks is None or len(landmarks) == 0:
        return None
    
    try:
        features = []
        
        keypoints = []
        for lm in landmarks:
            keypoints.append((lm.x, lm.y, lm.visibility))
        
        total_visibility = sum(kp[2] for kp in keypoints)
        if total_visibility < 5:
            return None
        
        for i in range(min(33, len(keypoints))):
            x, y, vis = keypoints[i]
            features.extend([x, y, vis])
        
        def distance(p1, p2):
            x1, y1 = p1[0], p1[1]
            x2, y2 = p2[0], p2[1]
            return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        def angle(p1, p2, p3):
            x1, y1 = p1[0], p1[1]
            x2, y2 = p2[0], p2[1]
            x3, y3 = p3[0], p3[1]
            
            v1 = np.array([x1 - x2, y1 - y2])
            v2 = np.array([x3 - x2, y3 - y2])
            
            dot = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1) + 1e-6
            norm2 = np.linalg.norm(v2) + 1e-6
            cos_angle = dot / (norm1 * norm2)
            cos_angle = max(-1, min(1, cos_angle))
            return np.arccos(cos_angle) * 180 / np.pi
        
        keypoint_dict = {}
        for i, kp in enumerate(keypoints):
            keypoint_dict[i] = kp
        
        nose = keypoint_dict.get(0, (0, 0, 0))
        left_shoulder = keypoint_dict.get(11, (0, 0, 0))
        right_shoulder = keypoint_dict.get(12, (0, 0, 0))
        left_hip = keypoint_dict.get(23, (0, 0, 0))
        right_hip = keypoint_dict.get(24, (0, 0, 0))
        left_knee = keypoint_dict.get(25, (0, 0, 0))
        right_knee = keypoint_dict.get(26, (0, 0, 0))
        left_ankle = keypoint_dict.get(27, (0, 0, 0))
        right_ankle = keypoint_dict.get(28, (0, 0, 0))
        left_wrist = keypoint_dict.get(15, (0, 0, 0))
        right_wrist = keypoint_dict.get(16, (0, 0, 0))
        left_elbow = keypoint_dict.get(13, (0, 0, 0))
        right_elbow = keypoint_dict.get(14, (0, 0, 0))
        
        torso_height = distance(left_shoulder, left_hip)
        if torso_height < 0.01:
            torso_height = 0.01
        
        leg_len = (distance(left_hip, left_knee) + distance(right_hip, right_knee)) / 2
        torso_len = distance(left_shoulder, left_hip)
        
        shoulder_w = distance(left_shoulder, right_shoulder)
        hip_w = distance(left_hip, right_hip)
        
        left_arm_len = distance(left_shoulder, left_wrist)
        right_arm_len = distance(right_shoulder, right_wrist)
        avg_arm_len = (left_arm_len + right_arm_len) / 2
        
        left_leg_len_full = distance(left_hip, left_ankle)
        right_leg_len_full = distance(right_hip, right_ankle)
        avg_leg_len = (left_leg_len_full + right_leg_len_full) / 2
        
        left_elbow_angle = angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = angle(right_shoulder, right_elbow, right_wrist)
        left_knee_angle = angle(left_hip, left_knee, left_ankle)
        right_knee_angle = angle(right_hip, right_knee, right_ankle)
        
        body_ratio = leg_len / torso_height if torso_height > 0.01 else 0
        arm_body_ratio = avg_arm_len / torso_height if torso_height > 0.01 else 0
        leg_body_ratio = avg_leg_len / torso_height if torso_height > 0.01 else 0
        
        features.extend([
            body_ratio,
            torso_len,
            shoulder_w,
            hip_w,
            arm_body_ratio,
            leg_body_ratio,
        ])
        
        features.extend([
            left_elbow_angle,
            right_elbow_angle,
            left_knee_angle,
            right_knee_angle,
        ])
        
        nose_y = nose[1]
        ankle_y_avg = (left_ankle[1] + right_ankle[1]) / 2
        features.append(nose_y - ankle_y_avg)
        
        left_wrist_y = left_wrist[1]
        right_wrist_y = right_wrist[1]
        features.append(left_wrist_y - nose_y)
        features.append(right_wrist_y - nose_y)
        
        features.append(avg_arm_len / (avg_leg_len + 0.01))
        features.append(leg_len / (torso_len + 0.01))
        
        if len(features) >= 100:
            return features[:100]
        else:
            return features
            
    except Exception as e:
        return None

def process_images(image_folder, label, pose, max_images=500):
    """处理图片并提取特征"""
    features_list = []
    labels = []
    errors = []
    
    image_files = glob.glob(os.path.join(image_folder, "*.jpg"))
    print(f"📁 发现 {len(image_files)} 张图片: {image_folder}")
    
    if len(image_files) == 0:
        print(f"   ⚠️ 在 {image_folder} 中没有找到jpg文件")
        return [], []
    
    processed = 0
    detected = 0
    
    for i, image_path in enumerate(image_files):
        if processed >= max_images:
            break
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                continue
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, _ = img.shape
            
            results = pose.process(img_rgb)
            
            if results.pose_landmarks and len(results.pose_landmarks.landmark) > 10:
                features = extract_features(results.pose_landmarks.landmark, w, h)
                
                if features is not None and len(features) >= 100:
                    features_list.append(features)
                    labels.append(label)
                    detected += 1
                    processed += 1
                    
                    if detected % 20 == 0:
                        print(f"   ✅ 已处理 {detected} 张, 检测到 {detected} 个人体姿态")
            else:
                processed += 1
                
        except Exception as e:
            errors.append(str(e))
            processed += 1
    
    print(f"   📊 成功提取 {len(features_list)} 个样本")
    if errors:
        print(f"   ⚠️ 发生 {len(errors)} 个错误")
    
    return features_list, labels

def main():
    print("=" * 60)
    print("🏋️ 摔倒检测模型训练")
    print("=" * 60)
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        min_detection_confidence=0.25,
        min_tracking_confidence=0.25
    )
    
    fall_folder = "fall"
    normal_folder = "normal"
    
    print("\n📂 处理摔倒图片...")
    fall_features, fall_labels = process_images(fall_folder, 1, pose, max_images=500)
    
    print("\n📂 处理正常图片...")
    normal_features, normal_labels = process_images(normal_folder, 0, pose, max_images=500)
    
    pose.close()
    
    if len(fall_features) == 0 or len(normal_features) == 0:
        print("\n❌ 错误: 没有足够的训练数据")
        print(f"   摔倒样本: {len(fall_features)}")
        print(f"   正常样本: {len(normal_features)}")
        print("\n💡 可能的原因:")
        print("   1. 图片中的人体姿态不清晰")
        print("   2. MediaPipe检测参数太严格")
        print("   3. 图片格式或质量问题")
        return
    
    all_features = fall_features + normal_features
    all_labels = fall_labels + normal_labels
    
    X = np.array(all_features)
    y = np.array(all_labels)
    
    print(f"\n📊 数据集统计:")
    print(f"   总样本数: {len(X)}")
    print(f"   特征维度: {X.shape[1]}")
    print(f"   摔倒样本: {sum(y == 1)}")
    print(f"   正常样本: {sum(y == 0)}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n🔧 训练模型...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n📈 模型评估:")
    print(f"   准确率: {accuracy * 100:.2f}%")
    print("\n分类报告:")
    print(classification_report(y_test, y_pred, target_names=["正常", "摔倒"]))
    
    model_path = "fall_detection_model.pkl"
    joblib.dump(model, model_path)
    print(f"\n💾 模型已保存: {model_path}")
    
    print("\n" + "=" * 60)
    print("✅ 训练完成!")
    print("=" * 60)
    print("\n💡 下一步: 运行 'python fall_detection_realtime.py' 启动实时检测")

if __name__ == "__main__":
    main()
