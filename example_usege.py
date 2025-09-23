import numpy as numpy
import matplotlib.pyplot as plt
from sr400 import SR400, DiscriminatorChannel, measure_s_curve, find_optimal_threshold

#Ejemplo de uso de eventos
def on_data_received(data):
    print(f"Datos recibidos: {data}")

def on_error(message):
    print(f"Error: {message}")

def on_status_change(status):
    print(f"Estado cambiado: {status}")

def on_couting_change(is_counting):
    print(f"Conteo {'iniciando' if is_counting else 'detenido'}")

def on_progress(progress, message):
    print(f"Progreso: {progress*100:.1f}% - {message}")

#Uso principal
def main():
    #Crear instancia del controlador
    sr400 = SR400('COM3')

    #Configurar event handlers
    sr400.on_data_received = on_data_received
    sr400.on_error = on_error
    sr400.on_status_change = on_status_change
    sr400.on_counting_change = on_couting_change

    try:
        #Conectar
        if sr400.connect():
            print("Conectado al SR400")

            #Configurar modo remoto
            sr400.set_remote_mode(RemoteMode.REMOTE)

            #Configurar valores por defecto
            sr400.set_default_configuration()

            #Medir curva S con progress callback
            print("Iniciando medición de curva S...")
            thresholds, counts = measure_s_curve(
                sr400,
                channel=DiscriminatorChannel.A,
                start_v=-0.1,
                end_v=0.1,
                step=30,
                dwell_time=0.5,
                progress_callback=on_progress
            )

            #Encontrar threshold óptimo
            optimal = find_optimal_threshold(thresholds, counts)
            print(f"Threshold óptimo encontrado: {optimal:.4f} V")

            #Graficar 
            plt.figure(figsize=(10, 6))
            plt.plot(thresholds, counts, 'bo-')
            plt.axvline(optimal, color='red', linestyle='--', label=f'Threshold Óptimo: {optimal:.4f} V')
            plt.xlabel('Threshold (V)')
            plt.ylabel('Tasa de Conteo (Hz)')
            plt.title('Curva S - SR400')
            plt.legend()
            plt.grid(True)
            plt.show()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        #Desconectar
        sr400.disconnect()
        print("Desconectado del SR400")
    
if __name__ == "__main__":
    main()

