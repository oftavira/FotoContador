import serial
import time
import re
import numpy as np
from typing import Callable, List, Tuple, Optional
import threading
from dataclasses import dataclass
from enum import Enum

#-----Enumeraciones para mejor control ------
class DiscriminatorChannel(Enum):
    A=1
    B=2
    T=3

class GateChannel(Enum):
    A=1
    B=2

class CountMode(Enum):
    A_B=0
    A_MINUS_B=1
    A_PLUS_B=2
    A_FOR_B=3

class InputSource(Enum):
    MHZ_10=0
    INP1=1
    INP2=2
    TRIG=3

class DiscriminatorSlope(Enum):
    RISE=0
    FALL=1

class DiscriminatorMode(Enum):
    FIXED=0
    SCAN=1

class GateMode(Enum):
    CW=0
    FIXED=1
    SCAN=2

class RemoteMode(Enum):
    LOCAL=0
    REMOTE=1
    LOCKED_OUT=2

#-----Data Classes para estado del equipo ------
@dataclass
class SR400Status:
    discriminator_levels: dict
    count_rate: dict
    gate_settings: dict
    scan_positions: int
    is_counting: bool

class SR400:
    def __init__(self, port: str, baudrate: int=9600, timeout: int = 1):
        """
        Inicializa la comunicación con el SR400
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.is_connected = False
        self.is_counting = False

        #Eventos para UI
        self.on_data_received = None
        self.on_error = None
        self.on_status_changed = None
        self.on_counting_changed = None

        #Thread para monitoreo en segundo plano
        self.monitor_thread = None
        self.monitoring = False

    def connect(self) -> bool:
        """
        Establece conexión con el SR400
        """
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            time.sleep(2)
            self.is_connected = True
            self._trigger_event(self.on_status_changed,"Conectado")
            return True
        except Exception as e:
            self._trigger_event(self.on_error, f"Error de conexión: {str(e)}")
            return False
        
    def disconnect(self):
        """
        Cierra la conexión
        """
        self.stop_monitoring()
        if self.ser and self.ser.is_open:
            self.set_remote_mode(RemoteMode.LOCAL)
            self.ser.close()
        self.is_connected = False
        self._trigger_event(self.on_status_changed,"Desconectado")
        
    def send_command(self, command:str, wait_time: float=0.1) -> bool:
        """
        Envía comando al instrumento
        """
        if not self.is_connected:
            self._trigger_event(self.on_error, "No conectado al SR400")
            return False
        try:
            if not command.endswith('\r'):
                command += '\r'
            self.ser.write(command.encode('ascii'))
            time.sleep(wait_time)
            return True
        except Exception as e:
            self._trigger_event(self.on_error, f"Error enviando comando: {str(e)}")
            return False
        
    def query(self, command: str, wait_time: float=0.2) -> Optional[str]:
        """
        Envía comando y espera respuesta
        """
        if self.send_command(command, wait_time):
            try:
                response = self.ser.readline().decode('ascii').strip()
                self._trigger_event(self.on_data_received, response)
                return response
            except Exception as e:
                self._trigger_event(self.on_error, f"Error leyendo respuesta: {str(e)}")
                return None
    #-----Comandos principales ------
    def set_discriminator_level(self, channel: DiscriminatorChannel, voltage: float) -> bool:
        """
        Configura el nivel del discriminador (-0.3V a +0.3v)
        """
        if -0.3 <= voltage <= 0.3:
            return self.send_command(f"DL{channel.value},{voltage:.4f}")
        else:
            self._trigger_event(self.on_error, "Voltaje fuera de rango (-0.3V a +0.3V)")
            return False
            
    def get_discriminator_level(self, channel: DiscriminatorChannel) -> Optional[float]:
        """
        Lee nivel actual del discriminador
        """
        response = self.query(f"DZ{channel.value}?")
        if response:
            try:
                return float(response) if response else None
            except ValueError:
                return None
            
    def set_discriminator_slope(self, channel: DiscriminatorChannel, slope: DiscriminatorSlope) -> bool:
        """
        Configura la pendiente del discriminador
        """
        return self.send_command(f"DS{channel.value},{slope.value}")
        
    def set_discriminator_mode(self, channel: DiscriminatorChannel, mode: DiscriminatorMode) -> bool:
        """
        Configura el modo del discriminador
        """
        return self.send_command(f"DM{channel.value},{mode.value}")

    def set_gate_width(self, channel: GateChannel, width_seconds: float) -> bool:
        """
        Configura el ancho de la puerta 
        """
        return self.send_command(f"GW{channel.value},{width_seconds}")
        
    def set_gate_delay(self, channel: GateChannel, delay_seconds: float) -> bool:
        """
        Establece delay de la puerta
        """
        return self.send_command(f"GD{channel.value},{delay_seconds}")
        
    def set_gate_mode(self, channel: GateChannel, mode: GateMode) -> bool:
        """
        Establce modo de conteo
        """
        return self.send_command(f"CM{mode.value}")
        
    def set_input_source(self, counter:DiscriminatorChannel, source:InputSource)->bool:
        """
        Establece la fuente de entrada
        """
        return self.send_command(f"CI{counter.value},{source.value}")
    
    #-----Medición y control-------
    def get_count_rate(self, counter: str='A') -> Optional[float]:
        """Obtiene tasa de conteo"""
        if not self.is_connected:
            return None

        try:
            counter_code = 'X' + counter.upper()
            response = self.query(counter_code)

            if not response:
                return None
            
            #Limpiar respuesta y convertir a float
            response = response.strip()
            try:
                return float(response)
            except ValueError:
                #Intentar extraer numero de respuestas complejas
                numbers = re.findall(r"[-+]?\d*\.\d+|\d+", response)
                return float(numbers[0]) if numbers else None
        
        except Exception as e:
            print(f"Error leyendo count rate: {str(e)}")
            return None

        
    def start_count(self) -> bool:
        """
        Inicia conteo
        """
        if self.send_command("CS"):
            self.is_counting = True
            self._trigger_event(self.on_counting_changed, True)
            return True
        return False

    def stop_count(self) -> bool:
        """
        Detiene conteo
        """
        if self.send_command("CH"):
            self.is_counting = False
            self._trigger_event(self.on_counting_changed, False)
            return True
        return False

    def reset_count(self) -> bool:
        """
        Resetea el contador
        """
        return self.send_command("CR")
        
    def set_dwell_time(self, time_seconds: float) -> bool:
        """
        Configura el tiempo de dwell
        """
        return self.send_command(f"DT{time_seconds}")
        
    def set_scan_periods(self, periods: int) -> bool:
        """
        Configura el número de periodos de sscan
        """
        if 1 <= periods <= 2000:
            return self.send_command(f"NP{periods}")
        return False
        
    #-----Monitoreo en segundo plano ------
    def start_monitoring(self, interval: float=1.0):
        """
        Inicia monitoreo automático del estado
        """
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop,args=(interval,),deamon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """
        Detiene el monitoreo automático
        """
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
    def _monitor_loop(self, interval: float):
        """
        Loop de monitoreo automático
        """
        while self.monitoring and self.is_connected:
            try:
                status = self.get_status()
                self._trigger_event(self.on_status_changed, status)
            except Exception as e:
                self._trigger_event(self.on_error, f"Error en monitoreo: {str(e)}")
            time.sleep(interval)
            
    def get_status(self) -> Optional[SR400Status]:
        """Obtiene el estado completo del equipo"""
        status = SR400Status(
            discriminator_levels={
                'A': self.get_discriminator_level(DiscriminatorChannel.A),
                'B': self.get_discriminator_level(DiscriminatorChannel.B),
                'T': self.get_discriminator_level(DiscriminatorChannel.T)
            },
            count_rate={
                'A': self.get_count_rate('A'),
                'B': self.get_count_rate('B'),},
            gate_settings={},
            scan_positions=self.get_scan_positions(),
            is_counting=self.is_counting
            )
        return status
    
    def get_scan_positions(self) -> Optional[int]:
        """
        Obtiene poisción actual del scan
        """
        response = self.query("NN")
        try:
            return int(response) if response else None
        except ValueError:
            return None
        
    #-----Configuarción por defecto------
    def set_default_configuration(self) -> bool:
        """
        Configura valores por defecto según manual
        """
        try:
            #Configurar discriminadores
            for channel in [DiscriminatorChannel.A, DiscriminatorChannel.B, DiscriminatorChannel.T]:
                self.set_discriminator_slope(channel, DiscriminatorSlope.FALL)
                self.set_discriminator_mode(channel, DiscriminatorMode.FIXED)
                self.set_discriminator_level(channel, -0.010) # -10mV

            #Configurar puertas
            for channel in [GateChannel.A, GateChannel.B]:
                self.set_gate_mode(channel, GateMode.CW)
                self.set_gate_width(channel, 0.000) 
                self.set_gate_delay(channel, 5e-9) # 5 ns
                
            #configurar contadores
            self.set_count_mode(CountMode.A_B)
            self.set_input_source(DiscriminatorChannel.A, InputSource.INP1)
            self.set_input_source(DiscriminatorChannel.B, InputSource.INP2)
            self.set_input_source(DiscriminatorChannel.T, InputSource.MHZ_10)

            #Tiempos de medición
            self.set_dwell_time(1.0)
            self.set_scan_periods(1)

            return True
        except Exception as e:
            self._trigger_event(self.on_error, f"Error configurando por defecto: {str(e)}")
            return False
            
    def set_remote_mode(self, mode: RemoteMode) -> bool:
        """
        Establece modo de control remoto
        """
        return self.send_command(f"MI{mode.value}")
            
    def reset_instrument(self) -> bool:
        """
        Resetea intrumento a configuración por defecto
        """
        return self.send_command("RC 0")
    
    #-----Event Handling------
    def _trigger_event(self, event_handler: Optional[Callable], data):
        """
        Dispara evento si handler está definido
        """
        if event_handler:
            try:
                event_handler(data)
            except Exception as e:
                print(f"Error en evento: {str(e)}")
        
    #-----Context Manager------
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()

#------Funciones de alto nivel ------
def measure_s_curve(self,
                    channel: DiscriminatorChannel,
                    start_v: float,
                    end_v: float,
                    steps: int,
                    dwell_time: float = 0.5,
                    progress_callback: Optional[Callable] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Realiza una medición de S-Curve variando el nivel del discriminador
    """
    if not self.is_connected:
        raise RuntimeError("Dispositivo no conectado")
    
    thresholds = np.linspace(start_v, end_v, steps)
    count_rates = []
    
    print(f"Iniciando medición de curva S: {start_v}V a {end_v}V, {steps} puntos ")

    #Guardar configuración actual
    original_threshold = self.get_discriminator_level(channel)

    try: 
        for i, threshold_v in enumerate(thresholds):
            #Establecer threshold
            self.set_dicriminator_level(channel, threshold_v)
            time.sleep(0.05)  # Tiempo de espera para estabilización

            #Realizar medición
            self.reset_count()
            self.start_count()
            time.sleep(dwell_time)
            self.stop_count()
            
            #Leer resultado
            count_rate = self.get_count_rate('A')  # Asumiendo canal A
            count_rates.append(count_rate if count_rate is not None else 0.0)
            
            print(f"Punto {i+1}/{steps}: Threshold={threshold_v:.4f}V -> {count_rates[-1]:.1f} Hz")

            #Restaurar threshold original
            self.set_discriminator_level(channel, original_threshold)

            return np.array(thresholds), np.array(count_rates)
    
    except Exception as e:
        #Restaurar threshold original en caso de error
        self.set_discriminator_level(channel, original_threshold)
        raise e

def quick_measure(self, dewel_time: float=0.1)-> float:
    """Medición rápida para actualizaciones en tiempo real"""

    try:
        self.reset_count()
        self.start_count()
        time.sleep
        self.stop_count()
        return self.get_count_rate('A') or 0.0
    except:
        return 0.0

def find_optimal_threshold(thresholds: np.ndarray, count_rates: np.ndarray) -> float:
    """
    Encuentra el nivel de discriminador óptimo a partir de la S-Curve """
    smoothed = np.convolve(count_rates, np.ones(3)/3, mode='valid')
    derivative = np.gradient(smoothed)

    #Encontar meseta (donde la derivada es cercana a cero)
    plateau_mask = np.abs(derivative) < np.std(derivative) * 0.5
    plateau_indices = np.where(plateau_mask)[0]

    if len(plateau_indices) > 0:
        #Ajustar índices por el suavizado
        optimal_idx = plateau_indices[len(plateau_indices)//2] + 1
        return thresholds[optimal_idx]
    else:
        #Fallback: máximo de la curva 
        return thresholds[np.argmax(count_rates)]