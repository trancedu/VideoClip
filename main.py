import sys
import os
import tempfile
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel, QSlider
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget

class VideoPlayerApp(QWidget):
    def __init__(self, debug=False, debug_video_path=None):
        super().__init__()
        self.setWindowTitle("English Listening Practice")
        
        # Initialize variables
        self.video_path = None
        self.is_playing = False
        self.favorites = []
        self.current_clip_start = None
        self.current_clip_end = None
        self.main_video_position = 0  # Store the last position of the main video
        self.position_saved = False  # Flag to check if the position has been saved
        
        # Create media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        # Create widgets
        self.create_widgets()
        
        # Connect media player signals
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        
        # Load a specific video if debug flag is set
        if debug and debug_video_path:
            self.load_video(video_path=debug_video_path)
        
    def create_widgets(self):
        layout = QVBoxLayout()
        
        # Load Video Button
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_button)
        
        # Video controls
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        self.play_button.setEnabled(False)
        layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        self.pause_button.setEnabled(False)
        layout.addWidget(self.pause_button)
        
        self.forward_button = QPushButton("Forward 5s")
        self.forward_button.clicked.connect(lambda: self.skip(5))
        self.forward_button.setEnabled(False)
        layout.addWidget(self.forward_button)
        
        self.backward_button = QPushButton("Backward 5s")
        self.backward_button.clicked.connect(lambda: self.skip(-5))
        self.backward_button.setEnabled(False)
        layout.addWidget(self.backward_button)
        
        # Initialize the position slider here
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        
        # Clip controls
        self.clip_button = QPushButton("Start Clip")
        self.clip_button.clicked.connect(self.start_clip)
        self.clip_button.setEnabled(False)
        layout.addWidget(self.clip_button)
        
        self.save_clip_button = QPushButton("Save Clip")
        self.save_clip_button.clicked.connect(self.save_clip)
        self.save_clip_button.setEnabled(False)
        layout.addWidget(self.save_clip_button)
        
        # Feedback label
        self.feedback_label = QLabel("")
        layout.addWidget(self.feedback_label)
        
        # Favorites
        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self.play_favorite)  # Connect double-click signal
        layout.addWidget(self.favorites_list)
        
        self.play_favorite_button = QPushButton("Play Favorite")
        self.play_favorite_button.clicked.connect(self.play_favorite)
        layout.addWidget(self.play_favorite_button)
        
        # Delete Clip Button
        self.delete_clip_button = QPushButton("Delete Clip")
        self.delete_clip_button.clicked.connect(self.delete_clip)
        layout.addWidget(self.delete_clip_button)
        
        # Return to Main Video Button
        self.return_button = QPushButton("Return to Main Video")
        self.return_button.clicked.connect(self.return_to_main_video)
        self.return_button.setEnabled(False)
        layout.addWidget(self.return_button)
        
        self.setLayout(layout)
        
    def update_position(self, position):
        self.position_slider.setValue(position)
        
    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)
        
    def set_position(self, position):
        self.media_player.setPosition(position)
        
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
                # Create a new window for video playback
                self.video_window = QWidget()
                self.video_window.setWindowTitle("Video Playback")
                
                # Calculate the aspect ratio based on the video's resolution
                video_width = 800
                video_height = 500  # Default height in case metadata is not available
                
                # Check if metadata is available
                if self.media_player.isMetaDataAvailable():
                    resolution = self.media_player.metaData("Resolution")
                    if resolution:
                        aspect_ratio = resolution.width() / resolution.height()
                        video_height = int(video_width / aspect_ratio)
                
                # Resize the window to fit the video
                self.video_window.resize(video_width, video_height)
                self.video_layout = QVBoxLayout()
                
                # Create a video widget and set it as the central widget of the new window
                self.video_widget = QVideoWidget()
                self.media_player.setVideoOutput(self.video_widget)
                self.video_layout.addWidget(self.video_widget)
                
                # Add the progress bar to the video playback window
                self.video_layout.addWidget(self.position_slider)
                
                self.video_window.setLayout(self.video_layout)
                
                # Show the video window and play the video
                self.video_window.show()
                self.media_player.play()
                self.is_playing = True
                self.feedback_label.setText("Playing video")
            except Exception as e:
                self.feedback_label.setText(f"Error playing video: {e}")
                
    def pause_video(self):
        if self.is_playing:
            self.media_player.pause()
            self.is_playing = False
            self.feedback_label.setText("Video paused")
            
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
                self.media_player.setPosition(int(clip_positions[0] * 1000))  # Convert to milliseconds
                self.media_player.play()
                self.is_playing = True
                self.return_button.setEnabled(True)
                self.feedback_label.setText(f"Playing clip {selected_row + 1}")
                
                # Stop the video at the end position
                self.media_player.positionChanged.connect(lambda pos: self.stop_at_end(pos, clip_positions[1]))
            else:
                self.feedback_label.setText("Main video file not found!")
        else:
            self.feedback_label.setText("No clip selected.")
            
    def stop_at_end(self, current_position, end_position):
        if current_position >= int(end_position * 1000):  # Convert to milliseconds
            self.media_player.pause()
            self.feedback_label.setText("Clip playback finished.")
            self.media_player.positionChanged.disconnect()  # Disconnect the signal to stop checking
            
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
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_clip()
        elif event.key() == Qt.Key_Right:
            self.skip(5)
        elif event.key() == Qt.Key_Left:
            self.skip(-5)
    
if __name__ == "__main__":
    debug_mode = True  # Set this to True to enable debug mode
    debug_video_path = "/Users/trance/Movies/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E03.1080p.AMZN.WEB.mp4"
    
    app = QApplication(sys.argv)
    window = VideoPlayerApp(debug=debug_mode, debug_video_path=debug_video_path)
    window.show()
    sys.exit(app.exec_())
