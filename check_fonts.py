import os

fonts_dir = "C:/Windows/Fonts"
if os.path.exists(fonts_dir):
    fonts = os.listdir(fonts_dir)
    chinese_fonts = [f for f in fonts if 'sim' in f.lower() or 'msy' in f.lower()]
    print("中文字体:", chinese_fonts[:10] if chinese_fonts else "未找到")
else:
    print("字体目录不存在")
