import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Change 1: DEFAULT_SETTINGS
content = content.replace(
    '"matrix_color_b": 81',
    '"matrix_color_b": 81,\n    "wear_sunglasses": False'
)

# Change 2: Settings UI
target_ui = """        matrix_layout.addWidget(self.rgb_group)"""
new_ui = """        matrix_layout.addWidget(self.rgb_group)
        
        self.sunglasses_cb = QCheckBox("Wear Sunglasses")
        self.sunglasses_cb.setChecked(self.settings.get("wear_sunglasses", False))
        matrix_layout.addWidget(self.sunglasses_cb)"""
content = content.replace(target_ui, new_ui)

# Change 3: Save settings
target_save = """        self.settings["matrix_color_g"] = self.g_slider.value()
        self.settings["matrix_color_b"] = self.b_slider.value()"""
new_save = """        self.settings["matrix_color_g"] = self.g_slider.value()
        self.settings["matrix_color_b"] = self.b_slider.value()
        self.settings["wear_sunglasses"] = self.sunglasses_cb.isChecked()"""
content = content.replace(target_save, new_save)

# Change 4: Sunglasses
target_sunglasses = """                    pupil_h = pixel_size * 2.0
                    
                    painter.drawRect(int(pupil_cx - pupil_w/2), int(pupil_cy - pupil_h/2), int(pupil_w), int(pupil_h))"""

new_sunglasses = """                    pupil_h = pixel_size * 2.0
                    
                    painter.drawRect(int(pupil_cx - pupil_w/2), int(pupil_cy - pupil_h/2), int(pupil_w), int(pupil_h))
                    
            if self.settings.get("wear_sunglasses", False) and anim_name != "SLEEPING":
                if left_eye_pixels and right_eye_pixels:
                    min_r = min(p[1] for p in left_eye_pixels + right_eye_pixels)
                    min_cl = min(p[0] for p in left_eye_pixels)
                    min_cr = min(p[0] for p in right_eye_pixels)
                    
                    painter.setBrush(Qt.GlobalColor.black)
                    painter.drawRect(int(dest_x + (min_cl-1)*pixel_size), int(dest_y + min_r*pixel_size), int(5*pixel_size), int(2*pixel_size))
                    painter.drawRect(int(dest_x + (min_cr-1)*pixel_size), int(dest_y + min_r*pixel_size), int(5*pixel_size), int(2*pixel_size))
                    painter.drawRect(int(dest_x + (min_cl+4)*pixel_size), int(dest_y + min_r*pixel_size), int((min_cr - min_cl - 4)*pixel_size), int(pixel_size))
                    
                    painter.setBrush(Qt.GlobalColor.white)
                    painter.drawRect(int(dest_x + min_cl*pixel_size), int(dest_y + min_r*pixel_size), int(pixel_size), int(pixel_size))
                    painter.drawRect(int(dest_x + min_cr*pixel_size), int(dest_y + min_r*pixel_size), int(pixel_size), int(pixel_size))"""

content = content.replace(target_sunglasses, new_sunglasses)

# Change 5: Speech bubbles
target_bubble = """        if self.pinned_message:
            msg_rect = painter.fontMetrics().boundingRect(self.pinned_message)
            bubble_width = msg_rect.width() + 20
            bubble_height = msg_rect.height() + 15
            bubble_x = max(5, cx - bubble_width // 2)
            bubble_y = max(5, cy - 30 + y_offset - bubble_height - 15)
            
            bubble_path = QPainterPath()
            bubble_path.addRoundedRect(float(bubble_x), float(bubble_y), float(bubble_width), float(bubble_height), 10.0, 10.0)
            
            tail_path = QPainterPath()
            tail_path.moveTo(float(cx), float(cy - 25 + y_offset))
            tail_path.lineTo(float(cx - 8), float(bubble_y + bubble_height))
            tail_path.lineTo(float(cx + 8), float(bubble_y + bubble_height))
            
            final_path = bubble_path.united(tail_path)
            
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawPath(final_path)
            
            painter.setPen(QColor(50, 50, 50))
            painter.drawText(int(bubble_x + 10), int(bubble_y + msg_rect.height() + 2), self.pinned_message)"""

new_bubble = """        if self.pinned_message:
            if self.settings.get("matrix_mode", False):
                font = QFont("Courier", 12, QFont.Weight.Bold)
                painter.setFont(font)
                msg_rect = painter.fontMetrics().boundingRect(self.pinned_message)
                bubble_w = msg_rect.width() + 20
                bubble_h = msg_rect.height() + 15
                
                cat_height = 16 * self.settings.get("scale_factor", 5.0)
                dest_y = cy - cat_height / 2
                
                bx = max(5, cx - bubble_w / 2)
                by = max(5, dest_y - bubble_h - 15)
                
                painter.setBrush(Qt.GlobalColor.black)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(int(bx - 4), int(by - 4), int(bubble_w + 8), int(bubble_h + 8))
                
                painter.setBrush(Qt.GlobalColor.white)
                painter.drawRect(int(bx), int(by), int(bubble_w), int(bubble_h))
                
                painter.setBrush(Qt.GlobalColor.black)
                painter.drawRect(int(cx - 5), int(by + bubble_h), 16, 6)
                painter.drawRect(int(cx - 1), int(by + bubble_h + 6), 12, 6)
                painter.drawRect(int(cx + 3), int(by + bubble_h + 12), 8, 6)
                
                painter.setBrush(Qt.GlobalColor.white)
                painter.drawRect(int(cx - 1), int(by + bubble_h), 8, 6)
                painter.drawRect(int(cx + 3), int(by + bubble_h + 6), 4, 6)
                
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(int(bx + 10), int(by + msg_rect.height() + 2), self.pinned_message)
            else:
                msg_rect = painter.fontMetrics().boundingRect(self.pinned_message)
                bubble_width = msg_rect.width() + 20
                bubble_height = msg_rect.height() + 15
                bubble_x = max(5, cx - bubble_width // 2)
                bubble_y = max(5, cy - 30 + y_offset - bubble_height - 15)
                
                bubble_path = QPainterPath()
                bubble_path.addRoundedRect(float(bubble_x), float(bubble_y), float(bubble_width), float(bubble_height), 10.0, 10.0)
                
                tail_path = QPainterPath()
                tail_path.moveTo(float(cx), float(cy - 25 + y_offset))
                tail_path.lineTo(float(cx - 8), float(bubble_y + bubble_height))
                tail_path.lineTo(float(cx + 8), float(bubble_y + bubble_height))
                
                final_path = bubble_path.united(tail_path)
                
                painter.setPen(QPen(QColor(200, 200, 200), 2))
                painter.setBrush(QColor(255, 255, 255))
                painter.drawPath(final_path)
                
                painter.setPen(QColor(50, 50, 50))
                painter.drawText(int(bubble_x + 10), int(bubble_y + msg_rect.height() + 2), self.pinned_message)"""

content = content.replace(target_bubble, new_bubble)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Sunglasses and speech bubbles injected successfully!")
