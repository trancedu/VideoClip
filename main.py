import sys
import os
import tempfile
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel, QSlider, QHBoxLayout, QToolTip
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimediaWidgets import QVideoWidget

class VideoPlayerApp(QWidget):
    def __init__(self, debug=False, debug_video_path=None):
        super().__init__()
        self.setWindowTitle("English Listening Practice")
        self.resize(1800, 1200)  # Set the window size to 1800x1200
        self.setFocusPolicy(Qt.StrongFocus)  # Ensure the window can capture key events
        
        # Initialize variables
        self.video_path = None
        self.is_playing = False
        self.favorites = []
        self.current_clip_start = None
        self.current_clip_end = None
        self.main_video_position = 0  # Store the last position of the main video
        self.position_saved = False  # Flag to check if the position has been saved
        self.loop_enabled = False  # Flag to check if looping is enabled
        
        # Create media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        # Create widgets
        self.create_widgets()
        
        # Timer for checking playback position
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.check_playback_position)
        
        # Connect media player signals
        self.media_player.durationChanged.connect(self.update_duration)
        
        # Load a specific video if debug flag is set
        if debug and debug_video_path:
            self.load_video(video_path=debug_video_path)
        
    def create_widgets(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Video display area
        video_layout = QVBoxLayout()
        self.video_widget = ClickableVideoWidget(self)  # Use the custom video widget
        self.media_player.setVideoOutput(self.video_widget)
        video_layout.addWidget(self.video_widget, stretch=1)  # Allow video to expand
        
        # Progress bar and duration label layout
        progress_layout = QHBoxLayout()
        
        # Progress bar
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.sliderPressed.connect(self.slider_clicked)  # Connect slider click
        self.position_slider.setToolTip("0:00")  # Initial tooltip
        self.position_slider.setMouseTracking(True)
        self.position_slider.installEventFilter(self)
        self.position_slider.setFixedHeight(20)  # Set a fixed height for the slider
        progress_layout.addWidget(self.position_slider)
        
        # Video duration label
        self.duration_label = QLabel("0:00 / 0:00")
        progress_layout.addWidget(self.duration_label)
        
        # Add progress layout to video layout
        video_layout.addLayout(progress_layout)
        
        # Add video layout to main layout
        main_layout.addLayout(video_layout, 7)  # 7/8 of the width
        
        # Control panel
        control_layout = QVBoxLayout()
        
        # Load Video Button
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        control_layout.addWidget(self.load_button)
        
        # Video controls
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        self.play_button.setEnabled(False)
        control_layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.forward_button = QPushButton("Forward 5s")
        self.forward_button.clicked.connect(lambda: self.skip(5))
        self.forward_button.setEnabled(False)
        control_layout.addWidget(self.forward_button)
        
        self.backward_button = QPushButton("Backward 5s")
        self.backward_button.clicked.connect(lambda: self.skip(-5))
        self.backward_button.setEnabled(False)
        control_layout.addWidget(self.backward_button)
        
        # Clip controls
        self.clip_button = QPushButton("Start Clip")
        self.clip_button.clicked.connect(self.start_clip)
        self.clip_button.setEnabled(False)
        control_layout.addWidget(self.clip_button)
        
        self.save_clip_button = QPushButton("Save Clip")
        self.save_clip_button.clicked.connect(self.save_clip)
        self.save_clip_button.setEnabled(False)
        control_layout.addWidget(self.save_clip_button)
        
        # Feedback label
        self.feedback_label = QLabel("")
        control_layout.addWidget(self.feedback_label)
        
        # Favorites
        self.favorites_list = CustomListWidget(self)  # Use the custom list widget
        self.favorites_list.itemDoubleClicked.connect(self.play_favorite)  # Connect double-click signal
        control_layout.addWidget(self.favorites_list)
        
        self.play_favorite_button = QPushButton("Play Favorite")
        self.play_favorite_button.clicked.connect(self.play_favorite)
        control_layout.addWidget(self.play_favorite_button)
        
        # Delete Clip Button
        self.delete_clip_button = QPushButton("Delete Clip")
        self.delete_clip_button.clicked.connect(self.delete_clip)
        control_layout.addWidget(self.delete_clip_button)
        
        # Return to Main Video Button
        self.return_button = QPushButton("Return to Main Video")
        self.return_button.clicked.connect(self.return_to_main_video)
        self.return_button.setEnabled(False)
        control_layout.addWidget(self.return_button)
        
        # Add control layout to main layout
        main_layout.addLayout(control_layout, 1)  # 1/8 of the width
        
        self.setLayout(main_layout)
        
    def toggle_play_pause(self):
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()

    def update_position(self, position):
        self.position_slider.setValue(position)
        current_time = self.format_time(position)
        total_time = self.format_time(self.media_player.duration())
        self.duration_label.setText(f"{current_time} / {total_time}")
        
    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)
        total_time = self.format_time(duration)
        current_time = self.format_time(self.media_player.position())
        self.duration_label.setText(f"{current_time} / {total_time}")
        
    def set_position(self, position):
        self.media_player.setPosition(position)
        
    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"
    
    def eventFilter(self, source, event):
        if source is self.position_slider and event.type() == event.MouseMove:
            pos = event.pos().x()
            value = self.position_slider.minimum() + (self.position_slider.maximum() - self.position_slider.minimum()) * pos / self.position_slider.width()
            tooltip_time = self.format_time(int(value))
            QToolTip.showText(event.globalPos(), tooltip_time, self.position_slider)
        return super().eventFilter(source, event)
    
    def load_video(self, video_path=None):
        if video_path and os.path.exists(video_path):
            self.video_path = video_path
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            self.video_path, _ = QFileDialog.getOpenFileName(
                self, "Open Video File", "", "Video Files (*.mp4 *.avi)", options=options)
        
        if self.video_path and os.path.exists(self.video_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.forward_button.setEnabled(True)
            self.backward_button.setEnabled(True)
            self.clip_button.setEnabled(True)
            self.save_clip_button.setEnabled(True)
            self.feedback_label.setText(f"Loaded video: {os.path.basename(self.video_path)}")
            
            # Load saved clip positions
            self.load_clips_from_file()
            
            # Automatically play the video after loading
            self.play_video()
        else:
            self.feedback_label.setText("Video file not found.")
    
    def play_video(self):
        if self.video_path:
            try:
                self.media_player.play()
                self.is_playing = True
                self.feedback_label.setText("Playing video")
                self.playback_timer.start(50)  # Start the timer to check playback position every 50ms
            except Exception as e:
                self.feedback_label.setText(f"Error playing video: {e}")
    
    def pause_video(self):
        if self.is_playing:
            self.media_player.pause()
            self.is_playing = False
            self.feedback_label.setText("Video paused")
            self.playback_timer.stop()  # Stop the timer when paused
            
    def skip(self, seconds):
        if self.media_player.duration() > 0:
            current_position = self.media_player.position()
            new_position = current_position + seconds * 1000  # milliseconds
            new_position = max(0, min(new_position, self.media_player.duration()))
            self.media_player.setPosition(new_position)
            direction = "forward" if seconds > 0 else "backward"
            self.feedback_label.setText(f"Skipped {direction} {abs(seconds)} seconds")
                
    def start_clip(self):
        if self.media_player.duration() > 0:
            self.current_clip_start = self.media_player.position() / 1000.0  # seconds
            self.feedback_label.setText("Clip start point set.")
            
    def save_clip(self):
        if self.current_clip_start is not None:
            self.current_clip_end = self.media_player.position() / 1000.0  # seconds
            if self.current_clip_end > self.current_clip_start:
                # Save the start and end positions as a tuple
                clip_positions = (self.current_clip_start, self.current_clip_end)
                self.favorites.append(clip_positions)
                self.favorites_list.addItem(f"Clip {len(self.favorites)}: {self.current_clip_start:.2f}s - {self.current_clip_end:.2f}s")
                self.feedback_label.setText("Clip positions saved!")

                # Save to JSON file
                self.save_clips_to_file()
            else:
                self.feedback_label.setText("Invalid clip duration.")
        else:
            self.feedback_label.setText("Set the clip start point first.")
            
    def save_clips_to_file(self):
        if self.video_path:
            config_dir = os.path.join(os.path.dirname(self.video_path), "config")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, f"{os.path.basename(self.video_path)}.json")
            
            with open(config_file, 'w') as f:
                json.dump(self.favorites, f)
            self.feedback_label.setText("Clip positions saved to file.")
            
    def load_clips_from_file(self):
        if self.video_path:
            config_dir = os.path.join(os.path.dirname(self.video_path), "config")
            config_file = os.path.join(config_dir, f"{os.path.basename(self.video_path)}.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.favorites = json.load(f)
                self.favorites_list.clear()
                for i, (start, end) in enumerate(self.favorites):
                    self.favorites_list.addItem(f"Clip {i + 1}: {start:.2f}s - {end:.2f}s")
                self.feedback_label.setText("Clip positions loaded from file.")
            else:
                self.feedback_label.setText("No saved clip positions found.")
                
    def play_favorite(self):
        selected_row = self.favorites_list.currentRow()
        if selected_row >= 0:
            clip_positions = self.favorites[selected_row]
            if self.video_path:
                # Save the current position of the main video only if not already saved
                if not self.position_saved:
                    self.main_video_position = self.media_player.position()
                    self.position_saved = True
                
                # Set the media to the main video and play from the start to end positions
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
                self.current_clip_start, self.current_clip_end = clip_positions  # Set the current clip start and end
                print(f"Playing clip from {self.current_clip_start} to {self.current_clip_end}")
                self.media_player.setPosition(int(self.current_clip_start * 1000))  # Convert to milliseconds
                self.media_player.play()
                self.is_playing = True
                self.return_button.setEnabled(True)
                self.feedback_label.setText(f"Playing clip {selected_row + 1}")
            else:
                self.feedback_label.setText("Main video file not found!")
        else:
            self.feedback_label.setText("No clip selected.")
            
    def check_playback_position(self):
        current_position = self.media_player.position()
        self.update_position(current_position)  # Update the progress bar less frequently if needed
        if self.current_clip_end is not None:  # Ensure current_clip_end is set
            #print(f"Current position: {current_position}, End position: {int(self.current_clip_end * 1000)}")
            if current_position >= int(self.current_clip_end * 1000):  # Convert to milliseconds
                if self.loop_enabled:
                    # Apply an additional 500ms buffer when looping
                    adjusted_start = max(0, self.current_clip_start * 1000 - 500)
                    #print(f"Looping from {self.current_clip_start} to {adjusted_start}")
                    self.media_player.setPosition(int(adjusted_start))
                else:
                    self.media_player.pause()
                    self.feedback_label.setText("Clip playback finished.")
    
    def return_to_main_video(self):
        if self.video_path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.media_player.setPosition(self.main_video_position)  # Resume from last position
            self.media_player.play()
            self.is_playing = True
            self.return_button.setEnabled(False)
            self.position_saved = False  # Reset the flag
            self.feedback_label.setText("Returned to main video")
        
    def delete_clip(self):
        selected_row = self.favorites_list.currentRow()
        if selected_row >= 0:
            del self.favorites[selected_row]
            self.favorites_list.takeItem(selected_row)
            self.save_clips_to_file()
            self.feedback_label.setText(f"Deleted clip {selected_row + 1}")
        else:
            self.feedback_label.setText("No clip selected to delete.")
    
    def toggle_loop(self):
        self.loop_enabled = not self.loop_enabled
        status = "enabled" if self.loop_enabled else "disabled"
        self.feedback_label.setText(f"Looping {status}")

    def next_clip(self):
        current_row = self.favorites_list.currentRow()
        if current_row < self.favorites_list.count() - 1:
            self.favorites_list.setCurrentRow(current_row + 1)
            self.play_favorite()

    def previous_clip(self):
        current_row = self.favorites_list.currentRow()
        if current_row > 0:
            self.favorites_list.setCurrentRow(current_row - 1)
            self.play_favorite()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_clip()
        elif event.key() == Qt.Key_Right:
            self.skip(3)  # Fine-tuned seeking
        elif event.key() == Qt.Key_Left:
            self.skip(-3)  # Fine-tuned seeking
        elif event.key() == Qt.Key_Space:
            if self.is_playing:
                self.pause_video()
            else:
                self.play_video()
        elif event.key() == Qt.Key_S:
            self.start_clip()
        elif event.key() == Qt.Key_E:
            self.save_clip()
        elif event.key() == Qt.Key_L:
            self.toggle_loop()
        elif event.key() == Qt.Key_N:
            self.next_clip()
        elif event.key() == Qt.Key_P:
            self.previous_clip()
    
    def slider_clicked(self):
        # Calculate the position based on the click
        value = self.position_slider.value()
        self.set_position(value)

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        # Propagate the event to the parent widget
        if event.key() in (Qt.Key_Space, Qt.Key_S, Qt.Key_E):
            self.parent().keyPressEvent(event)
        elif event.key() == Qt.Key_L:
            self.parent().toggle_loop()
        elif event.key() == Qt.Key_N:
            self.parent().next_clip()
        elif event.key() == Qt.Key_P:
            self.parent().previous_clip()
        else:
            super().keyPressEvent(event)

class ClickableVideoWidget(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        # Call the toggle play/pause method in the parent
        self.parent().toggle_play_pause()

if __name__ == "__main__":
    debug_mode = True  # Set this to True to enable debug mode
    debug_video_path = "/Users/trance/Movies/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E03.1080p.AMZN.WEB.mp4"
    
    app = QApplication(sys.argv)
    window = VideoPlayerApp(debug=debug_mode, debug_video_path=debug_video_path)
    window.show()
    sys.exit(app.exec_())
