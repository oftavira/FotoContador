# detection_system.py
"""
Sistema de detección automática de hardware SR400
"""

import serial.tools.list_ports
import serial
import time

class HardwareDetector:
    @staticmethod
    def detect_sr400_ports():
        """Detectar puertos seriales que podrían ser el SR400"""
        print("🔍 Buscando dispositivos SR400...")
        
        available_ports = []
        try:
            ports = list(serial.tools.list_ports.comports())
            
            for port in ports:
                print(f"   - Encontrado: {port.device} - {port.description}")
                
                # Buscar patrones que coincidan con SR400
                if any(keyword in port.description.upper() for keyword in ['SR400', 'STANFORD', 'SRS', 'SERIAL']):
                    available_ports.append({
                        'device': port.device,
                        'description': port.description,
                        'likely_sr400': True
                    })
                else:
                    available_ports.append({
                        'device': port.device,
                        'description': port.description, 
                        'likely_sr400': False
                    })
                    
        except Exception as e:
            print(f"❌ Error detectando puertos: {e}")
            
        return available_ports
    
    @staticmethod
    def test_connection(port_name):
        """Probar conexión con un puerto específico"""
        print(f"🧪 Probando conexión con {port_name}...")
        
        try:
            # Intentar conectar y enviar comando de prueba
            with serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2
            ) as ser:
                time.sleep(2)  # Tiempo de inicialización
                
                # Enviar comando de identificación si existe, o comando simple
                ser.write(b'ID?\r')
                time.sleep(0.5)
                
                response = ser.readline().decode('ascii', errors='ignore').strip()
                print(f"   - Respuesta: '{response}'")
                
                # Si hay respuesta, probablemente es el SR400
                if response:
                    return True, f"Dispositivo respondió: {response}"
                else:
                    return False, "No hubo respuesta del dispositivo"
                    
        except serial.SerialException as e:
            return False, f"Error de conexión: {e}"
        except Exception as e:
            return False, f"Error inesperado: {e}"