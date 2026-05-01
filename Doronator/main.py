
import sys
import math
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QGraphicsView, QGraphicsScene, QGraphicsPolygonItem,
                             QGraphicsTextItem, QTextEdit)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPolygonF, QBrush, QPen, QColor, QFont, QPainter

class ClickableText(QGraphicsTextItem):
    """A custom text item that supports clicking and hover colors."""
    def __init__(self, text, default_color, hover_color, callback, parent=None):
        super().__init__(text, parent)
        self.callback = callback
        self.default_color = QColor(default_color)
        self.hover_color = QColor(hover_color)
        
        self.setDefaultTextColor(self.default_color)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setDefaultTextColor(self.hover_color)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setDefaultTextColor(self.default_color)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callback()
            event.accept()
        else:
            super().mousePressEvent(event)

class HexItem(QGraphicsPolygonItem):
    """The main Hexagon item that holds the text and handles sound."""
    def __init__(self, size, hex_id, app_ref):
        super().__init__()
        self.hex_id_num = hex_id
        self.app = app_ref
        self.midi_note = 60 + hex_id

        # 1. Draw the pointy-topped Hexagon
        points = []
        for i in range(6):
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            px = size * math.cos(angle_rad)
            py = size * math.sin(angle_rad)
            points.append(QPointF(px, py))
        self.setPolygon(QPolygonF(points))

        # Styling the Hexagon
        self.setBrush(QBrush(QColor("#3498db")))
        self.setPen(QPen(QColor("#2c3e50"), 3))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 2. Add Text Elements (attached as children to the hexagon)
        self.idx_text = QGraphicsTextItem(f"Idx {hex_id}", self)
        self.idx_text.setDefaultTextColor(QColor("white"))
        self.idx_text.setFont(QFont("Arial", 8))

        self.note_text = ClickableText(self.get_note_name(), "#2ecc71", "#27ae60", self.play_sound, self)
        self.note_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.up_btn = ClickableText("▲", "#bdc3c7", "#ffffff", self.increment_note, self)
        self.up_btn.setFont(QFont("Arial", 10))

        self.down_btn = ClickableText("▼", "#bdc3c7", "#ffffff", self.decrement_note, self)
        self.down_btn.setFont(QFont("Arial", 10))

        self.position_texts()

    def position_texts(self):
        """Centers the text elements inside the hexagon mathematically."""
        def center(item, target_x, target_y):
            rect = item.boundingRect()
            item.setPos(target_x - rect.width() / 2, target_y - rect.height() / 2)

        center(self.idx_text, 0, -12)
        center(self.note_text, 0, 10)
        center(self.down_btn, -22, 10)
        center(self.up_btn, 22, 10)

    def get_note_name(self):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (self.midi_note // 12) - 1
        note = notes[self.midi_note % 12]
        return f"{note}{octave}"

    def increment_note(self):
        self.midi_note += 1
        self.note_text.setPlainText(self.get_note_name())
        self.position_texts() # Re-center in case text width changed
        self.app.update_cpp_output()

    def decrement_note(self):
        self.midi_note -= 1
        self.note_text.setPlainText(self.get_note_name())
        self.position_texts()
        self.app.update_cpp_output()

    def play_sound(self):
        frequency = 440 * math.pow(2, (self.midi_note - 69) / int(self.app.edo))
        t = np.linspace(0, 0.5, int(44100 * 0.5), endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        sd.play(audio, samplerate=44100)

    def mousePressEvent(self, event):
        """Play sound when clicking the blue area of the hexagon."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.play_sound()
            event.accept()
        else:
            super().mousePressEvent(event)


class HexApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Hex Layout Tool")
        self.resize(750, 600)
        self.setStyleSheet("background-color: #1e272e; color: white;")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # --- Top Controls ---
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row_label = QLabel("Row Layout:")
        row_label.setFont(QFont("Arial", 12))
        control_layout.addWidget(row_label)

        self.row_entry = QLineEdit("5, 4, 5")
        self.row_entry.setFont(QFont("Arial", 12))
        self.row_entry.setStyleSheet("background-color: #2d3436; color: #00d2d3; border: 1px solid #636e72; padding: 6px; border-radius: 4px;")
        self.row_entry.setFixedWidth(150)
        control_layout.addWidget(self.row_entry)
        
        edo_label = QLabel("EDO:")
        edo_label.setFont(QFont("Arial", 12))
        control_layout.addWidget(edo_label)

        self.edo_entry = QLineEdit("12")
        self.edo_entry.setFont(QFont("Arial", 12))
        self.edo_entry.setStyleSheet("background-color: #2d3436; color: #00d2d3; border: 1px solid #636e72; padding: 6px; border-radius: 4px;")
        self.edo_entry.setFixedWidth(150)
        control_layout.addWidget(self.edo_entry)

        gen_btn = QPushButton("Initialise Grid")
        gen_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        gen_btn.setStyleSheet("""
            QPushButton { background-color: #0984e3; color: white; padding: 6px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #74b9ff; }
            QPushButton:pressed { background-color: #0097e6; }
        """)
        gen_btn.clicked.connect(self.generate_grid)
        control_layout.addWidget(gen_btn)
        
        layout.addLayout(control_layout)

        # --- Canvas / Scene ---
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing) # Makes the lines ultra-smooth
        self.view.setStyleSheet("background-color: #1e272e; border: none;")
        layout.addWidget(self.view)

        # --- C++ Output Area ---
        self.cpp_output = QTextEdit()
        self.cpp_output.setReadOnly(True)
        self.cpp_output.setFont(QFont("Courier", 11))
        self.cpp_output.setStyleSheet("background-color: #2d3436; color: #ff9f43; border: 1px solid #636e72; padding: 10px; border-radius: 6px;")
        self.cpp_output.setFixedHeight(140)
        layout.addWidget(self.cpp_output)

        self.hex_items = []
        self.generate_grid()

    def generate_grid(self):
        self.scene.clear()
        self.hex_items.clear()

        try:
            rows_config = [int(x.strip()) for x in self.row_entry.text().split(",")]
        except ValueError:
            return 

        size = 45
        W = math.sqrt(3) * size
        H = 2 * size
        max_cols = max(rows_config)
        count = 0

        for r, num_in_row in enumerate(rows_config):
            # Hex staggered alignment math
            row_x_offset = (max_cols - num_in_row) * (W / 2)

            for c in range(num_in_row):
                x = row_x_offset + (c * W)
                y = r * (H * 0.75)

                hex_item = HexItem(size, count, self)
                hex_item.setPos(x, y)
                self.scene.addItem(hex_item)
                self.hex_items.append(hex_item)
                count += 1

        # Tell the view to exactly fit and center our drawn items
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.edo = self.edo_entry.text()
        self.update_cpp_output()

    def update_cpp_output(self):
        midi_notes = [str(item.midi_note) for item in self.hex_items]

        cpp_code = f"const int KEYS = {len(midi_notes)};\n\n"
        cpp_code += "const uint8_t ANALOG_NOTES[KEYS] = {\n    "
        cpp_code += ", ".join(midi_notes)
        cpp_code += "\n};"

        self.cpp_output.setPlainText(cpp_code)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HexApp()
    window.show()
    sys.exit(app.exec())
