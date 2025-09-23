STYLESHEET = """
/* Estilos principales de la aplicación */
QMainWindow {
    background-color: #f5f5f5;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Barra de menú */
QMenuBar {
    background-color: #2c3e50;
    color: white;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
}

QMenuBar::item:selected {
    background-color: #34495e;
    border-radius: 4px;
}

QMenu {
    background-color: white;
    border: 1px solid #bdc3c7;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

/* Barra de estado */
QStatusBar {
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 4px;
    border-top: 1px solid #bdc3c7;
}

/* Pestañas */
QTabWidget::pane {
    border: 1px solid #bdc3c7;
    background-color: white;
}

QTabBar::tab {
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 8px 16px;
    border: 1px solid #bdc3c7;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    color: #2980b9;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #d6dbdf;
}

/* Barras de progreso */
QProgressBar {
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    text-align: center;
    background-color: #ecf0f1;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 3px;
}

/* Combobox */
QComboBox {
    padding: 4px;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    background-color: white;
    min-width: 80px;
}

QComboBox:hover {
    border-color: #3498db;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #bdc3c7;
}

/* Spinboxes */
QDoubleSpinBox, QSpinBox {
    padding: 4px;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    background-color: white;
}

QDoubleSpinBox:hover, QSpinBox:hover {
    border-color: #3498db;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #bdc3c7;
    height: 8px;
    background: #ecf0f1;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #3498db;
    border: 1px solid #2980b9;
    width: 18px;
    margin: -4px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #2980b9;
}
"""