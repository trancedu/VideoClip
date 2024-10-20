import sys
import os
import tempfile
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
            self.video_path = debug_video_path
            if os.path.exists(self.video_path):
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
                self.play_button.setEnabled(True)
                self.pause_button.setEnabled(True)
                self.forward_button.setEnabled(True)
                self.backward_button.setEnabled(True)
                self.clip_button.setEnabled(True)
                self.save_clip_button.setEnabled(True)
                self.feedback_label.setText(f"Loaded video: {os.path.basename(self.video_path)}")
                self.play_video()  # Automatically play the video after loading
            else:
                self.feedback_label.setText("Debug video file not found.")
        
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
        
        # Progress bar
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.position_slider)
        
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
        layout.addWidget(self.favorites_list)
        
        self.play_favorite_button = QPushButton("Play Favorite")
        self.play_favorite_button.clicked.connect(self.play_favorite)
        layout.addWidget(self.play_favorite_button)
        
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
        
    def load_video(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.video_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi)", options=options)
        if self.video_path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.forward_button.setEnabled(True)
            self.backward_button.setEnabled(True)
            self.clip_button.setEnabled(True)
            self.save_clip_button.setEnabled(True)
            self.feedback_label.setText(f"Loaded video: {os.path.basename(self.video_path)}")
            self.play_video()  # Automatically play the video after loading
            
    def play_video(self):
        if self.video_path:
            try:
                # Create a new window for video playback
                self.video_window = QWidget()
                self.video_window.setWindowTitle("Video Playback")
                
                # Calculate the aspect ratio based on the video's resolution
                video_width = 800
                video_height = 450  # Default height in case metadata is not available
                
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
                # Use moviepy to extract the clip
                from moviepy.editor import VideoFileClip
                clip = VideoFileClip(self.video_path).subclip(self.current_clip_start, self.current_clip_end)
                # Save clip to temporary file
                temp_dir = tempfile.gettempdir()
                clip_filename = f"clip_{len(self.favorites)}.mp4"
                temp_file_path = os.path.join(temp_dir, clip_filename)
                self.feedback_label.setText("Saving clip, please wait...")
                QApplication.processEvents()  # Update UI
                
                try:
                    clip.write_videofile(temp_file_path, codec='libx264', audio_codec='aac', remove_temp=True, logger=None)
                    self.favorites.append(temp_file_path)
                    self.favorites_list.addItem(f"Clip {len(self.favorites)}")
                    self.feedback_label.setText("Clip saved!")
                except Exception as e:
                    self.feedback_label.setText(f"Error saving clip: {e}")
            else:
                self.feedback_label.setText("Invalid clip duration.")
        else:
            self.feedback_label.setText("Set the clip start point first.")
            
    def play_favorite(self):
        selected_row = self.favorites_list.currentRow()
        if selected_row >= 0:
            clip_path = self.favorites[selected_row]
            if os.path.exists(clip_path):
                # Save the current position of the main video only if not already saved
                if not self.position_saved:
                    self.main_video_position = self.media_player.position()
                    self.position_saved = True
                
                # Load the clip into media player
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(clip_path)))
                self.media_player.play()
                self.is_playing = True
                self.return_button.setEnabled(True)
                self.feedback_label.setText(f"Playing clip {selected_row + 1}")
            else:
                self.feedback_label.setText("Clip file not found!")
        else:
            self.feedback_label.setText("No clip selected.")
            
    def return_to_main_video(self):
        if self.video_path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
            self.media_player.setPosition(self.main_video_position)  # Resume from last position
            self.media_player.play()
            self.is_playing = True
            self.return_button.setEnabled(False)
            self.position_saved = False  # Reset the flag
            self.feedback_label.setText("Returned to main video")
        
if __name__ == "__main__":
    debug_mode = True  # Set this to True to enable debug mode
    debug_video_path = "/Users/trance/Movies/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E03.1080p.AMZN.WEB.mp4"
    
    app = QApplication(sys.argv)
    window = VideoPlayerApp(debug=debug_mode, debug_video_path=debug_video_path)
    window.show()
    sys.exit(app.exec_())
