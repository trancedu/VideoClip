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
        self.create_video_widget(video_player) 

    def create_video_widget(self, video_player: VideoPlayer):
        layout = QVBoxLayout(self)

        self.video_widget = ClickableVideoWidget(video_player, self)
        layout.addWidget(self.video_widget)

        self.play_button = QPushButton("Play/Pause", self)
        self.play_button.clicked.connect(self.video_widget.toggle_play_pause)
        layout.addWidget(self.play_button)

        self.create_slider()
        layout.addWidget(self.slider)
        
        self.setLayout(layout)
        self.resize(800, 600)

    def create_slider(self):
        self.slider = ClickableSlider(self.video_widget, self)

class ClickableVideoWidget(QWidget):
    def __init__(self, video_player: VideoPlayer, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.video_player = video_player
        self.video_player.set_output_widget(self)
    
    def mousePressEvent(self, event):
        self.toggle_play_pause()

    def toggle_play_pause(self):
        self.video_player.toggle_play_pause()

    def set_position(self, position):
        self.video_player.set_position(position)

    def is_playing(self):
        return self.video_player.is_playing


class ClickableSlider(QSlider):
    def __init__(self, video_widget: ClickableVideoWidget, parent=None):
        super().__init__()
        self.video_widget = video_widget
        self.setOrientation(Qt.Horizontal)
        self.setRange(0, 100)
        self.sliderMoved.connect(self.video_widget.set_position)
        self.sliderPressed.connect(self.slider_clicked)  # Connect slider click
        self.setToolTip("0:00")  # Initial tooltip
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedHeight(20)  # Set a fixed height for the slider

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Calculate the new position based on the click
            new_value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), event.x(), self.width())
            self.setValue(new_value)
            print(new_value)
            self.video_widget.set_position(new_value)
        super().mousePressEvent(event)
    
    def slider_clicked(self):
        value = self.value()
        self.video_widget.set_position(value)
        if not self.video_widget.is_playing:
            self.video_widget.play_video()

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