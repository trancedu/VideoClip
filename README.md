# English Listening Practice Video Player

A feature-rich video player application designed for language learning, offering clip management, speed control, and dual viewing modes.

## Features

- **Clip Management**
  - Create and save video clips with start/end markers
  - Organize clips in favorites list and tree view
  - Loop clips for repeated practice
  - Delete clips with keyboard shortcuts

- **Playback Controls**
  - Adjustable playback speed (0.25x - 2x)
  - Frame-accurate seeking (← → keys)
  - Save/load playback positions
  - Toggle between video/audio-only modes

- **Interface**
  - Dark/Light theme support
  - Responsive layout (fullscreen/desktop modes)
  - Dual display modes:
    - Single video view with favorites list
    - Multi-video tree view with saved clips

- **Keyboard Shortcuts**
  - Space: Play/Pause
  - S/E: Set clip start/end
  - Delete: Remove selected clip
  - L: Toggle clip looping
  - A: Toggle audio/video mode
  - Q: Toggle half-speed
  - N/P: Navigate clips

## Installation

1. **Prerequisites**
   - Python 3.6+
   - [VLC Media Player](https://www.videolan.org/vlc/)

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure paths** (in `main.py` if needed)
   ```python
   # Adjust these paths in the __main__ block
   hardcoded_video_path = "your/video/path"
   hardcoded_base_video_dir = "your/video/directory"
   ```

## Usage

**Basic Controls**
1. Load video using button or drag-and-drop
2. Use slider or arrow keys to navigate
3. Create clips with Start Clip/Save Clip buttons
4. Switch modes using toolbar buttons

**Advanced Features**
- Double-click clips to play
- Right-click context menus for clip management
- Tree view shows clips across multiple videos
- Config files stored in `config/` directory

## Key Bindings

| Key | Action                  |
|-----|-------------------------|
| Space | Play/Pause            |
| ← → | Seek 3 seconds         |
| S   | Set clip start        |
| E   | Set clip end          |
| L   | Toggle loop           |
| Q   | Half-speed toggle     |
| A   | Audio/Video mode      |
| N/P | Next/Previous clip    |
| Del | Delete selected clip  |

## Configuration

- **Clip Storage**: Saved as JSON in `config/` directory
- **UI Settings**: Persist between sessions
- **Video Directory**: Set in `base_video_dir` parameter

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request
4. Maintain coding style and add tests
