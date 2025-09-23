import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
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
        self.sr400 = SR400('COM1')
        self.init_ui()
        self.setup_connections()
        self.init_scuve_variables()
        self.setup_scuve_connections()
        
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
        self.scurve_teps = QSpinBox()
        self.scurve_teps.setRange(10, 200)
        self.scurve_teps.setValue(50)
        param_layout.addWidget(self.scurve_teps, 3, 1)

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
        self.apply_threshold_btn.setEnabled(False)
        results_layout.addWidget(self.apply_optimal_btn, 3, 0, 1, 2)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        self.tab_widget.addTab(tab, "📊 Curva S")
        
        return tab

    def setup_scuve_connections(self):
        """Configurar conexiones para la pestaña de curva S"""
        self.start_scurve_btn.clicked.connect(self.start_scurve_measurement)
        self.stop_scurve_btn.clicked.connect(self.stop_scurve_measurement)
        self.export_scurve_btn.clicked.connect(self.export_scurve_data)
        self.apply_optimal_btn.clicked.connect(self.apply_optimal_threshold)

    #Variables para control de la medicón de curva S
    def init_scuve_variables(self):
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
        
    def setup_connections(self):
        # Conectar señales de UI
        self.start_count_btn.clicked.connect(self.start_counting)
        self.stop_count_btn.clicked.connect(self.stop_counting)
        self.reset_btn.clicked.connect(self.reset_counting)
        self.apply_threshold_btn.clicked.connect(self.apply_threshold)
        self.threshold_slider.valueChanged.connect(self.update_threshold_display)
        self.setup_scuve_connections()

        # Conectar señales del controlador SR400
        self.sr400.on_data_received = self.on_data_received
        self.sr400.on_error = self.on_error
        self.sr400.on_status_changed = self.on_status_changed
        self.sr400.on_counting_changed = self.on_counting_changed
        
    def connect_device(self):
        """Conectar al dispositivo SR400"""
        print("Intentando conectar al SR400...")
        try:
            success = self.sr400.connect()
            print(f"Conexión exitosa: {success}")
            if success:
                #Configurar valores por defecto primero
                time.sleep(1)
                if self.sr400.set_default_configuration():
                    print("Configuración por defecto aplicada")

                    #Actulizar UI
                    self.conn_led.set_on('green')
                    self.connect_btn.setEnabled(False)
                    self.disconnect_btn.setEnabled(True)
                    self.statusBar().showMessage("Conectado al SR400")

                    #Iniciar actualizaciones en tiempo real
                    self.setup_real_time_updates()
                else:
                    self.show_error("Error en configuración inicial")
                    self.sr400.disconnect()

        except Exception as e:
            error_ms = f"Error al conectar: {str(e)}"
            print(error_ms)
            self.show_error(error_ms)
            
    def disconnect_device(self):
        """Desconectar del dispositivo SR400"""
        try:
            # Detener timers de actualización
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            
            #Desconectar dispositivo
            self.sr400.stop_monitoring()
            self.sr400.disconnect()

            #Actualizar UI
            self.conn_led.set_off()
            self.counting_led.set_off()
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)

            #Resetear displays
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
        """Iniciar conteo"""
        try:
            if self.sr400.start_count():
                self.counting_led.set_on('green')
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.start_count_btn.setEnabled(False)
                self.stop_count_btn.setEnabled(True)
                self.statusBar().showMessage("Conteo iniciado")
        except Exception as e:
            self.show_error(f"Error al iniciar conteo: {str(e)}")
            
    def stop_counting(self):
        """Detener conteo"""
        try:
            if self.sr400.stop_count():
                self.counting_led.set_off()
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.start_count_btn.setEnabled(True)
                self.stop_count_btn.setEnabled(False)
                self.statusBar().showMessage("Conteo detenido")
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
    
    def update_real_time_display(self):
        """Actualizar el displat con tasa de conteo actual"""
        if self.sr400.is_connected and not self.sr400.is_counting:
            try:
                #Leer la tasa de conteo del canal A
                count_rate = self.sr400.get_count_rate('A')
                if count_rate is not None:
                    self.count_display.display(count_rate)
                    self.rate_a_value.setText(f"Canal A: {count_rate:.1f} Hz")
            
            except Exception as e:
                print(f"Error actualizado display: {e}")
    
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

        #Obtener parámetros
        channel = DiscriminatorChannel.A if self.scurve_channel.currentIndex() == "Discriminador A" else DiscriminatorChannel.B
        start_v = self.start_v.value()
        end_v = self.end_v.value()
        steps = self.scurve_teps.value()
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

    def _run_scurve_measurement(self, channel, start_v, end_v, steps, dwell_time):
        """Ejecutar medición de Curva S (en hilo separado)"""
        try:
            thresholds, count_rates = self.sr400.measure_s_curve(
                channel, start_v, end_v, steps, dwell_time
                )
            #Actualizar UI en el hilo principal
            self._update_scurve_results(thresholds, count_rates)
        
        except Exception as e:
            #Manejar erro en hilo principal
            self._handle_scurve_error(str(e))
    
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


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())