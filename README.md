# Fall Detection Realtime

基于MediaPipe姿态估计和RandomForest机器学习模型的实时摔倒检测系统。

## 最新更新 (2026-04-15)
- 项目已正式迁移至 GitHub 仓库并重命名主分支为 `main`。
- 完整包含训练图片数据 (`fall/` 和 `normal/` 目录)。
- 初始化项目结构并完成首次提交。

## 项目概述

本系统通过摄像头实时捕获人体姿态数据，利用MediaPipe检测33个人体关键点，提取100维姿态特征，通过预训练的RandomForest模型判断是否发生摔倒。检测到摔倒后，系统会发出声光警报并通过MQTT推送报警消息。

## 数据来源

训练数据主要来自 **LE2I Fall Detection Dataset**（法国里昂大学发布的公开摔倒检测数据集），包含多种场景下的日常活动与摔倒视频序列。在此基础上，项目补充采集了真实应用场景的样本数据，以提升模型在实际部署环境中的适应性。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        系统架构图                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   摄像头      │───▶│  OpenCV      │───▶│  MediaPipe   │     │
│   │  (VideoCap)  │    │  图像预处理   │    │  姿态估计     │     │
│   └──────────────┘    └──────────────┘    └──────┬───────┘     │
│                                                   │              │
│                                                   ▼              │
│                                          ┌──────────────┐       │
│                                          │  33个关键点   │       │
│                                          │  (x,y,vis)   │       │
│                                          └──────┬───────┘       │
│                                                   │              │
│                                                   ▼              │
│                                          ┌──────────────┐       │
│                                          │  特征提取     │       │
│                                          │  (100维)     │       │
│                                          └──────┬───────┘       │
│                                                   │              │
│                                                   ▼              │
│                                          ┌──────────────┐       │
│                                          │ RandomForest  │       │
│                                          │   分类器      │       │
│                                          └──────┬───────┘       │
│                                                   │              │
│                              ┌────────────────────┼────────────┐ │
│                              ▼                    ▼            ▼ │
│                     ┌──────────────┐    ┌──────────────┐ ┌─────┐ │
│                     │   声光警报    │    │  MQTT推送    │ │GUI  │ │
│                     │ (winsound)   │    │ (paho-mqtt)  │ │显示 │ │
│                     └──────────────┘    └──────────────┘ └─────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 项目文件说明

### 核心脚本

| 文件 | 说明 |
|------|------|
| `fall_detection_realtime.py` | **主程序** - 实时摔倒检测，包含GUI界面、姿态可视化、报警逻辑 |
| `train_fall_model_v2.py` | **训练脚本** - 使用RandomForest训练摔倒检测模型 |
| `capture_samples.py` | **采样脚本** - 采集训练样本图片（摔倒/正常姿态） |

### 辅助脚本

| 文件 | 说明 |
|------|------|
| `pose_estimation.py` | 基础姿态估计演示，不含检测逻辑 |
| `mqtt_test.py` | MQTT连接测试工具 |
| `check_fonts.py` | 字体可用性检查 |

### 数据目录

| 目录 | 说明 |
|------|------|
| `fall/` | 摔倒样本图片目录 |
| `normal/` | 正常姿态样本目录（训练脚本自动使用） |

### 生成文件

| 文件 | 说明 |
|------|------|
| `fall_detection_model.pkl` | 训练好的模型文件 |

## 算法原理

### 特征提取 (100维)

```
特征构成:
├── 33个关键点 × 3维 (x, y, visibility) = 99维
└── 鼻相对于脚踝的Y坐标差 = 1维
    ───────────────
    总计: 100维
```

**关键点映射** (MediaPipe Pose):
```
0: 鼻子          11: 左肩        23: 左髋
1: 左眼外       12: 右肩        24: 右髋
2: 左眼内       13: 左肘        25: 左膝
3: 右眼内       14: 右肘        26: 右膝
4: 右眼外       15: 左手腕      27: 左踝
5: 左耳         16: 右手腕      28: 右踝
6: 右耳         ...
```

### 分类判定逻辑

```python
if prediction == 1:  # 摔倒
    if fall_duration >= 5秒:
        触发警报 (声 + MQTT)
    else:
        显示警告
else:  # 正常
    重置计数器
```

## 各脚本详解

### 1. fall_detection_realtime.py

**主程序**，实现完整的实时检测流程：

```
功能模块:
├── GUI摄像头选择界面 (select_camera_gui)
│   └── 鼠标交互选择摄像头，带悬停效果
├── MQTT连接 (mqtt_connect / mqtt_publish)
│   └── 支持IoT平台推送报警消息
├── 中文字体渲染 (put_chinese_text)
│   └── 遍历字体目录加载中文支持
├── 按钮绘制 (draw_button)
│   └── GUI按钮，带悬停高亮
├── 特征提取 (extract_features)
│   └── 100维姿态特征计算
├── 警报声音 (play_alarm_sound)
│   └── 多线程Beep警报
└── 主循环 (main)
    ├── 摄像头读取
    ├── 姿态检测
    ├── 骨骼可视化
    ├── 分类预测
    └── 状态显示/报警
```

