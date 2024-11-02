import sys
import os
import json
import vlc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QLabel, QSlider, QHBoxLayout, QToolTip, QInputDialog, QMenu,
    QStyle  # Add this import
)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QMouseEvent

class VideoPlayerApp(QWidget):
    def __init__(self, debug=False, debug_video_path=None, config_dir=None):
        super().__init__()
        self.setWindowTitle("English Listening Practice")

        # Get the screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.size()

        # Check if screen ratio is smaller than 2
        if screen_size.width() / screen_size.height() < 2:
            self.showFullScreen()  # Use showFullScreen to maximize the window to use full screen space
        else:
            self.resize(1800, 1200)  # Set window size to 1800x1200

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

        # Initialize mode
        self.audio_mode = False  # Start in video mode

        # Create VLC instance and media player
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Disable VLC's handling of mouse and key inputs
        self.media_player.video_set_mouse_input(False)
        self.media_player.video_set_key_input(False)
        
        # Create widgets
        self.create_widgets()

        # Create a timer to update the UI
        self.timer = QTimer(self)
        self.timer.setInterval(200)  # Adjust the interval as needed
        self.timer.timeout.connect(self.update_position)
        self.timer.timeout.connect(self.check_loop_position)

        # Set the config path
        if config_dir:
            self.config_dir = config_dir
        else:
            self.config_dir = os.path.join(os.getcwd(), "config")

        # Load a specific video if debug flag is set
        if debug and debug_video_path:
            self.load_video(video_path=debug_video_path)

        # Install an event filter to capture key events globally
        QApplication.instance().installEventFilter(self)

    def create_widgets(self):
        # Main layout
        main_layout = QHBoxLayout(self)

        # Video display area
        video_layout = QVBoxLayout()
        self.video_widget = ClickableVideoWidget(self)  # Use the custom video widget

        # Set the video output to the video widget
        if sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_widget.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.media_player.set_nsobject(int(self.video_widget.winId()))
        elif sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_widget.winId())

        video_layout.addWidget(self.video_widget, stretch=1)  # Allow video to expand

        # Progress bar and duration label layout
        progress_layout = QHBoxLayout()

        # Progress bar
        self.position_slider = ClickableSlider(Qt.Horizontal)  # Use the custom slider
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

        # Toggle Video/Audio Mode Button
        self.toggle_mode_button = QPushButton("Audio/Video Mode")
        self.toggle_mode_button.clicked.connect(self.toggle_video_audio_mode)
        control_layout.addWidget(self.toggle_mode_button)

        # Add control layout to main layout
        main_layout.addLayout(control_layout, 1)  # 1/8 of the width

        self.setLayout(main_layout)

    def toggle_play_pause(self):
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()

    def update_position(self):
        current_time = self.media_player.get_time()
        total_time = self.media_player.get_length()
        if total_time > 0:
            self.position_slider.setRange(0, total_time)
            self.position_slider.setValue(current_time)
            current_time_str = self.format_time(current_time)
            total_time_str = self.format_time(total_time)
            self.duration_label.setText(f"{current_time_str} / {total_time_str}")
        else:
            self.position_slider.setValue(0)
            self.duration_label.setText("0:00 / 0:00")

    def set_position(self, position):
        self.media_player.set_time(int(position))

    def format_time(self, ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02}"

    def eventFilter(self, source, event):
        if source is self.position_slider and event.type() == event.MouseMove:
            pos = event.pos().x()
            value = self.position_slider.minimum() + (self.position_slider.maximum() - self.position_slider.minimum()) * pos / self.position_slider.width()
            tooltip_time = self.format_time(int(value))
            QToolTip.showText(event.globalPos(), tooltip_time, self.position_slider)
        # Check if the event is a key press event
        elif event.type() == QEvent.KeyPress:
            # Handle left and right arrow keys globally
            if event.key() == Qt.Key_Right:
                self.skip(3)  # Fine-tuned seeking
                return True  # Event handled
            elif event.key() == Qt.Key_Left:
                self.skip(-3)  # Fine-tuned seeking
                return True  # Event handled
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
            # Create VLC media and set it to the player
            media = self.instance.media_new(self.video_path)
            self.media_player.set_media(media)

            # Update the paths for loading and saving clips
            self.update_clip_paths()

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

    def update_clip_paths(self):
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, f"{os.path.basename(self.video_path)}.json")

    def play_video(self):
        if self.video_path:
            try:
                if not self.media_player.get_media():
                    media = self.instance.media_new(self.video_path)
                    self.media_player.set_media(media)
                self.media_player.play()
                self.is_playing = True
                self.timer.start()
                self.feedback_label.setText("Playing video")
            except Exception as e:
                self.feedback_label.setText(f"Error playing video: {e}")

    def pause_video(self):
        if self.is_playing:
            self.media_player.pause()
            self.is_playing = False
            self.feedback_label.setText("Video paused")

    def skip(self, seconds):
        if self.media_player.get_length() > 0:
            current_time = self.media_player.get_time()
            new_time = current_time + seconds * 1000  # milliseconds
            new_time = max(0, min(new_time, self.media_player.get_length()))
            self.media_player.set_time(int(new_time))
            direction = "forward" if seconds > 0 else "backward"
            self.feedback_label.setText(f"Skipped {direction} {abs(seconds)} seconds")

    def start_clip(self):
        if self.media_player.get_length() > 0:
            self.current_clip_start = self.media_player.get_time() / 1000.0  # seconds
            self.feedback_label.setText("Clip start point set.")

    def save_clip(self):
        if self.current_clip_start is not None:
            self.current_clip_end = self.media_player.get_time() / 1000.0  # seconds
            if self.current_clip_end > self.current_clip_start:
                clip_data = {
                    'positions': (self.current_clip_start, self.current_clip_end),
                }
                self.favorites.append(clip_data)

                # Sort clips after adding a new one
                self.sort_clips()

                # Update the favorites list widget
                self.update_favorites_list()
                
                self.feedback_label.setText("Clip positions saved!")
                
                # Save to JSON file
                self.save_clips_to_file()

                # Find the index of the newly added clip
                new_clip_index = self.favorites.index(clip_data)

                # Select the newly added clip
                self.favorites_list.setCurrentRow(new_clip_index)
            else:
                self.feedback_label.setText("Invalid clip duration.")
        else:
            self.feedback_label.setText("Set the clip start point first.")

    def sort_clips(self):
        """Sort the favorites list by start time."""
        self.favorites.sort(key=lambda clip: clip['positions'][0])

    def save_clips_to_file(self):
        if self.video_path:
            # Use the updated config_file path
            clips_to_save = [{'positions': clip['positions']} for clip in self.favorites]

            with open(self.config_file, 'w') as f:
                json.dump(clips_to_save, f)

            # Update the favorites list widget
            self.update_favorites_list()
            self.feedback_label.setText("Clip positions saved to file.")

    def load_clips_from_file(self):
        if self.video_path:
            self.favorites = []
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_clips = json.load(f)

                if isinstance(loaded_clips, list) and all(isinstance(clip, dict) for clip in loaded_clips):
                    self.favorites = loaded_clips

                self.feedback_label.setText("Clip positions loaded from file.")
            else:
                self.feedback_label.setText("No saved clip positions found.")
            
            # Sort clips after loading
            self.sort_clips()

            # Update the favorites list widget
            self.update_favorites_list()

    def play_favorite(self):
        selected_row = self.favorites_list.currentRow()
        if selected_row >= 0:
            clip_data = self.favorites[selected_row]
            if self.video_path:
                # Save the current position of the main video only if not already saved
                if not self.position_saved:
                    self.main_video_position = self.media_player.get_time()
                    self.position_saved = True

                # Ensure media is loaded
                if not self.media_player.get_media():
                    media = self.instance.media_new(self.video_path)
                    self.media_player.set_media(media)

                # Set the media to the main video and play from the start to end positions
                self.current_clip_start, self.current_clip_end = clip_data['positions']  # Set the current clip start and end
                self.media_player.set_time(int(self.current_clip_start * 1000))  # Convert to milliseconds
                self.media_player.play()
                self.is_playing = True
                self.return_button.setEnabled(True)
                self.feedback_label.setText(f"Playing clip {selected_row + 1}")
            else:
                self.feedback_label.setText("Main video file not found!")
        else:
            self.feedback_label.setText("No clip selected.")

    def check_loop_position(self):
        current_position = self.media_player.get_time()
        if self.current_clip_end is not None:  # Ensure current_clip_end is set
            if current_position >= int(self.current_clip_end * 1000):  # Convert to milliseconds
                if self.loop_enabled:
                    # Apply an additional 500ms buffer when looping
                    adjusted_start = max(0, self.current_clip_start * 1000 - 1000)
                    self.media_player.set_time(int(adjusted_start))
                    self.media_player.play()
                else:
                    self.media_player.pause()
                    self.is_playing = False  # Update the is_playing flag
                    self.feedback_label.setText("Clip playback finished.")
                    self.current_clip_end = None

    def return_to_main_video(self):
        if self.video_path:
            # Ensure media is loaded
            if not self.media_player.get_media():
                media = self.instance.media_new(self.video_path)
                self.media_player.set_media(media)
            self.media_player.set_time(self.main_video_position)  # Resume from last position
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
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
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
        elif event.key() == Qt.Key_N or event.key() == Qt.Key_Down:
            self.next_clip()
        elif event.key() == Qt.Key_P or event.key() == Qt.Key_Up:
            self.previous_clip()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.play_favorite()

    def slider_clicked(self):
        # Reset the current clip end when the slider is clicked
        self.current_clip_end = None

        # Calculate the position based on the click
        value = self.position_slider.value()
        self.set_position(value)

        # If the video is paused, start playing from the new position
        if not self.is_playing:
            self.play_video()

    def update_favorites_list(self):
        """Update the favorites list widget with the current clips."""
        self.favorites_list.clear()
        for i, clip_data in enumerate(self.favorites):
            if isinstance(clip_data, dict) and 'positions' in clip_data:
                start, end = clip_data['positions']
                self.favorites_list.addItem(f"Clip {i + 1}: {start:.2f}s - {end:.2f}s")

    def toggle_video_audio_mode(self):
        """Toggle between video and audio mode."""
        self.audio_mode = not self.audio_mode
        if self.audio_mode:
            self.video_widget.hide()
            self.toggle_mode_button.setText("Switch to Video Mode")
            self.feedback_label.setText("Audio mode enabled.")
        else:
            self.video_widget.show()
            self.toggle_mode_button.setText("Switch to Audio Mode")
            self.feedback_label.setText("Video mode enabled.")

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self.parent().play_favorite)  # Connect double-click to play_favorite

    def keyPressEvent(self, event):
        # Propagate the event to the parent widget
        if event.key() in (Qt.Key_Space, Qt.Key_S, Qt.Key_E):
            self.parent().keyPressEvent(event)
        elif event.key() == Qt.Key_L:
            self.parent().toggle_loop()
        elif event.key() == Qt.Key_N or event.key() == Qt.Key_Down:
            self.parent().next_clip()
        elif event.key() == Qt.Key_P or event.key() == Qt.Key_Up:
            self.parent().previous_clip()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.parent().delete_clip()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.parent().play_favorite()
        else:
            super().keyPressEvent(event)

class ClickableVideoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)

    def mousePressEvent(self, event):
        # Call the toggle play/pause method in the parent
        self.parent().toggle_play_pause()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent().media_player:
            self.parent().media_player.video_set_scale(0)

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Calculate the new position based on the click
            new_value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), event.x(), self.width())
            self.setValue(new_value)
            self.parent().set_position(new_value)
        super().mousePressEvent(event)

if __name__ == "__main__":
    debug_mode = True  # Set this to True to enable debug mode
    home_path = os.path.expanduser("~")
    debug_video_path = os.path.join(home_path, r"Videos\S04.1080p.中英字幕\Fresh.Off.the.Boat.S04E01.1080p.AMZN.WEB.mp4")

    # Define the config path
    config_dir = os.path.join(home_path, r"OneDrive\Projects\config")

    app = QApplication(sys.argv)
    window = VideoPlayerApp(debug=debug_mode, debug_video_path=debug_video_path, config_dir=config_dir)
    window.show()
    sys.exit(app.exec_())
