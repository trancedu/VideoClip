import sys
import os
import platform
from video_player import VideoPlayerApp
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    debug_mode = True  # Set this to True to enable debug mode
    home_path = os.path.expanduser("~")

    # Define the video and config path
    hardcoded_video_path = r"Videos/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E01.1080p.AMZN.WEB.mp4"
    hardcoded_base_video_dir = r"Videos"
    mac_config_path = "Library/CloudStorage/OneDrive-Personal/Projects/config"
    win_config_path = r"OneDrive/Projects/config"

    # Define the base video directory
    base_video_dir = os.path.join(home_path, hardcoded_base_video_dir)

    debug_video_path = os.path.join(home_path, hardcoded_video_path)
    if platform.system() == "Darwin":  # Darwin is the system name for macOS
        config_dir = os.path.join(home_path, mac_config_path)
    elif platform.system() == "Windows":
        config_dir = os.path.join(home_path, win_config_path)
    else:
        raise ValueError(f"Unsupported system: {platform.system()}")

    app = QApplication(sys.argv)
    window = VideoPlayerApp(debug=debug_mode, debug_video_path=debug_video_path, config_dir=config_dir, base_video_dir=base_video_dir)
    window.show()
    sys.exit(app.exec())
