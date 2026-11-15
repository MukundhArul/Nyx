# 🐾 Nyx v1.2.0 — The Wardrobe & Wellness Update 🎩✨

> **A cozy, interactive pixel desktop companion that lives on your screen, helps you focus, and vibes with your day!**

---

## 🌟 What's New in v1.2.0

### 🎩 1. Pixel Wardrobe & Accessories
Dress up Nyx with adorable pixel accessories!
* 🎀 **Red Ribbon / Bowtie**: A dapper ruby-red ribbon bowtie resting snug below the cat's neck on its chest.
* 👑 **Golden Crown**: A royal 3-peak gold crown with ruby and sapphire jewel insets, centered proudly on top of the head between the ears.
* 🧙 **Wizard Hat**: A mystical pointed purple hat featuring an embroidered golden star band.
* 🧠 **Smart Context Hiding**: Accessories automatically hide when Nyx is typing on the keyboard or vibing with headphones, preventing any visual clutter or collision.
* ⚡ **Quick Switching**: Change accessories anytime via the desktop right-click menu, System Tray menu, or the new dedicated **Wardrobe** tab in Settings.

### 🎵 2. "Now Playing" Track Pop-Up
* Since Nyx already tracks Spotify and media windows, Nyx now pops up a cute speech bubble showing the song title whenever a new track starts (e.g., `🎵 Now Playing: Starboy`).
* Automatically disappears after 5 seconds or when the song ends.

### 🧘 3. 30-Minute Posture & Stretch Break Reminder
* Long computer sessions are tough on posture! Nyx now pops up a reminder every 30 minutes with an authentic **6-frame Comnyang stretching animation** (arched back, anchored front paws, squint eyes `><`, and tail curled high).
* Includes a **"Stretch Now"** button in Settings to trigger your break anytime on demand.

### 🎨 4. Curated Dark Coat Presets & 3 Fixed Sizes
* Replaced complex color pickers with 4 distinct, gorgeous dark cat shades:
  - 🖤 **Midnight Black** (`#18181B`)
  - 🌑 **Charcoal Slate** (`#282830`)
  - ☕ **Espresso Brown** (`#2E1E1A`)
  - 🌌 **Abyssal Navy** (`#121826`)
* 3 crisp fixed pixel sizes tailored to look sharp on any display: **Small (2x)**, **Medium (3x)**, and **Large (4x)**.

### ✨ 5. Pixel Art Polish & Connected Tail
* Tail is seamlessly fused and connected to the body across all poses (Idle, Sleeping, Dragging, Listening).
* Calmed down purring love hearts to a gentle, cozy 1–2 floaters.
* Clamped floating particles (hearts, music notes, Zzzs) within screen boundaries.

### 📁 6. Tabbed Settings UI
* Clean modern layout divided into 3 intuitive tabs:
  - 🎩 **Wardrobe**: Accessory selection with live status cards.
  - 🎨 **Appearance**: Coat shades, cat sizing, and feature toggles.
  - ⏱️ **Timers**: Pomodoro study/work intervals, break reminders, and pinned message bubbles.

---

## 📦 Downloads & Assets

| Asset | Description | Size |
|---|---|---|
| **`Nyx_Cat.exe`** | Standalone portable executable (No Python required) | ~39 MB |
| **`Nyx_v1.2.0_Windows_x64.zip`** | Portable Windows release bundle (EXE, icon, default config) | ~39 MB |
| **`Nyx_v1.2.0_Source.zip`** | Clean source code bundle | < 1 MB |

---

## 🚀 How to Run

### Portable Executable (Zero Setup)
1. Download **`Nyx_Cat.exe`** (or extract `Nyx_v1.2.0_Windows_x64.zip`).
2. Run **`Nyx_Cat.exe`**!
*(If Windows SmartScreen prompts on first launch, click "More info" → "Run anyway").*

### Running from Source
```bash
git clone https://github.com/MukundhArul/Nyx.git
cd Nyx
python -m venv venv
.\venv\Scripts\activate
pip install PyQt6 pynput psutil Pillow PyAudio PyGetWindow
python app.py
```

---

## 📋 Full Changelog (v1.1.1 → v1.2.0)
* **feat**: Add Wardrobe tab and accessories (Red Ribbon, Golden Crown, Wizard Hat) with auto-suppression during typing and music.
* **feat**: Add "Now Playing" track pop-up speech bubble for Spotify and media windows.
* **feat**: Add 30-minute posture stretch reminder and authentic 6-frame Comnyang stretching animation.
* **feat**: Curate 4 distinct dark coat presets (Midnight Black, Charcoal Slate, Espresso Brown, Abyssal Navy).
* **feat**: Add 3 crisp fixed sizes (Small, Medium, Large) to Settings.
* **fix**: Seamlessly connect cat tail in idle, sleeping, dragging, and listening poses.
* **fix**: Center crown and wizard hat on top of the head between the ears, and place red ribbon below the neck.
* **fix**: Clamp hearts, music notes, and Zzz particles to screen bounds; reduce purring heart rate.
* **docs**: Update README.md and add v1.2.0 release documentation.
