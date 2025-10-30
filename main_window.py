import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QCheckBox, 
                             QHBoxLayout, QGridLayout, QSplitter, QStatusBar, QProgressBar,
                             QMenuBar, QAction, QMessageBox, QFileDialog, QToolBar,
                             QLabel, QSlider, QComboBox, QDoubleSpinBox, QSpinBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from datetime import datetime

from ui.custom_widgets import (LEDIndicador, DigitalDisplay, ControlGroup, 
                              ModernButton, ScientificSpinBox)
from ui.styles import STYLESHEET
try:
    from sr400_controller import SR400, DiscriminatorChannel, GateChannel
    print("SR400 controller importado correctamente")
except ImportError as e:
    print(f"Error importando SR400: {e}")
    class SR400:
        def __init__(self,port):
            self.port = port
            self.is_connected = False
        def connect(self): return False
        def disconnect(self): pass
    class DiscriminatorChannel: A=1; B=2; T=3
    class GateChannel: A=1; B=2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        # ✅ SISTEMA INTELIGENTE DE DETECCIÓN
        self.setup_connection_mode()
    
        self.init_ui()
        self.setup_connections()
        self.init_scurve_variables()
        self.setup_scurve_connections()
    
        # ✅ FORZAR ESTADO INICIAL CORRECTO
        self.force_initial_state()

    def setup_development_mode(self):
        """Configurar modo desarrollo forzado - NO intenta conectar a hardware real"""
        print("🔧 MODO DESARROLLO FORZADO ACTIVADO")

        from sr400_controller import SR400Simulator
        self.sr400 = SR400Simulator()
        self.sr400.on_data_received = self.on_data_received
        self.sr400.on_error = self.on_error
        self.sr400.on_status_changed = self.on_status_changed
        self.sr400.on_counting_changed = self.on_counting_changed

        print("✅ Simulador SR400 inicializado (NO hay conexión real)")

    def changeEvent(self, event):
        """Manejar cambios de estado de la ventana - CORREGIDO"""
        # Llamar al método de la clase padre con el evento
        super(MainWindow, self).changeEvent(event)


    def init_ui(self):
        self.setWindowTitle("Control SR400 - Sistema Raman")
        self.setGeometry(100, 50, 1400, 900)
        self.setStyleSheet(STYLESHEET)
        
        # Crear menú
        self.create_menu()
        
        # Crear barra de herramientas
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Widget de pestañas (izquierda)
        self.tab_widget = QTabWidget()
        self.create_realtime_tab()
        self.create_config_tab()
        self.create_scurve_tab()
        self.create_data_tab()
        
        # Panel de estado (derecha)
        self.status_panel = self.create_status_panel()
        
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(self.status_panel)
        splitter.setSizes([1000, 400])
        
        main_layout.addWidget(splitter)
        
        # Barra de estado
        self.statusBar().showMessage("Sistema listo - Desconectado")
        
        # Timer para actualizaciones
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Actualizar cada segundo
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('Archivo')
        
        connect_action = QAction('Conectar', self)
        connect_action.triggered.connect(self.connect_device)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction('Desconectar', self)
        disconnect_action.triggered.connect(self.disconnect_device)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Salir', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Configuración
        config_menu = menubar.addMenu('Configuración')
        default_config_action = QAction('Configuración por Defecto', self)
        default_config_action.triggered.connect(self.set_default_config)
        config_menu.addAction(default_config_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('Ayuda')
        about_action = QAction('Acerca de', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        self.connect_btn = ModernButton("Conectar", color="#27ae60")
        self.connect_btn.clicked.connect(self.connect_device)
        toolbar.addWidget(self.connect_btn)
        
        self.disconnect_btn = ModernButton("Desconectar", color="#e74c3c")
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        self.disconnect_btn.setEnabled(False)
        toolbar.addWidget(self.disconnect_btn)
        
        toolbar.addSeparator()
        
        self.start_btn = ModernButton("Iniciar", color="#27ae60")
        self.start_btn.clicked.connect(self.start_counting)
        toolbar.addWidget(self.start_btn)
        
        self.stop_btn = ModernButton("Detener", color="#e74c3c")
        self.stop_btn.clicked.connect(self.stop_counting)
        self.stop_btn.setEnabled(False)
        toolbar.addWidget(self.stop_btn)

    def create_realtime_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Panel izquierdo - Control de conteo
        left_panel = ControlGroup("Control en Tiempo Real")
        left_layout = QVBoxLayout()

        self.test_btn = ModernButton("Prueba Lectura", color="#9b59b6")
        self.test_btn.clicked.connect(self.test_readings)
        left_layout.addWidget(self.test_btn)
        
        # Estado y display
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel("Estado:"))
        self.counting_led = LEDIndicador(size=24)
        state_layout.addWidget(self.counting_led)
        state_layout.addStretch()
        
        left_layout.addLayout(state_layout)
        
        left_layout.addWidget(QLabel("Tasa de Conteo (Hz):"))
        self.count_display = DigitalDisplay(8)
        left_layout.addWidget(self.count_display)
        
        # Botones de control
        btn_layout = QGridLayout()
        self.start_count_btn = ModernButton("Iniciar Conteo", color="#27ae60")
        self.stop_count_btn = ModernButton("Detener Conteo", color="#e74c3c")
        self.reset_btn = ModernButton("Resetear", color="#f39c12")
        
        btn_layout.addWidget(self.start_count_btn, 0, 0)
        btn_layout.addWidget(self.stop_count_btn, 0, 1)
        btn_layout.addWidget(self.reset_btn, 1, 0, 1, 2)
        
        left_layout.addLayout(btn_layout)
        left_panel.setLayout(left_layout)
        
        # Panel derecho - Controles rápidos
        right_panel = ControlGroup("Ajustes Rápidos")
        right_layout = QVBoxLayout()
        
        # Control de threshold
        right_layout.addWidget(QLabel("Threshold Discriminador A:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(-300, 300)
        self.threshold_slider.setValue(-100)
        right_layout.addWidget(self.threshold_slider)
        
        self.threshold_value = QLabel("-100.0 mV")
        self.threshold_value.setAlignment(Qt.AlignCenter)
        self.threshold_value.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(self.threshold_value)
        
        self.apply_threshold_btn = ModernButton("Aplicar Threshold")
        right_layout.addWidget(self.apply_threshold_btn)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        self.tab_widget.addTab(tab, "⏱️ Tiempo Real")

    def create_config_tab(self):
        """Pestaña de configuración (simplificada por ahora)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Configuración - En desarrollo"))
        self.tab_widget.addTab(tab, "⚙️ Configuración")

    def create_scurve_tab(self):
        """Pestaña de curva S (simplificada por ahora)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        #----Grupo de parámetros de barrido----
        param_group = ControlGroup("Parámetros de Barrido")
        param_layout = QGridLayout()

        #Configuración de rango
        param_layout.addWidget(QLabel("Canal:"), 0, 0)
        self.scurve_channel = QComboBox()
        self.scurve_channel.addItems(["Discriminador A", "Discriminador B"])
        param_layout.addWidget(self.scurve_channel, 0, 1)

        param_layout.addWidget(QLabel("Voltaje Inicial:"), 1, 0)
        self.start_v = QDoubleSpinBox()
        self.start_v.setRange(-0.3, 0.3)
        self.start_v.setValue(-0.1)
        self.start_v.setDecimals(3)
        self.start_v.setSuffix(" V")
        self.start_v.setSingleStep(0.01)
        param_layout.addWidget(self.start_v, 1, 1)

        param_layout.addWidget(QLabel("Voltaje Final:"), 2, 0)
        self.end_v = QDoubleSpinBox()
        self.end_v.setRange(-0.3, 0.3)
        self.end_v.setValue(0.1)
        self.end_v.setDecimals(3)
        self.end_v.setSuffix(" V")
        self.end_v.setSingleStep(0.01)
        param_layout.addWidget(self.end_v, 2, 1)

        param_layout.addWidget(QLabel("Número de Puntos:"), 3, 0)
        self.scurve_steps = QSpinBox()
        self.scurve_steps.setRange(10, 200)
        self.scurve_steps.setValue(50)
        param_layout.addWidget(self.scurve_steps, 3, 1)

        param_layout.addWidget(QLabel("Tiempo por punto:"), 4, 0)
        self.scurve_dwell = QDoubleSpinBox()
        self.scurve_dwell.setRange(0.1, 10.0)
        self.scurve_dwell.setValue(0.5)
        self.scurve_dwell.setSuffix(" s")
        self.scurve_dwell.setSingleStep(0.1)
        param_layout.addWidget(self.scurve_dwell, 4, 1)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        #---Grupo de control de medicón---
        control_group = ControlGroup("Control de Medición")
        control_layout = QVBoxLayout()

        #Barra de progreso
        self.scurve_progress = QProgressBar()
        self.scurve_progress.setVisible(False)
        control_layout.addWidget(self.scurve_progress)

        #Etiqueta de estado
        self.scurve_status = QLabel("Listo para medir Cruva S")
        self.scurve_status.setStyleSheet("font-weight: bold; padding: 5px;")
        control_layout.addWidget(self.scurve_status)

        #Botones de control
        btn_layout = QHBoxLayout()
        self.start_scurve_btn = ModernButton("Iniciar Medición", color="#27ae60")
        self.stop_scurve_btn = ModernButton("Detener Medición", color="#e74c3c")
        self.stop_scurve_btn.setEnabled(False)
        self.export_scurve_btn = ModernButton("Exportar Datos", color="#2980b9")
        btn_layout.addWidget(self.start_scurve_btn)

        btn_layout.addWidget(self.start_scurve_btn)
        btn_layout.addWidget(self.stop_scurve_btn)
        btn_layout.addWidget(self.export_scurve_btn)
        control_layout.addLayout(btn_layout)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        #---Grupo de gráfica---
        graph_group = ControlGroup("Gráfica Curva S")
        graph_layout = QVBoxLayout()

        #Widget de gráfica
        self.scurve_plot = pg.PlotWidget()
        self.scurve_plot.setLabel('left', 'Tasa de Conteo', units='Hz')
        self.scurve_plot.setLabel('bottom', 'Voltaje de Discriminador', units='V')
        self.scurve_plot.showGrid(x=True, y=True,alpha=0.3)
        self.scurve_plot.addLegend()

        #Curvas de la gráfica
        self.scurve_data_line = self.scurve_plot.plot([], [], pen='b', symbol= 'o', symbolSize=5, name='Datos')
        self.optimal_threshold_line = None

        graph_layout.addWidget(self.scurve_plot)
        graph_group.setLayout(graph_layout)
        layout.addWidget(graph_group)

        #---Grupo de resultados---
        results_group = ControlGroup("Resultados")
        results_layout = QGridLayout()
        results_layout.addWidget(QLabel("Threshold Óptimo:"), 0, 0)
        self.optimal_threshold_line = QLabel("-- V")
        self.optimal_threshold_line.setStyleSheet("font-weight: bold; color: #e74c3c")
        results_layout.addWidget(self.optimal_threshold_line, 0, 1)

        results_layout.addWidget(QLabel("Tasa Máxima:"), 1, 0)
        self.max_count_label = QLabel("-- Hz")
        results_layout.addWidget(self.max_count_label, 1, 1)

        results_layout.addWidget(QLabel("Puntos Medidos:"), 2, 0)
        self.points_measured_label = QLabel("--")
        results_layout.addWidget(self.points_measured_label, 2, 1)

        self.apply_optimal_btn = ModernButton("Aplicar Threshold Óptimo", color="#f39c12")
        self.apply_optimal_btn.setEnabled(False)
        results_layout.addWidget(self.apply_optimal_btn, 3, 0, 1, 2)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.tab_widget.addTab(tab, "📊 Curva S")
        
        return tab

    def setup_scurve_connections(self):
        """Configurar conexiones para la pestaña de curva S"""
        self.start_scurve_btn.clicked.connect(self.start_scurve_measurement)
        self.stop_scurve_btn.clicked.connect(self.stop_scurve_measurement)
        self.export_scurve_btn.clicked.connect(self.export_scurve_data)
        self.apply_optimal_btn.clicked.connect(self.apply_optimal_threshold)

    #Variables para control de la medicón de curva S
    def init_scurve_variables(self):  # ✅ CORREGIDO: init_scuve_variables -> init_scurve_variables
        """Variables para control de la medición de curva S"""
        self.scurve_measuring = False
        self.scurve_thread = None
        self.current_scurve_data = None

    def create_data_tab(self):
        """Pestaña de datos (simplificada por ahora)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Datos - En desarrollo"))
        self.tab_widget.addTab(tab, "💾 Datos")
        
    def create_status_panel(self):
        panel = ControlGroup("Estado del Sistema")
        layout = QVBoxLayout()
        
        # Información de conexión
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Conexión:"))
        self.conn_led = LEDIndicador(size=20)
        conn_layout.addWidget(self.conn_led)
        conn_layout.addStretch()
        layout.addLayout(conn_layout)
        
        # Valores actuales
        layout.addWidget(QLabel("Niveles de Discriminador:"))
        self.disc_a_value = QLabel("A: -- mV")
        self.disc_b_value = QLabel("B: -- mV")
        layout.addWidget(self.disc_a_value)
        layout.addWidget(self.disc_b_value)
        
        layout.addWidget(QLabel("Tasas de Conteo:"))
        self.rate_a_value = QLabel("Canal A: -- Hz")
        self.rate_b_value = QLabel("Canal B: -- Hz")
        layout.addWidget(self.rate_a_value)
        layout.addWidget(self.rate_b_value)
        
        layout.addStretch()
        
        # Información del sistema
        layout.addWidget(QLabel("Modo Actual:"))
        self.mode_value = QLabel("--")
        layout.addWidget(self.mode_value)
        
        layout.addWidget(QLabel("Última Actualización:"))
        self.update_time = QLabel("--")
        layout.addWidget(self.update_time)
        
        panel.setLayout(layout)
        return panel

    def setup_connection_mode(self):
        """Configurar modo de conexión - Detección automática + diálogo"""
        print("🔧 Configurando modo de conexión...")
    
        from detection_system import HardwareDetector
        from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget
    
        # Detectar hardware disponible
        available_ports = HardwareDetector.detect_sr400_ports()
        sr400_ports = [port for port in available_ports if port['likely_sr400']]
        other_ports = [port for port in available_ports if not port['likely_sr400']]
    
        # Si no hay puertos detectados, forzar simulación
        if not available_ports:
            print("❌ No se detectaron puertos seriales. Usando modo simulación.")
            self.setup_simulation_mode()
            return
    
        # Crear diálogo de selección
        dialog = QDialog(self)
        dialog.setWindowTitle("Selección de Modo - Control SR400")
        dialog.setFixedSize(500, 400)
    
        layout = QVBoxLayout()
    
        # Título
        title = QLabel("🔌 Configuración de Conexión SR400")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
    
        # Información de detección
        if sr400_ports:
            info_text = f"✅ Se detectaron {len(sr400_ports)} dispositivo(s) posible(es) SR400"
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: green; margin: 10px;")
            layout.addWidget(info_label)
        
            # Lista de dispositivos SR400 detectados
            sr400_list = QListWidget()
            for port in sr400_ports:
                sr400_list.addItem(f"📟 {port['device']} - {port['description']}")
            layout.addWidget(QLabel("Dispositivos SR400 detectados:"))
            layout.addWidget(sr400_list)
    
        if other_ports:
            other_label = QLabel(f"⚠️  También hay {len(other_ports)} otro(s) puerto(s) serial(es)")
            other_label.setStyleSheet("color: orange; margin: 10px;")
            layout.addWidget(other_label)
    
        # Botones de opción
        buttons_layout = QHBoxLayout()
    
        if sr400_ports:
            real_mode_btn = QPushButton("🚀 Modo Real (Hardware)")
            real_mode_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 10px; }")
            real_mode_btn.clicked.connect(lambda: self.select_real_mode(sr400_ports[0]['device'], dialog))
            buttons_layout.addWidget(real_mode_btn)
    
        simulation_btn = QPushButton("🔧 Modo Simulación")
        simulation_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 10px; }")
        simulation_btn.clicked.connect(lambda: self.select_simulation_mode(dialog))
        buttons_layout.addWidget(simulation_btn)
    
        layout.addLayout(buttons_layout)
    
        # Opción de recordar la elección
        remember_checkbox = QCheckBox("Recordar esta elección (puedes cambiarla después)")
        layout.addWidget(remember_checkbox)
    
        dialog.setLayout(layout)
    
        # Mostrar diálogo
        dialog.exec_()

    def select_real_mode(self, port, dialog):
        """Seleccionar modo real con hardware"""
        print(f"🚀 Seleccionado modo REAL con puerto: {port}")
        from sr400_controller import SR400
    
        # Probar conexión
        from detection_system import HardwareDetector
        success, message = HardwareDetector.test_connection(port)
    
        if success:
            print(f"✅ Conexión exitosa: {message}")
            self.sr400 = SR400(port)
            self.setup_sr400_events()
            dialog.accept()
            QMessageBox.information(self, "Conexión Exitosa", 
                               f"✅ Conectado exitosamente al SR400 en {port}\n\n{message}")
        else:
            print(f"❌ Falló la conexión: {message}")
            retry = QMessageBox.question(self, "Error de Conexión",
                                   f"❌ No se pudo conectar al SR400 en {port}\n\n{message}\n\n¿Quieres usar el modo simulación?",
                                   QMessageBox.Yes | QMessageBox.No)
        
            if retry == QMessageBox.Yes:
                self.select_simulation_mode(dialog)
            else:
                # Mantener el diálogo abierto para reintentar
                pass

    def select_simulation_mode(self, dialog):
        """Seleccionar modo simulación"""
        print("🔧 Seleccionado modo SIMULACIÓN")
        from sr400_controller import SR400Simulator
    
        self.sr400 = SR400Simulator()
        self.setup_sr400_events()
        dialog.accept()
    
        QMessageBox.information(self, "Modo Simulación", 
                           "🔧 Ejecutando en MODO SIMULACIÓN\n\n"
                           "Puedes probar todas las funciones sin hardware real.\n"
                           "Para cambiar al modo real, desconecta y vuelve a conectar.")
    def setup_simulation_mode(self):
        """Configurar modo simulación directamente"""
        print("🔧 Configurando modo simulación...")
        from sr400_controller import SR400Simulator
        self.sr400 = SR400Simulator()
        self.setup_sr400_events()
        print("✅ Simulador SR400 inicializado")

    def setup_sr400_events(self):
        """Configurar eventos del SR400 (común para ambos modos)"""
        self.sr400.on_data_received = self.on_data_received
        self.sr400.on_error = self.on_error
        self.sr400.on_status_changed = self.on_status_changed
        self.sr400.on_counting_changed = self.on_counting_changed

    def force_initial_state(self):
        """Forzar el estado inicial correcto de todos los controles"""
        print("🔧 Forzando estado inicial correcto...")
    
        # Asegurar que el simulador esté en estado correcto
        if hasattr(self.sr400, 'is_connected'):
            self.sr400.is_connected = False
        if hasattr(self.sr400, 'is_counting'):
            self.sr400.is_counting = False
    
        # Aplicar estado desconectado a la UI
        self.update_connection_indicators(False)
    
        print("✅ Estado inicial forzado:")
        print(f"   - Conectado: {getattr(self.sr400, 'is_connected', 'N/A')}")
        print(f"   - Contando: {getattr(self.sr400, 'is_counting', 'N/A')}")

    def setup_connections(self):
        # Conectar señales de UI
        self.start_count_btn.clicked.connect(self.start_counting)
        self.stop_count_btn.clicked.connect(self.stop_counting)
        self.reset_btn.clicked.connect(self.reset_counting)
        self.apply_threshold_btn.clicked.connect(self.apply_threshold)
        self.threshold_slider.valueChanged.connect(self.update_threshold_display)
        self.setup_scurve_connections()

        # Conectar señales del controlador SR400
        self.sr400.on_data_received = self.on_data_received
        self.sr400.on_error = self.on_error
        self.sr400.on_status_changed = self.on_status_changed
        self.sr400.on_counting_changed = self.on_counting_changed

    def check_development_mode(self):
        """Determina si estamos en modo desarrollo"""
        import os
        import sys
    
        # Opción 1: Variable de entorno
        if os.getenv('SR400_DEVELOPMENT'):
            print("🔧 Modo desarrollo activado por variable de entorno")
            return True
    
    # Opción 2: Archivo de configuración
        if os.path.exists('development_mode.txt'):
            print("🔧 Modo desarrollo activado por archivo de configuración")
            return True
        
    # Opción 3: Verificar si estamos ejecutando desde IDE/editor
        if any(ide in sys.argv[0] for ide in ['pydev', 'debugpy', 'spyder']):
            print("🔧 Modo desarrollo detectado (ejecutando desde IDE)")
            return True
        
    # Opción 4: Verificar si hay puertos seriales disponibles
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                print("⚠️  No se encontraron puertos seriales. Activando modo desarrollo.")
                return True
            
        # Verificar si el puerto COM1 específicamente existe
            com1_exists = any('COM1' in port.device for port in ports)
            if not com1_exists:
                print("⚠️  Puerto COM1 no encontrado. Activando modo desarrollo.")
                return True
            
        except ImportError:
            print("⚠️  No se pudo verificar puertos seriales. Activando modo desarrollo.")
            return True
        
        print("🔌 Modo producción: hardware real detectado")
        return False


    def connect_device(self):
        """Conectar al dispositivo SR400 - Versión desarrollo CORREGIDA"""
        print("🔄 Conectando al SIMULADOR SR400...")
    
        try:
            success = self.sr400.connect()
        
            if success:
                # Configurar valores por defecto
                time.sleep(0.5)
                if self.sr400.set_default_configuration():
                    print("✅ Configuración por defecto aplicada (SIMULADOR)")
                
                    # ✅ USAR EL MÉTODO CORREGIDO
                    self.update_connection_indicators(True)
                    self.statusBar().showMessage("✅ Conectado al SIMULADOR SR400")
                
                    # Iniciar actualizaciones en tiempo real
                    self.setup_real_time_updates()
                else:
                    self.show_error("Error en configuración inicial del simulador")
            else:
                self.show_error("No se pudo conectar al simulador")
                
        except Exception as e:
            error_msg = f"Error al conectar al simulador: {str(e)}"
            print(error_msg)
            self.show_error(error_msg)

            
    def disconnect_device(self):
        """Desconectar del dispositivo SR400 - CORREGIDO"""
        try:
            # Detener timers de actualización
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
        
            # Desconectar dispositivo
            self.sr400.stop_monitoring()
            self.sr400.disconnect()

            # ✅ USAR EL MÉTODO CORREGIDO
            self.update_connection_indicators(False)
            self.update_counting_indicators(False)

            # Resetear displays
            self.count_display.display(0)
            self.disc_a_value.setText("A: -- mV")
            self.disc_b_value.setText("B: -- mV")
            self.rate_a_value.setText("Canal A: -- Hz")
            self.rate_b_value.setText("Canal B: -- Hz")

            self.statusBar().showMessage("Desconectado")

        except Exception as e:
            error_msg = f"Error al desconectar: {str(e)}"
            print(error_msg)
            self.show_error(error_msg)

    def start_counting(self):
        """Iniciar conteo - SOLO cuando se presiona el botón"""
        try:
            if not self.sr400.is_connected:
                self.show_error("No conectado al SR400")
                return
            
            if self.sr400.is_counting:
                print("⚠️  El contador ya está iniciado")
                return
            
            success = self.sr400.start_count()
            if success:
                print("✅ Conteo INICIADO manualmente")
                self.update_counting_indicators(True)
                self.statusBar().showMessage("Conteo iniciado")
            
                # ✅ INICIAR actualización automática del display durante el conteo
                self.start_display_updates()
            else:
                self.show_error("Error al iniciar conteo")
            
        except Exception as e:
            self.show_error(f"Error al iniciar conteo: {str(e)}")
            
    def stop_counting(self):
        """Detener conteo - y detener actualizaciones del display"""
        try:
            if not self.sr400.is_counting:
                print("⚠️  El contador ya está detenido")
                return
            
            success = self.sr400.stop_count()
            if success:
                print("✅ Conteo DETENIDO manualmente")
                self.update_counting_indicators(False)
                self.statusBar().showMessage("Conteo detenido")
            
                # ✅ DETENER actualización automática del display
                self.stop_display_updates()
            else:
                self.show_error("Error al detener conteo")
            
        except Exception as e:
            self.show_error(f"Error al detener conteo: {str(e)}")

            
    def reset_counting(self):
        """Resetear conteo"""
        try:
            self.sr400.reset_count()
        except Exception as e:
            self.show_error(f"Error al resetear conteo: {str(e)}")
            
    def apply_threshold(self):
        """Aplicar threshold desde el slider"""
        try:
            threshold_mv = self.threshold_slider.value() / 10.0  # Convertir a mV
            threshold_v = threshold_mv / 1000.0  # Convertir a voltios
            self.sr400.set_discriminator_level(DiscriminatorChannel.A, threshold_v)
        except Exception as e:
            self.show_error(f"Error al aplicar threshold: {str(e)}")
            
    def update_threshold_display(self, value):
        """Actualizar display del threshold"""
        self.threshold_value.setText(f"{value/10:.1f} mV")
            
    def set_default_config(self):
        """Establecer configuración por defecto"""
        try:
            if self.sr400.set_default_configuration():
                QMessageBox.information(self, "Éxito", "Configuración por defecto aplicada")
        except Exception as e:
            self.show_error(f"Error al aplicar configuración: {str(e)}")
            
    def show_about(self):
        """Mostrar diálogo Acerca de"""
        QMessageBox.about(self, "Acerca de", 
                         "Control SR400 v1.0\n\n"
                         "Sistema de control para contador de fotones SR400\n"
                         "Para experimentos de espectroscopía Raman")
    
    def show_error(self, message):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", message)
        
    def on_data_received(self, data):
        """Manejar datos recibidos"""
        print(f"Datos: {data}")
        
    def on_error(self, message):
        """Manejar errores"""
        self.show_error(message)
        
    def on_status_changed(self, status):
        """Manejar cambios de estado"""
        # Actualizar UI con el estado del equipo
        if hasattr(status, 'discriminator_levels'):
            if status.discriminator_levels['A'] is not None:
                self.disc_a_value.setText(f"A: {status.discriminator_levels['A']*1000:.1f} mV")
            if status.discriminator_levels['B'] is not None:
                self.disc_b_value.setText(f"B: {status.discriminator_levels['B']*1000:.1f} mV")
                
        if hasattr(status, 'count_rates'):
            if status.count_rates['A'] is not None:
                self.rate_a_value.setText(f"Canal A: {status.count_rates['A']:.0f} Hz")
                self.count_display.display(status.count_rates['A'])
            if status.count_rates['B'] is not None:
                self.rate_b_value.setText(f"Canal B: {status.count_rates['B']:.0f} Hz")
        
        self.update_time.setText(datetime.now().strftime("%H:%M:%S"))
        
    def on_counting_changed(self, is_counting):
        """Manejar cambios de estado de conteo"""
        self.counting_led.set_on('green') if is_counting else self.counting_led.set_off()
        self.start_count_btn.setEnabled(not is_counting)
        self.stop_count_btn.setEnabled(is_counting)
        
    def update_status(self):
        """Actualizar estado periódicamente"""
        if self.sr400.is_connected:
            # Puedes agregar actualizaciones adicionales aquí
            pass
    def setup_real_time_updates(self):
        """Configurar actualizaciones en tiempo real"""
        # Timer para actualizar el display cada 500ms
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_real_time_display)
        self.update_timer.start(500)

        #Timer para actualizar el estado cada 1 segundo
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)
    
    def stop_counting(self):
        """Detener conteo - y detener actualizaciones del display"""
        try:
            if not self.sr400.is_counting:
                print("⚠️  El contador ya está detenido")
                return
            
            success = self.sr400.stop_count()
            if success:
                print("✅ Conteo DETENIDO manualmente")
                self.update_counting_indicators(False)
                self.statusBar().showMessage("Conteo detenido")
            
                # ✅ DETENER actualización automática del display
                self.stop_display_updates()
            else:
                self.show_error("Error al detener conteo")
            
        except Exception as e:
            self.show_error(f"Error al detener conteo: {str(e)}")

    def start_display_updates(self):
        """Iniciar actualización automática del display durante el conteo"""
        if hasattr(self, 'display_update_timer'):
            self.display_update_timer.stop()
    
        self.display_update_timer = QTimer()
        self.display_update_timer.timeout.connect(self.update_display_during_counting)
        self.display_update_timer.start(500)  # Actualizar cada 500ms durante el conteo
        print("🔄 Actualización automática del display INICIADA")

    def stop_display_updates(self):
        """Detener actualización automática del display"""
        if hasattr(self, 'display_update_timer'):
            self.display_update_timer.stop()
            print("⏹️ Actualización automática del display DETENIDA")
    
    def update_display_during_counting(self):
        """Actualizar el display SOLO durante el conteo activo"""
        if self.sr400.is_connected and self.sr400.is_counting:
            try:
                # Leer tasas de conteo actuales
                count_rate_a = self.sr400.get_count_rate('A')
                count_rate_b = self.sr400.get_count_rate('B')
            
                # Actualizar displays
                if count_rate_a is not None:
                    self.count_display.display(count_rate_a)
                    self.rate_a_value.setText(f"Canal A: {count_rate_a:.1f} Hz")
            
                if count_rate_b is not None:
                    self.rate_b_value.setText(f"Canal B: {count_rate_b:.1f} Hz")
                
                # Actualizar timestamp
                self.update_time.setText(datetime.now().strftime("%H:%M:%S"))
            
            except Exception as e:
                print(f"Error actualizando display durante conteo: {e}")

    def update_real_time_display(self):
        """Actualizar display cuando NO hay conteo activo"""
        if self.sr400.is_connected and not self.sr400.is_counting:
            try:
                # Solo leer si no estamos contando activamente
                count_rate_a = self.sr400.get_count_rate('A')
                count_rate_b = self.sr400.get_count_rate('B')
            
                if count_rate_a is not None:
                    self.count_display.display(count_rate_a)
                    self.rate_a_value.setText(f"Canal A: {count_rate_a:.1f} Hz")
            
                if count_rate_b is not None:
                    self.rate_b_value.setText(f"Canal B: {count_rate_b:.1f} Hz")
                
            except Exception as e:
                print(f"Error en actualización en tiempo real: {e}")
    
    def update_status_display(self):
        """Actualizar la información de estado del equipo"""
        if self.sr400.is_connected:
            try:
                #Leer niveles de discriminador
                disc_a = self.sr400.get_discriminator_level(DiscriminatorChannel.A)
                disc_b = self.sr400.get_discriminator_level(DiscriminatorChannel.B)

                if disc_a is not None:
                    self.disc_a_value.setText(f"A: {disc_a*1000:.1f} mV")
                if disc_b is not None:
                    self.disc_b_value.setText(f"B: {disc_b*1000:.1f} mV")
                
                #Lerr tasa del canal B también
                count_rate_b = self.sr400.get_count_rate('B')
                if count_rate_b is not None:
                    self.rate_b_value.setText(f"Canal B: {count_rate_b:.1f} Hz")

                #Acutalizar timestamp
                self.update_time.setText(datetime.now().strftime("%H:%M:%S"))
            
            except Exception as e:
                print(f"Error actualizando estado: {e}")
    
    def update_connection_indicators(self, connected):
        """Actualizar indicadores de conexión - CORREGIDO"""
        if connected:
            self.conn_led.set_on('green')
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_count_btn.setEnabled(True)
            self.stop_count_btn.setEnabled(False)
            self.reset_btn.setEnabled(True)
            self.test_btn.setEnabled(True)
        else:
            self.conn_led.set_off()
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.start_count_btn.setEnabled(False)
            self.stop_count_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.test_btn.setEnabled(False)
            self.update_counting_indicators(False)
            

    def update_counting_indicators(self, counting):
        """Actualizar indicadores de conteo - CORREGIDO"""
        if counting:
            self.counting_led.set_on('green')
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.start_count_btn.setEnabled(False)
            self.stop_count_btn.setEnabled(True)
            self.reset_btn.setEnabled(False)
            self.test_btn.setEnabled(False)
        else:
            self.counting_led.set_off()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.start_count_btn.setEnabled(True)
            self.stop_count_btn.setEnabled(False)
            self.reset_btn.setEnabled(True)
            self.test_btn.setEnabled(True)


    def test_readings(self):
        """Función de prueba lecturas"""
        if not self.sr400.is_connected:
            self.show_error("No conectado")
            return
        try:
            print("=== PRUEBA DE LECTURAS ===")

            #Leer tasa de conteo
            rate_a = self.sr400.get_count_rate('A')
            rate_b = self.sr400.get_count_rate('B')
            print(f"Tasa A: {rate_a} Hz, Tasa B: {rate_b} Hz")

            #Leer niveles
            disc_a = self.sr400.get_discriminator_level(DiscriminatorChannel.A)
            disc_b = self.sr400.get_discriminator_level(DiscriminatorChannel.B)
            print(f"Disc A: {disc_a} V, Disc B: {disc_b} V")

            #Actualizar displays
            if rate_a is not None:
                self.count_display.display(rate_a)
                self.rate_a_value.setText(f"Canal A: {rate_a:.1f} Hz")
            
            if rate_b is not None:
                self.count_display.display(rate_b)
                self.rate_b_value.setText(f"Canal B: {rate_b:.1f} Hz")

            if disc_a is not None:
                self.disc_a_value.setText(f"A: {disc_a*1000:.1f} mV")
            
            if disc_b is not None:
                self.disc_b_value.setText(f"B: {disc_b*1000:.1f} mV")
            
        except Exception as e:
            self.show_error(f"Error en prueba: {str(e)}")

    def start_scurve_measurement(self):
        """Iniciar medición de Curva S en un hilo separado"""
        if not self.sr400.is_connected:
            self.show_error("No conectado al SR400")
            return
        if self.scurve_measuring:
            return
    def stop_scurve_measurement(self):
        """Detener medición de Curva S"""
        print("⏹️ Deteniendo medición de curva S...")
        self.scurve_measuring = False
        self.scurve_status.setText("Medición detenida por el usuario")
        self.start_scurve_btn.setEnabled(True)
        self.stop_scurve_btn.setEnabled(False)
        self.scurve_progress.setVisible(False)
        
        # También podríamos agregar una bandera de cancelación al simulador
        if hasattr(self.sr400, '_scurve_cancel'):
            self.sr400._scurve_cancel = True
    def export_scurve_data(self):
        """Exportar datos de Curva S a archivo CSV"""
        if not hasattr(self, 'current_scurve_data') or not self.current_scurve_data:
            self.show_error("No hay datos de curva S para exportar")
            return
    def apply_optimal_threshold(self):
        """Aplicar el threshold óptimo calculado"""
        if not hasattr(self, 'current_scurve_data') or not self.current_scurve_data:
            self.show_error("No hay datos de curva S para aplicar threshold óptimo")
            return
            
        try:
            thresholds, count_rates = self.current_scurve_data
            optimal_threshold = self.calculate_optimal_threshold(thresholds, count_rates)
            
            # Determinar canal basado en la selección
            from sr400_controller import DiscriminatorChannel
            channel = DiscriminatorChannel.A if self.scurve_channel.currentIndex() == 0 else DiscriminatorChannel.B
            
            success = self.sr400.set_discriminator_level(channel, optimal_threshold)
            
            if success:
                message = f"Threshold óptimo aplicado: {optimal_threshold:.4f} V"
                self.show_info(message)
                self.statusBar().showMessage(message)
                print(f"✅ {message}")
            else:
                self.show_error("Error al aplicar threshold óptimo")
                
        except Exception as e:
            self.show_error(f"Error al aplicar threshold óptimo: {str(e)}")
    def _simple_scurve_measurement(self, channel, start_v, end_v, steps, dwell_time):
        """Medición de curva S simplificada - sin problemas de hilos"""
        try:
            print(f"🔧 Iniciando curva S: {steps} puntos")
            
            # Usar QTimer para actualizar UI desde hilo principal
            from PyQt5.QtCore import QTimer
            import numpy as np
            
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
            QTimer.singleShot(0, lambda: self._handle_scurve_error(str(e)))
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
            QTimer.singleShot(0, lambda: self._handle_scurve_error(str(e)))

        try:
            from PyQt5.QtWidgets import QFileDialog
            import numpy as np
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Datos Curva S", "", "CSV Files (*.csv)"
            )
            
            if filename:
                if not filename.endswith('.csv'):
                    filename += '.csv'
            
                thresholds, count_rates = self.current_scurve_data
                
                # Asegurarse de que son arrays numpy
                if not hasattr(thresholds, '__array__'):
                    thresholds = np.array(thresholds)
                if not hasattr(count_rates, '__array__'):
                    count_rates = np.array(count_rates)
                
                # Combinar datos
                data = np.column_stack((thresholds, count_rates))
                
                # Guardar con header
                np.savetxt(
                    filename, 
                    data, 
                    delimiter=',', 
                    header='Threshold (V),Count Rate (Hz)', 
                    comments='',
                    fmt='%.6f,%.2f'
                )
                
                self.show_info(f"Datos exportados a {filename}")
                print(f"💾 Datos exportados: {filename}")
        
        except Exception as e:
            self.show_error(f"Error al exportar: {str(e)}")
            print(f"❌ Error exportando: {e}")

        #Obtener parámetros
        channel = DiscriminatorChannel.A if self.scurve_channel.currentIndex() == "Discriminador A" else DiscriminatorChannel.B
        start_v = self.start_v.value()
        end_v = self.end_v.value()
        steps = self.scurve_steps.value()
        dwell_time = self.scurve_dwell.value()

        #Validar parametros
        if start_v >= end_v:
            self.show_error("Voltaje inicial debe ser menor que final")
            return

        #Configurar UI
        self.scurve_measuring = True
        self.start_scurve_btn.setEnabled(False)
        self.stop_scurve_btn.setEnabled(True)
        self.scurve_progress.setVisible(True)
        self.scurve_progress.setRange(0, steps)
        self.scurve_progress.setValue(0)
        self.scurve_status.setText("Iniciando medicion de  Curva S...")

        #Limpiar gráfica anterior
        self.scurve_data_line.setData([], [])
        if self.optimal_threshold_line:
            self.scurve_plot.removeItem(self.optimal_threshold_line)
            self.optimal_threshold_line = None
        
        #Ejecutar en hilo separado para no bloquear UI
        import threading
        self.scurve_thread = threading.Thread(
            target=self._run_scurve_measurement,
            args=(channel, start_v, end_v, steps, dwell_time),
            daemon=True
        )
        self.scurve_thread.start()

    # Agrega estos métodos a main_window.py

    
def _simple_scurve_measurement(self, channel, start_v, end_v, steps, dwell_time):
    """Medición de curva S simplificada - sin problemas de hilos"""
    try:
        print(f"🔧 Iniciando curva S: {steps} puntos")
        
        # Usar QTimer para actualizar UI desde hilo principal
        from PyQt5.QtCore import QTimer
        import numpy as np
        
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
        QTimer.singleShot(0, lambda: self._handle_scurve_error(str(e)))

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
        
        # Actualizar labels (corregir nombres)
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
    
    def _thread_safe_progress_callback(self, progress, message):
        """Callback seguro para hilos - usa invokeMethod"""
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        try:
            QMetaObject.invokeMethod(
                self, 
                "_update_progress_ui", 
                Qt.QueuedConnection,
                Q_ARG(float, progress),
                Q_ARG(str, message)
            )
        except Exception as e:
            print(f"Error en callback: {e}")

    def _invoke_update_progress(self, progress, message):
        """Actualizar progreso de forma segura"""
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self, 
            "_update_progress_ui", 
            Qt.QueuedConnection,
            Q_ARG(float, progress),
            Q_ARG(str, message)
        )

    def _invoke_update_results(self, thresholds, count_rates):
        """Actualizar resultados de forma segura"""
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        import numpy as np
    
        # Convertir a listas para serialización (Q_ARG no maneja numpy arrays bien)
        thresholds_list = thresholds.tolist() if hasattr(thresholds, 'tolist') else list(thresholds)
        count_rates_list = count_rates.tolist() if hasattr(count_rates, 'tolist') else list(count_rates)
    
        QMetaObject.invokeMethod(
            self, 
            "_update_scurve_ui", 
            Qt.QueuedConnection,
            Q_ARG(list, thresholds_list),
            Q_ARG(list, count_rates_list)
        )

    def _invuke_handle_error(self, error_msg):
        """Manejar error de forma segura"""
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(
            self, 
            "_show_scurve_error_ui", 
            Qt.QueuedConnection,
            Q_ARG(str, error_msg)
        )
        
    def _update_scurve_progress(self, progress, message):
        """Actualizar progreso desde el hilo de medición"""
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_progress_ui(progress, message))

    def _update_progress_ui(self, progress, message):
        """Actualizar UI de progreso en el hilo principal"""
        try:
            self.scurve_progress.setValue(int(progress * 100))
            self.scurve_status.setText(message)
            print(f"📊 Progreso: {progress*100:.1f}% - {message}")
        except Exception as e:
            print(f"Error actualizando progreso: {e}")
    
    def _update_scurve_results(self, thresholds, count_rates):
        """Actualizar UI con resultados de Curva S (llamar desde hilo principal)"""
        #Usar QTimer para ejecutar en hilo principal de Qt
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_scurve_ui(thresholds, count_rates))
    
    def _update_scurve_ui(self, thresholds, count_rates):
        """Actualizar UI con los resultados"""
        try:
            #Guardar datos
            self.current_scurve_data = (thresholds, count_rates)

            #Actualizar gráfica
            self.scurve_data_line.setData(thresholds, count_rates)

            #Calcular threshold óptimo
            optimal_threshold = self.calculate_optimal_threshold(thresholds, count_rates)
            max_count = np.max(count_rates) if len(count_rates) > 0 else 0

            #Dibujar linea de threshold óptimo
            if self.optimal_threshold_line:
                self.scurve_plot.removeItem(self.optimal_threshold_line)
            
            self.optimal_threshold_line = pg.InfiniteLine(
                pos=optimal_threshold, angle=90, pen='r',
                label=f'Óptimo: {optimal_threshold:.4f} V'
            )
            self.scurve_plot.addItem(self.optimal_threshold_line)

            #Actualizar labels
            self.optimal_threshold_label.setText(f"{optimal_threshold:.4f} V")
            self.max_count_label.setText(f"{max_count:.1f} Hz")
            self.points_measured_label.setText(f"{len(thresholds)}")

            #Habilitar botones
            self.export_scurve_btn.setEnabled(True)
            self.apply_optimal_btn.setEnabled(True)

            #Finalizar medición
            self.scurve_measuring = False
            self.start_scurve_btn.setEnabled(True)
            self.stop_scurve_btn.setEnabled(False)
            self.scurve_progress.setVisible(False)
            self.scurve_status.setText("Medición completada correctamente")
        
        except Exception as e:
            self._handle_scurve_error(str(e))

    def calculate_optimal_threshold(self, thresholds, count_rates):
        """Calcular threshold óptimo a partir de la curva S"""      
        if len(count_rates) == 0:
            return 0.0

        #Encontrar la meseta (donde la derivada es mínima)
        if len(count_rates)>3:
            derivative = np.gradient(count_rates)
            #Buscar región donde la derivada es cercana a cero
            plateau_indices = np.where(np.abs(derivative) < 0.1)[0]
            if len(plateau_indices) > 0:
                optimal_idx = plateau_indices[len(plateau_indices)//2]
                return thresholds[optimal_idx]

        #Fallback: máximo de la curva
        return thresholds[np.argmax(count_rates)]

    def stop_scurve_measurement(self):
        """Detener medición de Curva S"""
        self.scurve_measuring = False
        self.scurve_status.setText("Medición detenida por el usuario")
        self.start_scurve_btn.setEnabled(True)
        self.stop_scurve_btn.setEnabled(False)
        self.scurve_progress.setVisible(False)
        
    def apply_optimal_threshold(self):
        """Aplicar el threshold óptimo calculado"""
        if self.current_scurve_data:
            thresholds, count_rates = self.current_scurve_data
            optimal_threshold = self.calculate_optimal_threshold(thresholds, count_rates)
            channel = DiscriminatorChannel.A if self.scurve_channel.currentIndex() == "Discriminador A" else DiscriminatorChannel.B
            success = self.sr400.set_discriminator_level(channel, optimal_threshold)
            
            if success:
                self.show_info(f"Threshold óptimo hallado {optimal_threshold:.4f} V")
            else:
                self.show_error("Error al aplicar threshold óptimo")

    def export_scurve_data(self):
        """Exportar datos de Curva S a archivo CSV"""
        if not self.current_scurve_data:
            self.show_error("No hay datos para exportar")
            return

        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Datos Curva S", "", "CSV Files (*.csv)"
            )
            if filename:
                if not filename.endswith('.csv'):
                    filename += '.csv'
            
                thresholds, count_rates = self.current_scurve_data
                data = np.column_stack((thresholds, count_rates))
                np.savetxt(filename, data, delimiter=',', header='Threshold (V),Count Rate (Hz)', comments='')
                self.show_info(f"Datos exportados a {filename}")
    
        except Exception as e:
            self.show_error(f"Error al exportar: {str(e)}")

    def _handle_scurve_error(self, error_msg):
        """Manejar error de Curva S en la UI"""
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._show_scurve_error_ui(error_msg))

    def _show_scurve_error_ui(self, error_msg):
        """Mostrar error de Curva S en la UI"""
        self.scurve_measuring = False
        self.start_scurve_btn.setEnabled(True)
        self.stop_scurve_btn.setEnabled(False)
        self.scurve_progress.setVisible(False)
        self.scurve_status.setText(f"Error: {error_msg}")
        self.show_error(f"Error en Curva S: {error_msg}")

    def show_info(self, message):
        """Mostrar mensaje informativo"""
        QMessageBox.information(self, "Información", message)

    def verify_event_connections(self):
        """Verificar que todos los eventos estén correctamente conectados"""
        if not hasattr(self.sr400, 'on_data_received') or self.sr400.on_data_received != self.on_data_received:
            self.sr400.on_data_received = self.on_data_received
            print("✅ on_data_received conectado")
    
        if not hasattr(self.sr400, 'on_error') or self.sr400.on_error != self.on_error:
            self.sr400.on_error = self.on_error
            print("✅ on_error conectado")
        
        if not hasattr(self.sr400, 'on_status_changed') or self.sr400.on_status_changed != self.on_status_changed:
            self.sr400.on_status_changed = self.on_status_changed
            print("✅ on_status_changed conectado")
        
        if not hasattr(self.sr400, 'on_counting_changed') or self.sr400.on_counting_changed != self.on_counting_changed:
            self.sr400.on_counting_changed = self.on_counting_changed
            print("✅ on_counting_changed conectado")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())