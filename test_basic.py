# verify_complete_scurve.py
"""
Verificación completa de TODOS los métodos de curva S
"""

import os

def verify_complete_scurve():
    print("🔍 VERIFICACIÓN COMPLETA DE CURVA S")
    print("=" * 50)
    
    main_window_path = os.path.join(os.path.dirname(__file__), 'main_window.py')
    
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # TODOS los métodos necesarios para curva S
    all_scurve_methods = [
        # Métodos principales
        'start_scurve_measurement',
        'stop_scurve_measurement',
        
        # Métodos de hilo y progreso
        '_simple_scurve_measurement',
        '_safe_progress_update', 
        '_update_scurve_progress',
        '_finalize_scurve',
        '_handle_scurve_error',
        
        # Métodos de utilidad
        'calculate_optimal_threshold',
        'export_scurve_data',
        'apply_optimal_threshold'
    ]
    
    missing_methods = []
    for method in all_scurve_methods:
        if f'def {method}(' in content:
            print(f"✅ {method}")
        else:
            print(f"❌ {method}")
            missing_methods.append(method)
    
    print("\n" + "=" * 50)
    if not missing_methods:
        print("🎉 ¡TODOS los métodos de curva S están presentes!")
        return True
    else:
        print(f"❌ Faltan {len(missing_methods)} métodos:")
        for method in missing_methods:
            print(f"   - {method}")
        return False

if __name__ == "__main__":
    if verify_complete_scurve():
        print("\n🚀 Probando la curva S ahora...")
        
        # Test rápido funcional
        from main_window import MainWindow
        from PyQt5.QtWidgets import QApplication
        import sys
        import time
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        print("\n🧪 TEST FUNCIONAL RÁPIDO")
        print("-" * 30)
        
        # Conectar
        window.connect_device()
        time.sleep(1)
        
        # Configurar
        window.start_v.setValue(-0.02)
        window.end_v.setValue(0.02)
        window.scurve_steps.setValue(5)
        
        # Iniciar medición
        print("Iniciando medición...")
        window.start_scurve_measurement()
        
        # Esperar
        time.sleep(8)
        
        # Verificar
        if hasattr(window, 'current_scurve_data') and window.current_scurve_data:
            thresholds, count_rates = window.current_scurve_data
            print(f"✅ CURVA S EXITOSA: {len(thresholds)} puntos")
            print("🎉 ¡LA CURVA S FUNCIONA CORRECTAMENTE!")
        else:
            print("❌ La curva S no produjo datos")
        
    else:
        print("\n❌ Corrige los métodos faltantes primero")