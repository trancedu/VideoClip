import sys
import os
import json
import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QLabel, QSlider, QHBoxLayout, QToolTip, QInputDialog, QMenu,
    QStyle, QComboBox, QTreeWidget, QTreeWidgetItem  # Add this import
)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QMouseEvent
import platform

from config_manager import ConfigManager
from clip_manager import ClipManager
from video_player import VideoPlayer

class MainWindow(QWidget):
    def __init__(self, video_player: VideoPlayer):
        super().__init__()
        self.setWindowTitle("English Listening Practice")
        self.video_player = video_player
        self.create_video_widget()

    def create_video_widget(self):
        layout = QVBoxLayout(self)

        self.video_widget = QWidget(self)
        self.video_player.set_output_widget(self.video_widget)
        layout.addWidget(self.video_widget)

        self.setLayout(layout)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.video_player.play)
        layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.video_player.pause)
        layout.addWidget(self.pause_button)

        self.resize(800, 600)

def main():
    video_path = r"Videos/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E01.1080p.AMZN.WEB.mp4"
    mac_config_path = r"Library/CloudStorage/OneDrive-Personal/Projects/config"
    
    config_manager = ConfigManager(video_path, mac_config_path)
    clip_manager = ClipManager()
    video_player = VideoPlayer()
    video_player.load_video(config_manager.get_video_path())
    # video_player.play()

    app = QApplication(sys.argv)
    window = MainWindow(video_player)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()