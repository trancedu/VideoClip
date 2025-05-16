from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QLabel, QHBoxLayout, 
    QComboBox, QTreeWidgetItem, QStyle
)
from PyQt6.QtCore import Qt
from widgets import ClickableVideoWidget, ClickableSlider, CustomListWidget, CustomTreeWidget
import sys
import os  # Add import for os module


def create_widgets(self):
    """Create and layout all UI widgets."""
    # Main layout
    main_layout = QHBoxLayout(self)

    # Create video display area
    video_layout = create_video_layout(self)
    main_layout.addLayout(video_layout, 5)  # 5/6 of width

    # Create control panel
    control_layout = create_control_layout(self)
    main_layout.addLayout(control_layout, 1)  # 1/6 of width

    self.setLayout(main_layout)


def create_video_layout(self):
    """Create the video display area layout."""
    video_layout = QVBoxLayout()
    
    # Video widget
    self.video_widget = ClickableVideoWidget(self)
    
    # Set the video output to the video widget
    if sys.platform == "win32":  # for Windows
        self.media_player.set_hwnd(int(self.video_widget.winId()))
    elif sys.platform == "darwin":  # for MacOS
        self.media_player.set_nsobject(int(self.video_widget.winId()))
    elif sys.platform.startswith('linux'):  # for Linux using the X Server
        self.media_player.set_xwindow(int(self.video_widget.winId()))

    video_layout.addWidget(self.video_widget, stretch=1)  # Allow video to expand

    # Progress bar and duration label layout
    progress_layout = QHBoxLayout()

    # Progress bar
    self.position_slider = ClickableSlider(Qt.Orientation.Horizontal)
    self.position_slider.setRange(0, 0)
    self.position_slider.sliderMoved.connect(self.set_position)
    self.position_slider.sliderPressed.connect(self.slider_clicked)
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
    
    return video_layout


def create_control_layout(self):
    """Create the control panel layout."""
    control_layout = QVBoxLayout()

    # Load Video Button
    self.load_button = QPushButton("Load Video")
    self.load_button.clicked.connect(self.load_video)
    control_layout.addWidget(self.load_button)

    # Video controls
    create_video_controls(self, control_layout)

    # Clip controls
    create_clip_controls(self, control_layout)

    # Feedback label
    self.feedback_label = QLabel("")
    control_layout.addWidget(self.feedback_label)

    # Video Clips Tree
    self.video_clips_tree = CustomTreeWidget()
    self.video_clips_tree.setHeaderLabels(["Video"])
    self.video_clips_tree.itemClicked.connect(self.on_clip_selected)
    self.video_clips_tree.hide()  # Initially hide the tree
    control_layout.addWidget(self.video_clips_tree)

    # Favorites
    self.favorites_list = CustomListWidget(self)
    control_layout.addWidget(self.favorites_list)

    self.play_favorite_button = QPushButton("Play Favorite")
    self.play_favorite_button.clicked.connect(self.play_favorite)
    control_layout.addWidget(self.play_favorite_button)

    # Playback controls
    create_playback_controls(self, control_layout)
    
    return control_layout


def create_video_controls(self, layout):
    """Create basic video control buttons."""
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


def create_clip_controls(self, layout):
    """Create clip-related control buttons."""
    self.clip_button = QPushButton("Start Clip")
    self.clip_button.clicked.connect(self.start_clip)
    self.clip_button.setEnabled(False)
    layout.addWidget(self.clip_button)

    self.save_clip_button = QPushButton("Save Clip")
    self.save_clip_button.clicked.connect(self.save_clip)
    self.save_clip_button.setEnabled(False)
    layout.addWidget(self.save_clip_button)

    # Single/All Videos Button
    self.toggle_video_list_button = QPushButton("Single/All Videos")
    self.toggle_video_list_button.clicked.connect(self.toggle_video_list)
    layout.addWidget(self.toggle_video_list_button)

    # Open/Collapse All Button
    self.toggle_expand_button = QPushButton("Expand All")
    self.toggle_expand_button.clicked.connect(self.toggle_expand_collapse_all)
    self.toggle_expand_button.hide()  # Initially hidden
    layout.addWidget(self.toggle_expand_button)

    # Delete Clip Button
    self.delete_clip_button = QPushButton("Delete Clip")
    self.delete_clip_button.clicked.connect(self.delete_clip)
    layout.addWidget(self.delete_clip_button)

    # Return to Main Video Button
    self.return_button = QPushButton("Return to Main Video")
    self.return_button.clicked.connect(self.return_to_main_video)
    self.return_button.setEnabled(False)
    layout.addWidget(self.return_button)


def create_playback_controls(self, layout):
    """Create playback mode and speed controls."""
    # Toggle Video/Audio Mode Button
    self.toggle_mode_button = QPushButton("Audio/Video Mode")
    self.toggle_mode_button.clicked.connect(self.toggle_video_audio_mode)
    layout.addWidget(self.toggle_mode_button)

    # Toggle Dark Mode Button
    self.toggle_dark_mode_button = QPushButton("Dark/Light Mode")
    self.toggle_dark_mode_button.clicked.connect(self.toggle_dark_mode)
    layout.addWidget(self.toggle_dark_mode_button)

    # Playback speed controls
    self.speed_label = QLabel("Speed:")
    layout.addWidget(self.speed_label)

    self.speed_combo = QComboBox()
    self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1x", "1.25x", "1.5x", "2x"])
    self.speed_combo.setCurrentText("1x")
    self.speed_combo.currentIndexChanged.connect(self.change_speed)
    layout.addWidget(self.speed_combo)


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