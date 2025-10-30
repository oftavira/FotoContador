# fix_all_missing_methods.py
"""
Parche completo para agregar TODOS los métodos faltantes de curva S
"""

import os

def fix_all_missing_methods():
    print("🔧 AGREGANDO TODOS LOS MÉTODOS FALTANTES")
    print("=" * 50)
    
    main_window_path = os.path.join(os.path.dirname(__file__), 'main_window.py')
    
    if not os.path.exists(main_window_path):
        print("❌ No se encontró main_window.py")
        return
    
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar donde insertar los métodos (después de stop_scurve_measurement)
    stop_method_pos = content.find('def stop_scurve_measurement(')
    if stop_method_pos != -1:
        # Encontrar el final de stop_scurve_measurement
        method_end = content.find('\n\n', stop_method_pos)
        if method_end == -1:
            method_end = len(content)
        
        # TODOS los métodos faltantes
        missing_methods = '''
    def _safe_progress_update(self, progress, message):
        """Actualización segura de progreso"""
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_scurve_progress(progress, message))

    def _update_scurve_progress(self, progress, message):
        """Actualizar progreso en UI"""
        try:
            progress_percent = int(progress * 100)
            self.scurve_progress.setValue(progress_percent)
            self.scurve_status.setText(message)
            print(f"📊 Progreso: {progress_percent}% - {message}")
        except Exception as e:
            print(f"Error actualizando progreso: {e}")

    def _finalize_scurve(self, thresholds, count_rates):
        """Finalizar medición de curva S"""
        try:
            import numpy as np
            
            # Convertir a arrays numpy si es necesario
            if not hasattr(thresholds, '__array__'):
                thresholds = np.array(thresholds)
            if not hasattr(count_rates, '__array__'):
                count_rates = np.array(count_rates)
            
            print(f"📈 Finalizando: {len(thresholds)} puntos")
            
            # Guardar datos
            self.current_scurve_data = (thresholds, count_rates)
            
            # Actualizar gráfica
            self.scurve_data_line.setData(thresholds, count_rates)
            
            # Calcular threshold óptimo
            optimal_threshold = self.calculate_optimal_threshold(thresholds, count_rates)
            max_count = np.max(count_rates) if len(count_rates) > 0 else 0
            
            # Dibujar línea de threshold óptimo
            if self.optimal_threshold_line:
                self.scurve_plot.removeItem(self.optimal_threshold_line)
            
            import pyqtgraph as pg
            self.optimal_threshold_line = pg.InfiniteLine(
                pos=optimal_threshold, angle=90, pen='r',
                label=f'Óptimo: {optimal_threshold:.4f} V'
            )
            self.scurve_plot.addItem(self.optimal_threshold_line)
            
            # Actualizar labels
            if hasattr(self, 'optimal_threshold_label'):
                self.optimal_threshold_label.setText(f"{optimal_threshold:.4f} V")
            if hasattr(self, 'max_count_label'):  
                self.max_count_label.setText(f"{max_count:.1f} Hz")
            if hasattr(self, 'points_measured_label'):
                self.points_measured_label.setText(f"{len(thresholds)}")
            
            # Habilitar botones
            self.export_scurve_btn.setEnabled(True)
            self.apply_optimal_btn.setEnabled(True)
            
            # Finalizar medición
            self.scurve_measuring = False
            self.start_scurve_btn.setEnabled(True)
            self.stop_scurve_btn.setEnabled(False)
            self.scurve_progress.setVisible(False)
            self.scurve_status.setText("Medición completada correctamente")
            
            print("🎉 Curva S finalizada exitosamente")
            
        except Exception as e:
            print(f"Error finalizando curva S: {e}")
            self._handle_scurve_error(str(e))

    def _handle_scurve_error(self, error_msg):
        """Manejar error de curva S"""
        try:
            self.scurve_measuring = False
            self.start_scurve_btn.setEnabled(True)
            self.stop_scurve_btn.setEnabled(False)
            self.scurve_progress.setVisible(False)
            self.scurve_status.setText(f"Error: {error_msg}")
            print(f"❌ Error en curva S: {error_msg}")
        except Exception as e:
            print(f"Error manejando error de curva S: {e}")

    def _simple_scurve_measurement(self, channel, start_v, end_v, steps, dwell_time):
        """Medición de curva S simplificada - sin problemas de hilos"""
        try:
            print(f"🔧 Iniciando curva S: {steps} puntos")
            
            # Usar QTimer para actualizar UI desde hilo principal
            from PyQt5.QtCore import QTimer
            
            # Actualizar progreso inicial
            QTimer.singleShot(0, lambda: self._update_scurve_progress(0, "Iniciando..."))
            
            # Ejecutar medición
            thresholds, count_rates = self.sr400.measure_s_curve(
                channel, start_v, end_v, steps, dwell_time,
                progress_callback=self._safe_progress_update
            )
            
            print(f"✅ Curva S completada: {len(thresholds)} puntos")
            
            # Actualizar resultados finales
            QTimer.singleShot(0, lambda: self._finalize_scurve(thresholds, count_rates))
            
        except Exception as e:
            print(f"❌ Error en curva S: {e}")
            QTimer.singleShot(0, lambda: self._handle_scurve_error(str(e)))'''
        
        # Insertar después de stop_scurve_measurement
        content = content[:method_end] + missing_methods + content[method_end:]
        
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ TODOS los métodos faltantes agregados:")
        print("   - _safe_progress_update")
        print("   - _update_scurve_progress") 
        print("   - _finalize_scurve")
        print("   - _handle_scurve_error")
        print("   - _simple_scurve_measurement")
    else:
        print("❌ No se pudo encontrar stop_scurve_measurement")

if __name__ == "__main__":
    fix_all_missing_methods()