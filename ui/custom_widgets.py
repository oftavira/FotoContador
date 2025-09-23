from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QGroupBox,QPushButton, QSlider, QLCDNumber,
                             QDoubleSpinBox, QSpinBox, QComboBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont

class LEDIndicador(QLabel):
    """Indicador LED personalizado."""
    def __init__(self, parent=None, size=20):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.set_off()
    
    def set_on(self, color='green'):
        self.setStyleSheet(f"""
                           background-color: {color};
                           boder-radius: {self.width() // 2}px;
                           boder: 2px solid darkgray;
                           """)

    def set_off(self):
        self.setStyleSheet(f"""
                           background-color: gray;
                           border-radius: {self.width() // 2}px;
                           border: 2px solid darkgray;
                            """)
    
class DigitalDisplay(QLCDNumber):
    """Display digital personalizado."""
    def __init__(self, parent=None, digit_count=8):
        super().__init__(parent)
        self.setDigitCount(digit_count)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setStyleSheet("""
                           QLCDNumber {
                               background-color: black;
                               color: #00ff00;
                               border: 2px solid gray;
                               border-radius: 5px;
                           }
                           """)

class ScientificSpinBox(QDoubleSpinBox):
    """SpinBox para valores científicos"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDecimals(4)
        self.setMinimum(-1000.0)
        self.setMaximum(1000.0)
        self.setSingleStep(0.1)

class ControlGroup(QGroupBox):
    """Grupo de control personalizado."""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
                           QGroupBox {
                                font-weight: bold;
                                border: 2px solid #cccccc;
                                border-radius: 8px;
                                margin-top: 1ex;
                                padding-top: 15px;
                                background-color: #f8f8f8;
                           }
                           GroupBox::title {
                                subcontrol-origin: margin;
                                subcontrol-position: top center;
                                padding: 0 10px;
                                background-color: #e0e0e0;
                                border-radius: 4px;
                           }
                           """)

class ModernButton(QPushButton):
    """Botón moderno personalizado."""
    def __init__(self, text, parent=None, color='#4a86e8'):
        super().__init__(text, parent)
        self.color = color
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
                           QPushButton {{
                               background-color: {self.color};
                               color: white;
                               border: none;
                               border-radius: 6px;
                               padding: 8px 16px;
                               font-weight: bold;
                               min-width: 80px;
                           }}
                           QPushButton:hover {{
                               background-color: {self.darken_color(self.color)};
                           }}
                            QPushButton:pressed {{
                                 background-color: {self.darken_color(self.color, 40)};
                            }}
                            QPushButton:disabled {{
                                    background-color: #cccccc;
                                    color: #666666;
                                }}
                            """)
    
    def darken_color(self, color, percent=20):
        """Oscurecer color para efecto hover"""
        color = QColor(color)
        return color.darker(100 + percent).name()