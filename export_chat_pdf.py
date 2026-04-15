"""
导出聊天记录或文档为PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import sys

def export_to_pdf(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    margin = 20 * mm
    line_height = 14
    y = height - margin
    
    try:
        c.setFont("SimSun", 12)
    except:
        c.setFont("Helvetica", 12)
    
    lines = content.split('\n')
    
    for line in lines:
        if not line.strip():
            y -= line_height // 2
            continue
        
        if y < margin + line_height:
            c.showPage()
            try:
                c.setFont("SimSun", 12)
            except:
                c.setFont("Helvetica", 12)
            y = height - margin
        
        wrapped_lines = textwrap.wrap(line, width=95)
        for wrapped in wrapped_lines:
            if y < margin + line_height:
                c.showPage()
                try:
                    c.setFont("SimSun", 12)
                except:
                    c.setFont("Helvetica", 12)
                y = height - margin
            
            c.drawString(margin, y, wrapped)
            y -= line_height
    
    c.save()
    print(f"✅ 已导出: {output_file}")

if __name__ == "__main__":
    print("=" * 50)
    print("📄 导出PDF工具")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if not input_file.endswith('.txt'):
            input_file += '.txt'
    else:
        input_file = "任务记录.txt"
    
    output_file = input_file.replace('.txt', '.pdf')
    
    try:
        export_to_pdf(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ 未找到文件: {input_file}")
        print()
        print("可用文件：")
        import os
        for f in os.listdir('.'):
            if f.endswith('.txt'):
                print(f"  - {f}")