**依赖**: opencv-python, mediapipe, numpy, Pillow, paho-mqtt, joblib, winsound

### 2. train_fall_model_v2.py

**训练脚本**，从图片数据集训练RandomForest模型：

```
训练流程:
├── 数据加载 (process_folder)
│   ├── 遍历fall/和normal/目录的jpg图片
│   └── 调用MediaPipe提取关键点
├── 特征提取 (extract_features)
│   ├── 33个关键点坐标 (99维)
│   ├── 身体比例: 腿长/身高、肩宽/身高等
│   ├── 关节角度: 肘关节、膝关节、肩关节
│   └── 身体倾斜角度
├── 模型训练
│   └── RandomForestClassifier(n_estimators=100)
└── 模型保存
    └── joblib.dump → fall_detection_model.pkl
```

**数据集要求**:
- `fall/` 目录存放摔倒样本图片
- `normal/` 目录存放正常姿态图片
- 支持jpg格式

**输出**: 准确率、分类报告、模型文件

### 3. capture_samples.py

**样本采集工具**，用于采集训练数据：

```
功能:
├── 自动检测可用摄像头
├── 设置摄像头分辨率
├── 实时姿态检测显示
├── 按's'键保存当前帧到fall/目录
└── 显示已保存图片计数
```

**使用方式**:
```bash
python capture_samples.py
# 按 s 键拍照保存
# 按 q 键退出
```

### 4. pose_estimation.py

**基础演示**，仅展示MediaPipe姿态估计效果：

```
功能:
├── 调用摄像头
├── MediaPipe姿态检测
├── 绘制33个关键点和连接线
└── 显示关键点编号
```

### 5. mqtt_test.py

**MQTT调试工具**，测试IoT连接：

```
配置:
- Broker: iot.dfrobot.com.cn
- Port: 1883
- Topic: 1zAmJ1Hvg
- Username: HgKzJJHvR
```

## 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 采集训练样本

```bash
python capture_samples.py
```

### 3. 训练模型

```bash
python train_fall_model_v2.py
```

### 4. 运行实时检测

```bash
python fall_detection_realtime.py
```

### 5. MQTT测试（可选）

```bash
python mqtt_test.py
```

## 配置说明

### MQTT配置 (fall_detection_realtime.py)

```python
MQTT_CONFIG = {
    "broker": "iot.dfrobot.com.cn",
    "port": 1883,
    "topic": "your_topic",
    "username": "your_username",
    "password": "your_password"
}
```

### 报警阈值

```python
# 摔倒持续超过5秒才触发警报
if fall_duration >= 5 and not alarm_triggered:
    alarm_triggered = True
    mqtt_publish(MQTT_TOPIC, "Fall")
    play_alarm_sound()
```

## 依赖列表

| 包 | 版本 | 说明 |
|----|------|------|
| opencv-python | >=4.8.0 | 图像处理、摄像头捕获、GUI |
| mediapipe | >=0.10.0 | 人体姿态估计、33点检测 |
| numpy | >=1.24.0 | 数值计算、数组操作 |
| Pillow | >=9.0.0 | 中文字体渲染 |
| scikit-learn | >=1.0.0 | RandomForest分类器 |
| joblib | >=1.0.0 | 模型序列化 |
| paho-mqtt | >=1.6.1 | MQTT协议客户端 |

## 系统要求

- **操作系统**: Windows
- **Python**: 3.8+
- **硬件**: 支持OpenCV的摄像头
- **字体**: 系统字体目录中存在中文支持字体 (simhei.ttf, msyh.ttc, simsun.ttc)

## 技术细节

### 关键点检测置信度过滤

```python
if sum(kp[2] for kp in keypoints.values()) < 10:
    return None  # 过滤低置信度检测
```

### 身体比例特征

```python
features.extend([
    leg_length / body_height,      # 腿长/身高
    torso_length / body_height,    # 躯干/身高
    shoulder_width / body_height,  # 肩宽/身高
    hip_width / body_height,       # 髋宽/身高
    avg_arm_length / body_height,  # 臂长/身高
    avg_leg_length / body_height,  # 腿长/身高
])
```

### 关节角度计算

```python
def angle(p1, p2, p3):
    v1 = np.array([p1[0]-p2[0], p1[1]-p2[1]])
    v2 = np.array([p3[0]-p2[0], p3[1]-p2[1]])
    cos = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2))
    return arccos(cos) * 180 / pi
```

## 常见问题

**Q: 摄像头无法打开?**
- 检查摄像头是否被其他程序占用
- 尝试更换摄像头索引 (0, 1, 2...)

**Q: 模型文件不存在?**
- 确保已运行 `train_fall_model_v2.py` 生成模型

**Q: 中文显示乱码?**
- 确保系统中安装了中文字体 (simhei.ttf, msyh.ttc等)

**Q: MQTT推送失败?**
- 检查网络连接
- 确认MQTT配置信息正确
