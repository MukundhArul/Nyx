import sys
import time
import psutil
import os
import json
import math
import random
from datetime import datetime
import ctypes
from ctypes import wintypes
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import (QApplication, QWidget, QMenu, QInputDialog, QSystemTrayIcon,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSlider, QCheckBox, 
                             QLineEdit, QPushButton, QDateTimeEdit, QSpinBox, QGroupBox,
                             QTabWidget, QTabBar)
# pyrefly: ignore [missing-import]
from PyQt6.QtGui import (QPainter, QCursor, QColor, QAction, QFont, QPixmap,
                         QIcon, QPolygonF, QPen, QRadialGradient, QRegion)
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QRectF, QTimer, pyqtSignal, QThread, QDateTime
from pynput import mouse, keyboard
# pyrefly: ignore [missing-import]
import pygetwindow as gw

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "scale_factor": 3.0,
    "react_to_typing": True,
    "stretch_interval_min": 30,
    "water_interval_min": 60,
    "pomodoro_enabled": False,
    "pomo_focus_min": 25,
    "pomo_break_min": 5,
    "reminders": [],
    "always_on_top": True,
    "matrix_r": 24,
    "matrix_g": 24,
    "matrix_b": 27,
    "matrix_outline_r": 20,
    "matrix_outline_g": 20,
    "matrix_outline_b": 20,
    "coat_preset": "black",
    "accessory": "none"
}

ACCESSORIES = {
    "none": {
        "name": "None",
        "icon": "❌",
        "desc": "Natural Nyx without accessories",
        "sprite": [],
        "colors": {},
        "offsets": {},
    },
    "crown": {
        "name": "Golden Crown",
        "icon": "👑",
        "desc": "Grand royal gold crown with sparkling jewel insets",
        "sprite": [
            ".W.....W.....W.",
            "WGW...WGW...WGW",
            "WGGW.WGGGW.WGGW",
            "WGGGWWGGGWGGGGW",
            "WGgGGggGGggGGgW",
            "WGRBgRGBggGRBgW",
            "WGGGGGGGGGGGGGW",
            ".WGGGGGGGGGGGW.",
            "..WWWWWWWWWWW..",
        ],
        "colors": {
            'W': QColor(255, 255, 255),
            'G': QColor(255, 215, 0),
            'g': QColor(220, 145, 0),
            'R': QColor(255, 30, 70),
            'B': QColor(0, 220, 255),
            '#': QColor(50, 35, 0),
        },
        "offsets": {
            "IDLE": (6, -5),
            "DRAGGED": (6, -5),
            "SLEEPING": (6, -5),
        }
    },
    "wizard": {
        "name": "Wizard Hat",
        "icon": "🧙",
        "desc": "Grand mystical purple hat with glowing golden star band",
        "sprite": [
            "........YYY......",
            "........YYY......",
            ".........W.......",
            "........WPPW.....",
            ".......WPpPW.....",
            ".......WPPPW.....",
            "......WPpPPW.....",
            "......WPPPPW.....",
            ".....WPPpPPPW....",
            "....WPPPPPPPW....",
            "...WYYYYYYYYYW...",
            "...WYgBggBgGYW...",
            "..WPPPPPPPPPPPW..",
            ".WWWWWWWWWWWWWWW.",
            ".###############.",
        ],
        "colors": {
            'W': QColor(255, 255, 255),
            'P': QColor(138, 65, 225),
            'p': QColor(78, 30, 140),
            'Y': QColor(255, 215, 0),
            'g': QColor(215, 140, 0),
            'B': QColor(0, 230, 255),
            '#': QColor(25, 12, 45),
        },
        "offsets": {
            "IDLE": (5, -10),
            "DRAGGED": (5, -10),
            "SLEEPING": (5, -10),
        }
    },
    "party": {
        "name": "Party Hat",
        "icon": "🎉",
        "desc": "Joyful festive party cone hat with confetti stripes & pom-pom",
        "sprite": [
            "....WW....",
            "...WYYW...",
            "....##....",
            "...#CC#...",
            "..#CCCC#..",
            "..#YYYY#..",
            ".#YYYYYY#.",
            ".#MMMMMM#.",
            "#MMMMMMMM#",
            "#WWWWWWWW#",
        ],
        "colors": {
            'W': QColor(255, 255, 255),
            'Y': QColor(255, 215, 0),
            'C': QColor(0, 215, 235),
            'M': QColor(245, 55, 140),
            '#': QColor(40, 25, 50),
        },
        "offsets": {
            "IDLE": (8, -7),
            "DRAGGED": (8, -7),
            "SLEEPING": (8, -7),
        }
    }
}

