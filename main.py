from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from franz import TickCircleWidget
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F R A N Z")
        self.setStyleSheet("background-color: #0A0E1A;")

        self.tick_circle = TickCircleWidget(self)
        
        # Label for center text
        self.label = QLabel("F R A N Z", alignment=Qt.AlignCenter)
        self.label.setStyleSheet("color: #8fd3ff; font-size: 28px;")
        self.label.setAttribute(Qt.WA_TranslucentBackground)

        tick_layout = QVBoxLayout(self.tick_circle)
        tick_layout.setContentsMargins(0, 0, 0, 0)
        tick_layout.addStretch()
        tick_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        tick_layout.addStretch()

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.tick_circle, alignment=Qt.AlignHCenter)
        layout.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(720, 720)
    win.show()

    sys.exit(app.exec())