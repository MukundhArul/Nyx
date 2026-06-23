import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add QCursor import
if "QCursor" not in content:
    content = content.replace("from PyQt6.QtGui import QPainter", "from PyQt6.QtGui import QPainter, QCursor")

# 2. Replace WWWB and BWWW with EEEE in MATRIX_FRAMES
lines = content.split('\n')
in_matrix = False
for i, line in enumerate(lines):
    if "MATRIX_FRAMES = {" in line:
        in_matrix = True
    if in_matrix and "}" in line and "    ]" not in line:
        pass # End of matrix, but let's just do it for all lines to be safe
    
    if in_matrix:
        if "WWWB" in line or "BWWW" in line:
            lines[i] = line.replace("WWWB", "EEEE").replace("BWWW", "EEEE")

content = '\n'.join(lines)

# 3. Rewrite paintEvent drawing block
old_draw_block = """            painter.setPen(Qt.PenStyle.NoPen)
            for r, row_str in enumerate(frame_data):
                for c, char in enumerate(row_str):
                    if char in MATRIX_COLORS:
                        painter.setBrush(MATRIX_COLORS[char])
                        # Subtract 1 from size to create the gap (scanline effect!)
                        px_x = int(dest_x + c * pixel_size)
                        px_y = int(dest_y + r * pixel_size)
                        painter.drawRect(px_x, px_y, pixel_size - 1, pixel_size - 1)"""

new_draw_block = """            left_eye_pixels = []
            right_eye_pixels = []
            
            painter.setPen(Qt.PenStyle.NoPen)
            for r, row_str in enumerate(frame_data):
                for c, char in enumerate(row_str):
                    color = None
                    if char == 'E':
                        color = MATRIX_COLORS['W']
                        if c < 10:
                            left_eye_pixels.append((c, r))
                        else:
                            right_eye_pixels.append((c, r))
                    elif char in MATRIX_COLORS:
                        color = MATRIX_COLORS[char]
                        
                    if color:
                        painter.setBrush(color)
                        px_x = int(dest_x + c * pixel_size)
                        px_y = int(dest_y + r * pixel_size)
                        painter.drawRect(px_x, px_y, pixel_size - 1, pixel_size - 1)
                        
            # Draw Dynamic Pupils
            if left_eye_pixels and right_eye_pixels and anim_name != "SLEEPING":
                import math
                mouse_pos = QCursor.pos()
                cat_global = self.mapToGlobal(QPoint(int(cx), int(cy)))
                
                dx = mouse_pos.x() - cat_global.x()
                dy = mouse_pos.y() - cat_global.y()
                
                dist = math.hypot(dx, dy)
                max_off_x = pixel_size * 1.5
                max_off_y = pixel_size * 0.8
                
                if dist > 0:
                    off_x = (dx / dist) * max_off_x
                    off_y = (dy / dist) * max_off_y
                else:
                    off_x, off_y = 0, 0
                    
                painter.setBrush(MATRIX_COLORS['B'])
                
                for eye_pixels in [left_eye_pixels, right_eye_pixels]:
                    avg_c = sum(p[0] for p in eye_pixels) / len(eye_pixels)
                    avg_r = sum(p[1] for p in eye_pixels) / len(eye_pixels)
                    
                    pupil_cx = dest_x + avg_c * pixel_size + off_x + (pixel_size / 2)
                    pupil_cy = dest_y + avg_r * pixel_size + off_y + (pixel_size / 2)
                    
                    pupil_w = pixel_size * 1.5
                    pupil_h = pixel_size * 2.0
                    
                    painter.drawRect(int(pupil_cx - pupil_w/2), int(pupil_cy - pupil_h/2), int(pupil_w), int(pupil_h))"""

content = content.replace(old_draw_block, new_draw_block)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Eye tracking logic injected successfully!")
