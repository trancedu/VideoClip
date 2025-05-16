def format_time(ms):
    """Format milliseconds into minutes:seconds."""
    seconds = int(ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02}"


def parse_clip_text(clip_text):
    """Parse clip text (e.g., 'Clip: 10.00s - 20.00s') to extract start and end times."""
    parts = clip_text.split(": ")[1].split(" - ")
    start = float(parts[0].replace("s", ""))
    end = float(parts[1].replace("s", ""))
    return start, end


def light_mode_stylesheet():
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


def dark_mode_stylesheet():
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