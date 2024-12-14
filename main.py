from ui import MainWindow
from config_manager import ConfigManager
from clip_manager import ClipManager
from video_player import VideoPlayer

import sys
from PyQt5.QtWidgets import QApplication

def main():
    video_path = r"Videos/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E01.1080p.AMZN.WEB.mp4"
    mac_clip_path = r"Library/CloudStorage/OneDrive-Personal/Projects/config"
    video_base_path = r"Videos"
    
    config_manager = ConfigManager(video_path, mac_clip_path, video_base_path)
    clip_manager = ClipManager(config_manager.get_clip_path(), config_manager.get_video_base_path())
    video_player = VideoPlayer()
    video_player.load_video(config_manager.get_video_path())

    app = QApplication(sys.argv)
    window = MainWindow(video_player, clip_manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()