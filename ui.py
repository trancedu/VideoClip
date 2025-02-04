from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QLabel, QSlider, QHBoxLayout, QToolTip, QInputDialog, QMenu,
    QStyle, QComboBox, QTreeWidget, QTreeWidgetItem, QSizePolicy  # Add QSizePolicy here
)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QMouseEvent
import os

from clip_manager import ClipManager
from video_player import VideoPlayer

class MainWindow(QWidget):
    def __init__(self, video_player: VideoPlayer, clip_manager: ClipManager):
        super().__init__()
        self.clip_manager = clip_manager
        self.setWindowTitle("English Listening Practice")
        self.video_player = video_player
        self.main_layout = QHBoxLayout(self)
        self.create_widgets()
        self.setLayout(self.main_layout)
        self.resize(1000, 600)
    
    def create_widgets(self):
        self.create_video_slider_widget()
        self.create_control_panel()

    def create_video_slider_widget(self):
        layout = QVBoxLayout()
        self.video_widget = ClickableVideoWidget(self.video_player, self)
        layout.addWidget(self.video_widget)
        
        self.play_button = QPushButton("Play/Pause", self)
        self.play_button.clicked.connect(self.video_player.toggle_play_pause)
        layout.addWidget(self.play_button)
        
        self.slider = ClickableSlider(self.video_player, self)
        layout.addWidget(self.slider)
        
        self.main_layout.addLayout(layout, 3)

    def create_control_panel(self):
        # Create main container for right panel
        right_panel = QVBoxLayout()
        
        # Create button container
        control_layout = QVBoxLayout()
        
        # Load Video Button
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        control_layout.addWidget(self.load_button)

        # Clip controls
        self.clip_button = QPushButton("Start Clip")
        self.clip_button.clicked.connect(self.start_clip)
        control_layout.addWidget(self.clip_button)

        self.save_clip_button = QPushButton("Save Clip")
        self.save_clip_button.clicked.connect(self.save_clip)
        control_layout.addWidget(self.save_clip_button)

        # Delete Clip Button
        self.delete_clip_button = QPushButton("Delete Clip")
        self.delete_clip_button.clicked.connect(self.delete_clip)
        control_layout.addWidget(self.delete_clip_button)

        # Speed controls
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1.0x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentIndexChanged.connect(self.change_speed)
        control_layout.addWidget(QLabel("Playback Speed:"))
        control_layout.addWidget(self.speed_combo)

        # Dark Mode Toggle
        self.dark_mode = True
        self.toggle_dark_button = QPushButton("Toggle Dark Mode")
        self.toggle_dark_button.clicked.connect(self.toggle_dark_mode)
        control_layout.addWidget(self.toggle_dark_button)

        # Feedback label
        self.feedback_label = QLabel()
        control_layout.addWidget(self.feedback_label)

        # Add clip tree widget below buttons
        self.clip_tree_widget = ClipTreeWidget(self.clip_manager, self.video_player)
        control_layout.addWidget(self.clip_tree_widget)
        
        # Add stretch to push elements to top
        control_layout.setStretchFactor(self.clip_tree_widget, 1)
        self.clip_tree_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add the control layout to right panel
        right_panel.addLayout(control_layout)
        
        # Add the right panel to main layout with 1:3 ratio
        self.main_layout.addLayout(right_panel, 1)

    def create_video_list_widget(self):
        layout = QVBoxLayout()

        self.video_list_widget = QListWidget(self)
        layout.addWidget(self.video_list_widget)

        self.main_layout.addLayout(layout, 1)

    def _create_video_widget(self, video_player: VideoPlayer):
        return ClickableVideoWidget(video_player, self)
    
    def _create_play_button(self):
        button = QPushButton("Play/Pause", self)
        button.clicked.connect(self.video_player.toggle_play_pause)
        return button

    def _create_slider(self, video_player: VideoPlayer):
        return ClickableSlider(video_player, self)

    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if path:
            self.video_player.load_video(path)
            self.feedback_label.setText(f"Loaded: {os.path.basename(path)}")

    def start_clip(self):
        self.clip_start = self.video_player.get_time() / 1000
        self.feedback_label.setText(f"Clip start: {self.clip_start:.1f}s")

    def save_clip(self):
        if hasattr(self, 'clip_start'):
            clip_end = self.video_player.get_time() / 1000
            video_name = os.path.basename(self.video_player.video_path)
            
            clip_data = {'positions': (self.clip_start, clip_end)}
            self.clip_manager.add_clip_to_video(video_name, clip_data)
            self.clip_manager.save_video_clips(video_name)
            
            self.clip_tree_widget.populate_tree()
            self.feedback_label.setText(f"Saved clip: {self.clip_start:.1f}s-{clip_end:.1f}s")
            del self.clip_start
        else:
            self.feedback_label.setText("Set start point first!")

    def delete_clip(self):
        item = self.clip_tree_widget.currentItem()
        if item and item.parent():
            video_name = item.parent().text(0)
            clip_index = item.parent().indexOfChild(item)
            
            del self.clip_manager.video_clips[video_name][clip_index]
            self.clip_manager.save_video_clips(video_name)
            self.clip_tree_widget.populate_tree()
            self.feedback_label.setText("Clip deleted")

    def change_speed(self):
        speed = float(self.speed_combo.currentText()[:-1])
        self.video_player.set_speed(speed)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(self.dark_stylesheet())
        else:
            self.setStyleSheet(self.light_stylesheet())

    def dark_stylesheet(self):
        return """
        QWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #4A4A4A;
            border: 1px solid #5A5A5A;
            padding: 5px;
        }
        QTreeWidget {
            background-color: #3A3A3A;
        }
        """

    def light_stylesheet(self):
        return """
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
        }
        QPushButton {
            background-color: #F0F0F0;
            border: 1px solid #CCCCCC;
            padding: 5px;
        }
        QTreeWidget {
            background-color: #E0E0E0;
        }
        """

