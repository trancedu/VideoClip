import tkinter as tk
from tkinter import filedialog
import threading
from moviepy.editor import VideoFileClip

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Listening Practice")
        
        # Initialize variables
        self.video_path = None
        self.video_clip = None
        self.is_playing = False
        self.favorites = []
        self.current_clip_start = None
        self.current_clip_end = None

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Load Video Button
        self.load_button = tk.Button(self.root, text="Load Video", command=self.load_video)
        self.load_button.pack()

        # Video controls
        self.play_button = tk.Button(self.root, text="Play", command=self.play_video)
        self.play_button.pack()
        self.pause_button = tk.Button(self.root, text="Pause", command=self.pause_video)
        self.pause_button.pack()
        self.forward_button = tk.Button(self.root, text="Forward 5s", command=lambda: self.skip(5))
        self.forward_button.pack()
        self.backward_button = tk.Button(self.root, text="Backward 5s", command=lambda: self.skip(-5))
        self.backward_button.pack()

        # Clip controls
        self.clip_button = tk.Button(self.root, text="Start Clip", command=self.start_clip)
        self.clip_button.pack()
        self.save_clip_button = tk.Button(self.root, text="Save Clip", command=self.save_clip)
        self.save_clip_button.pack()

        # Favorites
        self.favorites_list = tk.Listbox(self.root)
        self.favorites_list.pack()
        self.play_favorite_button = tk.Button(self.root, text="Play Favorite", command=self.play_favorite)
        self.play_favorite_button.pack()

    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)

    def play_video(self):
        if not self.is_playing and self.video_path:
            self.is_playing = True
            threading.Thread(target=self.playback).start()

    def playback(self):
        if self.video_clip:
            self.video_clip.preview()
        self.is_playing = False

    def pause_video(self):
        self.is_playing = False

    def skip(self, seconds):
        if self.video_clip:
            current_time = self.video_clip.reader.pos / self.video_clip.fps
            new_time = current_time + seconds
            if new_time > 0:
                self.video_clip.reader.seek(new_time)

    def start_clip(self):
        if self.video_clip:
            self.current_clip_start = self.video_clip.reader.pos / self.video_clip.fps

    def save_clip(self):
        if self.video_clip and self.current_clip_start is not None:
            self.current_clip_end = self.video_clip.reader.pos / self.video_clip.fps
            clip = self.video_clip.subclip(self.current_clip_start, self.current_clip_end)
            self.favorites.append(clip)
            self.favorites_list.insert(tk.END, f"Clip {len(self.favorites)}")

    def play_favorite(self):
        selected = self.favorites_list.curselection()
        if selected:
            clip = self.favorites[selected[0]]
            clip.preview()

# Create the main window
root = tk.Tk()
app = VideoPlayerApp(root)
root.mainloop()
