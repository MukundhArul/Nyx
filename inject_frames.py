import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Generate the new MATRIX_FRAMES
new_frames = """MATRIX_FRAMES = {
    "IDLE": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPPPPPPPPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP...D.",
            "....PPPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ]
    ],
    "DRAGGED": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPWWWWPPWWWWPP...",
            ".D.PPWBBWPPWBBWPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP.....",
            ".....P.P....P.P.....",
            ".....P.P....P.P.....",
            ".....D.D....D.D....."
        ]
    ],
    "TYPING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            "...DD..........DD...",
            "...PP.PPPPPPPP.PPDD.",
            "...PP.PPPPPPPPP.P.D.",
            "....PPPPPPPPPPP...D.",
            "......P......P..DDD."
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
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPBBBBPPBBBBP..D.",
            "...PPPPPPPPPPPPPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP.DDD."
        ],
        [
            "....................",
            "....................",
            "....................",
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPBBBBPPBBBBP..D.",
            "...PPPPPPPPPPPPPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP.DDD."
        ]
    ],
    "SCROLLING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ],
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            "...DD..........DD...",
            "...PP.PPPPPPPP.PPDD.",
            "...PP.PPPPPPPPP.P.D.",
            "....PPPPPPPPPPP...D.",
            "......P......P..DDD."
        ]
    ],
    "VIBING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPWBBWPPWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ],
        [
            "....................",
            "....PP......PP......",
            "...PDBP....PDBP.....",
            "..PPPPPPPPPPPPPP....",
            "..PPPDPPDPDPPPPP....",
            ".PPPPPPPPPPPPPPPP...",
            "D.PPWWWWPPWWWWPP.D..",
            "..PPWBBWPPWBBWPP....",
            "D.PPPPPPPPPPPPPP.D..",
            "..PPPPPPBPPPPPPP....",
            "...PPPPPPPPPPPP.....",
            "....PPPPPPPPPP......",
            "....PPPPPPPPPP...DD.",
            "...PPPPPPPPPPP....D.",
            "...PPPPPPPPPPP....D.",
            "..DDPP....PPDD..DDD."
        ]
    ],
    "WATCHING": [
        [
            "....................",
            ".....PP......PP.....",
            "....PDBP....PDBP....",
            "...PPPPPPPPPPPPPP...",
            "...PPPDPPDPDPPPPP...",
            "..PPPPPPPPPPPPPPPP..",
            ".D.PPWWWWPPWWWWPP.D.",
            "...PPBWWBPWWBBWPP...",
            ".D.PPPPPPPPPPPPPP.D.",
            "...PPPPPPBPPPPPPP...",
            "....PPPPPPPPPPPP....",
            ".....PPPPPPPPPP.....",
            ".....PPPPPPPPPP..DD.",
            "....PPPPPPPPPPP...D.",
            "....PPPPPPPPPPP...D.",
            "...DDPP....PPDD.DDD."
        ]
    ]
}"""

content = re.sub(r'MATRIX_FRAMES\s*=\s*\{.*?\}\n}', new_frames, content, flags=re.DOTALL)
# The regex above won't work well due to nested brackets. We can just use split since we know exactly where it is.
part1 = content.split('MATRIX_FRAMES = {')[0]
part2 = 'def load_settings():' + content.split('def load_settings():')[1]
content = part1 + new_frames + "\n\n" + part2

# Modify scale logic
content = content.replace("pixel_size = int(self.scale_factor * 4) # Scale up block size", "pixel_size = max(2, int(self.scale_factor * 1.6)) # Scaled correctly to original PNG size")

# In paintEvent, anim_name can be any state now.
content = content.replace("anim_name = self.state if self.state in [\"IDLE\", \"DRAGGED\"] else \"IDLE\"", "anim_name = self.state if self.state in MATRIX_FRAMES else \"IDLE\"")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated successfully!")
