# Snake Pi

[![Language](https://img.shields.io/badge/language-python-blue.svg?style=flat)](https://www.python.org)
[![Module](https://img.shields.io/badge/module-pygame-brightgreen.svg?style=flat)](http://www.pygame.org/news.html)
[![Release](https://img.shields.io/badge/release-v1.0-orange.svg?style=flat)](https://github.com/MS-potilas/snake-pi)

## About

**Snake Pi** is a modern, retro-styled clone of the classic Nokia Snake II game. It features nostalgic Nokia 7110 and 3310 phone overlays and joystick support. 

While specifically optimized to run on **RetroPie**, it can also be played on any standard desktop environment (Linux, macOS, Windows). 

*This project is a fork of [Sara Martínez's snake-game](https://github.com/smartido/snake-game). It includes bug fixes, gameplay improvements, optimized game logic, and overlay images.*

## Controls

You can control the snake using a keyboard or a controller/joystick:

*   **Arrow Keys:** Move up, down, left, or right
*   **Numpad (2, 4, 6, 8):** Traditional Nokia-style movement
*   **Joystick / D-Pad:** Full analog or digital controller support for RetroPie setups
*   **Esc / Q:** Quit the game

## Screenshots

Click on any image to view it in full resolution.

<table align="center">
  <tr>
    <td align="center">
      <b>Nokia 7110: Title Screen</b><br>
      <a href="assets/7110_title.jpg"><img src="assets/7110_title.jpg" width="100%" alt="Nokia 7110 title screen"></a>
    </td>
    <td align="center">
      <b>Nokia 7110: Game</b><br>
      <a href="assets/7110_game.jpg"><img src="assets/7110_game.jpg" width="100%" alt="Nokia 7110 game"></a>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <b>Nokia 3310: Title Screen</b><br>
      <a href="assets/3310_title.jpg"><img src="assets/3310_title.jpg" width="100%" alt="Nokia 3310 title screen"></a>
    </td>
    <td align="center" width="50%">
      <b>Nokia 3310: Game</b><br>
      <a href="assets/3310_game.jpg"><img src="assets/3310_game.jpg" width="100%" alt="Nokia 3310 game"></a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>No Overlay, windowed</b><br>
      <a href="assets/no_case_windowed.jpg"><img src="assets/no_case_windowed.jpg" width="100%" alt="No overlay, game in window"></a>
    </td>
    <td align="center">
      <b>Nokia 7110, windowed (Ubuntu 24.04)</b><br>
      <a href="assets/7110_windowed.jpg"><img src="assets/7110_windowed.jpg" width="100%" alt="Nokia 7110 game in window"></a>
    </td>
  </tr>
</table>

## Retro Surprise

Once you reach 500 points and more, you may see a retro surprise.

## Installation & Running

Follow these steps to get the game running on your system.

### Prerequisites

You will need **Python** and **Pygame** installed:
* **Python** (version 3.7.3 or newer)
* **Pygame** (version 1.9.4 or newer)

On Debian-based systems (like Ubuntu or RetroPie / Raspberry Pi OS), you can install Pygame via apt:
```bash
sudo apt update
sudo apt install python3-pygame
```

### Setup

1. **Clone the repository** and navigate to the project directory:
   ```bash
   git clone https://github.com/MS-potilas/snake-pi.git
   cd snake-pi
   ```

2. **Run the game**:
   ```bash
   python3 snake.py
   ```

### RetroPie Installation (Ports menu)

To add Snake Pi to your RetroPie **Ports** menu so it can be launched directly from EmulationStation, follow these steps:

1. **Move the project folder** to your RetroPie roms directory:
   ```bash
   mv ../snake-pi ~/RetroPie/roms/ports/
   ```

2. **Create a launch script** inside the ports directory:
   ```bash
   nano ~/RetroPie/roms/ports/Snake_Pi.sh
   ```

3. **Paste the following content** into the file (save with `Ctrl+O`, `Enter`, and exit with `Ctrl+X`):
   ```bash
   #!/bin/bash
   cd "~/RetroPie/roms/ports/snake-pi"
   python3 snake.py
   ```

4. **Make the script executable**:
   ```bash
   chmod +x ~/RetroPie/roms/ports/Snake_Pi.sh
   ```

5. **Restart EmulationStation** (via the Main Menu -> Quit -> Restart EmulationStation), and **Snake Pi** will appear under the *Ports* system!

### Command line options
   ```bash
   --fullscreen     opens the game full screen
   --windowed       opens the game in window
   --7110           uses Nokia 7110 overlay
   --3310           uses Nokia 3310 overlay
   --nocase         runs the game without overlay
   ```

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

*   Background framework & initial code © 2023 Sara Martínez
*   RetroPie modifications, Nokia overlays, and game logic enhancements © 2026 MS-potilas
