from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QBrush


class TickCircleWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.setFixedSize(520, 520)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.timer.start(16)  

    def advance(self):
        self.angle = (self.angle + 0.5) % 360 
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        painter.translate(cx, cy)
        painter.rotate(self.angle)
        radius = min(cx, cy) - 20
        
        for i in range(60):
            painter.save()
            theta = i * (360.0 / 60.0)
            painter.rotate(theta)
            painter, w, h = self._generate_tick_dimensions(painter, i)

            self._draw_rect_at_top(painter, w, h, radius)

    def _generate_tick_dimensions(self, painter, index):
        if index % 5 == 0:
            w, h = 8, 18
            color = QColor("#b5e5ff")
        else:
            w, h = 2, 18
            color = QColor("#3fa8ff")
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        return painter, w, h
    
    def _draw_rect_at_top(self, painter, w, h, radius):
        """Draws a rectangle at the top position after rotation"""
        rect_x = -w/2
        rect_y = -radius
        painter.drawRoundedRect(rect_x, rect_y, w, h, 1, 1)
        painter.restore()