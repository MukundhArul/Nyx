import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. New MATRIX_FRAMES
new_frames = """MATRIX_FRAMES = {
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
}"""

part1 = content.split('MATRIX_FRAMES = {')[0]
part2 = 'def load_settings():' + content.split('def load_settings():')[1]
content = part1 + new_frames + "\n\n" + part2

# 2. Update update_animation speed
old_anim = """    def update_animation(self):
        self.tick_count += 1
        
        if self.tick_count % 3 == 0:
            anim_name = self.get_current_animation_name()
            anim_list = self.animations.get(anim_name, self.animations["IDLE"])
            self.current_frame_index = (self.current_frame_index + 1) % len(anim_list)"""

new_anim = """    def update_animation(self):
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
            self.current_frame_index += 1"""

content = content.replace(old_anim, new_anim)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Smooth animations injected successfully!")
