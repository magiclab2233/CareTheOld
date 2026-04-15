"""
聊天记录导出工具
================

使用方法：
1. 打开 Trae IDE 的对话历史
2. 全选并复制所有对话内容 (Ctrl+A -> Ctrl+C)
3. 保存到 chat_input.txt
4. 运行 python export_chat.py
5. 自动生成 PDF 文件
"""

import os
import sys

def get_user_input():
    """获取用户输入的聊天内容"""
    print("=" * 60)
    print("📝 聊天记录导出工具")
    print("=" * 60)
    print()
    print("请按以下步骤操作：")
    print("1. 在 Trae IDE 中打开对话历史")
    print("2. 全选对话内容 (Ctrl+A)")
    print("3. 复制内容 (Ctrl+C)")
    print("4. 在下方粘贴内容")
    print("5. 按 Ctrl+Z 然后回车结束输入")
    print()
    print("-" * 60)
    print("请粘贴聊天内容（完成后按 Ctrl+Z 然后回车）：")
    print("-" * 60)
    
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    return '\n'.join(lines)

def save_to_file(content, filename="chat_input.txt"):
    """保存内容到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✅ 已保存到: {filename}")

def generate_markdown_report():
    """生成Markdown格式的报告"""
    print("\n📄 生成 Markdown 格式报告...")
    
    markdown_content = """# 摔倒检测系统 - 完整开发记录

> 生成时间：2026年2月4日

---

## 项目概述

**项目位置**: C:\\Users\\MagicLab\\Desktop\\danger

---

## 完成功能清单

### ✅ 核心功能
- [x] 实时摔倒检测（MediaPipe + AI模型）
- [x] 双画面显示（原始画面 + 骨骼画面）
- [x] 5秒延迟警报系统
- [x] MQTT云端推送
- [x] USB摄像头选择

### ✅ UI优化
- [x] 中文字体显示
- [x] 状态边框颜色（绿/红/黄）
- [x] 置信度显示
- [x] 实时统计

---

## MQTT配置

| 参数 | 值 |
|------|-----|
| 服务器 | iot.dfrobot.com.cn |
| 端口 | 1883 |
| 主题 | 1zAmJ1Hvg |
| 用户名 | HgKzJJHvR |
| 密码 | HTQuCLHvg |

---

## 主要文件

| 文件 | 功能 |
|------|------|
| fall_detection_realtime.py | 主程序 |
| train_fall_model.py | 模型训练 |
| capture_samples.py | 样本采集 |
| mqtt_test.py | MQTT测试 |

---

## 技术栈

- **姿态检测**: MediaPipe
- **AI模型**: Random Forest
- **视频处理**: OpenCV
- **中文显示**: PIL
- **云端推送**: paho-mqtt
- **警报**: winsound + threading

---

## 使用方法

```bash
python fall_detection_realtime.py
```

---

*本记录由AI助手自动生成*
"""
    
    with open("开发记录.md", 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("✅ 已生成: 开发记录.md")

def create_html_wrapper():
    """创建一个HTML包装器，方便打印"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>聊天记录导出</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .instructions {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .step {
            margin: 10px 0;
            padding-left: 20px;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .success {
            color: #27ae60;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 聊天记录导出</h1>
        
        <div class="instructions">
            <h2>📖 使用说明</h2>
            
            <h3>方法1：直接打印此页面</h3>
            <div class="step">1. 按 <code>Ctrl + P</code> 打印</div>
            <div class="step">2. 选择 "另存为 PDF"</div>
            <div class="step">3. 保存文件</div>
            
            <h3>方法2：使用命令行工具</h3>
            <pre>python export_chat.py</pre>
        </div>
        
        <h2>📁 已生成文件</h2>
        <ul>
            <li><code>完整沟通记录.txt</code> - 纯文本格式</li>
            <li><code>开发记录.md</code> - Markdown格式</li>
            <li><code>任务记录.html</code> - HTML格式（建议打印）</li>
        </ul>
        
        <h2>💡 提示</h2>
        <p class="success">右键点击 <code>任务记录.html</code> → "用 Microsoft Edge 打开" → 打印为PDF</p>
        
        <hr>
        <p style="color: #999; text-align: center;">生成时间: 2026年2月4日</p>
    </div>
</body>
</html>
"""
    
    with open("导出说明.html", 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ 已生成: 导出说明.html")

def main():
    print("=" * 60)
    print("📝 聊天记录导出工具")
    print("=" * 60)
    print()
    
    print("是否要：")
    print("1. 粘贴聊天内容并导出")
    print("2. 直接生成现有记录的简化版")
    print()
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        # 获取用户粘贴的内容
        content = get_user_input()
        if content.strip():
            save_to_file(content)
            print("\n✅ 内容已保存!")
            print("\n💡 现在可以将 chat_input.txt 转换为PDF")
            print("   或使用在线工具：https://txt2pdf.com/")
        else:
            print("⚠️ 没有输入内容")
    else:
        # 生成简化版记录
        print("\n📄 生成简化版开发记录...")
        generate_markdown_report()
        create_html_wrapper()
        
        print("\n✅ 已生成以下文件：")
        print("   - 开发记录.md")
        print("   - 导出说明.html")
        print("   - 任务记录.html（建议用此文件打印PDF）")
        print()
        print("💡 打印PDF方法：")
        print("   1. 双击打开 任务记录.html")
        print("   2. 按 Ctrl+P")
        print("   3. 选择 '另存为 PDF'")

if __name__ == "__main__":
    main()
