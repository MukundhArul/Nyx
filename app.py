import sys
import time
import math
from PyQt6.QtWidgets import QApplication, QWidget, QMenu, QInputDialog, QSystemTrayIcon
from PyQt6.QtGui import QPainter, QColor, QAction, QPen, QFont, QPainterPath
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread
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

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(200, 160) # Increased size for text bubbles
        self.setupTray()

    def setupTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Actions
        show_action = QAction("Show", self)
        set_pin_action = QAction("Set Pinned Message", self)
        clear_pin_action = QAction("Clear Pinned Message", self)
        toggle_pomo_action = QAction("Toggle Pomodoro (25m)", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        set_pin_action.triggered.connect(self.prompt_pinned_message)
        clear_pin_action.triggered.connect(self.clear_pinned_message)
        toggle_pomo_action.triggered.connect(self.toggle_pomodoro)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        # Menu
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(set_pin_action)
        tray_menu.addAction(clear_pin_action)
        tray_menu.addSeparator()
        tray_menu.addAction(toggle_pomo_action)
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

    def toggle_pomodoro(self):
        if self.pomo_active:
            self.pomo_active = False
        else:
            self.pomo_active = True
            self.pomo_seconds = 25 * 60

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
                self.pinned_message = "Pomodoro Finished!"
                
        self.stretch_timer += 1
        if self.stretch_timer >= self.STRETCH_INTERVAL:
            self.stretch_timer = 0
            self.pinned_message = "Time to Stretch!"

    def update_animation(self):
        self.tick_count += 1
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
        cx, cy = 60, 60
        y_offset = 0
        
        if self.state == "DRAGGED":
            y_offset = -10 # Dangle effect
        elif self.active_app_state == "VIBING" and self.state != "SLEEPING":
            y_offset = int(math.sin(self.tick_count * 0.4) * 5)
            
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

        # Pomodoro Timer (Clock next to cat)
        if self.pomo_active:
            clock_cx, clock_cy = cx + 60, cy + 10 + y_offset
            clock_radius = 16
            
            # Background circle
            painter.setBrush(QColor(240, 240, 240))
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawEllipse(clock_cx - clock_radius, clock_cy - clock_radius, clock_radius * 2, clock_radius * 2)
            
            # Pie for time remaining
            fraction = self.pomo_seconds / (25 * 60)
            painter.setBrush(QColor(255, 100, 100))
            painter.setPen(Qt.PenStyle.NoPen)
            # drawPie takes (x, y, w, h, startAngle, spanAngle). Angles are in 1/16th of a degree.
            # 90 degrees (12 o'clock) is 90 * 16. We draw backwards (negative span)
            painter.drawPie(clock_cx - clock_radius, clock_cy - clock_radius, clock_radius * 2, clock_radius * 2, 90 * 16, int(-360 * fraction * 16))
            
            # Draw text below clock
            painter.setPen(QColor(0, 0, 0))
            mins = self.pomo_seconds // 60
            secs = self.pomo_seconds % 60
            timer_str = f"{mins:02d}:{secs:02d}"
            painter.drawText(clock_cx - 15, clock_cy + 32, timer_str)

        # --- Draw Cat ---
        cat_color = QColor(250, 180, 100) # Orange cat
        
        # Body
        painter.setBrush(cat_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - 40, cy - 20 + y_offset, 80, 60)
        
        # Ears
        painter.drawPolygon(QPoint(cx - 30, cy - 10 + y_offset), QPoint(cx - 25, cy - 40 + y_offset), QPoint(cx - 10, cy - 15 + y_offset))
        painter.drawPolygon(QPoint(cx + 10, cy - 15 + y_offset), QPoint(cx + 25, cy - 40 + y_offset), QPoint(cx + 30, cy - 10 + y_offset))
        
        # Eyes
        painter.setBrush(QColor(0, 0, 0))
        if self.state == "SLEEPING":
            # Sleepy eyes
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(cx - 25, cy + y_offset, cx - 15, cy + y_offset)
            painter.drawLine(cx + 15, cy + y_offset, cx + 25, cy + y_offset)
        elif self.active_app_state == "WATCHING":
            # Big eyes
            painter.drawEllipse(cx - 25, cy - 5 + y_offset, 14, 14)
            painter.drawEllipse(cx + 11, cy - 5 + y_offset, 14, 14)
        else:
            # Normal eyes
            painter.drawEllipse(cx - 25, cy - 5 + y_offset, 10, 10)
            painter.drawEllipse(cx + 15, cy - 5 + y_offset, 10, 10)
            
        # Paws
        paw_color = QColor(255, 220, 180)
        painter.setBrush(paw_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        paw_y_left = cy + 30 + y_offset
        paw_y_right = cy + 30 + y_offset
        
        if self.is_typing and self.state != "SLEEPING":
            paw_y_left += int(math.sin(self.tick_count) * 5)
            paw_y_right += int(math.cos(self.tick_count) * 5)
        elif self.active_app_state == "SCROLLING" and self.state != "SLEEPING":
            paw_y_right += int(math.sin(self.tick_count * 0.5) * 10)
            
        painter.drawEllipse(cx - 30, paw_y_left, 20, 15)
        painter.drawEllipse(cx + 10, paw_y_right, 20, 15)
        
        # Zzz for sleeping
        if self.state == "SLEEPING":
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            z_offset = (self.tick_count % 60) / 2
            painter.drawText(cx + 20 + int(z_offset), cy - 30 - int(z_offset), "z")
            if self.tick_count % 60 > 20:
                painter.drawText(cx + 35 + int(z_offset), cy - 45 - int(z_offset), "Z")

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
