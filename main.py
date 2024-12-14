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
    def __init__(self, video_player: VideoPlayer, clip_manager: ClipManager):
        super().__init__()
        self.setWindowTitle("English Listening Practice")
        self.main_layout = QHBoxLayout(self)
        self.create_widgets(video_player, clip_manager)
        self.setLayout(self.main_layout)
        self.resize(1000, 600)
    
    def create_widgets(self, video_player: VideoPlayer, clip_manager: ClipManager):
        self.create_video_slider_widget(video_player)
        # self.create_video_list_widget()
        self.create_clip_tree_widget(clip_manager)

    def create_video_slider_widget(self, video_player: VideoPlayer):
        layout = QVBoxLayout()

        self.video_widget = self._create_video_widget(video_player)
        layout.addWidget(self.video_widget)

        self.play_button = self._create_play_button()
        layout.addWidget(self.play_button)

        self.slider = self._create_slider(video_player)
        layout.addWidget(self.slider)
        
        self.main_layout.addLayout(layout, 3)

    def create_video_list_widget(self):
        layout = QVBoxLayout()

        self.video_list_widget = QListWidget(self)
        layout.addWidget(self.video_list_widget)

        self.main_layout.addLayout(layout, 1)

    def create_clip_tree_widget(self, clip_manager: ClipManager):
        layout = QVBoxLayout()

        self.video_clips_tree = QTreeWidget()
        self.video_clips_tree.setHeaderLabels(["Video"])
        # self.video_clips_tree.itemClicked.connect(self.on_clip_selected)  # Connect item click event
        # self.video_clips_tree.hide()  # Initially hide the tree
        layout.addWidget(self.video_clips_tree)

        for video_name, clips in clip_manager.video_clips.items():
            video_item = QTreeWidgetItem(self.video_clips_tree, [video_name])
            for clip in clips:
                start, end = clip['positions']
                clip_item = QTreeWidgetItem(video_item, [f"Clip: {start:.2f}s - {end:.2f}s"])
                video_item.addChild(clip_item)

        self.main_layout.addLayout(layout, 1)

    def _create_video_widget(self, video_player: VideoPlayer):
        return ClickableVideoWidget(video_player, self)
    
    def _create_play_button(self):
        button = QPushButton("Play/Pause", self)
        button.clicked.connect(self.video_widget.toggle_play_pause)
        return button

    def _create_slider(self, video_player: VideoPlayer):
        return ClickableSlider(video_player, self)


class ClickableVideoWidget(QWidget):
    def __init__(self, video_player: VideoPlayer, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.video_player = video_player
        self.video_player.set_output_widget(self)
        self.video_player.play()
    
    def mousePressEvent(self, event):
        self.toggle_play_pause()

    def toggle_play_pause(self):
        self.video_player.toggle_play_pause()


class ClickableSlider(QSlider):
    def __init__(self, video_player: VideoPlayer, parent=None):
        super().__init__()
        self.video_player = video_player
        self.setOrientation(Qt.Horizontal)
        self.setRange(0, 0)
        self.setValue(self.video_player.get_time())
        self.sliderMoved.connect(self.video_player.set_time)
        self.sliderPressed.connect(self.slider_clicked)  # Connect slider click
        self.setToolTip("0:00")  # Initial tooltip
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.setFixedHeight(20)  # Set a fixed height for the slider

        # Initialize a timer to update the slider position
        self.timer = QTimer(self)
        self.timer.setInterval(200)  # Update every 200 ms
        self.timer.timeout.connect(self.update_position)
        self.timer.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Calculate the new position based on the click
            new_value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), event.x(), self.width())
            self.setValue(new_value)
            
            # Debugging output
            # print(f"Clicked position: {event.x()}, New slider value: {new_value}")
            # print(f"Slider range: {self.minimum()} - {self.maximum()}")
            
            # Set the new position in the video widget
            self.video_player.set_time(new_value)
            
            # Check if the video player is in a state to accept the new position
            if not self.video_player.is_playing():
                # print("Video is not playing, attempting to play.")
                self.video_player.toggle_play_pause()

        # Call the base class implementation
        # super().mousePressEvent(event)
    
    def slider_clicked(self):
        value = self.value()
        self.video_player.set_time(value)
        if not self.video_player.is_playing():
            self.video_player.play()

    def update_position(self):
        current_time = self.video_player.get_time()
        total_time = self.video_player.get_length()
        
        if total_time > 0:
            self.setRange(0, total_time)
            self.setValue(current_time)
            # Update tooltip or label if needed
            current_time_str = self.format_time(current_time)
            total_time_str = self.format_time(total_time)
            self.setToolTip(f"{current_time_str} / {total_time_str}")

    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"

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