import sys
import time
import math
from PyQt6.QtWidgets import QApplication, QWidget, QMenu
from PyQt6.QtGui import QPainter, QColor, QAction, QPen
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import QSystemTrayIcon
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
        self.SLEEP_THRESHOLD = 300 # 5 minutes of inactivity to sleep, we'll use 30 seconds for easier testing for now
        self.SLEEP_THRESHOLD = 30
        
        self.is_dragging = False
        self.oldPos = self.pos()
        self.tick_count = 0
        
        self.active_app_state = ""
        self.is_typing = False
        self.typing_timer = 0
        
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
        self.resize(120, 120)
        self.setupTray()

    def setupTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

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
        
        # Calculate bounce based on state
        y_offset = 0
        if self.state == "DRAGGED":
            y_offset = -10 # Dangle effect
        elif self.active_app_state == "VIBING" and self.state != "SLEEPING":
            y_offset = int(math.sin(self.tick_count * 0.4) * 5)
            
        # Base colors
        cat_color = QColor(250, 180, 100) # Orange cat
        
        # Body
        painter.setBrush(cat_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(20, 40 + y_offset, 80, 60)
        
        # Ears
        painter.drawPolygon(QPoint(30, 50 + y_offset), QPoint(35, 20 + y_offset), QPoint(50, 45 + y_offset))
        painter.drawPolygon(QPoint(70, 45 + y_offset), QPoint(85, 20 + y_offset), QPoint(90, 50 + y_offset))
        
        # Eyes
        painter.setBrush(QColor(0, 0, 0))
        if self.state == "SLEEPING":
            # Sleepy eyes (lines)
            pen = QPen(QColor(0, 0, 0))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(35, 60 + y_offset, 45, 60 + y_offset)
            painter.drawLine(75, 60 + y_offset, 85, 60 + y_offset)
        elif self.active_app_state == "WATCHING":
            # Big eyes
            painter.drawEllipse(35, 55 + y_offset, 14, 14)
            painter.drawEllipse(71, 55 + y_offset, 14, 14)
        else:
            # Normal eyes
            painter.drawEllipse(35, 55 + y_offset, 10, 10)
            painter.drawEllipse(75, 55 + y_offset, 10, 10)
            
        # Paws
        paw_color = QColor(255, 220, 180)
        painter.setBrush(paw_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        paw_y_left = 90 + y_offset
        paw_y_right = 90 + y_offset
        
        if self.is_typing and self.state != "SLEEPING":
            paw_y_left += int(math.sin(self.tick_count) * 5)
            paw_y_right += int(math.cos(self.tick_count) * 5)
        elif self.active_app_state == "SCROLLING" and self.state != "SLEEPING":
            paw_y_right += int(math.sin(self.tick_count * 0.5) * 10)
            
        painter.drawEllipse(30, paw_y_left, 20, 15)
        painter.drawEllipse(70, paw_y_right, 20, 15)
        
        # Zzz for sleeping
        if self.state == "SLEEPING":
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            z_offset = (self.tick_count % 60) / 2
            painter.drawText(80 + int(z_offset), 30 - int(z_offset), "z")
            if self.tick_count % 60 > 20:
                painter.drawText(95 + int(z_offset), 15 - int(z_offset), "Z")

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
