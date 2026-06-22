import sys
import time
import math
import os
import threading
import winsound
import random
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QInputDialog, QSystemTrayIcon,
                             QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox, 
                             QLineEdit, QPushButton, QDateTimeEdit, QSpinBox, QGroupBox)
from PyQt6.QtGui import QPainter, QCursor, QColor, QAction, QPen, QFont, QPainterPath, QPixmap
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread, QRect, QDateTime
from pynput import mouse, keyboard
import pygetwindow as gw

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "scale_factor": 5.0,
    "react_to_typing": True,
    "stretch_interval_min": 30,
    "water_interval_min": 60,
    "pomodoro_enabled": False,
    "pomo_focus_min": 25,
    "pomo_break_min": 5,
    "reminders": [],
    "matrix_mode": False,
    "matrix_r": 198,
    "matrix_g": 154,
    "matrix_b": 150
}

MATRIX_COLORS = {
    'P': QColor(198, 154, 150), # Dusty Pinkish Brown (Default, will be overridden)
    'D': QColor(75, 54, 50),    # Dark Brown
    'W': QColor(255, 255, 255), # White
    'B': QColor(34, 34, 34),    # Black
    'K': QColor(180, 180, 180), # Keyboard Box
}

MATRIX_FRAMES = {
    "IDLE": [
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP...D.",
            ".....PPPPPPPPPP..DD.",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPPPPPPPPPPPP...",
            "...PPBBBBPPBBBBPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ]
    ],
    "SLEEPING": [
        [
            "....................",
            "....................",
            "....................",
            "....................",
            "....................",
            ".........WWW........",
            "...........W........",
            ".........WWW........",
            "....................",
            ".......PPPP.........",
            "......PDBPP.........",
            ".....PPPPPPPP.......",
            "....PPPPPPPPPP......",
            "...PPPPPPPPPPPP.....",
            "...PPPPBBBBPPPP.DD..",
            "..DDDDDDDDDDDDDDD..."
        ],
        [
            "....................",
            ".........WWW........",
            "...........W........",
            ".........WWW........",
            "....................",
            ".......WW...........",
            "........W...........",
            ".......WW...........",
            "....................",
            ".......PPPP.........",
            "......PDBPP.........",
            ".....PPPPPPPP.......",
            "....PPPPPPPPPP......",
            "...PPPPPPPPPPPP.....",
            "...PPPPBBBBPPPP.DD..",
            "..DDDDDDDDDDDDDDD..."
        ],
        [
            "......WWWW..........",
            ".........W..........",
            ".......WW...........",
            "......WWWW..........",
            "....................",
            "....................",
            ".......WW...........",
            "........W...........",
            ".......WW...........",
            ".......PPPP.........",
            "......PDBPP.........",
            ".....PPPPPPPP.......",
            "....PPPPPPPPPP......",
            "...PPPPPPPPPPPP.....",
            "...PPPPBBBBPPPP.DD..",
            "..DDDDDDDDDDDDDDD..."
        ],
        [
            "....................",
            "....................",
            "......WWWW..........",
            ".........W..........",
            ".......WW...........",
            "......WWWW..........",
            "....................",
            "....................",
            "....................",
            ".......PPPP.........",
            "......PDBPP.........",
            ".....PPPPPPPP.......",
            "....PPPPPPPPPP......",
            "...PPPPPPPPPPPP.....",
            "...PPPPBBBBPPPP.DD..",
            "..DDDDDDDDDDDDDDD..."
        ]
    ],
    "DRAGGED": [
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....P........P.....",
            ".....P........P.....",
            "....P..........P....",
            "....D..........D....",
            "....................",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....P........P.....",
            ".....P........P.....",
            ".....P........P.....",
            ".....D........D.....",
            "....................",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....P........P.....",
            ".....P........P.....",
            "......P........P....",
            "......D........D....",
            "....................",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....P........P.....",
            ".....P........P.....",
            ".....P........P.....",
            ".....D........D.....",
            "....................",
            "...................."
        ]
    ],
    "TYPING": [
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            "..............DD....",
            ".....PPPPPPPP.P.DD..",
            ".....PPPPPPPP.P..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..PPPP.DD..",
            "....DPPPD..BKKKB....",
            "....BKKKB..BBBBB...."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "....BKKKB..BKKKB...."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            "....DD..............",
            "....P.PPPPPPPP..DD..",
            "....P.PPPPPPPP...D..",
            ".....PPPPPPPPP...D..",
            ".....PPPP..DPPPD.DD.",
            "....BKKKB..DPPPD....",
            "....BBBBB..BKKKB...."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "....BKKKB..BKKKB...."
        ]
    ],
    "WATCHING": [
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            "....PPPPPPPPPPPP....",
            "....PPPPPPPPPPPP....",
            "....PPPPPPPPPPPP.DD.",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ]
    ],
    "VIBING": [
        [
            "....PP......PP......",
            "...PDBP....PDBP.....",
            "...PPPPPPPPPPPP.....",
            "..PPPPPPPPPPPPPP....",
            "..PPEEEEPPEEEEPP....",
            "..PPEEEEPPEEEEPP....",
            "..PPPPPPPPPPPPPP....",
            "...PPPPPPBPPPPP.....",
            "....PPPPPPPPPP......",
            "..D.PPPPPPPPPP......",
            ".P..PPPPPPPPPP.DD...",
            "P...PPPPPPPPPP..D...",
            "P...PPPPPPPPP...D...",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            "......PP......PP....",
            ".....PDBP....PDBP...",
            ".....PPPPPPPPPPPP...",
            "....PPPPPPPPPPPPPP..",
            "....PPEEEEPPEEEEPP..",
            "....PPEEEEPPEEEEPP..",
            "....PPPPPPPPPPPPPP..",
            ".....PPPPPPBPPPPP...",
            "......PPPPPPPPPP....",
            "......PPPPPPPPPP.D..",
            "......PPPPPPPPPP..P.",
            "......PPPPPPPPPP...P",
            "......PPPPPPPPP....P",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            "....PPPPPPPPPPPP....",
            "....PPPPPPPPPPPP....",
            "....PPPPPPPPPPPP.DD.",
            ".....PPPPPPPPP...D..",
            "....DPPPD..DPPPD.DD.",
            "....DPPPD..DPPPD....",
            "...................."
        ]
    ],
    "SCROLLING": [
        [
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPEEEEPPEEEEPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            "..............DD....",
            ".....PPPPPPPP.P.DD..",
            ".....PPPPPPPP.P..D..",
            ".....PPPPPPPPP...D..",
            "....DPPPD..PPPP.DD..",
            "....DPPPD..BKKKB....",
            "....BKKKB..BBBBB...."
        ]
    ]
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                s = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in s:
                        s[k] = v
                return s
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class SettingsWindow(QWidget):
    def __init__(self, pet_widget):
        super().__init__()
        self.pet = pet_widget
        self.setWindowTitle("Nyx Settings")
        self.setFixedSize(350, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e24;
                color: #e0e0e0;
                font-family: Arial;
                font-size: 12px;
            }
            QGroupBox {
                border: 1px solid #333;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #a0a0a0;
            }
            QLineEdit, QSpinBox, QDateTimeEdit {
                background-color: #2b2b36;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #5c6bc0;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #7986cb;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #2b2b36;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #90caf9;
                border: 1px solid #5c6bc0;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)

        layout = QVBoxLayout()
        
        # Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(20, 100) # 2.0 to 10.0 scale
        self.size_slider.setValue(int(self.pet.settings["scale_factor"] * 10))
        self.size_slider.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.size_slider)
        layout.addLayout(size_layout)
        
        # React to typing
        self.typing_cb = QCheckBox("React to typing")
        self.typing_cb.setChecked(self.pet.settings["react_to_typing"])
        self.typing_cb.stateChanged.connect(self.on_typing_changed)
        layout.addWidget(self.typing_cb)
        
        # Matrix Mode
        self.matrix_cb = QCheckBox("Use Code-Generated Pixel Art (Matrix Mode)")
        self.matrix_cb.setChecked(self.pet.settings.get("matrix_mode", False))
        self.matrix_cb.stateChanged.connect(self.on_matrix_changed)
        layout.addWidget(self.matrix_cb)
        

        # --- Matrix Mode Colors ---
        color_group = QGroupBox("Matrix Cat Color")
        color_layout = QVBoxLayout()
        
        r_row = QHBoxLayout()
        r_row.addWidget(QLabel("Red:"))
        self.r_slider = QSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(0, 255)
        self.r_slider.setValue(self.pet.settings.get("matrix_r", 198))
        self.r_slider.valueChanged.connect(self.on_color_changed)
        r_row.addWidget(self.r_slider)
        color_layout.addLayout(r_row)
        
        g_row = QHBoxLayout()
        g_row.addWidget(QLabel("Green:"))
        self.g_slider = QSlider(Qt.Orientation.Horizontal)
        self.g_slider.setRange(0, 255)
        self.g_slider.setValue(self.pet.settings.get("matrix_g", 154))
        self.g_slider.valueChanged.connect(self.on_color_changed)
        g_row.addWidget(self.g_slider)
        color_layout.addLayout(g_row)
        
        b_row = QHBoxLayout()
        b_row.addWidget(QLabel("Blue:"))
        self.b_slider = QSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(0, 255)
        self.b_slider.setValue(self.pet.settings.get("matrix_b", 150))
        self.b_slider.valueChanged.connect(self.on_color_changed)
        b_row.addWidget(self.b_slider)
        color_layout.addLayout(b_row)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Reminders
        rem_group = QGroupBox("Reminders")
        rem_layout = QVBoxLayout()
        self.rem_input = QLineEdit()
        self.rem_input.setPlaceholderText("What should I remind you?")
        rem_layout.addWidget(self.rem_input)
        
        rem_row = QHBoxLayout()
        self.rem_date = QDateTimeEdit(QDateTime.currentDateTime())
        self.rem_date.setDisplayFormat("dd-MM-yyyy HH:mm")
        rem_row.addWidget(self.rem_date)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_reminder)
        rem_row.addWidget(add_btn)
        rem_layout.addLayout(rem_row)
        
        help_label = QLabel("The pet walks to the center and holds the message. Drag it to acknowledge and clear the reminder.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #888;")
        rem_layout.addWidget(help_label)
        rem_group.setLayout(rem_layout)
        layout.addWidget(rem_group)
        
        # Intervals
        int_group = QGroupBox("Timers")
        int_layout = QVBoxLayout()
        
        s_row = QHBoxLayout()
        s_row.addWidget(QLabel("Stretch break (min, 0 = off)"))
        self.stretch_spin = QSpinBox()
        self.stretch_spin.setMaximum(999)
        self.stretch_spin.setValue(self.pet.settings["stretch_interval_min"])
        self.stretch_spin.valueChanged.connect(self.on_stretch_changed)
        s_row.addWidget(self.stretch_spin)
        int_layout.addLayout(s_row)
        
        w_row = QHBoxLayout()
        w_row.addWidget(QLabel("Drink water (min, 0 = off)"))
        self.water_spin = QSpinBox()
        self.water_spin.setMaximum(999)
        self.water_spin.setValue(self.pet.settings["water_interval_min"])
        self.water_spin.valueChanged.connect(self.on_water_changed)
        w_row.addWidget(self.water_spin)
        int_layout.addLayout(w_row)
        
        self.pomo_cb = QCheckBox("Pomodoro enabled")
        self.pomo_cb.setChecked(self.pet.settings["pomodoro_enabled"])
        self.pomo_cb.stateChanged.connect(self.on_pomo_cb_changed)
        int_layout.addWidget(self.pomo_cb)
        
        pf_row = QHBoxLayout()
        pf_row.addWidget(QLabel("Focus (min)"))
        self.pomo_f_spin = QSpinBox()
        self.pomo_f_spin.setMaximum(999)
        self.pomo_f_spin.setValue(self.pet.settings["pomo_focus_min"])
        self.pomo_f_spin.valueChanged.connect(self.on_pomo_f_changed)
        pf_row.addWidget(self.pomo_f_spin)
        int_layout.addLayout(pf_row)
        
        pb_row = QHBoxLayout()
        pb_row.addWidget(QLabel("Break (min)"))
        self.pomo_b_spin = QSpinBox()
        self.pomo_b_spin.setMaximum(999)
        self.pomo_b_spin.setValue(self.pet.settings["pomo_break_min"])
        self.pomo_b_spin.valueChanged.connect(self.on_pomo_b_changed)
        pb_row.addWidget(self.pomo_b_spin)
        int_layout.addLayout(pb_row)
        
        int_group.setLayout(int_layout)
        layout.addWidget(int_group)
        
        self.setLayout(layout)

    def on_size_changed(self, val):
        self.pet.settings["scale_factor"] = val / 10.0
        self.pet.scale_factor = val / 10.0
        self.pet.save_and_apply_settings()

    def on_typing_changed(self, val):
        self.pet.settings["react_to_typing"] = bool(val)
        self.pet.save_and_apply_settings()
        

    def on_color_changed(self):
        self.pet.settings["matrix_r"] = self.r_slider.value()
        self.pet.settings["matrix_g"] = self.g_slider.value()
        self.pet.settings["matrix_b"] = self.b_slider.value()
        self.pet.save_and_apply_settings()

    def on_matrix_changed(self, val):
        self.pet.settings["matrix_mode"] = bool(val)
        self.pet.save_and_apply_settings()
        
    def on_stretch_changed(self, val):
        self.pet.settings["stretch_interval_min"] = val
        self.pet.save_and_apply_settings()
        
    def on_water_changed(self, val):
        self.pet.settings["water_interval_min"] = val
        self.pet.save_and_apply_settings()

    def on_pomo_cb_changed(self, val):
        self.pet.settings["pomodoro_enabled"] = bool(val)
        self.pet.save_and_apply_settings()

    def on_pomo_f_changed(self, val):
        self.pet.settings["pomo_focus_min"] = val
        self.pet.save_and_apply_settings()

    def on_pomo_b_changed(self, val):
        self.pet.settings["pomo_break_min"] = val
        self.pet.save_and_apply_settings()

    def add_reminder(self):
        msg = self.rem_input.text().strip()
        if not msg: return
        dt = self.rem_date.dateTime().toPyDateTime()
        self.pet.settings["reminders"].append({
            "time": dt.isoformat(),
            "message": msg
        })
        self.pet.save_and_apply_settings()
        self.rem_input.clear()


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
        
        self.settings = load_settings()
        
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
        self.water_timer = 0
        
        # Phase 5 Sprite states
        self.setup_sprites()
        self.scale_factor = self.settings["scale_factor"]
        
        self.settings_window = SettingsWindow(self)
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
        
    def save_and_apply_settings(self):
        save_settings(self.settings)

    def setup_sprites(self):
        asset_path = os.path.join(os.path.dirname(__file__), "assets", "Cat Sprite Sheet.png")
        self.sprite_sheet = QPixmap(asset_path)
        
        alarm_path = os.path.join(os.path.dirname(__file__), "assets", "updated clock.png")
        full_pixmap = QPixmap(alarm_path)
        self.alarm_pixmap = full_pixmap.copy(470, 158, 997, 725)
        
        self.frame_width = 32
        self.frame_height = 32
        
        self.animations = {
            "IDLE": [(c, 0) for c in range(4)],          # Row 0
            "IDLE_2": [(c, 2) for c in range(4)],        # Row 2 (Unused 1)
            "IDLE_3": [(c, 3) for c in range(4)],        # Row 3 (Unused 2)
            "IDLE_4": [(c, 5) for c in range(8)],        # Row 5 (Unused 3)
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
        self.resize(500, 300)
        self.setupTray()

    def setupTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Actions
        show_action = QAction("Show", self)
        set_pin_action = QAction("Set Pinned Message", self)
        clear_pin_action = QAction("Clear Pinned Message", self)
        toggle_alarm_action = QAction("Toggle Pomodoro", self)
        settings_action = QAction("Settings", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        set_pin_action.triggered.connect(self.prompt_pinned_message)
        clear_pin_action.triggered.connect(self.clear_pinned_message)
        toggle_alarm_action.triggered.connect(self.toggle_alarm)
        settings_action.triggered.connect(self.settings_window.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        # Menu
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(set_pin_action)
        tray_menu.addAction(clear_pin_action)
        tray_menu.addSeparator()
        tray_menu.addAction(toggle_alarm_action)
        tray_menu.addAction(settings_action)
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
        if not self.settings["pomodoro_enabled"]:
            self.pinned_message = "Pomodoro disabled in Settings"
            return
            
        self.pomo_active = not self.pomo_active
        if self.pomo_active:
            self.pomo_seconds = self.settings["pomo_focus_min"] * 60
        else:
            self.pomo_seconds = 0

    def play_alarm_sound(self):
        def beep_thread():
            for _ in range(5):
                winsound.Beep(800, 200)
                winsound.Beep(1200, 200)
        threading.Thread(target=beep_thread, daemon=True).start()

    # --- Signals ---
    def on_input_activity(self):
        self.idle_time = 0
        if self.state == "SLEEPING":
            self.state = "IDLE"
            
    def on_typing_activity(self):
        if not self.settings.get("react_to_typing", True):
            return
        self.is_typing = True
        self.typing_timer = 10
        
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
        if self.state in ["IDLE", "IDLE_2", "IDLE_3", "IDLE_4"]: return self.state
        return "IDLE"

    # --- Logic Updates ---
    def update_logic(self):
        if not self.is_dragging:
            self.idle_time += 1
            if self.idle_time > self.SLEEP_THRESHOLD:
                self.state = "SLEEPING"
            elif self.idle_time % 6 == 0:
                self.state = random.choice(["IDLE", "IDLE_2", "IDLE_3", "IDLE_4"])
                self.current_frame_index = 0
                

        
        # Reminders
        now = datetime.now()
        reminders_to_keep = []
        for r in self.settings.get("reminders", []):
            try:
                rt = datetime.fromisoformat(r["time"])
                if now >= rt:
                    self.pinned_message = f"🔔 {r['message']}"
                    self.play_alarm_sound()
                else:
                    reminders_to_keep.append(r)
            except:
                pass
        
        if len(reminders_to_keep) != len(self.settings.get("reminders", [])):
            self.settings["reminders"] = reminders_to_keep
            self.save_and_apply_settings()

        # Stretch
        s_min = self.settings.get("stretch_interval_min", 0)
        if s_min > 0:
            self.stretch_timer += 1
            if self.stretch_timer >= s_min * 60:
                self.stretch_timer = 0
                self.pinned_message = "Time to Stretch!"
                self.play_alarm_sound()
                
        # Water
        w_min = self.settings.get("water_interval_min", 0)
        if w_min > 0:
            self.water_timer += 1
            if self.water_timer >= w_min * 60:
                self.water_timer = 0
                self.pinned_message = "Drink some water!"
                self.play_alarm_sound()

        # Productivity Logic
        if self.pomo_active:
            if self.pomo_seconds > 0:
                self.pomo_seconds -= 1
            else:
                self.pomo_active = False
                self.pinned_message = "⏰ POMODORO DONE! ⏰"
                self.play_alarm_sound()

    def update_animation(self):
        self.tick_count += 1
        
        anim_name = self.get_current_animation_name()
        
        # Determine speed (matrix mode allows variable speed)
        speed = 2 # 60ms
        if self.settings.get("matrix_mode", False):
            if anim_name == "TYPING":
                speed = 1 # 30ms (Super fast)
            elif anim_name == "SLEEPING":
                speed = 4 # 120ms (Slow Zzzs)
            elif anim_name == "VIBING":
                speed = 2 # 60ms (Dance)
            elif anim_name == "WATCHING":
                speed = 3 # 90ms (Smooth breath)
        else:
            speed = 3
            
        if self.tick_count % speed == 0:
            self.current_frame_index += 1

        if self.typing_timer > 0:
            self.typing_timer -= 1
            if self.typing_timer <= 0:
                self.is_typing = False
                
        self.update() 

    # --- Drawing ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = 150, 150
        y_offset = 0
        
        if self.state == "DRAGGED":
            y_offset = -10
            
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        if self.pinned_message:
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
            painter.drawText(int(bubble_x + 10), int(bubble_y + msg_rect.height() + 2), self.pinned_message)

        if self.pomo_active:
            alarm_w = 60
            alarm_h = 44
            alarm_x = cx + 45
            alarm_y = cy + 20 + y_offset
            
            if not self.alarm_pixmap.isNull():
                painter.drawPixmap(alarm_x, alarm_y, alarm_w, alarm_h, self.alarm_pixmap)
                
                painter.setPen(QColor(255, 255, 255))
                painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
                
                mins = self.pomo_seconds // 60
                secs = self.pomo_seconds % 60
                timer_str = f"{mins:02d}:{secs:02d}"
                
                screen_rect = QRect(alarm_x, alarm_y, alarm_w, alarm_h)
                painter.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, timer_str)

        if self.settings.get("matrix_mode", False):
            # MATRIX MODE RENDERING
            anim_name = self.get_current_animation_name()
            if anim_name not in MATRIX_FRAMES:
                anim_name = "IDLE"
            anim_list = MATRIX_FRAMES.get(anim_name, MATRIX_FRAMES["IDLE"])
            if self.current_frame_index >= len(anim_list):
                self.current_frame_index = 0
            
            frame_data = anim_list[self.current_frame_index]
            
            grid_w = len(frame_data[0])
            grid_h = len(frame_data)
            pixel_size = max(2, int(self.scale_factor * 1.6)) # Scaled correctly to original PNG size
            
            dest_width = grid_w * pixel_size
            dest_height = grid_h * pixel_size
            dest_x = cx - (dest_width // 2)
            dest_y = cy - (dest_height // 2) + y_offset
            
            # Override body color with settings
            custom_r = self.settings.get("matrix_r", 198)
            custom_g = self.settings.get("matrix_g", 154)
            custom_b = self.settings.get("matrix_b", 150)
            MATRIX_COLORS['P'] = QColor(custom_r, custom_g, custom_b)
            
            left_eye_pixels = []
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
                    
                    painter.drawRect(int(pupil_cx - pupil_w/2), int(pupil_cy - pupil_h/2), int(pupil_w), int(pupil_h))
        else:
            anim_name = self.get_current_animation_name()
            anim_list = self.animations.get(anim_name, self.animations["IDLE"])
            
            if self.current_frame_index >= len(anim_list):
                self.current_frame_index = 0
                
            col, row = anim_list[self.current_frame_index]
            source_rect = QRect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
            
            dest_width = int(self.frame_width * self.scale_factor)
            dest_height = int(self.frame_height * self.scale_factor)
            
            dest_x = cx - (dest_width // 2)
            dest_y = cy - (dest_height // 2) + y_offset
            dest_rect = QRect(dest_x, dest_y, dest_width, dest_height)
            
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            
            if not self.sprite_sheet.isNull():
                painter.drawPixmap(dest_rect, self.sprite_sheet, source_rect)
            else:
                painter.setPen(QColor(255, 0, 0))
                painter.drawText(dest_x, dest_y + 20, "Missing Sprite!")

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
            self.clear_pinned_message()

if __name__ == '__main__':
    import traceback
    def excepthook(exc_type, exc_value, exc_tb):
        with open("error.log", "w") as f:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.excepthook = excepthook

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    pet = PetWidget()
    pet.show()
    sys.exit(app.exec())