class ClickableVideoWidget(QWidget):
    def __init__(self, video_player: VideoPlayer, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.video_player = video_player
        self.video_player.set_output_widget(self)
        self.video_player.play()
        self.setFocusPolicy(Qt.StrongFocus)
    
    def mousePressEvent(self, event):
        self.toggle_play_pause()

    def toggle_play_pause(self):
        self.video_player.toggle_play_pause()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.toggle_play_pause()
        elif key in (Qt.Key_Right, Qt.Key_K, Qt.Key_F):
            self.video_player.fast_forward(3)
        elif key in (Qt.Key_Left, Qt.Key_J, Qt.Key_D):
            self.video_player.fast_backward(3)
        else:
            super().keyPressEvent(event)


class ClickableSlider(QSlider):
    def __init__(self, video_player: VideoPlayer, parent=None):
        super().__init__(parent)
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
        self.timer.setInterval(100)  # Update every 100 ms
        self.timer.timeout.connect(self.update_position)
        self.timer.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            new_value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), event.x(), self.width())
            self.setValue(new_value)
            self.video_player.set_time(new_value)
            self.video_player.current_clip_end = None  # Reset clip tracking
            if not self.video_player.is_playing():
                self.video_player.toggle_play_pause()

    def slider_clicked(self):
        value = self.value()
        self.video_player.set_time(value)
        self.video_player.current_clip_end = None  # Reset clip tracking
        if not self.video_player.is_playing():
            self.video_player.play()

    def update_position(self):
        current_time = self.video_player.get_time()
        total_time = self.video_player.get_length()
        
        if total_time > 0:
            self.setRange(0, total_time)
            self.setValue(current_time)
            current_time_str = self.format_time(current_time)
            total_time_str = self.format_time(total_time)
            self.setToolTip(f"{current_time_str} / {total_time_str}")

        # Add clip boundary check
        if (self.video_player.current_clip_end is not None and 
            current_time >= self.video_player.current_clip_end):
            self.video_player.pause()
            self.video_player.current_clip_end = None

    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"
    

class ClipTreeWidget(QTreeWidget):
    def __init__(self, clip_manager: ClipManager, video_player: VideoPlayer, parent=None):
        super().__init__(parent)
        self.clip_manager = clip_manager
        self.video_player = video_player
        self.setHeaderLabels(["Video"])
        self.populate_tree()
        self.itemClicked.connect(self.on_clip_selected)

    def populate_tree(self):
        for video_name, clips in self.clip_manager.video_clips.items():
            video_item = QTreeWidgetItem(self, [video_name])
            for clip in clips:
                start, end = clip['positions']
                clip_item = QTreeWidgetItem(video_item, [f"Clip: {start:.2f}s - {end:.2f}s"])
                video_item.addChild(clip_item)

    def on_clip_selected(self):
        """Play the selected clip not video in the tree"""
        item = self.currentItem()
        if item and item.parent():
            video_name = item.parent().text(0)
            clip_text = item.text(0)
            start, end = self.parse_clip_text(clip_text)

            video_path = self.clip_manager.get_video_path(video_name)
            if self.video_player.get_video_path() != video_path:
                self.video_player.load_video(video_path=video_path)
                self.video_player.play()

            # Set clip boundaries and play
            self.video_player.play(int(start * 1000))
            self.video_player.current_clip_end = int(end * 1000)

    def parse_clip_text(self, clip_text):
        """Parse the clip text to extract start and end times."""
        # Example clip text: "Clip: 10.00s - 20.00s"
        parts = clip_text.split(": ")[1].split(" - ")
        start = float(parts[0].replace("s", ""))
        end = float(parts[1].replace("s", ""))
        return start, end
