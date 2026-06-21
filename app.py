import sys
import time
import math
import os
import threading
import winsound
from PyQt6.QtWidgets import QApplication, QWidget, QMenu, QInputDialog, QSystemTrayIcon
from PyQt6.QtGui import QPainter, QColor, QAction, QPen, QFont, QPainterPath, QPixmap
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread, QRect
from pynput import mouse, keyboard
import pygetwindow as gw

class MonitorThread(QThread):
    input_activity = pyqtSignal()
    typing_activity = pyqtSignal()
    active_window = pyqtSignal(str)

    def run(self):
        def on_move(x, y):
            self.input_activity.emit()
        
        def on_click(x, y, button, pressed):
            self.input_activity.emit()
            
        def on_press(key):
            self.input_activity.emit()
            self.typing_activity.emit()
        
        mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
        keyboard_listener = keyboard.Listener(on_press=on_press)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        while True:
            try:
                window = gw.getActiveWindow()
                title = window.title if window else ""
                self.active_window.emit(title.lower())
            except Exception:
                pass
            time.sleep(1)

class PetWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # State variables
        self.state = "IDLE"
        self.idle_time = 0
        self.SLEEP_THRESHOLD = 30 # Sleep after 30s of inactivity
        
        self.is_dragging = False
        self.oldPos = self.pos()
        self.tick_count = 0
        
        self.active_app_state = ""
        self.is_typing = False
        self.typing_timer = 0
        
        # Phase 4 Productivity states
        self.pinned_message = ""
        self.pomo_active = False
        self.pomo_seconds = 0
        self.stretch_timer = 0
        self.STRETCH_INTERVAL = 30 * 60 # 30 minutes in seconds
        
        # Phase 5 Sprite states
        self.setup_sprites()
        
        self.initUI()
        
        # Animation loop (30 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(33)
        
        # One second logic timer
        self.logic_timer = QTimer(self)
        self.logic_timer.timeout.connect(self.update_logic)
        self.logic_timer.start(1000)
        
        # Start monitoring thread
        self.monitor = MonitorThread()
        self.monitor.input_activity.connect(self.on_input_activity)
        self.monitor.typing_activity.connect(self.on_typing_activity)
        self.monitor.active_window.connect(self.on_active_window)
        self.monitor.start()

    def setup_sprites(self):
        asset_path = os.path.join(os.path.dirname(__file__), "assets", "Cat Sprite Sheet.png")
        self.sprite_sheet = QPixmap(asset_path)
        
        alarm_path = os.path.join(os.path.dirname(__file__), "assets", "updated clock.png")
        full_pixmap = QPixmap(alarm_path)
        # Dynamically crop the clock out of the 1920x1080 canvas
        self.alarm_pixmap = full_pixmap.copy(470, 158, 997, 725)
        
        self.frame_width = 32
        self.frame_height = 32
        self.scale_factor = 5 # 32x32 scaled to 160x160
        
        self.animations = {
            "IDLE": [(c, 0) for c in range(4)],          # Row 0
            "SLEEPING": [(c, 6) for c in range(4)],      # Row 6
            "DRAGGED": [(c, 1) for c in range(4)],       # Row 1
            "TYPING": [(c, 7) for c in range(6)],        # Row 7
            "VIBING": [(c, 8) for c in range(7)],        # Row 8
            "WATCHING": [(c, 9) for c in range(8)],      # Row 9
            "SCROLLING": [(c, 4) for c in range(8)]      # Row 4
        }
        self.current_frame_index = 0

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 300) # Increased size significantly to prevent cutting off
        self.setupTray()

    def setupTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Actions
        show_action = QAction("Show", self)
        set_pin_action = QAction("Set Pinned Message", self)
        clear_pin_action = QAction("Clear Pinned Message", self)
        toggle_alarm_action = QAction("Toggle Alarm Timer", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        set_pin_action.triggered.connect(self.prompt_pinned_message)
        clear_pin_action.triggered.connect(self.clear_pinned_message)
        toggle_alarm_action.triggered.connect(self.toggle_alarm)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        # Menu
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(set_pin_action)
        tray_menu.addAction(clear_pin_action)
        tray_menu.addSeparator()
        tray_menu.addAction(toggle_alarm_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # --- Productivity Prompts ---
    def prompt_pinned_message(self):
        text, ok = QInputDialog.getText(self, "Pinned Message", "Enter your reminder:")
        if ok and text:
            self.pinned_message = text

    def clear_pinned_message(self):
        self.pinned_message = ""

    def toggle_alarm(self):
        if self.pomo_active:
            self.pomo_active = False
        else:
            mins, ok = QInputDialog.getInt(self, "Set Alarm", "Enter minutes for the alarm:", 1, 1, 120)
            if ok:
                self.pomo_active = True
                self.pomo_seconds = mins * 60

    def play_alarm_sound(self):
        def beep_thread():
            for _ in range(5): # beep 5 times
                winsound.Beep(800, 200)
                winsound.Beep(1200, 200)
        threading.Thread(target=beep_thread, daemon=True).start()

    # --- Signals ---
    def on_input_activity(self):
        self.idle_time = 0
        if self.state == "SLEEPING":
            self.state = "IDLE"
            
    def on_typing_activity(self):
        self.is_typing = True
        self.typing_timer = 10 # frames to show typing animation
        
    def on_active_window(self, title):
        if "spotify" in title:
            self.active_app_state = "VIBING"
        elif "youtube" in title:
            self.active_app_state = "WATCHING"
        elif "instagram" in title or "twitter" in title or "x" in title:
            self.active_app_state = "SCROLLING"
        else:
            self.active_app_state = ""

    def get_current_animation_name(self):
        if self.state == "SLEEPING": return "SLEEPING"
        if self.state == "DRAGGED": return "DRAGGED"
        if self.is_typing: return "TYPING"
        if self.active_app_state != "": return self.active_app_state
        return "IDLE"

    # --- Logic Updates ---
    def update_logic(self):
        if not self.is_dragging:
            self.idle_time += 1
            if self.idle_time > self.SLEEP_THRESHOLD:
                self.state = "SLEEPING"
                
        # Productivity Logic
        if self.pomo_active:
            if self.pomo_seconds > 0:
                self.pomo_seconds -= 1
            else:
                self.pomo_active = False
                self.pinned_message = "⏰ ALARM! ⏰"
                self.play_alarm_sound()
                
        self.stretch_timer += 1
        if self.stretch_timer >= self.STRETCH_INTERVAL:
            self.stretch_timer = 0
            self.pinned_message = "Time to Stretch!"

    def update_animation(self):
        self.tick_count += 1
        
        # Advance sprite frame every 3 ticks (approx 10 FPS)
        if self.tick_count % 3 == 0:
            anim_name = self.get_current_animation_name()
            anim_list = self.animations.get(anim_name, self.animations["IDLE"])
            self.current_frame_index = (self.current_frame_index + 1) % len(anim_list)

        if self.typing_timer > 0:
            self.typing_timer -= 1
            if self.typing_timer <= 0:
                self.is_typing = False
                
        self.update() # triggers paintEvent

    # --- Drawing ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center offsets for drawing the cat
        cx, cy = 150, 150
        y_offset = 0
        
        if self.state == "DRAGGED":
            y_offset = -10 # Dangle effect
            
        # --- Draw Productivity Elements ---
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        # Pinned Message (Speech Bubble)
        if self.pinned_message:
            msg_rect = painter.fontMetrics().boundingRect(self.pinned_message)
            bubble_width = msg_rect.width() + 20
            bubble_height = msg_rect.height() + 15
            bubble_x = max(5, cx - bubble_width // 2)
            bubble_y = max(5, cy - 30 + y_offset - bubble_height - 15)
            
            # Create bubble path
            bubble_path = QPainterPath()
            bubble_path.addRoundedRect(float(bubble_x), float(bubble_y), float(bubble_width), float(bubble_height), 10.0, 10.0)
            
            # Create tail path
            tail_path = QPainterPath()
            tail_path.moveTo(float(cx), float(cy - 25 + y_offset)) # tip near cat
            tail_path.lineTo(float(cx - 8), float(bubble_y + bubble_height))
            tail_path.lineTo(float(cx + 8), float(bubble_y + bubble_height))
            
            # Combine paths
            final_path = bubble_path.united(tail_path)
            
            painter.setPen(QPen(QColor(200, 200, 200), 2))
            painter.setBrush(QColor(255, 255, 255))
            painter.drawPath(final_path)
            
            # Draw text
            painter.setPen(QColor(50, 50, 50))
            painter.drawText(int(bubble_x + 10), int(bubble_y + msg_rect.height() + 2), self.pinned_message)

        # Alarm Timer (Image next to cat)
        if self.pomo_active:
            alarm_w = 60
            alarm_h = 44
            alarm_x = cx + 45 # Bring very close to the cat
            alarm_y = cy + 20 + y_offset
            
            # Draw Alarm Clock Image
            if not self.alarm_pixmap.isNull():
                painter.drawPixmap(alarm_x, alarm_y, alarm_w, alarm_h, self.alarm_pixmap)
                
                # Draw Text inside the screen
                painter.setPen(QColor(255, 255, 255)) # White digital text
                painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
                
                mins = self.pomo_seconds // 60
                secs = self.pomo_seconds % 60
                timer_str = f"{mins:02d}:{secs:02d}"
                
                # Screen bounding box for the green area (approximate)
                screen_rect = QRect(alarm_x, alarm_y, alarm_w, alarm_h)
                
                painter.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, timer_str)

        # --- Draw Cat Sprite ---
        anim_name = self.get_current_animation_name()
        anim_list = self.animations.get(anim_name, self.animations["IDLE"])
        
        # Safety check
        if self.current_frame_index >= len(anim_list):
            self.current_frame_index = 0
            
        col, row = anim_list[self.current_frame_index]
        
        source_rect = QRect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
        
        # Target drawing area (scaled)
        dest_width = self.frame_width * self.scale_factor
        dest_height = self.frame_height * self.scale_factor
        
        dest_x = cx - (dest_width // 2)
        dest_y = cy - (dest_height // 2) + y_offset
        dest_rect = QRect(dest_x, dest_y, dest_width, dest_height)
        
        # Disable smooth scaling to keep pixel art crisp
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        
        if not self.sprite_sheet.isNull():
            painter.drawPixmap(dest_rect, self.sprite_sheet, source_rect)
        else:
            painter.setPen(QColor(255, 0, 0))
            painter.drawText(dest_x, dest_y + 20, "Missing Sprite!")

    # --- Drag and Drop Mechanics ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.state = "DRAGGED"
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.state = "IDLE"
            self.idle_time = 0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    pet = PetWidget()
    pet.show()
    sys.exit(app.exec())
