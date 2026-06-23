import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update DEFAULT_SETTINGS to include RGB
settings_replacement = """    "matrix_mode": False,
    "matrix_r": 198,
    "matrix_g": 154,
    "matrix_b": 150
}"""
content = content.replace('    "matrix_mode": False\n}', settings_replacement)

# 2. Update MATRIX_COLORS to not hardcode P, but keep it for default parsing
colors_replacement = """MATRIX_COLORS = {
    'P': QColor(198, 154, 150), # Dusty Pinkish Brown (Default, will be overridden)
    'D': QColor(75, 54, 50),    # Dark Brown
    'W': QColor(255, 255, 255), # White
    'B': QColor(34, 34, 34),    # Black
}"""
content = content.replace("""MATRIX_COLORS = {
    'P': QColor(198, 154, 150), # Dusty Pinkish Brown
    'D': QColor(75, 54, 50),    # Dark Brown
    'W': QColor(255, 255, 255), # White
    'B': QColor(34, 34, 34),    # Black
}""", colors_replacement)

# 3. Inject new Matrix Frames (Cuter rounded cat shape)
new_frames = """MATRIX_FRAMES = {
    "IDLE": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPPPPPPPPPPPP...",
            "...PPPPPPPPPPPPPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP...D.",
            ".....PPPPPPPPPP..DD.",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ]
    ],
    "DRAGGED": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPBWWWPPWWWBP....",
            "...PPBWWWPPWWWBP....",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....P........P.....",
            ".....P........P.....",
            ".....D........D.....",
            "....................",
            "...................."
        ]
    ],
    "TYPING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            "....DD........DD....",
            "....PP.PPPPPP.P.DD..",
            "....PP.PPPPPP.P..D..",
            ".....PPPPPPPPP...D..",
            ".......P....P...DD..",
            "...................."
        ]
    ],
    "SLEEPING": [
        [
            "....................",
            "....................",
            "....................",
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPBBBBPPBBBBPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP.DD..",
            "....PPPPPPPPPPP.D...",
            "....DDDDDDDDDDDD...."
        ]
    ],
    "SCROLLING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPWWWBPBWWWPP....",
            "...PPWWWBPBWWWPP....",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ]
    ],
    "VIBING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPWWWBPPBWWWPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ],
        [
            "....................",
            "......PP......PP....",
            ".....PDBP....PDBP...",
            ".....PPPPPPPPPPPP...",
            "....PPPPPPPPPPPPPP..",
            "....PPWWWBPPBWWWPP..",
            "....PPWWWBPPBWWWPP..",
            "....PPPPPPPPPPPPPP..",
            ".....PPPPPPBPPPPP...",
            "......PPPPPPPPPP....",
            "......PPPPPPPPPP....",
            "......PPPPPPPPPP..DD",
            "......PPPPPPPPPP...D",
            "......PPPPPPPPP....D",
            ".....DDD....DDD..DD.",
            "...................."
        ]
    ],
    "WATCHING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "....PPPPPPPPPPPP....",
            "...PPPPPPPPPPPPPP...",
            "...PPBWWWPPBWWWPP...",
            "...PPBWWWPPBWWWPP...",
            "...PPPPPPPPPPPPPP...",
            "....PPPPPPBPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.DD..",
            ".....PPPPPPPPPP..D..",
            ".....PPPPPPPPP...D..",
            ".....PPP....PPP.DD..",
            "...................."
        ]
    ]
}"""
part1 = content.split('MATRIX_FRAMES = {')[0]
part2 = 'def load_settings():' + content.split('def load_settings():')[1]
content = part1 + new_frames + "\n\n" + part2

# 4. Inject Sliders to SettingsWindow
ui_injection = """
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
        
        # Reminders"""
content = content.replace("        # Reminders", ui_injection)

# 5. Add handler for color slider
handler_injection = """
    def on_color_changed(self):
        self.pet.settings["matrix_r"] = self.r_slider.value()
        self.pet.settings["matrix_g"] = self.g_slider.value()
        self.pet.settings["matrix_b"] = self.b_slider.value()
        self.pet.save_and_apply_settings()

    def on_matrix_changed(self, val):"""
content = content.replace("    def on_matrix_changed(self, val):", handler_injection)

# 6. Override the 'P' color in paintEvent based on settings
paint_injection = """            # Override body color with settings
            custom_r = self.settings.get("matrix_r", 198)
            custom_g = self.settings.get("matrix_g", 154)
            custom_b = self.settings.get("matrix_b", 150)
            MATRIX_COLORS['P'] = QColor(custom_r, custom_g, custom_b)
            
            painter.setPen(Qt.PenStyle.NoPen)"""
content = content.replace("            painter.setPen(Qt.PenStyle.NoPen)", paint_injection)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("RGB features injected successfully!")