COAT_PRESETS = {
    "black": {
        "name": "Midnight Black",
        "icon": "🌑",
        "r": 24, "g": 24, "b": 27,
        "outline_r": 20, "outline_g": 20, "outline_b": 20,
        "nose_r": 255, "nose_g": 140, "nose_b": 165,
        "hex": "#18181B",
        "desc": "Classic sleek obsidian midnight shade"
    },
    "charcoal": {
        "name": "Charcoal Slate",
        "icon": "🌪️",
        "r": 72, "g": 78, "b": 92,
        "outline_r": 40, "outline_g": 44, "outline_b": 54,
        "nose_r": 255, "nose_g": 150, "nose_b": 170,
        "hex": "#484E5C",
        "desc": "Cool smoky graphite slate shade"
    },
    "navy": {
        "name": "Abyssal Navy",
        "icon": "🌊",
        "r": 34, "g": 56, "b": 96,
        "outline_r": 18, "outline_g": 30, "outline_b": 54,
        "nose_r": 255, "nose_g": 145, "nose_b": 175,
        "hex": "#223860",
        "desc": "Deep oceanic midnight starlight blue"
    },
    "espresso": {
        "name": "Espresso Brown",
        "icon": "☕",
        "r": 84, "g": 52, "b": 38,
        "outline_r": 48, "outline_g": 28, "outline_b": 20,
        "nose_r": 255, "nose_g": 155, "nose_b": 160,
        "hex": "#543426",
        "desc": "Rich roasted coffee mocha brown"
    }
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
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WPPPPPPPPPPPPPPPPPWW.....WWW",
            "....WWPPPPPPPPPPPPPPPWW.....WPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPWPPPW..",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WWPPPPPPPPPPPPPPPWW...WWWW..",
            "....WPPPPPPPPPPPPPPPPPWW.WPPPPW.",
            "...WWPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            ".............PP.........PPP...................",
            "............PPPPWWWWWWWWWPPP..................",
            "............PPPWMMMMMMMMMWPP..................",
            "........WWWWPPWMPPPPPPPPPMWWWWW...............",
            ".......WMMMMWMPPPPPPPPPPPPWMMMMW..............",
            ".......WMMMMWPPPPPPPPPPPPPWMMMMW..............",
            ".......WMMMMWPPPPPPPPPPPPPWMMMMW..............",
            ".......WMMMMWPPPPPPPPPPPPPWMMMMW..............",
            "........WWWWPPPPPPPPPPPPPPPWWWW..........PP...",
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
            "............PPPPWWWWWWWWWPPP..................",
            "............PPPWMMMMMMMMMWPP..................",
            "........WWWWPPWMPPPPPPPPPMWWWWW...............",
            ".......WMMMMWMPPPPPPPPPPPPWMMMMW..............",
            ".......WMMMMWPPPPPPPPPPPPPWMMMMW..............",
            ".......WMMMMWPPPPPPPPPPPPPWMMMMW..............",
            ".......WMMMMWPPPPPPPPPPPPPWMMMMW..............",
            "........WWWWPPPPPPPPPPPPPPPWWWW...............",
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
            "...WPWWPPWPPPPPPWPPWWPPWW.......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "...WPWWPPWPPPPPPWPPWWPPWW.......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW.....WWW",
            "....WWPPPPPPPPPPPPPPPWW.....WPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPWPPPW..",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "...WPWWPPWPPPPPPWPPWWPPWW.......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW...WWWW..",
            "....WPPPPPPPPPPPPPPPPPWW.WPPPPW.",
            "...WWPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "...WPPPPPPPPPPPPPPPPPPPPW.......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW.....WWW",
            "....WWPPPPPPPPPPPPPPPWW.....WPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPWPPPW..",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            ".....WWPPPPPPPPPPPPPPWWPPPPPW...",
            ".....WPPPPPPPPPPPPPPPPPPPPPW....",
            ".....WPPPPPPPPPPPPPPPPPPPPW.....",
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
            ".....WWPPPPPPPPPPPPPPWWPPPPPW...",
            ".....WPPPPPPPPPPPPPPPPPPPPPW....",
            ".....WPPPPPPPPPPPPPPPPPPPPW.....",
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
            ".....WWPPPPPPPPPPPPPPWWPPPPPPW..",
            ".....WPPPPPPPPPPPPPPPPPPWWPPW...",
            ".....WPPPPPPPPPPPPPPPPPPPPPW....",
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
            "......WWPWWWWWWWWWPWW...........",
            ".....WWPPWMMMMMMMMWPWW..........",
            ".....WPPWMWWWWWWWPMWPW..........",
            "..WWWWMWMPPPPPPPPPPMWMWWWW......",
            ".WMMMWPPPPPPPPPPPPPPPWWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            "..WWWWPWWWPPPPPPPWWWPPWWWW......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPWWWWWWWWWPWW...........",
            ".....WWPPWMMMMMMMMWPWW..........",
            ".....WPPWMWWWWWWWPMWPW..........",
            "..WWWWMWMPPPPPPPPPPMWMWWWW......",
            ".WMMMWPPPPPPPPPPPPPPPWWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            "..WWWWPWWWPPPPPPPWWWPPWWWW......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW.....WWW",
            "....WWPPPPPPPPPPPPPPPWW.....WPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPWPPPW..",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPWWWWWWWWWPWW...........",
            ".....WWPPWMMMMMMMMWPWW..........",
            ".....WPPWMWWWWWWWPMWPW..........",
            "..WWWWMWMPPPPPPPPPPMWMWWWW......",
            ".WMMMWPPPPPPPPPPPPPPPWWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            "..WWWWPWWWPPPPPPPWWWPPWWWW......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW........",
            "....WWPPPPPPPPPPPPPPPWW...WWWW..",
            "....WPPPPPPPPPPPPPPPPPWW.WPPPPW.",
            "...WWPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
            "........WWWWWWWWWWWW............",
        ],
        [
            ".......WWW.......WWW............",
            "......WWPWWWWWWWWWPWW...........",
            ".....WWPPWMMMMMMMMWPWW..........",
            ".....WPPWMWWWWWWWPMWPW..........",
            "..WWWWMWMPPPPPPPPPPMWMWWWW......",
            ".WMMMWPPPPPPPPPPPPPPPWWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            ".WMMMWPPPPPPPPPPPPPPPPWMMMW.....",
            "..WWWWPWWWPPPPPPPWWWPPWWWW......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "...WPPWPPPWPPPPPPWPPPWPPW.......",
            "WWWWPPWPPPWPPPPPPWPPPWPPWWWW....",
            "...WPPPWWWPPPPPPPPWWWPPPPW......",
            "WWWWPPPPPPPPPPPPPPPPPPPPPWWWW...",
            "...WPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW......",
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WPPPPPPPPPPPPPPPPPWW.....WWW",
            "....WWPPPPPPPPPPPPPPPWW.....WPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPWW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPW..WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPPWW.WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPPWPPPW.",
            "....WPPPPPPPPPPPPPPPPPPPPWPPPW..",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WWPPPPPPPPPPPPPPPWW...WWWW..",
            "....WPPPPPPPPPPPPPPPPPWW.WPPPPW.",
            "...WWPPPPPPPPPPPPPPPPPPW.WPPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
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
            "....WPPPPPPPPPPPPPPPPPWW....WWW.",
            "....WWPPPPPPPPPPPPPPPWW....WPPPW",
            "....WPPPPPPPPPPPPPPPPPWW...WPPPW",
            "...WWPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW...WPPPW",
            "...WPPPPPPPPPPPPPPPPPPPW..WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPWW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPW.WPPPW.",
            "...WPPPPPPPPPPPPPPPPPPPPWWPPPW..",
            "...WWPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWPPPPPPPPPPPPWWWWPPPPW...",
            "......WWWWPPWWWWPPWWWWWWWWWWW...",
            "........WWWWWWWWWWWW............",
        ],
    ],
    'STRETCHING': [
        [
            ".......................................................",
            ".........WWW........WWW................................",
            "........WWPWW......WWPWW...............................",
            ".......WWPPWWW....WWPPPWW.......................WWWW...",
            ".......WPPPPWW....WWPPPPW........WWWWWWW.......WWPPWW..",
            "......WWPPPPPWWWWWWPPPPPW......WWWPPPPPWWW.....WPPPPWW.",
            "......WPPPPPPPPPPPPPPPPPW....WWWPPPPPPPPPWWW...WPPPPPW.",
            "......WPPPPPPPPPPPPPPPPPW...WWPPPPPPPPPPPPPW...WPPPPPW.",
            "......WPPPPPPPPPPPPPPPPPWWWWWPPPPPPPPPPPPPPWW..WWPPPPW.",
            ".....WWPPPPPPPPPPPPPPPPPPWWPPPPPPPPPPPPPPPPPWWWWPPPPPW.",
            ".....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWWPPPPPPPW.",
            "....WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW.",
            "....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW..",
            "....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWWW...",
            "....WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPPWWWW.....",
            "WWWWWWPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPPW........",
            "....WPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPPW........",
            "WWWWWWPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPPW........",
            "....WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPPW........",
            "....WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW........",
            ".....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW........",
            ".....WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            "......WWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            ".........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            ".........WPPPPPPPWWPPPPPPPWWWWPPPPPPWWPPPPPPPW.........",
            ".........WPPPPPPPWWPPPPPPPWPWWPPPPPPWWPPPPPPPW.........",
            "........WWPPPPPPPWWPPPPPPPPWWPPPPPPPWWPPPPPPPW.........",
            "........WPPPPPPPPPPPPPPPPPPWPPPPPPPPWWPPPPPPPW.........",
            "........WPPPPPPPPPPPPPPPPWWWWPPPPPPWWPPPPPPPWW.........",
            "........WPPPPPPPWWPPPPPPPWW.WPPPPPPW.WPPPPPPW..........",
            ".......WWPPPPPPPWWPPPPPPWW..WPPPPPPW.WPPPPPPW..........",
            ".......WPPPPPPPPPPPPPPPPW...WPPPPPPW.WPPPPPPW..........",
            ".......WPPPPPPPWWPPPPPPPW...WWPPPPWW.WWPPPPWW..........",
            ".......WPPPPPPPWWPPPPPPPW....WWWWWW...WWWWWW...........",
            ".......WWPPPPPWWWWPPPPPWW..............................",
            "........WWWWWWW..WWWWWWW...............................",
        ],
        [
            "................................................WWWW...",
            "...............................................WWPPWW..",
            "...............................................WPPPPWW.",
            "............WWW........WWW.....................WPPPPPW.",
            "...........WWPWW......WWPWW.........WWWWWWW....WPPPPPW.",
            "..........WWPPWWW....WWPPPPW......WWWPPPPPPWW..WWPPPPWW",
            "..........WPPPPWW....WWPPPPW....WWWPPPPPPPPPWWWWPPPPPWW",
            ".........WWPPPPPWWWWWWPPPPPW...WWPPPPPPPPPPPPPPPPPPPPWW",
            ".........WPPPPPPPPPPPPPPPPPW.WWWPPPPPPPPPPPPPPPPPPPPPWW",
            ".........WPPPPPPPPPPPPPPPPPWWWPPPPPPPPPPPPPPPPPPPPPPWW.",
            ".........WPPPPPPPPPPPPPPPPPWPPPPPPPPPPPPPPPPPPPPPPWWW..",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW....",
            "........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW.....",
            ".......WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWWWWPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWWWWPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            "........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            "......WWPPPPPPPPPPPPPPPPPPWWWWWWWWWWPPPPPPWPPPPPW......",
            ".....WWPPPPPPPPPPPPPPPPPPWW.......WWPPPPPWWPPPPPW......",
            "....WWPPPPPPPPPPPPPPPPPPWW........WPPPPPPWWPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW........WPPPPPPWWPPPPW.......",
            "..WWPPPPPPPPPPPPPPPPPPPWW.........WPPPPPPWWPPPPW.......",
            "..WPPPPPPPPPPPPPPPPPPPPW..........WPPPPPPWWPPPPW.......",
            "..WPPPPPPPPPPPPPPPPPPPW...........WWPPPPPWWWPPPWW......",
            "..WWPPPPPPPPPPPPPPPPPWW............WWWWWWW.WWWWWW......",
            "...WWPPPPPPWWPPPPPPWWW.................................",
            "....WWPPPPWWWWPPPPWW...................................",
            ".....WWWWWW..WWWWWW....................................",
            ".......................................................",
        ],
        [
            "...............................................WWWW....",
            "..............................................WWPPWW...",
            "..............................................WPPPPWWW.",
            "..............................................WPPPPPWW.",
            "..............................................WPPPPPPW.",
            "..............................................WWPPPPPW.",
            ".............WWWW........WWW.........WWWWWWWW.WWPPPPPW.",
            "............WWPPWW......WWPPWW......WWWPPPPPWWWPPPPPPW.",
            "...........WWPPPWW.....WWPPPWW....WWPPPPPPPPPPPPPPPPWW.",
            "...........WPPPPPWW...WWPPPPPW...WWPPPPPPPPPPPPPPPPWW..",
            "..........WWPPPPPPWWWWWPPPPPPW.WWWPPPPPPPPPPPPPPPPWW...",
            "..........WWPPPPPPPPPPPPPPPPPWWPPPPPPPPPPPPPPPPPPWW....",
            "..........WWPPPPPPPPPPPPPPPPPWPPPPPPPPPPPPPPPPPPPWW....",
            "..........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "..........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "..........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "........WPPWWPPPPPPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPWW...",
            "....WWWWWPPPPWWPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW...",
            "........WPPPPPPWWPPWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWWPPPPWWPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW...",
            "........WPPWWPPPPPPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPWW...",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "..........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".......WWWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".....WWWPPPPPPPPPPPPPPPPPPPPWWWWWWWWWWPPPPPPWPPPPPW....",
            "...WWWPPPPPPPPPPPPPPPPPPPPPWW.......WWPPPPPWWPPPPWW....",
            "..WWPPPPPPPPPPPPPPPPPPPPPPWW........WWPPPPPWWPPPPW.....",
            ".WWPPPPPPPPPPPPPPPPPPPPPWWW.........WPPPPPPWWPPPPW.....",
            ".WPPPPPPPPPPPPPPPPPPPPPWW...........WPPPPPPWWPPPPW.....",
            ".WPPPPPPPPPPPPPPPPPPPPWW............WWPPPPPWWWPPPWW....",
            ".WWPPPPPPPPPPPPPPPPPPWW..............WWWWWWW..WWWWW....",
            "..WWPPPPPPPWWPPPPPPWWW.................................",
            "...WWWWPPPWWWWPPPPWW...................................",
            "......WWWWW..WWWWWW....................................",
            ".......................................................",
        ],
        [
            "...............................................WWWW....",
            "..............................................WWPPWW...",
            "..............................................WPPPPWWW.",
            "..............................................WPPPPPWW.",
            "..............................................WPPPPPPW.",
            "..............................................WWPPPPPW.",
            ".............WWWW........WWW.........WWWWWWWW.WWPPPPPW.",
            "............WWPPWW......WWPPWW......WWWPPPPPWWWPPPPPPW.",
            "...........WWPPPWW.....WWPPPWW....WWPPPPPPPPPPPPPPPPWW.",
            "...........WPPPPPWW...WWPPPPPW...WWPPPPPPPPPPPPPPPPWW..",
            "..........WWPPPPPPWWWWWPPPPPPW.WWWPPPPPPPPPPPPPPPPWW...",
            "..........WWPPPPPPPPPPPPPPPPPWWPPPPPPPPPPPPPPPPPPWW....",
            "..........WWPPPPPPPPPPPPPPPPPWPPPPPPPPPPPPPPPPPPPWW....",
            "..........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "..........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "..........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "........WPPWWPPPPPPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPWW...",
            "....WWWWWPPPPWWPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW...",
            "........WPPPPPPWWPPWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW...",
            "....WWWWWPPPPWWPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW...",
            "........WPPWWPPPPPPPPPPWWPPPPPPPPPPPPPPPPPPPPPPPPPWW...",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            "..........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".......WWWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW....",
            ".....WWWPPPPPPPPPPPPPPPPPPPPWWWWWWWWWWPPPPPPWPPPPPW....",
            "...WWWPPPPPPPPPPPPPPPPPPPPPWW.......WWPPPPPWWPPPPWW....",
            "..WWPPPPPPPPPPPPPPPPPPPPPPWW........WWPPPPPWWPPPPW.....",
            ".WWPPPPPPPPPPPPPPPPPPPPPWWW.........WPPPPPPWWPPPPW.....",
            ".WPPPPPPPPPPPPPPPPPPPPPWW...........WPPPPPPWWPPPPW.....",
            ".WPPPPPPPPPPPPPPPPPPPPWW............WWPPPPPWWWPPPWW....",
            ".WWPPPPPPPPPPPPPPPPPPWW..............WWWWWWW..WWWWW....",
            "..WWPPPPPPPWWPPPPPPWWW.................................",
            "...WWWWPPPWWWWPPPPWW...................................",
            "......WWWWW..WWWWWW....................................",
            ".......................................................",
        ],
        [
            "................................................WWWW...",
            "...............................................WWPPWW..",
            "...............................................WPPPPWW.",
            "............WWW........WWW.....................WPPPPPW.",
            "...........WWPWW......WWPWW.........WWWWWWW....WPPPPPW.",
            "..........WWPPWWW....WWPPPPW......WWWPPPPPPWW..WWPPPPWW",
            "..........WPPPPWW....WWPPPPW....WWWPPPPPPPPPWWWWPPPPPWW",
            ".........WWPPPPPWWWWWWPPPPPW...WWPPPPPPPPPPPPPPPPPPPPWW",
            ".........WPPPPPPPPPPPPPPPPPW.WWWPPPPPPPPPPPPPPPPPPPPPWW",
            ".........WPPPPPPPPPPPPPPPPPWWWPPPPPPPPPPPPPPPPPPPPPPWW.",
            ".........WPPPPPPPPPPPPPPPPPWPPPPPPPPPPPPPPPPPPPPPPWWW..",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW....",
            "........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW.....",
            ".......WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWWWWPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPW......",
            "...WWWWWPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            "........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            ".......WWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW......",
            "......WWPPPPPPPPPPPPPPPPPPWWWWWWWWWWPPPPPPWPPPPPW......",
            ".....WWPPPPPPPPPPPPPPPPPPWW.......WWPPPPPWWPPPPPW......",
            "....WWPPPPPPPPPPPPPPPPPPWW........WPPPPPPWWPPPPWW......",
            "...WWPPPPPPPPPPPPPPPPPPPWW........WPPPPPPWWPPPPW.......",
            "..WWPPPPPPPPPPPPPPPPPPPWW.........WPPPPPPWWPPPPW.......",
            "..WPPPPPPPPPPPPPPPPPPPPW..........WPPPPPPWWPPPPW.......",
            "..WPPPPPPPPPPPPPPPPPPPW...........WWPPPPPWWWPPPWW......",
            "..WWPPPPPPPPPPPPPPPPPWW............WWWWWWW.WWWWWW......",
            "...WWPPPPPPWWPPPPPPWWW.................................",
            "....WWPPPPWWWWPPPPWW...................................",
            ".....WWWWWW..WWWWWW....................................",
            ".......................................................",
        ],
        [
            ".......................................................",
            ".........WWW........WWW................................",
            "........WWPWW......WWPWW...............................",
            ".......WWPPWWW....WWPPPWW.......................WWWW...",
            ".......WPPPPWW....WWPPPPW........WWWWWWW.......WWPPWW..",
            "......WWPPPPPWWWWWWPPPPPW......WWWPPPPPWWW.....WPPPPWW.",
            "......WPPPPPPPPPPPPPPPPPW....WWWPPPPPPPPPWWW...WPPPPPW.",
            "......WPPPPPPPPPPPPPPPPPW...WWPPPPPPPPPPPPPW...WPPPPPW.",
            "......WPPPPPPPPPPPPPPPPPWWWWWPPPPPPPPPPPPPPWW..WWPPPPW.",
            ".....WWPPPPPPPPPPPPPPPPPPWWPPPPPPPPPPPPPPPPPWWWWPPPPPW.",
            ".....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWWPPPPPPPW.",
            "....WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW.",
            "....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW..",
            "....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWWW...",
            "....WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPPWWWW.....",
            "WWWWWWPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPPW........",
            "....WPPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPPW........",
            "WWWWWWPPWPPPWPPPPPPWPPPWPPPPPPPPPPPPPPPPPPPPPPW........",
            "....WPPPPWWWWPPPPPPPWWWWPPPPPPPPPPPPPPPPPPPPPPW........",
            "....WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW........",
            ".....WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPWW........",
            ".....WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            "......WWWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            "........WWPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            ".........WPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW.........",
            ".........WPPPPPPPWWPPPPPPPWWWWPPPPPPWWPPPPPPPW.........",
            ".........WPPPPPPPWWPPPPPPPWPWWPPPPPPWWPPPPPPPW.........",
            "........WWPPPPPPPWWPPPPPPPPWWPPPPPPPWWPPPPPPPW.........",
            "........WPPPPPPPPPPPPPPPPPPWPPPPPPPPWWPPPPPPPW.........",
            "........WPPPPPPPPPPPPPPPPWWWWPPPPPPWWPPPPPPPWW.........",
            "........WPPPPPPPWWPPPPPPPWW.WPPPPPPW.WPPPPPPW..........",
            ".......WWPPPPPPPWWPPPPPPWW..WPPPPPPW.WPPPPPPW..........",
            ".......WPPPPPPPPPPPPPPPPW...WPPPPPPW.WPPPPPPW..........",
            ".......WPPPPPPPWWPPPPPPPW...WWPPPPWW.WWPPPPWW..........",
            ".......WPPPPPPPWWPPPPPPPW....WWWWWW...WWWWWW...........",
            ".......WWPPPPPWWWWPPPPPWW..............................",
            "........WWWWWWW..WWWWWWW...............................",
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
        self.setFixedSize(380, 530)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e24;
                color: #e0e0e0;
                font-family: Arial;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #36364c;
                background-color: #1e1e28;
                border-radius: 6px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #2b2b36;
                color: #a0a0a0;
                padding: 8px 14px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background-color: #5c6bc0;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #383848;
                color: #ffffff;
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

        # Root Layout with TabWidget
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(10, 10, 10, 10)
        
        self.tabs = QTabWidget()
        
        # ==========================================
        # TAB 1: 🎩 WARDROBE (Ribbons & Hats)
        # ==========================================
        tab_wardrobe = QWidget()
        wardrobe_layout = QVBoxLayout()
        wardrobe_layout.setContentsMargins(10, 12, 10, 10)
        wardrobe_layout.setSpacing(10)
        
        w_title = QLabel("Nyx's Wardrobe")
        w_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        wardrobe_layout.addWidget(w_title)
        
        w_desc = QLabel("Equip an adorable pixel accessory for Nyx to wear:")
        w_desc.setStyleSheet("color: #a0a5b5; font-size: 11px;")
        wardrobe_layout.addWidget(w_desc)
        
        self.acc_buttons = []
        acc_list = [
            ("none", "None", "❌", "Natural Nyx without accessories"),
            ("crown", "Golden Crown", "👑", "Grand royal gold crown with sparkling jewel insets"),
            ("wizard", "Wizard Hat", "🧙", "Grand mystical purple hat with glowing star band"),
            ("party", "Party Hat", "🎉", "Joyful festive party cone hat with confetti & pom-pom"),
        ]
        
        acc_cards_layout = QGridLayout()
        acc_cards_layout.setSpacing(8)
        
        for idx, (key, name, icon, desc) in enumerate(acc_list):
            btn = QPushButton(f"{icon}  {name}\n    {desc}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.set_accessory(k))
            row = idx // 2
            col = idx % 2
            acc_cards_layout.addWidget(btn, row, col)
            self.acc_buttons.append((btn, key, icon, name))
            
        wardrobe_layout.addLayout(acc_cards_layout)
        
        self.wardrobe_status_label = QLabel()
        self.wardrobe_status_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #80cbc4; margin-top: 6px;")
        wardrobe_layout.addWidget(self.wardrobe_status_label)
        wardrobe_layout.addStretch()
        tab_wardrobe.setLayout(wardrobe_layout)
        self.update_wardrobe_buttons_ui()
        
        # ==========================================
        # TAB 2: 🎨 APPEARANCE (Size & Coat Color)
        # ==========================================
        tab_appearance = QWidget()
        app_layout = QVBoxLayout()
        app_layout.setContentsMargins(10, 12, 10, 10)
        app_layout.setSpacing(12)
        
        # Cat Size (Small, Medium, Large)
        size_group = QGroupBox("Cat Size")
        size_layout = QVBoxLayout()
        size_btns_layout = QHBoxLayout()
        size_btns_layout.setSpacing(8)
        self.size_presets = [
            ("Small", 2.0),
            ("Medium", 3.0),
            ("Large", 4.0),
        ]
        self.size_buttons = []
        for name, factor in self.size_presets:
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, f=factor: self.set_size(f))
            size_btns_layout.addWidget(btn)
            self.size_buttons.append((btn, factor))
        size_layout.addLayout(size_btns_layout)
        
        self.size_status_label = QLabel()
        self.size_status_label.setStyleSheet("font-size: 11px; margin-top: 4px;")
        size_layout.addWidget(self.size_status_label)
        size_group.setLayout(size_layout)
        app_layout.addWidget(size_group)
        self.update_size_buttons_ui()
        
        # --- Predefined Cat Coats (Solid Dark Shades) ---
        color_group = QGroupBox("Cat Coat Shades")
        color_layout = QVBoxLayout()
        color_layout.setSpacing(6)
        
        desc_label = QLabel("Choose a curated dark coat shade for Nyx:")
        desc_label.setStyleSheet("color: #a0a5b5; font-size: 11px;")
        color_layout.addWidget(desc_label)
        
        swatches_layout = QHBoxLayout()
        swatches_layout.setSpacing(8)
        
        self.preset_buttons = []
        for key, info in COAT_PRESETS.items():
            btn = QPushButton(f"{info['icon']} {info['name']}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self.set_coat_preset(k))
            swatches_layout.addWidget(btn)
            self.preset_buttons.append((btn, key, info["hex"]))
            
        color_layout.addLayout(swatches_layout)
        
        self.color_status_label = QLabel()
        self.color_status_label.setStyleSheet("font-size: 11px; margin-top: 4px;")
        color_layout.addWidget(self.color_status_label)
        self.update_preset_buttons_ui()
        
        color_group.setLayout(color_layout)
        app_layout.addWidget(color_group)

        # Behavior & Reactions
        beh_group = QGroupBox("Behavior")
        beh_layout = QVBoxLayout()
        self.typing_cb = QCheckBox("React to typing (tap paws along with keystrokes)")
        self.typing_cb.setChecked(self.pet.settings.get("react_to_typing", True))
        self.typing_cb.stateChanged.connect(self.on_typing_changed)
        beh_layout.addWidget(self.typing_cb)
        beh_group.setLayout(beh_layout)
        app_layout.addWidget(beh_group)

        app_layout.addStretch()
        tab_appearance.setLayout(app_layout)
        
        # ==========================================
        # TAB 3: ⏱️ TIMERS & REMINDERS (General)
        # ==========================================
        tab_general = QWidget()
        gen_layout = QVBoxLayout()
        gen_layout.setContentsMargins(10, 12, 10, 10)
        gen_layout.setSpacing(10)
        
        # Intervals / Timers
        int_group = QGroupBox("Timers")
        int_layout = QVBoxLayout()
        
        s_row = QHBoxLayout()
        s_row.addWidget(QLabel("Stretch break (min, 0 = off)"))
        self.stretch_spin = QSpinBox()
        self.stretch_spin.setMaximum(999)
        self.stretch_spin.setValue(self.pet.settings["stretch_interval_min"])
        self.stretch_spin.valueChanged.connect(self.on_stretch_changed)
        s_row.addWidget(self.stretch_spin)
        
        test_stretch_btn = QPushButton("Stretch Nyx")
        test_stretch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_stretch_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2d3d;
                color: #5c9aff;
                border: 1px solid #5c6bc0;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #33364a;
                border: 1px solid #7986cb;
            }
        """)
        test_stretch_btn.clicked.connect(self.pet.trigger_stretch)
        s_row.addWidget(test_stretch_btn)
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
        gen_layout.addWidget(int_group)
        
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
        
        help_label = QLabel("Nyx holds the message above its head. Drag it to acknowledge and clear the reminder.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #888;")
        rem_layout.addWidget(help_label)
        rem_group.setLayout(rem_layout)
        gen_layout.addWidget(rem_group)
        gen_layout.addStretch()
        tab_general.setLayout(gen_layout)
        
        # Add Tabs
        self.tabs.addTab(tab_wardrobe, "🎩 Wardrobe")
        self.tabs.addTab(tab_appearance, "🎨 Appearance")
        self.tabs.addTab(tab_general, "⏱️ Timers")
        
        root_layout.addWidget(self.tabs)
        self.setLayout(root_layout)

    def set_accessory(self, acc_key):
        self.pet.settings["accessory"] = acc_key
        save_settings(self.pet.settings)
        self.update_wardrobe_buttons_ui()
        if hasattr(self.pet, 'update_tray_wardrobe_checks'):
            self.pet.update_tray_wardrobe_checks()
        self.pet.update()

    def update_wardrobe_buttons_ui(self):
        current_acc = self.pet.settings.get("accessory", "none")
        for btn, key, icon, name in self.acc_buttons:
            if key == current_acc:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 8px 12px;
                        background-color: #3949ab;
                        color: #ffffff;
                        border: 2px solid #7986cb;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 8px 12px;
                        background-color: #2b2b36;
                        color: #c0c0c0;
                        border: 1px solid #444;
                        border-radius: 6px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #383848;
                        border: 1px solid #666;
                        color: #ffffff;
                    }
                """)
        acc_data = ACCESSORIES.get(current_acc, ACCESSORIES["none"])
        self.wardrobe_status_label.setText(f"Equipped: {acc_data['icon']} {acc_data['name']}")

    def set_size(self, factor):
        self.pet.settings["scale_factor"] = factor
        self.pet.scale_factor = factor
        self.pet.save_and_apply_settings()
        self.update_size_buttons_ui()
        self.pet.update()

    def update_size_buttons_ui(self):
        curr_scale = round(float(self.pet.settings.get("scale_factor", 3.0)))
        matched_name = "Medium"
        for btn, factor in self.size_buttons:
            is_active = (round(factor) == curr_scale)
            if is_active:
                for name, f in self.size_presets:
                    if round(f) == curr_scale:
                        matched_name = name
                        break
            border_col = "#5c6bc0" if is_active else "#444455"
            border_width = "2px" if is_active else "1px"
            bg_col = "#2a2d3d" if is_active else "#1e1e28"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_col};
                    color: {'#5c9aff' if is_active else '#FFFFFF'};
                    border: {border_width} solid {border_col};
                    border-radius: 5px;
                    padding: 5px 2px;
                    font-size: 11px;
                    font-weight: {'bold' if is_active else 'normal'};
                }}
                QPushButton:hover {{
                    background-color: #33364a;
                    border: 1px solid #7986cb;
                }}
            """)
        self.size_status_label.setText(f"Active Size: <b>{matched_name}</b>")

    def on_typing_changed(self, val):
        self.pet.settings["react_to_typing"] = bool(val)
        self.pet.save_and_apply_settings()

    def set_coat_preset(self, preset_key):
        if preset_key not in COAT_PRESETS:
            return
        preset = COAT_PRESETS[preset_key]
        self.pet.settings["coat_preset"] = preset_key
        self.pet.settings["matrix_r"] = preset["r"]
        self.pet.settings["matrix_g"] = preset["g"]
        self.pet.settings["matrix_b"] = preset["b"]
        self.pet.settings["matrix_outline_r"] = preset.get("outline_r", 20)
        self.pet.settings["matrix_outline_g"] = preset.get("outline_g", 20)
        self.pet.settings["matrix_outline_b"] = preset.get("outline_b", 20)
        self.pet.settings["matrix_nose_r"] = preset.get("nose_r", 255)
        self.pet.settings["matrix_nose_g"] = preset.get("nose_g", 140)
        self.pet.settings["matrix_nose_b"] = preset.get("nose_b", 165)
        self.update_preset_buttons_ui()
        self.pet.save_and_apply_settings()
        if hasattr(self.pet, 'update_tray_coat_checks'):
            self.pet.update_tray_coat_checks()
        self.pet.update()

    def set_preset_color(self, r, g, b):
        self.pet.settings["matrix_r"] = r
        self.pet.settings["matrix_g"] = g
        self.pet.settings["matrix_b"] = b
        self.update_preset_buttons_ui()
        self.pet.save_and_apply_settings()
        self.pet.update()

    def update_preset_buttons_ui(self):
        curr_preset = self.pet.settings.get("coat_preset", "black")
        matched_info = COAT_PRESETS.get(curr_preset, COAT_PRESETS["black"])
        
        for btn, key, hex_col in self.preset_buttons:
            is_active = (key == curr_preset)
            border_col = "#5c6bc0" if is_active else "#444455"
            border_width = "2px" if is_active else "1px"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_col};
                    color: {'#5c9aff' if is_active else '#FFFFFF'};
                    border: {border_width} solid {border_col};
                    border-radius: 5px;
                    padding: 5px 4px;
                    font-size: 10px;
                    font-weight: {'bold' if is_active else 'normal'};
                }}
                QPushButton:hover {{
                    border: 2px solid #88AAFF;
                }}
            """)
        self.color_status_label.setText(f"Active Coat: {matched_info['icon']} <b>{matched_info['name']}</b> ({matched_info['desc']})")
        
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
    track_changed = pyqtSignal(str)

    def run(self):
        last_move_time = 0.0

        def on_move(x, y):
            nonlocal last_move_time
            now = time.time()
            if now - last_move_time >= 0.5:
                last_move_time = now
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
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        last_track = ""
        
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
                
                detected_track = ""
                is_spotify = False
                
                # 1. Enumerate top-level windows to check if Spotify is playing (even in background)
                def enum_spotify_cb(w_hwnd, lparam):
                    nonlocal detected_track, is_spotify
                    try:
                        if user32.IsWindowVisible(w_hwnd):
                            w_pid = ctypes.c_ulong(0)
                            user32.GetWindowThreadProcessId(w_hwnd, ctypes.byref(w_pid))
                            h_p = kernel32.OpenProcess(0x0410, False, w_pid)
                            if h_p:
                                p_name = ctypes.create_unicode_buffer(260)
                                psapi.GetModuleBaseNameW(h_p, None, p_name, ctypes.sizeof(p_name))
                                kernel32.CloseHandle(h_p)
                                if p_name.value.lower() == "spotify.exe":
                                    is_spotify = True
                                    length = user32.GetWindowTextLengthW(w_hwnd)
                                    if length > 0:
                                        t_buf = ctypes.create_unicode_buffer(length + 1)
                                        user32.GetWindowTextW(w_hwnd, t_buf, length + 1)
                                        val = t_buf.value.strip()
                                        if val and not val.lower().startswith("spotify") and not val.lower().startswith("gdi+"):
                                            detected_track = val
                                            return False # found playing track, stop enumeration
                    except Exception:
                        pass
                    return True

                try:
                    user32.EnumWindows(WNDENUMPROC(enum_spotify_cb), 0)
                except Exception:
                    pass

                # 2. If Spotify wasn't playing track, check active window for media players (YouTube Music, SoundCloud, Apple Music, Tidal)
                if not detected_track and title:
                    lower_t = title.lower()
                    if any(m in lower_t for m in ["youtube music", "soundcloud", "apple music", "tidal", "deezer"]):
                        cleaned = title
                        for b in [' - Google Chrome', ' - Mozilla Firefox', ' - Brave', ' - Microsoft Edge', ' - Opera']:
                            if cleaned.endswith(b):
                                cleaned = cleaned[:-len(b)].strip()
                        for s in [' - YouTube Music', ' - Apple Music', ' - SoundCloud', ' - Tidal', ' - Spotify']:
                            if cleaned.endswith(s):
                                cleaned = cleaned[:-len(s)].strip()
                        if cleaned and not cleaned.lower().startswith("youtube music"):
                            detected_track = cleaned

                self.spotify_status.emit(is_spotify)

                # 3. Track change bubble notification
                if detected_track:
                    if detected_track != last_track:
                        last_track = detected_track
                        self.track_changed.emit(detected_track)
                else:
                    if last_track:
                        last_track = ""
            except Exception:
                pass
            time.sleep(1)


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
        
        self.cat_interactive_rect = QRect()
        self.bubble_interactive_rect = QRect()
        self.track_bubble_message = None
        self._track_bubble_timer = None
        self.landing_cushion_frames = 0
        self.waking_frames = 0
        
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
        self.monitor.track_changed.connect(self.on_track_changed)
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
        self.clearMask()
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
        stretch_action = QAction("Stretch Nyx 🐾", self)
        set_task_action = QAction("Set Pomodoro Task...", self)
        toggle_alarm_action = QAction("Toggle Pomodoro", self)
        set_pin_action = QAction("Set Pinned Message...", self)
        clear_pin_action = QAction("Clear Pinned Message", self)
        
        pin_window_action = QAction("Always on Top", self, checkable=True)
        pin_window_action.setChecked(self.settings.get("always_on_top", True))
        
        settings_action = QAction("Settings...", self)
        quit_action = QAction("Exit Nyx", self)
        
        show_action.triggered.connect(self.show)
        stretch_action.triggered.connect(self.trigger_stretch)
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
        tray_menu.addAction(stretch_action)
        
        # Wardrobe Submenu
        wardrobe_menu = tray_menu.addMenu("Wardrobe 🎩")
        self.tray_wardrobe_actions = {}
        wardrobe_items = [
            ("none", ("None", "❌")),
            ("crown", ("Golden Crown", "👑")),
            ("wizard", ("Wizard Hat", "🧙")),
            ("party", ("Party Hat", "🎉")),
        ]
        for k, info in wardrobe_items:
            act = QAction(f"{info[1]}  {info[0]}", self)
            act.setCheckable(True)
            act.setChecked(self.settings.get("accessory", "none") == k)
            act.triggered.connect(lambda checked, acc_k=k: self.set_accessory_from_tray(acc_k))
            wardrobe_menu.addAction(act)
            self.tray_wardrobe_actions[k] = act

        # Coat Presets Submenu
        coat_menu = tray_menu.addMenu("Coat Presets 🐾")
        self.tray_coat_actions = {}
        for k, info in COAT_PRESETS.items():
            act = QAction(f"{info['icon']}  {info['name']}", self)
            act.setCheckable(True)
            act.setChecked(self.settings.get("coat_preset", "black") == k)
            act.triggered.connect(lambda checked, coat_k=k: self.set_coat_preset_from_tray(coat_k))
            coat_menu.addAction(act)
            self.tray_coat_actions[k] = act

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



    def set_accessory_from_tray(self, acc_key):
        self.settings["accessory"] = acc_key
        save_settings(self.settings)
        self.update_tray_wardrobe_checks()
        if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.isVisible():
            self.settings_window.update_wardrobe_buttons_ui()
        self.update()

    def update_tray_wardrobe_checks(self):
        curr = self.settings.get("accessory", "none")
        if hasattr(self, 'tray_wardrobe_actions'):
            for k, act in self.tray_wardrobe_actions.items():
                act.setChecked(k == curr)

    def set_coat_preset_from_tray(self, coat_key):
        if hasattr(self, 'settings_window') and self.settings_window:
            self.settings_window.set_coat_preset(coat_key)
        else:
            if coat_key in COAT_PRESETS:
                p = COAT_PRESETS[coat_key]
                self.settings["coat_preset"] = coat_key
                self.settings["matrix_r"] = p["r"]
                self.settings["matrix_g"] = p["g"]
                self.settings["matrix_b"] = p["b"]
                self.settings["matrix_outline_r"] = p.get("outline_r", 20)
                self.settings["matrix_outline_g"] = p.get("outline_g", 20)
                self.settings["matrix_outline_b"] = p.get("outline_b", 20)
                self.settings["matrix_nose_r"] = p.get("nose_r", 255)
                self.settings["matrix_nose_g"] = p.get("nose_g", 140)
                self.settings["matrix_nose_b"] = p.get("nose_b", 165)
                save_settings(self.settings)
                self.update_tray_coat_checks()
                self.update()

    def update_tray_coat_checks(self):
        curr = self.settings.get("coat_preset", "black")
        if hasattr(self, 'tray_coat_actions'):
            for k, act in self.tray_coat_actions.items():
                act.setChecked(k == curr)

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

    def wake_up(self):
        if self.state == "SLEEPING":
            self.state = "WAKING"
            self.waking_frames = 15  # ~300ms waking blink transition at 50 FPS
            self.is_blinking = True
            if hasattr(self, 'sleeping_zzzs'):
                self.sleeping_zzzs.clear()
            self.current_frame_index = 0

    # --- Signals ---
    def on_input_activity(self):
        self.idle_time = 0
        if self.state == "SLEEPING":
            self.wake_up()
        self.update()
            
    def on_typing_activity(self):
        if not self.settings.get("react_to_typing", True):
            return
        self.idle_time = 0
        if self.state == "SLEEPING":
            self.wake_up()
        self.is_typing = True
        if self.state != "WAKING":
            # Crucial: NEVER blink while typing unless waking up!
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
                self.wake_up()
        elif is_watching:
            self.is_listening_to_music = False
            self.active_app_state = "WATCHING"
            self.idle_time = 0
            if self.state == "SLEEPING":
                self.wake_up()
        else:
            self.is_listening_to_music = False
            self.active_app_state = ""

    def on_spotify_status(self, is_spotify):
        self._raw_is_spotify = is_spotify
        self.update_active_app_state()

    def on_track_changed(self, track_name):
        if not track_name:
            return
        
        display_track = track_name.strip()
        if len(display_track) > 34:
            display_track = display_track[:31] + "..."
            
        self.track_bubble_message = f"🎵 Now Playing:\n{display_track}"
        self.update()
        
        if hasattr(self, '_track_bubble_timer') and self._track_bubble_timer:
            self._track_bubble_timer.stop()
        self._track_bubble_timer = QTimer(self)
        self._track_bubble_timer.setSingleShot(True)
        self._track_bubble_timer.timeout.connect(self.clear_track_bubble)
        self._track_bubble_timer.start(5500)

    def clear_track_bubble(self):
        self.track_bubble_message = None
        self.update()

    def trigger_stretch(self):
        if getattr(self, 'is_dragging', False):
            return
        self.state = "STRETCHING"
        self.current_frame_index = 0
        self.idle_time = 0
        self.stretch_cycles_left = 3
        self.track_bubble_message = "Time to stretch! 🐾\nTake a quick break"
        if hasattr(self, '_track_bubble_timer') and self._track_bubble_timer:
            self._track_bubble_timer.stop()
        self._track_bubble_timer = QTimer(self)
        self._track_bubble_timer.setSingleShot(True)
        self._track_bubble_timer.timeout.connect(self.clear_track_bubble)
        self._track_bubble_timer.start(5500)
        self.update()

    def on_active_window(self, title):
        self.current_window_title = title.lower()
        self.update_active_app_state()

    def get_current_animation_name(self):
        if self.state == "DRAGGED": return "DRAGGED"
        if self.state == "STRETCHING": return "STRETCHING"
        if hasattr(self, 'is_petting') and self.is_petting: return "PURRING"
        
        is_typing = getattr(self, 'is_typing', False)
        if is_typing:
            return "TYPING"
            
        app_state = getattr(self, 'active_app_state', "")
        if app_state != "":
            return app_state
            
        if self.state == "SLEEPING":
            return "SLEEPING"
            
        if self.state == "WAKING":
            return "IDLE"
            
        return self.state

    # --- Logic Updates ---
    def update_logic(self):
        if getattr(self, 'active_app_state', '') in ["WATCHING", "VIBING"]:
            self.idle_time = 0
            if self.state == "SLEEPING":
                self.wake_up()
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
                self.trigger_stretch()
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
            
            if hasattr(self, 'is_petting') and self.is_petting and len(self.hearts) < 2 and self.tick_count % 30 == 0:
                self.hearts.append([random.randint(-10, 10), random.randint(-30, -18), 255.0, random.uniform(0.8, 1.3)])

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
        elif anim_name == "STRETCHING":
            speed = 10 # ~200ms per frame (smooth satisfying cat stretch)
            
        # Natural blinking logic (NEVER while typing, dragged, sleeping, purring, or stretching!)
        if getattr(self, 'state', '') == "WAKING":
            self.is_blinking = True
        elif getattr(self, 'is_typing', False) or anim_name in ["TYPING", "DRAGGED", "SLEEPING", "PURRING", "STRETCHING"]:
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

        # Cushioned Landing on Drop: decay frame counter
        if getattr(self, 'landing_cushion_frames', 0) > 0:
            self.landing_cushion_frames -= 1

        # Gentle Wake-Up Transition: decay waking frames and open eyes
        if getattr(self, 'state', '') == "WAKING":
            self.waking_frames = getattr(self, 'waking_frames', 0) - 1
            if self.waking_frames <= 0:
                self.state = "IDLE"
                self.is_blinking = False
                self.blink_timer = random.randint(180, 360)
            else:
                self.is_blinking = True

        # Advance frames for multi-frame animations (typing steps via keystrokes)
        if anim_name != "TYPING":
            if self.tick_count % speed == 0:
                anim_list_len = len(MATRIX_FRAMES.get(anim_name, [0]))
                self.current_frame_index = (self.current_frame_index + 1) % max(1, anim_list_len)
                if anim_name == "STRETCHING":
                    next_idx = self.current_frame_index + 1
                    if next_idx >= anim_list_len:
                        self.stretch_cycles_left = getattr(self, 'stretch_cycles_left', 1) - 1
                        if self.stretch_cycles_left <= 0:
                            self.state = "IDLE"
                            self.current_frame_index = 0
                        else:
                            self.current_frame_index = 0
                    else:
                        self.current_frame_index = next_idx
                else:
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
            
        cat_bottom = max(dest_y + dest_height + 8, floor_y + 12)
        self.cat_interactive_rect = QRect(dest_x - 10, dest_y - 10, dest_width + 20, (cat_bottom - dest_y) + 14)
        
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

        # 2. Scruff Pivot Physics & Transforms
        painter.save()

        # Cushioned Landing on Drop: squash and rebound
        cushion_frames = getattr(self, 'landing_cushion_frames', 0)
        if cushion_frames > 0 and anim_name != "DRAGGED":
            if cushion_frames >= 4:
                # Squash phase (frames 6, 5, 4): cat compresses slightly into the floor and widens
                sy = 0.91
                sx = 1.07
            elif cushion_frames >= 2:
                # Rebound phase (frames 3, 2): slight upward bounce
                sy = 1.04
                sx = 0.98
            else:
                # Settle phase (frame 1)
                sy = 1.01
                sx = 0.99
            painter.translate(cx, floor_y)
            painter.scale(sx, sy)
            painter.translate(-cx, -floor_y)

        # Pendulum wobble when dragged
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

        # 3.5 Draw Equipped Wardrobe Accessory (Ribbon, Hat, Crown)
        # Suppress accessories while typing, listening to music, or stretching
        is_typing_active = (anim_name in ["TYPING", "TYPING_MUSIC"] or getattr(self, 'is_typing', False))
        is_music_active = (anim_name in ["VIBING", "TYPING_MUSIC"] or getattr(self, 'is_listening_to_music', False))
        is_stretching_active = (anim_name == "STRETCHING" or getattr(self, 'is_stretching', False))
        
        acc_key = self.settings.get("accessory", "none")
        if is_typing_active or is_music_active or is_stretching_active:
            acc_key = "none"

        if acc_key in ACCESSORIES and acc_key != "none":
            acc_data = ACCESSORIES[acc_key]
            acc_sprite = acc_data.get("sprite", [])
            acc_colors = acc_data.get("colors", {})
            offsets = acc_data.get("offsets", {})
            
            if anim_name == "DRAGGED":
                off_key = "DRAGGED"
            elif anim_name == "SLEEPING":
                off_key = "SLEEPING"
            else:
                off_key = "IDLE"
                
            off_x, off_y = offsets.get(off_key, offsets.get("IDLE", (0, 0)))
            
            # Breathing & sleeping subtle bob
            if anim_name == "SLEEPING" and self.current_frame_index == 1:
                off_y += 1
            elif anim_name == "IDLE" and self.current_frame_index in [1, 2]:
                off_y += 1
                
            acc_px_x = int(dest_x + off_x * pixel_size)
            acc_px_y = int(dest_y + off_y * pixel_size)
            
            painter.setPen(Qt.PenStyle.NoPen)
            for sy, sline in enumerate(acc_sprite):
                for sx, sch in enumerate(sline):
                    if sch in acc_colors:
                        painter.setBrush(acc_colors[sch])
                        painter.drawRect(
                            acc_px_x + sx * pixel_size,
                            acc_px_y + sy * pixel_size,
                            pixel_size,
                            pixel_size
                        )

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
        
        if getattr(self, 'is_blinking', False) and anim_name != "DRAGGED":
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

        # 7. Speech Bubble / Reminders / Pomodoro / Now Playing
        self.bubble_interactive_rect = QRect()
        msg_to_draw = None
        if hasattr(self, 'track_bubble_message') and self.track_bubble_message:
            msg_to_draw = self.track_bubble_message
        elif hasattr(self, 'pinned_message') and self.pinned_message:
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
            self.bubble_interactive_rect = QRect(int(bx - 6), int(by - 6), int(bubble_w + 12), int(bubble_h + 16))
            
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
            # 1. Click-to-Dismiss Speech Bubbles ("Now Playing" or sticky reminders)
            if hasattr(self, 'bubble_interactive_rect') and not self.bubble_interactive_rect.isNull():
                if self.bubble_interactive_rect.contains(event.pos()):
                    self.track_bubble_message = None
                    self.pinned_message = ""
                    if hasattr(self, '_track_bubble_timer') and self._track_bubble_timer:
                        self._track_bubble_timer.stop()
                    self.bubble_interactive_rect = QRect()
                    self.update()
                    return  # Dismiss immediately without waiting for timeout, consume click

            if self.state == "SLEEPING":
                self.wake_up()

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
                self.landing_cushion_frames = 6  # ~120ms squash-and-rebound cushion upon landing
            else:
                if self.state != "WAKING":
                    # Petting / Purring on click!
                    self.state = "PURRING"
                    self.is_petting = True
                    self.idle_time = 0
                    self.hearts.append([random.randint(-8, 8), random.randint(-28, -16), 255.0, random.uniform(0.8, 1.4)])
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

