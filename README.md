<div align="center">
  <h1>✨ Nyx ✨<br>Your Cozy Desktop Companion 🐾</h1>
  <p>A lightweight, interactive pixel pet that lives on your screen to keep you company, help you focus, and vibe with your daily workflow!</p>
  <img src="https://img.shields.io/badge/Windows-Supported-blue.svg?style=flat-square&logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-UI-green.svg?style=flat-square&logo=qt" alt="PyQt6">
</div>

---

## 🌟 What's New in v1.2.0?

Nyx has received a major upgrade with cute new accessories, smart media tracking, posture reminders, and aesthetic refinements!

- **🎩 Wardrobe & Cute Pixel Accessories:**
  - Dress up Nyx from the new **Wardrobe** tab in Settings or directly from the System Tray menu!
  - 🎀 **Red Ribbon:** A dapper ruby red ribbon bowtie resting right below the neck.
  - 👑 **Golden Crown:** Sparkling royal gold crown with ruby and sapphire jewel insets, centered proudly on the head between the ears.
  - 🧙 **Wizard Hat:** Pointed mystical purple wizard hat with a golden star band.
  - 🧠 **Smart Context Hiding:** Accessories automatically tuck away while typing on the keyboard or jamming with headphones so there is never visual overlap or clutter.
- **🎵 "Now Playing" Track Pop-Up:**
  - When you listen to music on Spotify or supported media players, Nyx automatically pops up a cute speech bubble announcing the song title (e.g. `🎵 Now Playing: Starboy`) as soon as the track changes.
- **🧘 Authentic Stretch Break Reminder & Animation:**
  - Nyx now reminds you to stretch every 30 minutes with a dedicated 6-frame Comnyang stretching animation (arched back, anchored front paws, squint eyes `><`, and curled tail).
  - Includes a **"Stretch Now"** button in settings to trigger your break anytime.
- **🎨 Curated Dark Coat Presets & 3 Fixed Sizes:**
  - Replaced clumsy color wheels with 4 distinct, aesthetic dark coat shades:
    - 🖤 **Midnight Black**
    - 🌑 **Charcoal Slate**
    - ☕ **Espresso Brown**
    - 🌌 **Abyssal Navy**
  - Pick between 3 crisp pixel sizes: **Small (2x)**, **Medium (3x)**, and **Large (4x)**.
- **✨ Pixel-Perfect Tail & Animation Polishing:**
  - Connected tail in all states (Idle, Sleeping, Dragging, Listening).
  - Reduced and calmed purring love hearts for a gentle, cozy petting experience.
  - Screen boundary clamping to keep hearts, notes, and Zzzs strictly within desktop view.

---

## 🌟 What is Nyx?

Nyx is a completely free, open-source desktop overlay inspired by cozy virtual pets and companions. Nyx sits happily on your desktop, fully transparent and frameless, reacting to your mouse, keystrokes, and active apps without ever getting in your way! 🧡

---

## 🐈 Features & Animations

Nyx is powered by a custom procedural string matrix engine: every frame is drawn natively with crisp pixel edges and full dynamic color support!

### 🎮 Interactive Animations
* **🖱️ Drag & Drop:** Click and hold to pick Nyx up. Nyx dangles gently with physics-based wobble while you move it around the desktop.
* **⌨️ Keyboard Kneading:** Start typing code or writing documents, and Nyx taps its paws along with your keystrokes. Fast typing even makes Nyx sweat heat steam!
* **👀 Cursor Tracking & Blinking:** Nyx's eyes follow your mouse cursor smoothly around your monitors, with natural blinking intervals when idle.
* **💕 Purring:** Click or pet Nyx to make it happy! It will close its eyes in bliss and float gentle pink hearts.
* **🎙️ Voice Reactions (Mic Support):** Speak into your microphone and Nyx opens its mouth in real-time to talk back with you.
* **💤 Sleep Mode:** Step away from your computer for 30 seconds, and Nyx curls up into a peaceful nap with floating blue Zzzs.

### 📱 App & Media Reactions
* **🎧 Vibing:** Open **Spotify** or a music player, and Nyx throws on retro coral headphones to bob to the beat.
* **🎵 Now Playing Speech Bubble:** Track changes pop up right above Nyx's head so you always know what song is playing.
* **📺 Watching:** Switch to **YouTube** or a video player, and Nyx widens its eyes to watch videos attentively with you.

### ⏰ Productivity & Health Tools
* **🍅 Pomodoro Timers:** Toggle customizable focus intervals and break timers right from the settings window.
* **🧘 Posture & Stretch Reminders:** Set reminders every 30 minutes to stretch alongside Nyx.
* **💬 Pinned Sticky Notes:** Keep a quick task or reminder pinned in a speech bubble above Nyx's head.

---

## 🚀 How to Run (Easy Way)

You do not need to know how to code to enjoy Nyx!

1. Go to the [Releases](https://github.com/MukundhArul/Nyx/releases) page on GitHub.
2. Download `Nyx_Cat.exe` (or `Nyx.exe`).
3. Place it anywhere on your computer (e.g. your Desktop or Startup folder).
4. Double-click `Nyx_Cat.exe` to run it!
*(Note: Windows SmartScreen may show an unrecognized app banner on first launch. Click "More info" and "Run anyway").*

---

## 🛠️ For Developers (Build From Source)

### 1. Clone the repository
```bash
git clone https://github.com/MukundhArul/Nyx.git
cd Nyx
```

### 2. Set up your virtual environment
```bash
python -m venv venv

# Windows (Command Prompt / PowerShell):
.\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install PyQt6 pynput psutil Pillow PyAudio PyGetWindow
```

### 4. Run Nyx
```bash
python app.py
```

### 5. Build Standalone Executable (Optional)
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name Nyx_Cat --icon=cat.ico app.py
```

---

## ⚙️ Settings & Controls

* **Right-Click Nyx or System Tray Icon**:
  - Open **Settings** dialog
  - Quick-switch **Wardrobe Accessories** (None, Red Ribbon, Golden Crown, Wizard Hat)
  - Quick-trigger **Stretch Now**
  - Toggle **Always on Top**
  - Reset to Default or Exit Nyx

* **Tabbed Settings Window**:
  - **🎩 Wardrobe**: Preview and equip accessories with one click.
  - **🎨 Appearance**: Choose between Midnight Black, Charcoal Slate, Espresso Brown, and Abyssal Navy coats; select Small (2x), Medium (3x), or Large (4x) cat sizes; toggle microphone reactions.
  - **⏱️ Timers**: Configure Pomodoro study/work intervals, break reminders, and pinned message bubbles.

---

<div align="center">
  <i>Built with ❤️ for a cozier desktop experience.</i>
</div>
