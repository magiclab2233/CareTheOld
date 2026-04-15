import cv2
import mediapipe as mp
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import glob

def extract_features(landmarks):
    if landmarks is None or len(landmarks) == 0:
        return None
    
    try:
        features = []
        keypoints = [(lm.x, lm.y, lm.visibility) for lm in landmarks]
        
        for i in range(len(keypoints)):
            x, y, vis = keypoints[i]
            features.extend([x, y, vis])
        
        def dist(p1, p2):
            return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        
        def ang(p1, p2, p3):
            v1 = np.array([p1[0]-p2[0], p1[1]-p2[1]])
            v2 = np.array([p3[0]-p2[0], p3[1]-p2[1]])
            cos = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2) + 1e-6)
            cos = max(-1, min(1, cos))
            return np.arccos(cos) * 180 / np.pi
        
        kp = {i: kp for i, kp in enumerate(keypoints)}
        
        nose = kp.get(0, (0,0,0))
        ls, rs = kp.get(11, (0,0,0)), kp.get(12, (0,0,0))
        lh, rh = kp.get(23, (0,0,0)), kp.get(24, (0,0,0))
        lk, rk = kp.get(25, (0,0,0)), kp.get(26, (0,0,0))
        la, ra = kp.get(27, (0,0,0)), kp.get(28, (0,0,0))
        lw, rw = kp.get(15, (0,0,0)), kp.get(16, (0,0,0))
        le, re = kp.get(13, (0,0,0)), kp.get(14, (0,0,0))
        
        torso = dist(ls, lh)
        if torso < 0.01: torso = 0.01
        
        leg = (dist(lh, lk) + dist(rh, rk)) / 2
        shoulder_w = dist(ls, rs)
        hip_w = dist(lh, rh)
        arm = (dist(ls, lw) + dist(rs, rw)) / 2
        full_leg = (dist(lh, la) + dist(rh, ra)) / 2
        
        features.extend([
            leg/torso if torso > 0.01 else 0,
            torso,
            shoulder_w,
            hip_w,
            arm/torso if torso > 0.01 else 0,
            full_leg/torso if torso > 0.01 else 0,
        ])
        
        features.extend([
            ang(ls, le, lw),
            ang(rs, re, rw),
            ang(lh, lk, la),
            ang(rh, rk, ra),
        ])
        
        features.append(nose[1] - (la[1]+ra[1])/2)
        features.append(lw[1] - nose[1])
        features.append(rw[1] - nose[1])
        features.append(arm/(full_leg+0.01))
        features.append(leg/(torso+0.01))
        
        return features[:100]
    except:
        return None

def process_folder(folder, label, pose, max_samples=500):
    features, labels = [], []
    files = glob.glob(f"{folder}/*.jpg")
    print(f"📁 {folder}: 发现 {len(files)} 张图片")
    
    count = 0
    for f in files:
        if count >= max_samples:
            break
        try:
            img = cv2.imread(f)
            if img is None: continue
            
            results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            
            if results.pose_landmarks and len(results.pose_landmarks.landmark) > 5:
                feat = extract_features(results.pose_landmarks.landmark)
                if feat and len(feat) >= 100:
                    features.append(feat)
                    labels.append(label)
                    count += 1
        except:
            continue
    
    print(f"   ✅ 成功提取 {len(features)} 个样本")
    return features, labels

def main():
    print("="*60)
    print("🏋️ 摔倒检测模型训练")
    print("="*60)
    
    pose = mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=0,
        min_detection_confidence=0.15,
        min_tracking_confidence=0.15
    )
    
    fall_feat, fall_lab = process_folder("fall", 1, pose)
    norm_feat, norm_lab = process_folder("normal", 0, pose)
    pose.close()
    
    if not fall_feat or not norm_feat:
        print("\n❌ 数据不足!")
        print(f"   fall: {len(fall_feat)}, normal: {len(norm_feat)}")
        return
    
    X, y = np.array(fall_feat + norm_feat), np.array(fall_lab + norm_lab)
    print(f"\n📊 数据集: {len(X)} 样本, {X.shape[1]} 特征")
    print(f"   摔倒: {sum(y==1)}, 正常: {sum(y==0)}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    
    print("\n🔧 训练模型...")
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"\n📈 准确率: {acc*100:.1f}%")
    print(classification_report(y_test, model.predict(X_test), target_names=["正常","摔倒"]))
    
    joblib.dump(model, "fall_detection_model.pkl")
    print(f"\n💾 模型已保存: fall_detection_model.pkl")
    print("\n✅ 完成! 运行 'python fall_detection_realtime.py' 启动实时检测")

if __name__ == "__main__":
    main()
