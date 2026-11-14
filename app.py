import sys
import time
import psutil
import os
import json
import math
import random
from datetime import datetime
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QInputDialog, QSystemTrayIcon,
                             QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox, 
                             QLineEdit, QPushButton, QDateTimeEdit, QSpinBox, QGroupBox)
# pyrefly: ignore [missing-import]
from PyQt6.QtGui import QPainter, QCursor, QColor, QAction, QFont, QPixmap
from PyQt6.QtGui import (QPainter, QCursor, QColor, QAction, QFont, QPixmap,
                         QIcon, QPolygonF, QPen, QRadialGradient)
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QTimer, pyqtSignal, QThread, QDateTime
from pynput import mouse, keyboard
# pyrefly: ignore [missing-import]
import pygetwindow as gw

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "scale_factor": 4.0,
    "react_to_typing": True,
    "stretch_interval_min": 30,
    "water_interval_min": 60,
    "pomodoro_enabled": False,
    "pomo_focus_min": 25,
    "pomo_break_min": 5,
    "reminders": [],
    "matrix_mode": False,
    "matrix_r": 26,
    "matrix_g": 26,
    "matrix_b": 26,
    "matrix_outline_r": 20,
    "matrix_outline_g": 20,
    "matrix_outline_b": 20
}

MATRIX_COLORS = {
    'P': QColor(26, 26, 26),     # Comnyang official dark body (#1A1A1A, overridden by settings)
    'W': QColor(255, 255, 255),  # Pure white eyes, whiskers, markings
    'E': QColor(26, 26, 26),     # Eye socket interior (tracks pupil)
    'B': QColor(10, 10, 10),     # Dark pupil / mouth
    'K': QColor(153, 151, 151),  # Official keycap top (#999797)
    'k': QColor(96, 94, 94),     # Official keycap side bevel (#605E5E)
    'D': QColor(34, 34, 34),     # Official keycap bottom bevel (#222222)
    'S': QColor(20, 20, 20),     # Outline / shading
    'N': QColor(255, 140, 165),  # Pink nose & inner ears
    'Z': QColor(110, 180, 255),  # Sleeping Zzzs
    'M': QColor(255, 75, 95),    # Coral red headphones
    'L': QColor(42, 42, 42),     # Subtle fur highlight
}

