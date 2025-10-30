"""
PARCHES CALIENTES para SR400 - Ejecutar antes de main.py
"""

def apply_hotfixes():
    print("🔧 Aplicando parches...")

    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    try:
        from custom_widgets import LEDIndicador

        def set_on_fixed(self, color='green'):
            self.setStyleSheet(f"""
                background-color: {color};
                border-radius: {self.width() // 2}px;  # ✅ CORREGIDO: border-radius
                border: 2px solid darkgray;            # ✅ CORREGIDO: border
            """)

        def set_off_fixed(self):
            self.setStyleSheet(f"""
                background-color: gray;
                border-radius: {self.width() // 2}px;  # ✅ CORREGIDO
                border: 2px solid darkgray;            # ✅ CORREGIDO
            """)
        
        LEDIndicador.set_on = set_on_fixed
        LEDIndicador.set_off = set_off_fixed
        print("✅ LEDIndicador corregido")

    except Exception as e:
        print(f"⚠️  No se pudo corregir LEDIndicador: {e}")
    

    try:
        from main_window import MainWindow

        def changeEvent_fixed(self, event):
            from PyQt5.QtCore import QEvent
            if event.type() == QEvent.WindowStateChange:
                pass
            super(MainWindow, self).changeEvent(event)
        
        MainWindow.changeEvent = changeEvent_fixed
        print("✅ changeEvent corregido")
    
    except Exception as e:
        print(f"⚠️  No se pudo corregir MainWindow: {e}")
    
if __name__ == "__main__":
    apply_hotfixes()