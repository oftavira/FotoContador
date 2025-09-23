import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

#Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    #Configurar la aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("Control SR400")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Laboratorio de Física Avanzada - Fotoluminiciencia Ramman")

    #Crear y mostrar la venta principal
    from main_window import MainWindow
    window = MainWindow()
    window.show()

    #Ejecutar la aplicación
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Error en la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()