MATRIX_FRAMES = {
    'IDLE': [
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPW....WWW.",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "....WPPPPPPPPPPPPPPPPPPW.WPPPW..",
            "....WPPPPPPPPPPPPPPPPPPPWWPP....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW..WWWW..",
            "...WPPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWWWPPPW..",
            "...WPPPPPPPPPPPPPPPPPPPWWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
    ],
    'TYPING': [
        [
            "..............P..........P....................",
            ".............PP.........PPP...................",
            "............PPPP........PPPP..................",
            "............PPPPP......PPPPP..................",
            "...........PPPPPPPPPPPPPPPPP..................",
            "...........PPPPPPPPPPPPPPPPP..................",
            "...........PPPPPPPPPPPPPPPPP..................",
            "...........PPPPPPPPPPPPPPPPPP.................",
            "..........PPPPPPPPPPPPPPPPPPPP................",
            "..........PPPPPPPPPPPPPPPPPPPP...........PP...",
            ".........PPPPPPPPPPPPPPPPPPPPPP.........PPPP..",
            ".........PPPWWWPPPPPPWWWPPPPPPPPP.......PPPPP.",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPP......PPPPP.",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPPP......PPPP.",
            ".....PPPPPPWPPPWPPPPWPPPWPPPPPPPPPPP....PPPPP.",
            "..........PPWWWPPPPPPWWWPPPPPPPPPPPPP.PPPPPPP.",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP..",
            "......PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP...",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP.....",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPP........",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPP.PPPPPPPPPPPKKKKKKKP.......",
            "............PPPPPPP..PPPKPPPPPPKKKKKKKK.......",
            "............PPPPPPP..PPKKPPPPPPKKKKKKKKP......",
            "...........PPPPPPPP..PPKPPPPPPPKKKKKKKKP......",
            ".....KKKKKKPPPPPPPP..PKKPPPPPPPKKKKKKKPP......",
            "....KKKKKKKPPPPPPPk..PKKPPPPPPkKKKKKKKPP......",
            "...KKKKKKKKPPPPPPPKP.KKKKPPPPPKKKKKKKKPP......",
            "...KKKKKKKPPPPPPPPKP.KKKKKKKKKKKKKKKKPPP......",
            "..KKKKKKKKPPPPPPPPPPWKKKKKKKKKKKKKKKWPPP......",
            "..KKKKKKKKPPPPPPPKP.KWKKKKKKKKKKKKKWPPP.......",
            ".KKKKKKKKKPPPPPPKKP.kKWWWWWWWWWWWWWKPPP.......",
            ".KKKKKKKKKKKKKKKKPP.kkkkkkkkkkkkkkkkPPP.......",
            "WKKKKKKKKKKKKKKKWP..kkkkkkkkkkkkkkkkPP........",
            "KWKKKKKKKKKKKKKWPP..kkkkkkkkkkkkkkkkPP........",
            "kKWWWWWWWWWWWWWKP...kkkkkkkkkkkkkkkkP.........",
            ".kkkkkkkkkkkkkkPP....kkkkkkkkkkkkkkPP.........",
            "..kkkkkkkkkkkkkP......kkkkkkkkkkkkkP..........",
        ],
        [
            "..............P..........P....................",
            ".............PP.........PPP...................",
            "............PPPP........PPPP..................",
            "............PPPPP......PPPPP..................",
            "...........PPPPPPPPPPPPPPPPP..................",
            "...........PPPPPPPPPPPPPPPPP..................",
            "...........PPPPPPPPPPPPPPPPP..................",
            "...........PPPPPPPPPPPPPPPPPP.................",
            "..........PPPPPPPPPPPPPPPPPPPP................",
            "..........PPPPPPPPPPPPPPPPPPPP................",
            ".........PPPPPPPPPPPPPPPPPPPPPP...............",
            ".........PPPWWWPPPPPPWWWPPPPPPPPP.........PP..",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPP.......PPPP.",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPPP......PPPPP",
            "......PPPPPWPPPWPPPPWPPPWPPPPPPPPPPP.....PPPPP",
            "..........PPWWWPPPPPPWWWPPPPPPPPPPPPP.....PPPP",
            ".......PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP....PPPPP",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPP.PPPPPPP",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP.",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP..",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP....",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "...........PPPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "...........PPPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            ".....KKKKKKPPPPPPPP.PPPPPPPPPPPPPPPPPPP.......",
            "....KKKKKKKPPPPPPPK..PPPPPPPPPPPPPPPPPP.......",
            "...KKKKKKKPPPPPPPPKP.PPPPPPPPPPPPPPPPPP.......",
            "...KKKKKKKPPPPPPPPKP.PPPPPPPPPPPPPPPPPP.......",
            "..KKKKKKKKPPPPPPPKPP.PPPPPPPPPPKKKKKKKP.......",
            "..KKKKKKKKPPPPPPKKPP.PPPPPPPPPPKKKKKKKK.......",
            ".KKKKKKKKKKKKKKKKKPP.PPKPPPPPPKKKKKKKKKP......",
            ".KKKKKKKKKKKKKKKKPPP.PPKPPPPPPKKKKKKKKKP......",
            "WKKKKKKKKKKKKKKKWPPP.PKKPPPPPPKKKKKKKKPP......",
            "KWKKKKKKKKKKKKKWPPP..PKPPPPPPPKKKKKKKKP.......",
            "kKWWWWWWWWWWWWWKPPP..KKPPPPPPPKKKKKKKKP.......",
            "kkkkkkkkkkkkkkkkPPP..KKPPPPPPkKKKKKKKPP.......",
            "kkkkkkkkkkkkkkkkPP..WKKKPPPPPKKKKKKKWP........",
            "kkkkkkkkkkkkkkkkPP..KWKKKKKKKKKKKKKWPP........",
            "kkkkkkkkkkkkkkkkP...kKWWWWWWWWWWWWWKP.........",
            ".kkkkkkkkkkkkkkPP....kkkkkkkkkkkkkkPP.........",
            "..kkkkkkkkkkkkkP......kkkkkkkkkkkkkP..........",
        ],
    ],
    'TYPING_MUSIC': [
        [
            "..............P..........P....................",
            ".............PP.WWWWWWWWPPP...................",
            "............PPPMMMMMMMMMMPPP..................",
            "............PPPPP......PPPPP..................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            "..........WWPPPPPPPPPPPPPPPWWP...........PP...",
            ".........PPPPPPPPPPPPPPPPPPPPPP.........PPPP..",
            ".........PPPWWWPPPPPPWWWPPPPPPPPP.......PPPPP.",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPP......PPPPP.",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPPP......PPPP.",
            ".....PPPPPPWPPPWPPPPWPPPWPPPPPPPPPPP....PPPPP.",
            "..........PPWWWPPPPPPWWWPPPPPPPPPPPPP.PPPPPPP.",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP..",
            "......PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP...",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP.....",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPP........",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "............PPPPPPP.PPPPPPPPPPPKKKKKKKP.......",
            "............PPPPPPP..PPPKPPPPPPKKKKKKKK.......",
            "............PPPPPPP..PPKKPPPPPPKKKKKKKKP......",
            "...........PPPPPPPP..PPKPPPPPPPKKKKKKKKP......",
            ".....KKKKKKPPPPPPPP..PKKPPPPPPPKKKKKKKPP......",
            "....KKKKKKKPPPPPPPk..PKKPPPPPPkKKKKKKKPP......",
            "...KKKKKKKKPPPPPPPKP.KKKKPPPPPKKKKKKKKPP......",
            "...KKKKKKKPPPPPPPPKP.KKKKKKKKKKKKKKKKPPP......",
            "..KKKKKKKKPPPPPPPPPPWKKKKKKKKKKKKKKKWPPP......",
            "..KKKKKKKKPPPPPPPKP.KWKKKKKKKKKKKKKWPPP.......",
            ".KKKKKKKKKPPPPPPKKP.kKWWWWWWWWWWWWWKPPP.......",
            ".KKKKKKKKKKKKKKKKPP.kkkkkkkkkkkkkkkkPPP.......",
            "WKKKKKKKKKKKKKKKWP..kkkkkkkkkkkkkkkkPP........",
            "KWKKKKKKKKKKKKKWPP..kkkkkkkkkkkkkkkkPP........",
            "kKWWWWWWWWWWWWWKP...kkkkkkkkkkkkkkkkP.........",
            ".kkkkkkkkkkkkkkPP....kkkkkkkkkkkkkkPP.........",
            "..kkkkkkkkkkkkkP......kkkkkkkkkkkkkP..........",
        ],
        [
            "..............P..........P....................",
            ".............PP.WWWWWWWWPPP...................",
            "............PPPMMMMMMMMMMPPP..................",
            "............PPPPP......PPPPP..................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            ".........WMMWPPPPPPPPPPPPPWMMW................",
            "..........WWPPPPPPPPPPPPPPPWWP................",
            ".........PPPPPPPPPPPPPPPPPPPPPP...............",
            ".........PPPWWWPPPPPPWWWPPPPPPPPP.........PP..",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPP.......PPPP.",
            ".........PPWPPPWPPPPWPPPWPPPPPPPPPP......PPPPP",
            "......PPPPPWPPPWPPPPWPPPWPPPPPPPPPPP.....PPPPP",
            "..........PPWWWPPPPPPWWWPPPPPPPPPPPPP.....PPPP",
            ".......PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP....PPPPP",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPP.PPPPPPP",
            "..........PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP.",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP..",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP....",
            "............PPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "...........PPPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            "...........PPPPPPPPPPPPPPPPPPPPPPPPPPPP.......",
            ".....KKKKKKPPPPPPPP.PPPPPPPPPPPPPPPPPPP.......",
            "....KKKKKKKPPPPPPPK..PPPPPPPPPPPPPPPPPP.......",
            "...KKKKKKKPPPPPPPPKP.PPPPPPPPPPPPPPPPPP.......",
            "...KKKKKKKPPPPPPPPKP.PPPPPPPPPPPPPPPPPP.......",
            "..KKKKKKKKPPPPPPPKPP.PPPPPPPPPPKKKKKKKP.......",
            "..KKKKKKKKPPPPPPKKPP.PPPPPPPPPPKKKKKKKK.......",
            ".KKKKKKKKKKKKKKKKKPP.PPKPPPPPPKKKKKKKKKP......",
            ".KKKKKKKKKKKKKKKKPPP.PPKPPPPPPKKKKKKKKKP......",
            "WKKKKKKKKKKKKKKKWPPP.PKKPPPPPPKKKKKKKKPP......",
            "KWKKKKKKKKKKKKKWPPP..PKPPPPPPPKKKKKKKKP.......",
            "kKWWWWWWWWWWWWWKPPP..KKPPPPPPPKKKKKKKKP.......",
            "kkkkkkkkkkkkkkkkPPP..KKPPPPPPkKKKKKKKPP.......",
            "kkkkkkkkkkkkkkkkPP..WKKKPPPPPKKKKKKKWP........",
            "kkkkkkkkkkkkkkkkPP..KWKKKKKKKKKKKKKWPP........",
            "kkkkkkkkkkkkkkkkP...kKWWWWWWWWWWWWWKP.........",
            ".kkkkkkkkkkkkkkPP....kkkkkkkkkkkkkkPP.........",
            "..kkkkkkkkkkkkkP......kkkkkkkkkkkkkP..........",
        ],
    ],
    'PURRING': [
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPWWPPPPPPWPWWPPPW........",
            "...WPWWPPWPPPPPPWPPWWPPW........",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPWWPPPPPPWPWWPPPW........",
            "...WPWWPPWPPPPPPWPPWWPPW........",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPW....WWW.",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "....WPPPPPPPPPPPPPPPPPPW.WPPPW..",
            "....WPPPPPPPPPPPPPPPPPPPWWPP....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPWWPPPPPPWPWWPPPW........",
            "...WPWWPPWPPPPPPWPPWWPPW........",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW..WWWW..",
            "...WPPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWWWPPPW..",
            "...WPPPPPPPPPPPPPPPPPPPWWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
    ],
    'SLEEPING': [
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPWWWWPPPPPPPWWWWPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW........",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPWWWWPPPPPPPWWWWPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW........",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPW....WWW.",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "....WPPPPPPPPPPPPPPPPPPW.WPPPW..",
            "....WPPPPPPPPPPPPPPPPPPPWWPP....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
    ],
    'DRAGGED': [
        [
            ".......WWW........WWW...........",
            "......WWPWW......WWPWW..........",
            ".....WWPPWW......WWPPWW.........",
            ".....WPPPPWWWWWWWWPPPPW.........",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPWWWWPPPPPPPPWWWWPPW.......",
            "WWWWPPWPPWPPPPPPPPWPPWPPWWWW....",
            "WPPPWPPWPPWPPPPPPWPPWPPWPPPW....",
            "WWWWPPWPPWPPWWWWPPWPPWPPWWWW....",
            "...WPPWWWW.WWBBWW.WWWWPPW.......",
            "...WWPPPPP.WBBBBW.PPPPPWW.......",
            "WWWWPPPPPP.WWWWWW.PPPPPPWWWW....",
            "WPPPWPPPPPPPPPPPPPPPPPPWPPPW....",
            "WWWWPPPPPPPPPPPPPPPPPPPPWWWW....",
            "....WWPPPPPPPPPPPPPPPPWW........",
            ".....WPPPPPPPPPPPPPPPPW.........",
            ".....WWPPPPPPPPPPPPPPWW.........",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPWPPPPPPPPPPPPPPWPPW.......",
            "...WPPWPPPPPPPPPPPPPPWPPW.......",
            "...WWPWPPPPPPPPPPPPPPWPWW.......",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW...WWW....",
            "......WPPPPPPPPPPPPPPW..WPPPW...",
            ".....WWPPPPPPPPPPPPPPWW.WPPPW...",
            ".....WPPPPPPPPPPPPPPPPWWPPPW....",
            ".....WPPPPPPPPPPPPPPPPPWWPW.....",
            ".....WPPPPPPPPPPPPPPPPPPWW......",
            ".....WPPPPPW....WWPPPPPW........",
            ".....WPPPPPW.....WPPPPPW........",
            ".....WPPPPPW.....WWWWWW.........",
            ".....WWWWWW.....................",
        ],
        [
            ".......WWW........WWW...........",
            "......WWPWW......WWPWW..........",
            ".....WWPPWW......WWPPWW.........",
            ".....WPPPPWWWWWWWWPPPPW.........",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPWWWWPPPPPPPPWWWWPPW.......",
            "WWWWPPWPPWPPPPPPPPWPPWPPWWWW....",
            "WPPPWPPWPPWPPPPPPWPPWPPWPPPW....",
            "WWWWPPWPPWPPWWWWPPWPPWPPWWWW....",
            "...WPPWWWW.WWBBWW.WWWWPPW.......",
            "...WWPPPPP.WBBBBW.PPPPPWW.......",
            "WWWWPPPPPP.WWWWWW.PPPPPPWWWW....",
            "WPPPWPPPPPPPPPPPPPPPPPPWPPPW....",
            "WWWWPPPPPPPPPPPPPPPPPPPPWWWW....",
            "....WWPPPPPPPPPPPPPPPPWW........",
            ".....WPPPPPPPPPPPPPPPPW.........",
            ".....WWPPPPPPPPPPPPPPWW.........",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPWPPPPPPPPPPPPPPWPPW.......",
            "...WPPWPPPPPPPPPPPPPPWPPW.......",
            "...WWPWPPPPPPPPPPPPPPWPWW.......",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW...WWW....",
            "......WPPPPPPPPPPPPPPW..WPPPW...",
            ".....WWPPPPPPPPPPPPPPWW.WPPPW...",
            ".....WPPPPPPPPPPPPPPPPWWPPPW....",
            ".....WPPPPPPPPPPPPPPPPPWWPW.....",
            ".....WPPPPPPPPPPPPPPPPPPWW......",
            ".....WPPPPPWW....WWPPPPPPW......",
            ".....WPPPPPW......WPPPPPPW......",
            ".....WPPPPPW......WPPPPPPW......",
            ".....WWWWWW......WWWWWW.........",
        ],
        [
            ".......WWW........WWW...........",
            "......WWPWW......WWPWW..........",
            ".....WWPPWW......WWPPWW.........",
            ".....WPPPPWWWWWWWWPPPPW.........",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPWWWWPPPPPPPPWWWWPPW.......",
            "WWWWPPWPPWPPPPPPPPWPPWPPWWWW....",
            "WPPPWPPWPPWPPPPPPWPPWPPWPPPW....",
            "WWWWPPWPPWPPWWWWPPWPPWPPWWWW....",
            "...WPPWWWW.WWBBWW.WWWWPPW.......",
            "...WWPPPPP.WBBBBW.PPPPPWW.......",
            "WWWWPPPPPP.WWWWWW.PPPPPPWWWW....",
            "WPPPWPPPPPPPPPPPPPPPPPPWPPPW....",
            "WWWWPPPPPPPPPPPPPPPPPPPPWWWW....",
            "....WWPPPPPPPPPPPPPPPPWW........",
            ".....WPPPPPPPPPPPPPPPPW.........",
            ".....WWPPPPPPPPPPPPPPWW.........",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPWPPPPPPPPPPPPPPWPPW.......",
            "...WPPWPPPPPPPPPPPPPPWPPW.......",
            "...WWPWPPPPPPPPPPPPPPWPWW.......",
            "....WWPPPPPPPPPPPPPPPPWW........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW..........",
            "......WPPPPPPPPPPPPPPW....WW....",
            "......WPPPPPPPPPPPPPPW...WPPPW..",
            "......WPPPPPPPPPPPPPPW...WPPPW..",
            ".....WWPPPPPPPPPPPPPPWW..WPPPW..",
            ".....WPPPPPPPPPPPPPPPPWWWWPPW...",
            ".....WPPPPPPPPPPPPPPPPPWWPPW....",
            ".....WPPPPPPPPPPPPPPPPPPWW......",
            ".....WWPPPPPW....WPPPPPW........",
            "......WPPPPPW....WPPPPPW........",
            "......WWWWWW.....WPPPPPW........",
            ".................WWWWWW.........",
        ],
    ],
    'VIBING': [
        [
            ".......WWW.......WWW............",
            "......MMPWWWWWWWWWMMW...........",
            ".....WMMMMMMMMMMMPMMWW..........",
            "....WMMPPPWWWWWWWPPMMW..........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMWW........",
            "....WWPPPPPPPPPPPPPPWWPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......MMPWWWWWWWWWMMW...........",
            ".....WMMMMMMMMMMMPMMWW..........",
            "....WMMPPPWWWWWWWPPMMW..........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMWW........",
            "....WWPPPPPPPPPPPPPPWWPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPW....WWW.",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "....WPPPPPPPPPPPPPPPPPPW.WPPPW..",
            "....WPPPPPPPPPPPPPPPPPPPWWPP....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......MMPWWWWWWWWWMMW...........",
            ".....WMMMMMMMMMMMPMMWW..........",
            "....WMMPPPWWWWWWWPPMMW..........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMWW........",
            "....WWPPPPPPPPPPPPPPWWPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW..WWWW..",
            "...WPPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWWWPPPW..",
            "...WPPPPPPPPPPPPPPPPPPPWWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......MMPWWWWWWWWWMMW...........",
            ".....WMMMMMMMMMMMPMMWW..........",
            "....WMMPPPWWWWWWWPPMMW..........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMW.........",
            "...WMMWPPPPPPPPPPPPWMMWW........",
            "....WWPPPPPPPPPPPPPPWWPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
    ],
    'WATCHING': [
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPWW.....WWPWW...........",
            ".....WWPPWW.....WWPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPW...WWW..",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "...WWPPPPPPPPPPPPPPPPPPWW.......",
            "...WPPPPPPPPPPPPPPPPPPPW....WWW.",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "....WPPPPPPPPPPPPPPPPPPW.WPPPW..",
            "....WPPPPPPPPPPPPPPPPPPPWWPP....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPW......WWPWW...........",
            ".....WWPPWW.....WPPPWW..........",
            ".....WPPPPWWWWWWWPPPPW..........",
            "....WWPPPPPPPPPPPPPPPW..........",
            "....WPPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WPPPPPPPPPPPPPPPPPPW........",
            "...WWPPWWWPPPPPPPWWWPPPW........",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW.........",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "...WWPPPPPPPPPPPPPPPPPPW........",
            "...WPPPPPPPPPPPPPPPPPPPW..WWWW..",
            "...WPPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWWWPPPW..",
            "...WPPPPPPPPPPPPPPPPPPPWWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWPPPW...",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPWWPPPW...",
            "....WPPPPPPPPPPPPPPPPPPWPPPW....",
            "....WPPPPPPPPPPPPPPPPPPPWWP.....",
            "....WWWWPPPPPPPPPPPPWWWWWW......",
            "......WWWWPPWWWWPPWWWW..........",
            "........WWWWWWWWWWWW............",
        ],
    ],
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
            QLineEdit, QDateTimeEdit {
                background-color: #2b2b36;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 4px;
            }
            QSpinBox {
                background-color: #2b2b36;
                border: 1px solid #444;
                padding: 2px;
                border-radius: 4px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
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
        

        # --- Matrix Mode Colors ---
        color_group = QGroupBox("Matrix Cat Colors")
        color_layout = QVBoxLayout()
        
        # Body Color
        body_row = QHBoxLayout()
        body_row.addWidget(QLabel("Body:"))
        self.body_preview = QLabel()
        self.body_preview.setFixedSize(25, 25)
        self.update_body_preview(self.pet.settings.get("matrix_r", 198), self.pet.settings.get("matrix_g", 154), self.pet.settings.get("matrix_b", 150))
        self.body_btn = QPushButton("Pick")
        self.body_btn.clicked.connect(self.pick_body_color)
        body_row.addWidget(self.body_preview)
        body_row.addWidget(self.body_btn)
        color_layout.addLayout(body_row)
        
        # Outline Color
        outline_row = QHBoxLayout()
        outline_row.addWidget(QLabel("Outline:"))
        self.outline_preview = QLabel()
        self.outline_preview.setFixedSize(25, 25)
        self.update_outline_preview(self.pet.settings.get("matrix_outline_r", 160), self.pet.settings.get("matrix_outline_g", 110), self.pet.settings.get("matrix_outline_b", 110))
        self.outline_btn = QPushButton("Pick")
        self.outline_btn.clicked.connect(self.pick_outline_color)
        outline_row.addWidget(self.outline_preview)
        outline_row.addWidget(self.outline_btn)
        color_layout.addLayout(outline_row)
        
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


        


    def update_body_preview(self, r, g, b):
        self.body_preview.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid black; border-radius: 5px;")
        
    def update_outline_preview(self, r, g, b):
        self.outline_preview.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid black; border-radius: 5px;")

    def pick_body_color(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        r = self.pet.settings.get("matrix_r", 198)
        g = self.pet.settings.get("matrix_g", 154)
        b = self.pet.settings.get("matrix_b", 150)
        current = QColor(r, g, b)
        
        color = QColorDialog.getColor(current, self, "Pick Body Color")
        if color.isValid():
            self.pet.settings["matrix_r"] = color.red()
            self.pet.settings["matrix_g"] = color.green()
            self.pet.settings["matrix_b"] = color.blue()
            self.update_body_preview(color.red(), color.green(), color.blue())
            self.pet.save_and_apply_settings()

    def pick_outline_color(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        r = self.pet.settings.get("matrix_outline_r", 160)
        g = self.pet.settings.get("matrix_outline_g", 110)
        b = self.pet.settings.get("matrix_outline_b", 110)
        current = QColor(r, g, b)
        
        color = QColorDialog.getColor(current, self, "Pick Outline Color")
        if color.isValid():
            self.pet.settings["matrix_outline_r"] = color.red()
            self.pet.settings["matrix_outline_g"] = color.green()
            self.pet.settings["matrix_outline_b"] = color.blue()
            self.update_outline_preview(color.red(), color.green(), color.blue())
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
        
        if "reminders" not in self.pet.settings:
            self.pet.settings["reminders"] = []
            
        self.pet.settings["reminders"].append({
            "time": dt.isoformat(),
            "message": msg
        })
        self.pet.save_and_apply_settings()
        self.rem_input.setText("")
        self.pet.save_and_apply_settings()
        self.rem_input.clear()


class MonitorThread(QThread):
    input_activity = pyqtSignal()
    typing_activity = pyqtSignal()
    active_window = pyqtSignal(str)
    spotify_status = pyqtSignal(bool)

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
        
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        
        while True:
            try:
                hwnd = user32.GetForegroundWindow()
                title = ""
                if hwnd:
                    buf = ctypes.create_unicode_buffer(512)
                    user32.GetWindowTextW(hwnd, buf, 512)
                    title = buf.value
                
                # Fallback to PyGetWindow if empty
                if not title:
                    try:
                        window = gw.getActiveWindow()
                        if window and window.title:
                            title = window.title
                    except Exception:
                        pass
                
                self.active_window.emit(title.lower() if title else "")
                
                # Check if foreground window is spotify
                is_spotify = False
                if hwnd:
                    pid = ctypes.c_ulong(0)
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    h_process = kernel32.OpenProcess(0x0410, False, pid)
                    if h_process:
                        exe_name = ctypes.create_unicode_buffer(260)
                        psapi.GetModuleBaseNameW(h_process, None, exe_name, ctypes.sizeof(exe_name))
                        kernel32.CloseHandle(h_process)
                        if "spotify" in exe_name.value.lower():
                            is_spotify = True
                self.spotify_status.emit(is_spotify)
            except Exception:
                pass
            time.sleep(1)


def epx_scale(frame):
    height = len(frame)
    width = max((len(r) for r in frame), default=0)
    out = [["." for _ in range(width * 2)] for _ in range(height * 2)]
    def get_p(x, y):
        if y < 0 or y >= height or x < 0 or x >= len(frame[y]): return "."
        return frame[y][x]
    for y in range(height):
        for x in range(width):
            P = get_p(x, y)
            A = get_p(x, y - 1)
            B = get_p(x + 1, y)
            C = get_p(x, y + 1)
            D = get_p(x - 1, y)
            P1, P2, P3, P4 = P, P, P, P
            if A != C and B != D:
                if A == D: P1 = A
                if A == B: P2 = B
                if C == D: P3 = C
                if C == B: P4 = B
                
            if P == 'P':
                if P1 == 'P' and (x + y) % 2 == 0: P1 = 'L'
                if P2 == 'P' and (x + y) % 3 == 0: P2 = 'D'
                if P3 == 'P' and (x + y) % 3 == 1: P3 = 'D'
                if P4 == 'P' and (x + y) % 2 == 1: P4 = 'L'
                
            out[y*2][x*2] = P1
            out[y*2][x*2+1] = P2
            out[y*2+1][x*2] = P3
            out[y*2+1][x*2+1] = P4
    return ["".join(row) for row in out]

# Apply EPX to all matrix frames
MATRIX_FRAMES_HIGH_RES = {}
scaled_ids = {}
for anim_name, frames in MATRIX_FRAMES.items():
    if id(frames) in scaled_ids:
        MATRIX_FRAMES_HIGH_RES[anim_name] = scaled_ids[id(frames)]
        continue
    if isinstance(frames, list) and isinstance(frames[0], list):
        new_frames = []
        for frame in frames:
            if isinstance(frame[0], str):
                new_frames.append(epx_scale(frame))
            else:
                new_frames.append(frame)
        MATRIX_FRAMES_HIGH_RES[anim_name] = new_frames
        scaled_ids[id(frames)] = new_frames
    else:
        MATRIX_FRAMES_HIGH_RES[anim_name] = frames




def generate_mochi_sprite(base_matrix, stretch_rows=0):
    if stretch_rows <= 0:
        return base_matrix
    top = base_matrix[0:26] # Rows 0 to 25 (Head, arms, paws)
    bottom = base_matrix[29:] # Rows 29 to end (Pelvis, tail, legs)
    
    total_mid_rows = 3 + stretch_rows
    mid = []
    for i in range(total_mid_rows):
        t = i / max(1, total_mid_rows - 1)
        pinch = int(round(math.sin(t * math.pi) * min(2, stretch_rows // 6)))
        left = 6 + pinch
        right = 21 - pinch
        row = "." * left + "W" + "P" * (right - left - 1) + "W" + "." * (32 - right - 1)
        mid.append(row)
        
    return top + mid + bottom

class PetWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.settings = load_settings()
        
        # State variables
        self.state = "IDLE"
        self.idle_time = 0
        self.SLEEP_THRESHOLD = 30 # Sleep after 30s of inactivity
        
        self.is_dragging = False
        self.is_petting = False
        self.drag_vx = 0.0
        self.drag_vy = 0.0
        self.wobble_angle = 0.0
        self.wobble_vel = 0.0
        self.lift_offset = 0.0
        self.current_stretch_rows = 0.0
        self.last_drag_pos = QPoint()
        self.is_blinking = False
        self.blink_timer = 250
        self.blink_duration = 0
        self.hearts = []
        self.sleeping_zzzs = []
        self.music_notes = []
        self.is_petting = False
        self.drag_has_started = False
        self.mouse_press_pos = None
        self.oldPos = self.pos()
        self.tick_count = 0
        
        self.active_app_state = ""
        self.is_typing = False
        self.typing_timer = 0
        self.typing_heat = 0.0
        self.keystroke_times = []
        self.current_wpm = 0.0
        self.is_angry = False
        self.is_listening_to_music = False
        
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
        
        # Animation loop (50 FPS for fluid physics)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(20)
        
        # One second logic timer
        self.logic_timer = QTimer(self)
        self.logic_timer.timeout.connect(self.update_logic)
        self.logic_timer.start(1000)
        
        # Start monitoring thread
        self.monitor = MonitorThread()
        self.monitor.input_activity.connect(self.on_input_activity)
        self.monitor.typing_activity.connect(self.on_typing_activity)
        self.monitor.active_window.connect(self.on_active_window)
        self.monitor.spotify_status.connect(self.on_spotify_status)
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
            "WALKING": [(c, 2) for c in range(8)],       # Row 2
            "DRAGGED": [(c, 1) for c in range(4)],       # Row 1
            "TYPING": [(c, 7) for c in range(6)],        # Row 7
        "CODING_IDLE": [
        [
            "....................",
            ".....PH......HP.....",
            "....PPSP....PPSP....",
            "....HPPPHHHPPPHS....",
            "...HGGGGGGGGGGGGGS..",
            "...SPGGGGGGGGGGGS...",
            "...SPPPPPPPPPPPPS..S",
            "...SPPPPPPPPPPPPS.S.",
            "...SSPPPPPPPPPPS..S.",
            "...SSPPPPPPPPPPS.S..",
            "...SSPPPPPPPPPPSSS..",
            "...SSPPPPPPPPPPS....",
            ".............SS.....",
            "...................."
        ]
    ],
    "CODING_TYPING": [
        [
            "....................",
            ".....PH......HP.....",
            "....PPSP....PPSP....",
            "....HPPPHHHPPPHS....",
            "...HGGGGGGGGGGGGGS..",
            "...SPGGGGGGGGGGGS...",
            "...SPPPPPPPPPPPPS..S",
            "...SPPPPPPPPPPPPS.S.",
            "...SSPPPPPPPPPPS..S.",
            "...SSPPPPPPPPPPS.S..",
            "...SSPPPPPPPPPPSSS..",
            "...SSPPPPPPPPPPS....",
            ".............SS.....",
            "...................."
        ],
        [
            "....................",
            ".....PH......HP.....",
            "....PPSP....PPSP....",
            "....HPPPHHHPPPHS....",
            "...HGGGGGGGGGGGGGS..",
            "...SPGGGGGGGGGGGS...",
            "...SPPPPPPPPPPPPS..S",
            "...SPPPPPPPPPPPPS.S.",
            "....SPPPPPPPPSS...S.",
            "....SPPPPPPPPSS..S..",
            "....SPPPPPPPPSS.SS..",
            "....SPPS............",
            ".....SS.............",
            "...................."
        ]
    ],
    "PURRING": [
        [
            "....................",
            ".....PH......HP.....",
            "....PPSP....PPSP....",
            "....HPPPHHHPPPHS....",
            "...HPPBBBBPPBBBBS...",
            "...SPPBBBBPPBBBBS...",
            "...SPPPPPPPPPPPPS..S",
            "...SPPPPPPPPPPPPS.S.",
            "....SPPPPPPPPPPS..S.",
            "....SPPPPPPPPPPS.S..",
            "....SPPPPPPPPPPSSS..",
            "....SPPPPPPPPPPS....",
            "....SPPS....SPPS....",
            "....SPPS....SPPS....",
            ".....SS......SS.....",
            "...................."
        ]
    ],
    "VIBING": [(c, 8) for c in range(7)],        # Row 8
            "WATCHING": [(c, 9) for c in range(8)],      # Row 9
            "SCROLLING": [(c, 4) for c in range(8)]      # Row 4
        }
        self.current_frame_index = 0

    def initUI(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 440)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_window_flags()
        self.setupTray()

    def setupTray(self):
        self.tray_icon = QSystemTrayIcon(QApplication.instance())
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        icon_path = os.path.join(os.path.dirname(__file__), "cat.ico")
        if os.path.exists(icon_path):
            cat_icon = QIcon(icon_path)
            self.tray_icon.setIcon(cat_icon)
            self.setWindowIcon(cat_icon)
        else:
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
        
        # Actions
        show_action = QAction("Show", self)
        set_task_action = QAction("Set Pomodoro Task...", self)
        set_pin_action = QAction("Set Pinned Message", self)
        clear_pin_action = QAction("Clear Pinned Message", self)
        set_pin_action = QAction("Set Speech Note...", self)
        clear_pin_action = QAction("Clear Note", self)
        toggle_alarm_action = QAction("Toggle Pomodoro", self)
        
        pin_window_action = QAction("Always Pin Nyx", self, checkable=True)
        pin_window_action = QAction("Always on Top", self, checkable=True)
        pin_window_action.setChecked(self.settings.get("always_on_top", True))
        
        settings_action = QAction("Settings...", self)
        quit_action = QAction("Exit Nyx", self)
        
        settings_action = QAction("Settings", self)
        quit_action = QAction("Exit", self)
        
        show_action.triggered.connect(self.show)
        set_task_action.triggered.connect(self.set_pomodoro_task)
        set_pin_action.triggered.connect(self.prompt_pinned_message)
        clear_pin_action.triggered.connect(self.clear_pinned_message)
        toggle_alarm_action.triggered.connect(self.toggle_alarm)
        pin_window_action.triggered.connect(self.toggle_pin)
        settings_action.triggered.connect(self.settings_window.show)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        # Menu
        # Styled Menu
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e28;
                color: #e4e4ed;
                border: 1px solid #36364c;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #5c6bc0;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #313145;
                margin: 4px 6px;
            }
        """)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(pin_window_action)
        tray_menu.addSeparator()
        tray_menu.addAction(set_task_action)
        tray_menu.addAction(toggle_alarm_action)
        tray_menu.addSeparator()
        tray_menu.addAction(set_pin_action)
        tray_menu.addAction(clear_pin_action)
        tray_menu.addSeparator()
        tray_menu.addAction(settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def contextMenuEvent(self, event):
        # Allow right-clicking directly on the desktop cat
        if hasattr(self, 'tray_icon') and self.tray_icon.contextMenu():
            self.tray_icon.contextMenu().exec(event.globalPos())

    def apply_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.settings.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
            
        if int(self.windowFlags()) != int(flags):
            # Temporarily hide tray to avoid ghosting on Windows
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.tray_icon.hide()
            self.setWindowFlags(flags)
            self.show()
            if hasattr(self, 'tray_icon'):
                self.tray_icon.show()

    # --- Productivity Prompts ---
    def set_pomodoro_task(self):
        from PyQt6.QtWidgets import QInputDialog
        task, ok = QInputDialog.getText(self, "Set Task", "What are you working on right now?")
        if ok:
            self.current_task = task
            self.pomo_active = True
            if self.pomo_seconds == 0:
                self.pomo_seconds = self.settings.get("pomo_focus_min", 25) * 60

    def toggle_pin(self, checked):
        self.settings["always_on_top"] = checked
        self.save_and_apply_settings()
        self.apply_window_flags()

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
            self.pomo_seconds = self.settings.get("pomo_focus_min", 25) * 60
        else:
            self.pomo_seconds = 0

    # --- Signals ---
    def on_input_activity(self):
        self.idle_time = 0
        if self.state == "SLEEPING":
            self.state = "IDLE"
        self.update()
            
    def on_typing_activity(self):
        if not self.settings.get("react_to_typing", True):
            return
        self.idle_time = 0
        if self.state == "SLEEPING":
            self.state = "IDLE"
        self.is_typing = True
        # Crucial: NEVER blink while typing!
        self.is_blinking = False
        self.blink_timer = random.randint(300, 500)
        # Hold keycaps for ~700ms after keystroke
        self.typing_timer = 24
        
        # Calculate WPM over 3.0 second sliding window
        now = time.time()
        self.keystroke_times.append(now)
        self.keystroke_times = [t for t in self.keystroke_times if now - t <= 3.0]
        # Require at least 6 keys over >= 1.2s to establish actual sustained typing speed
        if len(self.keystroke_times) >= 6:
            dt = now - self.keystroke_times[0]
            if dt >= 1.2:
                self.current_wpm = (len(self.keystroke_times) / 5.0) / (dt / 60.0)
            else:
                self.current_wpm = 0.0
        else:
            self.current_wpm = 0.0

        # Trigger angry red mode ONLY when sustained typing speed strictly exceeds 60 WPM!
        if self.current_wpm >= 60.0:
            self.is_angry = True
            self.typing_heat = min(1.0, getattr(self, 'typing_heat', 0.0) + 0.15)
        else:
            self.is_angry = False
        
        # Immediately alternate paw on key press for responsive tactile feel
        if hasattr(self, 'current_frame_index'):
            self.current_frame_index = (self.current_frame_index + 1) % 2
        self.update()
        
    def play_alarm_sound(self):
        try:
            import winsound
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

    def update_active_app_state(self):
        title = getattr(self, 'current_window_title', '').lower()
        
        # 1. Video Watching Detection (YouTube, Twitch, Netflix, Disney+, Anime, Media Players)
        watching_keywords = [
            "youtube", "twitch", "netflix", "disney+", "crunchyroll",
            "prime video", "bilibili", "vlc", "mpv", "media player",
            "potplayer", "hulu", "kick.com"
        ]
        
        # 2. Music Vibing Detection (Spotify, Apple Music, YouTube Music, SoundCloud, Tidal, etc.)
        music_keywords = [
            "spotify", "apple music", "soundcloud", "tidal", "deezer", "pandora", "amazon music"
        ]
        
        is_yt_music = "youtube music" in title or "music.youtube" in title
        is_music = is_yt_music or any(k in title for k in music_keywords) or getattr(self, '_raw_is_spotify', False)
        is_watching = not is_yt_music and any(k in title for k in watching_keywords)
        
        if is_music:
            self.is_listening_to_music = True
            self.active_app_state = "VIBING"
            self.idle_time = 0
            if self.state == "SLEEPING":
                self.state = "IDLE"
        elif is_watching:
            self.is_listening_to_music = False
            self.active_app_state = "WATCHING"
            self.idle_time = 0
            if self.state == "SLEEPING":
                self.state = "IDLE"
        else:
            self.is_listening_to_music = False
            self.active_app_state = ""

    def on_spotify_status(self, is_spotify):
        self._raw_is_spotify = is_spotify
        self.update_active_app_state()

    def on_active_window(self, title):
        self.current_window_title = title.lower()
        self.update_active_app_state()

    def get_current_animation_name(self):
        if self.state == "DRAGGED": return "DRAGGED"
        if hasattr(self, 'is_petting') and self.is_petting: return "PURRING"
        
        is_typing = getattr(self, 'is_typing', False)
        if is_typing:
            return "TYPING"
            
        app_state = getattr(self, 'active_app_state', "")
        if app_state != "":
            return app_state
            
        if self.state == "SLEEPING":
            return "SLEEPING"
            
        return self.state

    # --- Logic Updates ---
    def update_logic(self):
        if getattr(self, 'active_app_state', '') in ["WATCHING", "VIBING"]:
            self.idle_time = 0
            if self.state == "SLEEPING":
                self.state = "IDLE"
        elif not self.is_dragging:
            self.idle_time += 1
            if self.idle_time > self.SLEEP_THRESHOLD:
                self.state = "SLEEPING"
            elif self.idle_time % 6 == 0:
                self.state = "IDLE"
                self.current_frame_index = 0
                

        

        
        # Reminders
        now = datetime.now()
        reminders_to_keep = []
        for r in self.settings.get("reminders", []):
            try:
                rt = datetime.fromisoformat(r["time"])
                if now >= rt:
                    self.pinned_message = r['message']
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
                self.pinned_message = "ΓÅ░ POMODORO DONE! ΓÅ░"
                self.play_alarm_sound()

    def update_animation(self):
        self.tick_count += 1
        
        if hasattr(self, 'hearts'):
            for h in self.hearts:
                h[1] -= h[3]
                h[2] -= 3.5
                h[0] += math.sin(h[1] * 0.12) * 0.6
            self.hearts = [h for h in self.hearts if h[2] > 0]
            
            if hasattr(self, 'is_petting') and self.is_petting and self.tick_count % 3 == 0:
                self.hearts.append([random.randint(-16, 16), random.randint(-38, -15), 255.0, random.uniform(1.2, 2.0)])

        anim_name = self.get_current_animation_name()
        
        # Floating Zzzs for SLEEPING state
        if anim_name == "SLEEPING":
            if self.tick_count % 30 == 0:
                self.sleeping_zzzs.append([random.randint(4, 12), random.randint(-4, 4), 255.0, random.uniform(1.0, 1.6), random.uniform(0.0, 6.28)])
        else:
            if hasattr(self, 'sleeping_zzzs') and self.sleeping_zzzs:
                self.sleeping_zzzs.clear()
                
        if hasattr(self, 'sleeping_zzzs') and self.sleeping_zzzs:
            for z in self.sleeping_zzzs:
                z[1] -= z[3] # Float upward
                z[4] += 0.08 # Sway phase
                z[0] += math.sin(z[4]) * 0.45 + 0.35 # Drift upward and to the right
                z[2] -= 3.5 # Fade out
            self.sleeping_zzzs = [z for z in self.sleeping_zzzs if z[2] > 0]

        # Floating Musical Notes for VIBING / music playback
        is_music = (anim_name == "VIBING" or getattr(self, 'is_listening_to_music', False))
        if is_music and anim_name != "SLEEPING":
            if self.tick_count % 16 == 0:
                note_symbols = ["♫", "♪", "♬", "♩"]
                sym = random.choice(note_symbols)
                side = random.choice([-1, 1])
                ox = side * random.randint(10, 17)
                oy = random.randint(-16, -8)
                drift_speed = random.uniform(0.8, 1.4)
                note_color = random.choice([
                    QColor(255, 110, 150),  # Pastel coral pink
                    QColor(100, 210, 255),  # Cyan
                    QColor(255, 220, 100),  # Sunny gold
                    QColor(180, 140, 255)   # Lavender
                ])
                self.music_notes.append([ox, oy, 255.0, drift_speed, sym, note_color, random.uniform(0.0, 6.28)])
        else:
            if hasattr(self, 'music_notes') and self.music_notes and not is_music:
                self.music_notes.clear()

        if hasattr(self, 'music_notes') and self.music_notes:
            for n in self.music_notes:
                n[1] -= n[3]  # float upward
                n[6] += 0.10  # sway phase
                n[0] += math.sin(n[6]) * 0.4  # gentle sway
                n[2] -= 4.0   # fade out
            self.music_notes = [n for n in self.music_notes if n[2] > 0]
        
        # Fluid per-state animation speeds
        speed = 10
        if anim_name == "TYPING":
            speed = 1 if getattr(self, 'is_angry', False) else 2
        elif anim_name == "IDLE":
            speed = 14 # ~280ms per frame (calm 1.1s breathing and tail sway loop)
        elif anim_name == "DRAGGED":
            speed = 6  # ~120ms per frame (lively leg kicking and tail wiggle)
        elif anim_name == "SLEEPING":
            speed = 20 # ~400ms per frame (peaceful deep breathing)
        elif anim_name == "PURRING":
            speed = 8  # ~160ms per frame (soft purring vibration and breathing swell)
        elif anim_name == "VIBING":
            speed = 7  # ~140ms per frame (energetic rhythmic beat bounce)
        elif anim_name == "WATCHING":
            speed = 16 # ~320ms per frame (calm, attentive screen gazing)
            
        # Natural blinking logic (NEVER while typing, dragged, sleeping, or purring!)
        if getattr(self, 'is_typing', False) or anim_name in ["TYPING", "DRAGGED", "SLEEPING", "PURRING"]:
            self.is_blinking = False
            self.blink_timer = random.randint(300, 500)
        else:
            if self.is_blinking:
                self.blink_duration -= 1
                if self.blink_duration <= 0:
                    self.is_blinking = False
                    self.blink_timer = random.randint(180, 420)
            else:
                self.blink_timer -= 1
                if self.blink_timer <= 0:
                    self.is_blinking = True
                    self.blink_duration = 3

        # Update WPM sliding window
        now = time.time()
        self.keystroke_times = [t for t in self.keystroke_times if now - t <= 3.0]
        if len(self.keystroke_times) >= 6:
            dt = now - self.keystroke_times[0]
            if dt >= 1.2:
                self.current_wpm = (len(self.keystroke_times) / 5.0) / (dt / 60.0)
            else:
                self.current_wpm = 0.0
        else:
            self.current_wpm = 0.0

        if self.current_wpm < 55.0:
            self.is_angry = False

        # Heat natural cooling: if not typing > 60 WPM, decay heat to 0
        if hasattr(self, 'typing_heat') and self.typing_heat > 0:
            if not getattr(self, 'is_angry', False):
                self.typing_heat = max(0.0, self.typing_heat - 0.015)

        # FLUID MOCHI DRAG PHYSICS
        if getattr(self, 'is_dragging', False):
            # 1. Smooth scruff lift
            self.lift_offset += (24.0 - self.lift_offset) * 0.22
            
            # 2. Pendulum Tilt: opposes horizontal movement with fluid inertia
            target_tilt = max(-24.0, min(24.0, -self.drag_vx * 1.5))
            tilt_force = (target_tilt - self.wobble_angle) * 0.22
            self.wobble_vel = (self.wobble_vel + tilt_force) * 0.82
            self.wobble_angle += self.wobble_vel
            
            # 3. Fluid Mochi Stretch: stretches midsection based on vertical pull & drag speed
            drag_speed = math.hypot(self.drag_vx, self.drag_vy)
            target_stretch_rows = min(26.0, max(0.0, self.drag_vy * 0.85 + drag_speed * 0.40))
            self.current_stretch_rows += (target_stretch_rows - self.current_stretch_rows) * 0.25
            
            # Velocity decay
            self.drag_vx *= 0.86
            self.drag_vy *= 0.86
        else:
            # Dropped: fluid landing settle
            self.lift_offset += (0.0 - self.lift_offset) * 0.25
            self.wobble_angle *= 0.78
            if abs(self.wobble_angle) < 0.05:
                self.wobble_angle = 0.0
            self.wobble_vel = 0.0
            self.current_stretch_rows += (0.0 - self.current_stretch_rows) * 0.30

        # Advance frames for multi-frame animations (typing steps via keystrokes)
        if anim_name != "TYPING":
            if self.tick_count % speed == 0:
                anim_list_len = len(MATRIX_FRAMES.get(anim_name, [0]))
                self.current_frame_index = (self.current_frame_index + 1) % max(1, anim_list_len)

        if self.typing_timer > 0:
            self.typing_timer -= 1
            if self.typing_timer == 0:
                self.is_typing = False
                self.current_frame_index = 0
                
        self.update() 

    # --- Drawing ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        cx = self.width() // 2
        cy = self.height() // 2
        
        anim_name = self.get_current_animation_name()
        frames_dict = MATRIX_FRAMES
        
        if anim_name not in frames_dict:
            anim_name = "IDLE"
        anim_list = frames_dict.get(anim_name, frames_dict["IDLE"])
        if anim_name == "TYPING" and getattr(self, 'is_listening_to_music', False):
            anim_list = frames_dict.get("TYPING_MUSIC", anim_list)
        if self.current_frame_index >= len(anim_list):
            self.current_frame_index = 0
        
        frame_data = list(anim_list[self.current_frame_index])
        
        grid_w = len(frame_data[0])
        grid_h = len(frame_data)
        # High fidelity pixel sizing
        pixel_size = max(2, int(self.scale_factor))
        floor_y = cy + int(16 * pixel_size)
        
        if anim_name == "DRAGGED":
            active_drag_frame = anim_list[self.current_frame_index % len(anim_list)]
            frame_data = generate_mochi_sprite(active_drag_frame, int(getattr(self, 'current_stretch_rows', 0.0)))
            grid_w = len(frame_data[0])
            grid_h = len(frame_data)
            dest_width = grid_w * pixel_size
            dest_height = grid_h * pixel_size
            dest_x = cx - (dest_width // 2)
            dest_y = int(floor_y - dest_height - getattr(self, 'lift_offset', 0.0))
        else:
            frame_data = list(anim_list[self.current_frame_index])
            grid_w = len(frame_data[0])
            grid_h = len(frame_data)
            dest_width = grid_w * pixel_size
            dest_height = grid_h * pixel_size
            dest_x = cx - (dest_width // 2)
            dest_y = floor_y - dest_height
        
        # Override body, outline, and cute pink colors from settings
        custom_r = self.settings.get("matrix_r", 26)
        custom_g = self.settings.get("matrix_g", 26)
        custom_b = self.settings.get("matrix_b", 26)
        
        # ANGRY RED MODE ONLY WHEN SUSTAINED TYPING SPEED STRICTLY EXCEEDS 60 WPM
        heat = getattr(self, 'typing_heat', 0.0)
        is_angry = getattr(self, 'is_angry', False)
        if anim_name == "TYPING" and is_angry and heat > 0.35:
            # Smooth transition to flaming angry red (235, 40, 40)
            t = min(1.0, (heat - 0.35) / 0.50)
            cr = int(custom_r + (235 - custom_r) * t)
            cg = int(custom_g + (40 - custom_g) * t)
            cb = int(custom_b + (40 - custom_b) * t)
            cat_body_color = QColor(cr, cg, cb)
        else:
            cat_body_color = QColor(custom_r, custom_g, custom_b)
            
        MATRIX_COLORS['P'] = cat_body_color
        
        out_r = self.settings.get("matrix_outline_r", 20)
        out_g = self.settings.get("matrix_outline_g", 20)
        out_b = self.settings.get("matrix_outline_b", 20)
        MATRIX_COLORS['S'] = QColor(out_r, out_g, out_b)

        nose_r = self.settings.get("matrix_nose_r", 255)
        nose_g = self.settings.get("matrix_nose_g", 140)
        nose_b = self.settings.get("matrix_nose_b", 165)
        MATRIX_COLORS['N'] = QColor(nose_r, nose_g, nose_b)

        # 1. Ground Shadow (anchored on desktop floor)
        shadow_w = int(dest_width * (0.50 if anim_name == "DRAGGED" else 0.70))
        shadow_h = max(5, int(dest_height * 0.10))
        shadow_x = cx - shadow_w // 2
        shadow_y = floor_y - (shadow_h // 2) + 2
        
        grad = QRadialGradient(shadow_x + shadow_w / 2, shadow_y + shadow_h / 2, shadow_w / 2)
        grad.setColorAt(0.0, QColor(15, 20, 30, 70 if anim_name != "DRAGGED" else 30))
        grad.setColorAt(0.5, QColor(15, 20, 30, 30 if anim_name != "DRAGGED" else 12))
        grad.setColorAt(1.0, QColor(15, 20, 30, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(shadow_x, shadow_y, shadow_w, shadow_h)

        # 2. Scruff Pivot Physics: Natural pendulum wobble rotation
        painter.save()
        wobble = getattr(self, 'wobble_angle', 0.0)
        if anim_name == "DRAGGED" and abs(wobble) > 0.05:
            pivot_x = dest_x + dest_width / 2.0
            pivot_y = dest_y + 4.0 * pixel_size # Scruff grab point between ears
            painter.translate(pivot_x, pivot_y)
            painter.rotate(wobble)
            painter.translate(-pivot_x, -pivot_y)

        # 3. Draw Cat Matrix
        painter.setPen(Qt.PenStyle.NoPen)
        for r, row_str in enumerate(frame_data):
            for c, char in enumerate(row_str):
                if char == 'L':
                    color = QColor(min(255, custom_r + 20), min(255, custom_g + 20), min(255, custom_b + 20))
                elif char == 'D':
                    color = QColor(max(0, custom_r - 20), max(0, custom_g - 20), max(0, custom_b - 20))
                elif char in MATRIX_COLORS:
                    color = MATRIX_COLORS[char]
                else:
                    color = None
                    
                if color:
                    painter.setBrush(color)
                    px_x = int(dest_x + c * pixel_size)
                    px_y = int(dest_y + r * pixel_size)
                    painter.drawRect(px_x, px_y, pixel_size, pixel_size)

        # Rising heat steam vapors when cat is angry or hot from typing (matching Image 5 reference)
        if (is_angry or heat > 0.40) and anim_name == "TYPING":
            steam_offsets = [-7, 0, 7]
            head_cx = dest_x + int(18 * pixel_size)
            head_top_y = dest_y + int(1 * pixel_size)
            painter.setPen(Qt.PenStyle.NoPen)
            for i, sx in enumerate(steam_offsets):
                phase = (self.tick_count * 3 + i * 11) % 40
                drift_x = head_cx + int((sx + math.sin(phase * 0.3) * 1.5) * pixel_size)
                drift_y = head_top_y - int(phase * pixel_size * 0.5)
                alpha = max(0, min(250, int(255 * (1.0 - phase / 40.0))))
                steam_color = QColor(235, 40, 40, alpha)
                painter.setBrush(steam_color)
                dash_w = max(2, int(pixel_size * 0.9))
                dash_h = max(3, int(pixel_size * 2.2))
                painter.drawRect(drift_x, drift_y, dash_w, dash_h)


        # Floating Sleeping Zzzs
        if anim_name == "SLEEPING" and hasattr(self, 'sleeping_zzzs') and self.sleeping_zzzs:
            font = QFont("Segoe UI", 12, QFont.Weight.Bold)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            painter.setFont(font)
            head_x = dest_x + int(18 * pixel_size)
            head_y = dest_y + int(4 * pixel_size)
            for z in self.sleeping_zzzs:
                alpha = int(max(0, min(255, z[2])))
                painter.setPen(QColor(120, 190, 255, alpha))
                zx = int(head_x + z[0] * pixel_size * 0.4)
                zy = int(head_y + z[1] * pixel_size * 0.4)
                painter.drawText(zx, zy, "z" if alpha < 120 else "Z")

        # Floating Musical Notes for VIBING & music playback
        is_music = (anim_name == "VIBING" or getattr(self, 'is_listening_to_music', False))
        if is_music and hasattr(self, 'music_notes') and self.music_notes and anim_name != "SLEEPING":
            font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            painter.setFont(font)
            head_x = dest_x + int(13.5 * pixel_size)
            head_y = dest_y + int(4 * pixel_size)
            for n in self.music_notes:
                alpha = int(max(0, min(255, n[2])))
                col = QColor(n[5])
                col.setAlpha(alpha)
                painter.setPen(col)
                nx = int(head_x + n[0] * pixel_size * 0.45)
                ny = int(head_y + n[1] * pixel_size * 0.45)
                painter.drawText(nx, ny, n[4])

        # 5. Eye Rendering (Active Real-time Mouse Eye Follow for IDLE & TYPING)
        # Eye tracking is active in BOTH IDLE and TYPING (and VIBING/WATCHING)!
        has_dynamic_eyes = (anim_name in ["IDLE", "TYPING", "VIBING", "WATCHING"])
        
        if anim_name == "PURRING" or (hasattr(self, 'is_petting') and self.is_petting):
            # Rosy blushing cheeks!
            blush_color = QColor(255, 110, 150, 180)
            painter.setBrush(blush_color)
            painter.setPen(Qt.PenStyle.NoPen)
            ps = pixel_size
            painter.drawEllipse(int(dest_x + 6.5 * ps), int(dest_y + 12 * ps), int(4 * ps), int(2.5 * ps))
            painter.drawEllipse(int(dest_x + 18.5 * ps), int(dest_y + 12 * ps), int(4 * ps), int(2.5 * ps))

        elif getattr(self, 'is_blinking', False) and anim_name != "DRAGGED":
            # Natural blinking: clean sleeping slit _ _ across row 10 (IDLE) or row 13 (TYPING)
            ps = pixel_size
            painter.setPen(Qt.PenStyle.NoPen)
            if anim_name == "TYPING":
                # Cover typing eyes with body color and draw clean horizontal slits
                painter.setBrush(cat_body_color)
                painter.drawRect(int(dest_x + 11 * ps), int(dest_y + 11 * ps), int(5 * ps), int(5 * ps))
                painter.drawRect(int(dest_x + 20 * ps), int(dest_y + 11 * ps), int(5 * ps), int(5 * ps))
                painter.setBrush(QColor(255, 255, 255))
                painter.drawRect(int(dest_x + 11 * ps), int(dest_y + 13 * ps), int(5 * ps), ps)
                painter.drawRect(int(dest_x + 20 * ps), int(dest_y + 13 * ps), int(5 * ps), ps)
            else:
                # Cover idle eyes with body color and draw clean horizontal slits
                painter.setBrush(cat_body_color)
                painter.drawRect(int(dest_x + 6 * ps), int(dest_y + 8 * ps), int(5 * ps), int(5 * ps))
                painter.drawRect(int(dest_x + 17 * ps), int(dest_y + 8 * ps), int(5 * ps), int(5 * ps))
                painter.setBrush(QColor(255, 255, 255))
                painter.drawRect(int(dest_x + 6 * ps), int(dest_y + 10 * ps), int(5 * ps), ps)
                painter.drawRect(int(dest_x + 17 * ps), int(dest_y + 10 * ps), int(5 * ps), ps)

        elif has_dynamic_eyes:
            # Active Real-time Mouse Eye Follow for BOTH eyes (works in IDLE AND TYPING)!
            mouse_pos = QCursor.pos()
            cat_global = self.mapToGlobal(QPoint(int(cx), int(cy)))
            dx = mouse_pos.x() - cat_global.x()
            dy = mouse_pos.y() - cat_global.y()
            dist = math.hypot(dx, dy)
            
            # Gaze offset inside the 3x3 eye socket (-1, 0, or +1 pixel):
            if dist > 25:
                gaze_x = int(round(max(-1.0, min(1.0, dx / (dist * 0.7)))))
                gaze_y = int(round(max(-1.0, min(1.0, dy / (dist * 0.7)))))
            else:
                gaze_x = 0
                gaze_y = 0
                
            ps = pixel_size
            painter.setBrush(QColor(255, 255, 255))
            painter.setPen(Qt.PenStyle.NoPen)
            
            if anim_name == "TYPING":
                # In TYPING, eyes are centered at col 13 and col 22, row 13
                lx = int(dest_x + (13 + gaze_x) * ps)
                ly = int(dest_y + (13 + gaze_y) * ps)
                painter.drawRect(lx, ly, ps, ps)
                
                rx = int(dest_x + (22 + gaze_x) * ps)
                ry = int(dest_y + (13 + gaze_y) * ps)
                painter.drawRect(rx, ry, ps, ps)
            else:
                # In IDLE_32 (and WATCHING, VIBING), eyes are centered at col 8 and col 19, row 10
                lx = int(dest_x + (8 + gaze_x) * ps)
                ly = int(dest_y + (10 + gaze_y) * ps)
                painter.drawRect(lx, ly, ps, ps)
                
                rx = int(dest_x + (19 + gaze_x) * ps)
                ry = int(dest_y + (10 + gaze_y) * ps)
                painter.drawRect(rx, ry, ps, ps)


        # Restore coordinate space for speech bubble
        painter.restore()

        # 7. Speech Bubble / Reminders / Pomodoro
        msg_to_draw = None
        if hasattr(self, 'pinned_message') and self.pinned_message:
            msg_to_draw = self.pinned_message
        elif hasattr(self, 'pomo_active') and self.pomo_active:
            mins = self.pomo_seconds // 60
            secs = self.pomo_seconds % 60
            msg_to_draw = f"🍅 {mins:02d}:{secs:02d}"

        if msg_to_draw:
            font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            painter.setFont(font)
            fm = painter.fontMetrics()
            
            lines = msg_to_draw.split('\n')
            max_w = max(fm.horizontalAdvance(l) for l in lines)
            pad_x = 16
            pad_y = 10
            bubble_w = max(max_w + (pad_x * 2), 70)
            bubble_h = len(lines) * fm.height() + (pad_y * 2)
            
            dest_cat_y = dest_y
            bx = cx - (bubble_w / 2)
            by = dest_cat_y - bubble_h - 14
            
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setBrush(QColor(255, 255, 255, 245))
            painter.setPen(QColor(180, 185, 200, 180))
            painter.drawRoundedRect(int(bx), int(by), int(bubble_w), int(bubble_h), 12, 12)
            
            # Pointer tail pointing down to cat head
            pointer = QPolygonF([
                QPointF(cx - 7, by + bubble_h),
                QPointF(cx + 7, by + bubble_h),
                QPointF(cx, by + bubble_h + 9)
            ])
            painter.setBrush(QColor(255, 255, 255, 245))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(pointer)
            
            painter.setPen(QColor(180, 185, 200, 180))
            painter.drawLine(QPointF(cx - 7, by + bubble_h), QPointF(cx, by + bubble_h + 9))
            painter.drawLine(QPointF(cx + 7, by + bubble_h), QPointF(cx, by + bubble_h + 9))
            
            # Text rendering
            painter.setPen(QColor(30, 35, 45))
            y_start = int(by + pad_y + fm.ascent())
            for l in lines:
                text_x = int(bx + (bubble_w - fm.horizontalAdvance(l)) / 2)
                painter.drawText(text_x, y_start, l)
                y_start += fm.height()

        # 8. Floating Love Hearts (only during purring or petting)
        if (anim_name == "PURRING" or getattr(self, 'is_petting', False)) and hasattr(self, 'hearts') and self.hearts:
            heart_matrix = [
                ".XX.XX.",
                "XXXXXXX",
                "XXXXXXX",
                ".XXXXX.",
                "..XXX..",
                "...X..."
            ]
            painter.setPen(Qt.PenStyle.NoPen)
            ps = 2
            for h in self.hearts:
                alpha = int(max(0, min(255, h[2])))
                hx = int(cx + h[0])
                hy = int(cy + h[1])
                
                fill_color = QColor(255, 75, 115, alpha)
                highlight_color = QColor(255, 185, 205, alpha)
                
                for r_idx, row in enumerate(heart_matrix):
                    for c_idx, ch in enumerate(row):
                        if ch == 'X':
                            px = hx + (c_idx - 3) * ps
                            py = hy + (r_idx - 3) * ps
                            if r_idx == 1 and c_idx in (1, 4):
                                painter.setBrush(highlight_color)
                            else:
                                painter.setBrush(fill_color)
                            painter.drawRect(px, py, ps, ps)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_press_pos = event.globalPosition().toPoint()
            self.last_drag_pos = event.globalPosition().toPoint()
            self.drag_has_started = False
            self.drag_vx = 0.0
            self.drag_vy = 0.0
            self.wobble_angle = 0.0
            self.wobble_vel = 0.0

    def mouseMoveEvent(self, event):
        if getattr(self, 'mouse_press_pos', None):
            curr_pos = event.globalPosition().toPoint()
            if not getattr(self, 'drag_has_started', False):
                dist = math.hypot(curr_pos.x() - self.mouse_press_pos.x(), curr_pos.y() - self.mouse_press_pos.y())
                if dist >= 4:
                    self.drag_has_started = True
                    self.is_dragging = True
                    self.is_petting = False
                    self.state = "DRAGGED"
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
            
            if getattr(self, 'is_dragging', False):
                dx = curr_pos.x() - self.last_drag_pos.x()
                dy = curr_pos.y() - self.last_drag_pos.y()
                self.last_drag_pos = curr_pos
                self.move(self.x() + dx, self.y() + dy)
                # Fluid velocity tracking
                self.drag_vx = self.drag_vx * 0.65 + dx * 0.35
                self.drag_vy = self.drag_vy * 0.65 + dy * 0.35
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            was_dragging = getattr(self, 'drag_has_started', False)
            self.is_dragging = False
            self.drag_has_started = False
            self.mouse_press_pos = None
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            if was_dragging:
                self.state = "IDLE"
                self.idle_time = 0
            else:
                # Petting / Purring on click!
                self.state = "PURRING"
                self.is_petting = True
                self.idle_time = 0
                for _ in range(5):
                    self.hearts.append([random.randint(-16, 16), random.randint(-35, -15), 255.0, random.uniform(1.2, 2.0)])
                QTimer.singleShot(3000, self.reset_to_idle)
            self.update()

    def reset_to_idle(self):
        if self.state == "PURRING":
            self.state = "IDLE"
            self.is_petting = False
            self.update()

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

