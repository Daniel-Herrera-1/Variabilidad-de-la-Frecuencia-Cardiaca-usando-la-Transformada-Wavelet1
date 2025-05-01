import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, lfilter
import pywt
import time as tm

with open('DANIEL01.txt', 'r') as file:
    data = file.readlines()

# datos a números
senal_ecg = np.array([int(x.strip()) for x in data])

# parámetros
frecuenciamuestreo = 400  # Hz
lowcut = 0.5  # Hz
highcut = 40.0  # Hz
order = 2

time = np.arange(len(senal_ecg)) / frecuenciamuestreo


# Función de filtro

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def aplicar_filtro_butterworth(señal, fs, lowcut=0.5, highcut=40.0, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order)

    if order == 1:
        eq = f"y[n] = ({b[0]:.4f} * x[n] + {b[1]:.4f} * x[n-1] - {a[1]:.4f} * y[n-1])"
        print("\nEcuación en diferencias del filtro Butterworth (orden 1):")
        print(eq)
    else:
        print(f"\nFiltro Butterworth aplicado (orden {order})")
        print(f"Coeficientes b: {b}")
        print(f"Coeficientes a: {a}")

    return lfilter(b, a, señal)


# Convertir la señal cruda a milivoltios antes de filtrar
adc_max = 4095
v_ref = 3.3  # voltios
ecg_mv = (senal_ecg / adc_max) * v_ref * 1000  # señal en milivoltios

# Aplicar el filtro Butterworth
filtered_ecg = aplicar_filtro_butterworth(ecg_mv, frecuenciamuestreo, lowcut, highcut, order)

# oGraficar señal original y filtrada


plt.figure(figsize=(15, 5))
plt.plot(time, ecg_mv, color='gray')
plt.title('ECG ORIGINAL Escala mv')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.grid(True)
plt.show()

plt.figure(figsize=(15, 5))
plt.plot(time, filtered_ecg, color='teal')
plt.title('ECG Filtrado')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.grid(True)
plt.show()

# Detección de picos R 

distance = int( 0.2 * frecuenciamuestreo)  # 0.2 es el tiempo  entre picos(Tiempo) , entre mayor tiempo menos reconocimiento de picos
min_height = 80  # mV Deteccion de picos desde un minimo de 80mV
max_height = 130  # mV Deteccion de picos hasta un maximo de 130 (Asegurar que capte todos los picos)

# Detección de picos R dentro del rango de altura
peaks, properties = find_peaks(filtered_ecg, distance=distance, height=(min_height, max_height))

# Tiempos de ocurrencia
t_peaks = peaks / frecuenciamuestreo

# Visualización
plt.figure(figsize=(15, 5))
plt.plot(time, filtered_ecg, label='ECG Filtrado', color='royalblue')
plt.plot(time[peaks], filtered_ecg[peaks], 'rx', label=f'Picos R detectados ({min_height}-{max_height} mV)')
plt.title('Detección de Picos R con Rango de Amplitud')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.legend()
plt.grid(True)
plt.show()

print(f"Cantidad de picos R detectados: {len(peaks)}")

#  Calcular intervalos R-R 

rr_intervalos = np.diff(peaks) / frecuenciamuestreo  # en segundos

mean_rr = np.mean(rr_intervalos)
std_rr = np.std(rr_intervalos)

print(f"Media de Intervalos R-R: {mean_rr:.4f} s")
print(f"Desviación estándar de R-R: {std_rr:.4f} s")

plt.figure(figsize=(12, 5))
plt.plot(rr_intervalos, marker='o', color='indigo')
plt.title('Intervalos R-R')
plt.xlabel('Tiempo entre cada pico(s)')
plt.ylabel('Intervalo (s)')
plt.grid(True)
plt.show()

tm.sleep(2)


print(f"Cantidad de picos R detectados: {len(peaks)}")


# Análisis HRV con  Wavelet



wavelet_type = 'morl'
scales = np.arange(1, 1000)  # Más escalas , mayor resolución en la frecuencia es decir aumentar los valores (b)
sampling_period = 1  

# (Transformada Wavelet Continua)
coeffs, freqs = pywt.cwt(rr_intervalos, scales=scales, wavelet=wavelet_type, sampling_period=sampling_period)


plt.figure(figsize=(12,5))
plt.imshow(np.abs(coeffs), extent=[0, len(rr_intervalos), freqs[-1], freqs[0]],
           aspect='auto', cmap='jet', interpolation='bicubic')  

plt.colorbar(label='Amplitud de Coeficientes')
plt.title(f'Espectrograma Wavelet HRV (Wavelet: {wavelet_type})', fontsize=14)
plt.xlabel('Tiempo(s)', fontsize=12)
plt.ylabel('Frecuencia (Hz)', fontsize=12)

# Líneas guía para bandas fisiológicas
plt.axhline(0.04, color='white', linestyle='--', linewidth=1, label='Límite Banda LF (0.04 Hz)')
plt.axhline(0.15, color='white', linestyle='--', linewidth=1, label='Límite LF/HF (0.15 Hz)')
plt.axhline(0.4, color='white', linestyle='--', linewidth=1, label='Límite Banda HF (0.4 Hz)')

plt.legend(loc='upper right', fontsize=9)
plt.tight_layout()
plt.show()
