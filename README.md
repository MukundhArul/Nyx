<div align="center">
  <h1>✨ Nyx ✨<br>Your Cozy Desktop Companion 🐾</h1>
  <p>A lightweight, interactive pixel pet that lives on your screen to keep you company, help you focus, and vibe with your daily tasks!</p>
  <img src="https://img.shields.io/badge/Windows-Supported-blue.svg?style=flat-square&logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-UI-green.svg?style=flat-square&logo=qt" alt="PyQt6">
</div>

---

## 🌟 What's New in v1.1.0?
Nyx has received a massive internal and external overhaul!
- **🎨 String-Based Matrix Rendering Engine:** Nyx no longer uses traditional image sprites! Every frame is procedurally generated from custom ASCII matrices, meaning absolutely zero blurry pixels and full RGB color customization!
- **🎧 Intelligent Context Awareness:** Nyx now hooks directly into the Windows API to detect window focus without performance lag. Open Spotify, and Nyx will instantly throw on some headphones.
- **⏱️ Pomodoro Workflow:** The custom settings menu now features an integrated Pomodoro timer system alongside the classic stretch and water reminders!
- **⌨️ Enhanced Contextual Actions:** Completely revamped typing animations (faster typing = angry cat!), scrolling reactions, and idle sleep animations.
  
## 🌟 What is Nyx?

Nyx is a totally free, open-source desktop overlay inspired by cozy companion apps. Nyx sits happily on your desktop, completely frameless and transparent, silently reacting to what you are doing without ever getting in your way! 🧡

## 🐈 Features & Animations

Nyx isn't just a static image; it's a reactive companion powered by a custom string-rendering engine!

### 🎮 Interactive Animations
*   **🖱️ Drag & Drop:** Click and hold to pick Nyx up and move it anywhere on your screen. When dragged, Nyx gracefully dangles!
*   **⌨️ Keyboard Kneading:** Start typing an essay or writing code, and Nyx will tap its little paws along with your keystrokes.
*   **💤 Sleep Mode:** If you step away from your keyboard and mouse for 30 seconds, Nyx will close its eyes and drift off to sleep.

### 📱 App Reactions
Nyx knows what you're doing and reacts accordingly!
*   **🎧 Vibing:** Focus on **Spotify**, and Nyx will throw on headphones and vibe to your music.
*   **📺 Watching:** Open **YouTube**, and Nyx's eyes will get huge to watch the videos with you!
  
### ⏰ Productivity Tools
Nyx comes with built-in features to keep your workflow healthy and focused (accessible via right-clicking the System Tray icon):
*   **🍅 Pomodoro Timers:** Toggle a custom focus timer directly from the settings menu to keep you productive.
*   **💬 Pinned Sticky Notes:** Need to remember a quick task? Set a pinned message, and Nyx will hold it in a cute white **speech bubble** above its head.
*   **🧘 Routine Reminders:** Configure Nyx to remind you to stretch or drink water during long computing sessions!

---

## 🚀 How to Run (Easy Way)

You do not need to know how to code to use Nyx!

1. Go to the main page of this GitHub repository and download `Nyx_Cat.exe` (or `Nyx.exe`).
2. Place it anywhere on your computer (like your Desktop).
3. Double-click `Nyx_Cat.exe` to run it! 
*(Note: Windows SmartScreen might prompt you that this is an unrecognized app. Click "More info" and "Run anyway").*

---

## 🛠️ For Developers (Build from source)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MukundhArul/Nyx.git
   cd Nyx
   ```
2. **Set up your environment:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install PyQt6 pynput psutil Pillow
   ```
4. **Run Nyx:**
   ```bash
   python app.py
   ```
5. **Build Executable (Optional):**
   ```bash
   pip install pyinstaller Pillow
   pyinstaller --noconfirm --onefile --windowed --name Nyx_Cat --icon=cat.ico app.py
   ```

---

<div align="center">
  <i>Built with ❤️ for a cozier desktop experience.</i>
</div>
