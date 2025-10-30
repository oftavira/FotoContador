import sys
import os
import logging

# Agregar la ruta del proyecto al path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

# Aplicar parches ANTES de importar los módulos
try:
    # Intentar importar desde la carpeta ui
    from ui.custom_widgets import LEDIndicador
    
    # Parche para LEDIndicador
    def set_on_fixed(self, color='green'):
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {self.width() // 2}px;
            border: 2px solid darkgray;
        """)
        
    def set_off_fixed(self):
        self.setStyleSheet(f"""
            background-color: gray;
            border-radius: {self.width() // 2}px;
            border: 2px solid darkgray;
        """)
    
    LEDIndicador.set_on = set_on_fixed
    LEDIndicador.set_off = set_off_fixed
    print("✅ LEDIndicador corregido")
    
except ImportError as e:
    print(f"⚠️  No se pudo corregir LEDIndicador: {e}")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Configurar la aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("Control SR400")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Laboratorio de Física Avanzada - Fotoluminiciencia Ramman")

    # Crear y mostrar la ventana principal
    from main_window import MainWindow
    window = MainWindow()
    window.show()

    # Ejecutar la aplicación
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Error en la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()