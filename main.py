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

class VideoPlayerApp(QWidget):
    def __init__(self, debug=False, debug_video_path=None, config_dir=None, base_video_dir=None):
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

        # Initialize dark mode
        self.dark_mode = True  # Start in dark mode
        self.setStyleSheet(self.dark_mode_stylesheet())  # Apply dark mode stylesheet

        # Initialize playback speed
        self.playback_speed = 1.0  # Default speed is 1x

        # Create VLC instance and media player
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Disable VLC's handling of mouse and key inputs
        self.media_player.video_set_mouse_input(False)
        self.media_player.video_set_key_input(False)
        
        # Initialize a dictionary to store video clips
        self.video_clips = {}

        # Define the base video directory
        self.base_video_dir = base_video_dir

        # Initialize mode for displaying videos
        self.single_video_mode = True  # Start in single video mode

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

        # Single/All Videos Button
        self.toggle_video_list_button = QPushButton("Single/All Videos")
        self.toggle_video_list_button.clicked.connect(self.toggle_video_list)
        control_layout.addWidget(self.toggle_video_list_button)

        # Open/Collapse All Button
        self.toggle_expand_button = QPushButton("Expand All")
        self.toggle_expand_button.clicked.connect(self.toggle_expand_collapse_all)
        self.toggle_expand_button.hide()  # Initially hidden
        control_layout.addWidget(self.toggle_expand_button)

        # Feedback label
        self.feedback_label = QLabel("")
        control_layout.addWidget(self.feedback_label)

        # Video Clips Tree
        self.video_clips_tree = CustomTreeWidget()
        self.video_clips_tree.setHeaderLabels(["Video"])
        self.video_clips_tree.itemClicked.connect(self.on_clip_selected)  # Connect item click event
        self.video_clips_tree.hide()  # Initially hide the tree
        control_layout.addWidget(self.video_clips_tree)

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

        # Toggle Dark Mode Button
        self.toggle_dark_mode_button = QPushButton("Dark/Light Mode")
        self.toggle_dark_mode_button.clicked.connect(self.toggle_dark_mode)
        control_layout.addWidget(self.toggle_dark_mode_button)

        # Playback speed controls
        self.speed_label = QLabel("Speed:")
        control_layout.addWidget(self.speed_label)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1x", "1.25x", "1.5x", "2x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.currentIndexChanged.connect(self.change_speed)
        control_layout.addWidget(self.speed_combo)

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
            if event.key() in [Qt.Key_Right, Qt.Key_K, Qt.Key_F]:
                self.skip(3)  # Fine-tuned seeking
                return True  # Event handled
            elif event.key() in [Qt.Key_Left, Qt.Key_J, Qt.Key_D]:
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

            # Set focus to the main window to prevent spacebar from triggering the button again
            self.setFocus()
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
            self.current_clip_start = max(0, self.media_player.get_time() / 1000.0 - 0.5) # seconds
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

                # Save to JSON file
                self.save_clips_to_file()

                # Find the index of the newly added clip
                new_clip_index = self.favorites.index(clip_data)

                if not self.single_video_mode:
                    # Update the video clips tree
                    self.update_video_clips_tree()

                    # Select the newly added clip in the video clips tree
                    self.select_clip_in_tree(new_clip_index)
                else:
                    # Select the newly added clip in the favorites list
                    self.favorites_list.setCurrentRow(new_clip_index)

                self.feedback_label.setText("Clip positions saved!")
            else:
                self.feedback_label.setText("Invalid clip duration.")
        else:
            self.feedback_label.setText("Set the clip start point first.")

    def select_clip_in_tree(self, clip_index):
        """Select the newly added clip in the video clips tree."""
        video_name = os.path.basename(self.video_path)
        for i in range(self.video_clips_tree.topLevelItemCount()):
            video_item = self.video_clips_tree.topLevelItem(i)
            if video_item.text(0) == video_name:
                clip_item = video_item.child(clip_index)
                if clip_item:
                    self.video_clips_tree.setCurrentItem(clip_item)
                break

    def update_video_clips_tree(self):
        """Update the video clips tree with the current clips for the loaded video."""
        video_name = os.path.basename(self.video_path)
        for i in range(self.video_clips_tree.topLevelItemCount()):
            video_item = self.video_clips_tree.topLevelItem(i)
            if video_item.text(0) == video_name:
                # Clear existing clips
                video_item.takeChildren()
                # Add updated clips
                for clip in self.favorites:
                    start, end = clip['positions']
                    clip_item = QTreeWidgetItem(video_item, [f"Clip: {start:.2f}s - {end:.2f}s"])
                    video_item.addChild(clip_item)
                break

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
            # Save the current position of the main video only if not already saved
            if not self.position_saved:
                self.main_video_position = self.media_player.get_time()
                self.position_saved = True

            # Extract start and end positions from the clip data
            start, end = clip_data['positions']

            # Call play_clip with the start and end positions
            self.play_clip(start, end)

            self.return_button.setEnabled(True)
        else:
            self.feedback_label.setText("No clip selected.")

    def check_loop_position(self):
        current_position = self.media_player.get_time()
        if self.current_clip_end is not None:  # Ensure current_clip_end is set
            if current_position >= int(self.current_clip_end * 1000):  # Convert to milliseconds
                if self.loop_enabled:
                    # Apply an additional 200ms buffer when looping
                    adjusted_start = max(0, self.current_clip_start * 1000 - 100)
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
        if self.single_video_mode:
            # Get the selected row from the favorites list
            selected_row = self.favorites_list.currentRow()
            if selected_row >= 0:
                del self.favorites[selected_row]
                self.favorites_list.takeItem(selected_row)
                self.save_clips_to_file()
                self.update_favorites_list()  # Update the favorites list widget
                self.feedback_label.setText(f"Deleted clip {selected_row + 1}")
                if self.favorites_list.count() > 0:
                    self.favorites_list.setCurrentRow(max(selected_row - 1, 0))
            else:
                self.feedback_label.setText("No clip selected to delete.")
        else:
            # Get the selected item from the video clips tree
            current_item = self.video_clips_tree.currentItem()
            if current_item and current_item.parent():  # Ensure it's a clip, not a video
                parent_item = current_item.parent()
                clip_index = parent_item.indexOfChild(current_item)
                del self.favorites[clip_index]
                parent_item.takeChild(clip_index)
                self.save_clips_to_file()
                self.update_video_clips_tree()  # Update the video clips tree
                self.feedback_label.setText(f"Deleted clip {clip_index + 1}")
                if parent_item.childCount() > 0:
                    self.video_clips_tree.setCurrentItem(parent_item.child(max(clip_index - 1, 0)))
            else:
                self.feedback_label.setText("No clip selected to delete.")

    def toggle_loop(self):
        self.loop_enabled = not self.loop_enabled
        status = "enabled" if self.loop_enabled else "disabled"
        self.feedback_label.setText(f"Looping {status}")

    def next_clip(self):
        current_row = self.favorites_list.currentRow()
        next_row = 0
        if current_row < self.favorites_list.count() - 1:
            next_row = current_row + 1
        self.favorites_list.setCurrentRow(next_row)
        self.play_favorite()
 
    def previous_clip(self):
        current_row = self.favorites_list.currentRow()
        prev_row = self.favorites_list.count() - 1
        if current_row > 0:
            prev_row = current_row - 1
        self.favorites_list.setCurrentRow(prev_row)
        self.play_favorite()

    def keyPressEvent(self, event):
        key = event.key()
        
        if key in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_clip()
        elif key == Qt.Key_Right:
            self.skip(3)  # Fine-tuned seeking
        elif key == Qt.Key_Left:
            self.skip(-3)  # Fine-tuned seeking
        elif key == Qt.Key_Space:
            if self.is_playing:
                self.pause_video()
            else:
                self.play_video()
        elif key == Qt.Key_S:
            self.start_clip()
        elif key == Qt.Key_E:
            self.save_clip()
        elif key == Qt.Key_L:
            self.toggle_loop()
        elif key in (Qt.Key_N, Qt.Key_Down):
            if self.single_video_mode:
                self.next_clip()
            else:
                self.navigate_tree(1)  # Move down in the tree
        elif key in (Qt.Key_P, Qt.Key_Up):
            if self.single_video_mode:
                self.previous_clip()
            else:
                self.navigate_tree(-1)  # Move up in the tree
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            if self.single_video_mode:
                self.play_favorite()
            else:
                current_item = self.video_clips_tree.currentItem()
                if current_item and not current_item.parent():  # Check if it's a top-level item (video)
                    if current_item.isExpanded():
                        self.video_clips_tree.collapseItem(current_item)
                    else:
                        self.video_clips_tree.expandItem(current_item)
                else:
                    self.play_selected_clip()  # Play the selected clip if it's not a video
        elif key == Qt.Key_A:
            self.toggle_video_audio_mode()  # Toggle video/audio mode with 'A' key
        elif key == Qt.Key_Q:
            self.toggle_half_speed()  # Toggle half speed with 'Q' key

    def navigate_tree(self, direction):
        """Navigate the video clips tree."""
        current_item = self.video_clips_tree.currentItem()
        if current_item:
            if direction > 0:  # Move down
                next_item = self.video_clips_tree.itemBelow(current_item)
            else:  # Move up
                next_item = self.video_clips_tree.itemAbove(current_item)

            if next_item:
                self.video_clips_tree.setCurrentItem(next_item)
                self.play_selected_clip()  # Play the clip after navigating

    def play_selected_clip(self):
        """Play the currently selected clip in the tree."""
        current_item = self.video_clips_tree.currentItem()
        if current_item and current_item.parent():  # Ensure it's a clip, not a video
            self.on_clip_selected(current_item, 0)

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

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(self.dark_mode_stylesheet())
            self.toggle_dark_mode_button.setText("Disable Dark Mode")
            self.feedback_label.setText("Dark mode enabled.")
        else:
            self.setStyleSheet(self.light_mode_stylesheet())  # Apply light mode stylesheet
            self.toggle_dark_mode_button.setText("Enable Dark Mode")
            self.feedback_label.setText("Dark mode disabled.")

    def light_mode_stylesheet(self):
        """Return the stylesheet for light mode."""
        return """
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
        }
        QPushButton {
            font-size: 20px;  /* Adjusted font size */
            background-color: #F0F0F0;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        QPushButton:hover {
            background-color: #E0E0E0;
        }
        QSlider::groove:horizontal {
            border: 1px solid #CCCCCC;
            height: 8px;
            background: #E0E0E0;
        }
        QSlider::handle:horizontal {
            background: #CCCCCC;
            border: 1px solid #CCCCCC;
            width: 18px;
            margin: -2px 0;
            border-radius: 3px;
        }
        QListWidget {
            background-color: #FFFFFF;
            color: #000000;
        }
        QLabel {
            color: #000000;
        }
        """

    def dark_mode_stylesheet(self):
        """Return the stylesheet for dark mode."""
        return """
        QWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QPushButton {
            background-color: #4A4A4A;
            color: #FFFFFF;
            border: 1px solid #5A5A5A;
            font-size: 20px;  /* Adjusted font size */
        }
        QPushButton:hover {
            background-color: #5A5A5A;
        }
        QSlider::groove:horizontal {
            border: 1px solid #5A5A5A;
            height: 8px;
            background: #3A3A3A;
        }
        QSlider::handle:horizontal {
            background: #5A5A5A;
            border: 1px solid #5A5A5A;
            width: 18px;
            margin: -2px 0;
            border-radius: 3px;
        }
        QListWidget {
            background-color: #3A3A3A;
            color: #FFFFFF;
        }
        QLabel {
            color: #FFFFFF;
        }
        QTreeWidget {
            background-color: #3A3A3A;
            color: #FFFFFF;  /* Set text color for QTreeWidget */
        }
        QTreeWidget::item {
            background-color: #3A3A3A;  /* Set background color for items */
            color: #FFFFFF;  /* Ensure text color for items */
        }
        QTreeWidget::item:selected {
            background-color: #5A5A5A;  /* Set background color for selected items */
        }
        QHeaderView::section {
            background-color: #3A3A3A;  /* Set header background color */
            color: #FFFFFF;  /* Set header text color */
            border: 1px solid #5A5A5A;
        }
        """

    def change_speed(self):
        # Get the selected speed from the combo box
        speed_text = self.speed_combo.currentText()
        self.playback_speed = float(speed_text.replace("x", ""))
        self.media_player.set_rate(self.playback_speed)
        self.feedback_label.setText(f"Playback speed set to {self.playback_speed}x")

    def toggle_half_speed(self):
        """Toggle between half speed and normal speed."""
        if self.playback_speed != 0.5:
            self.playback_speed = 0.5
        else:
            self.playback_speed = 1.0
        self.media_player.set_rate(self.playback_speed)
        self.speed_combo.setCurrentText(f"{self.playback_speed}x")
        self.feedback_label.setText(f"Playback speed set to {self.playback_speed}x")

    def load_config_files(self):
        """Load all config files and list videos with their clips."""
        self.video_clips_tree.clear()  # Clear existing items
        self.video_clips = {}  # Reset the video clips dictionary

        # Get all JSON files in the config directory and sort them by name
        json_files = sorted([f for f in os.listdir(self.config_dir) if f.endswith('.json')])

        # Iterate over sorted JSON files
        for file_name in json_files:
            video_name = file_name[:-5]  # Remove the '.json' extension
            video_path = os.path.join(self.base_video_dir, video_name)

            # Check if the video file exists
            if not os.path.exists(video_path):
                continue  # Skip this config file if the video file does not exist

            file_path = os.path.join(self.config_dir, file_name)

            with open(file_path, 'r') as f:
                clips = json.load(f)

            # Add video and clips to the tree
            video_item = QTreeWidgetItem(self.video_clips_tree, [video_name])
            for clip in clips:
                start, end = clip['positions']
                clip_item = QTreeWidgetItem(video_item, [f"Clip: {start:.2f}s - {end:.2f}s"])
                video_item.addChild(clip_item)

            self.video_clips[video_name] = clips

        self.video_clips_tree.collapseAll()  # Collapse all items initially

    def on_clip_selected(self, item, column):
        """Handle the event when a clip is selected in the tree."""
        parent = item.parent()
        if parent is not None:  # Ensure the item is a clip, not a video
            video_name = parent.text(0)
            clip_text = item.text(0)
            start, end = self.parse_clip_text(clip_text)

            # Construct the full video path
            video_path = os.path.join(self.base_video_dir, video_name)

            # Check if the current video is the same as the new video
            if self.video_path != video_path:
                self.load_video(video_path=video_path)

            # Play the clip
            self.play_clip(start, end)

    def parse_clip_text(self, clip_text):
        """Parse the clip text to extract start and end times."""
        # Example clip text: "Clip: 10.00s - 20.00s"
        parts = clip_text.split(": ")[1].split(" - ")
        start = float(parts[0].replace("s", ""))
        end = float(parts[1].replace("s", ""))
        return start, end

    def play_clip(self, start, end):
        """Play the video from start to end time."""
        if self.video_path:
            # Ensure media is loaded
            if not self.media_player.get_media():
                media = self.instance.media_new(self.video_path)
                self.media_player.set_media(media)

            # Set the media to the main video and play from the start to end positions
            self.current_clip_start = start
            self.current_clip_end = end
            self.media_player.set_time(int(start * 1000))  # Convert to milliseconds

            # Reapply the current playback speed
            self.media_player.set_rate(self.playback_speed)

            self.media_player.play()
            self.is_playing = True
            self.feedback_label.setText(f"Playing clip: {start:.2f}s - {end:.2f}s")
        else:
            self.feedback_label.setText("Video file not found!")

    def toggle_video_list(self):
        """Toggle between single video mode and all videos mode."""
        self.single_video_mode = not self.single_video_mode
        if self.single_video_mode:
            self.video_clips_tree.hide()
            self.favorites_list.show()
            self.toggle_video_list_button.setText("Single/All Videos")
            self.feedback_label.setText("Single video mode enabled.")
            self.favorites_list.setFocus()  # Set focus to the favorites list
            self.toggle_expand_button.hide()  # Hide the expand/collapse button
        else:
            self.favorites_list.hide()
            self.video_clips_tree.show()
            self.load_config_files()  # Load the config files when switching to all videos mode
            self.video_clips_tree.collapseAll()  # Collapse all items by default
            self.toggle_video_list_button.setText("Single/All Videos")
            self.feedback_label.setText("All videos mode enabled.")
            self.video_clips_tree.setFocus()  # Set focus to the video clips tree
            self.toggle_expand_button.show()  # Show the expand/collapse button

    def toggle_expand_collapse_all(self):
        """Toggle between expanding and collapsing all items in the video clips tree."""
        if self.toggle_expand_button.text() == "Expand All":
            self.video_clips_tree.expandAll()
            self.toggle_expand_button.setText("Collapse All")
        else:
            self.video_clips_tree.collapseAll()
            self.toggle_expand_button.setText("Expand All")

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self.parent().play_favorite)  # Connect double-click to play_favorite

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_L:
            self.parent().toggle_loop()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.parent().delete_clip()
        else:
            self.parent().keyPressEvent(event)

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

class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)

if __name__ == "__main__":
    debug_mode = True  # Set this to True to enable debug mode
    home_path = os.path.expanduser("~")

    # Define the video and config path
    hardcoded_video_path = r"Videos/S04.1080p.中英字幕/Fresh.Off.the.Boat.S04E01.1080p.AMZN.WEB.mp4"
    hardcoded_base_video_dir = r"Videos/S04.1080p.中英字幕"
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
    sys.exit(app.exec_())
