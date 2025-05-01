# Variabilidad-de-la-Frecuencia-Cardiaca-usando-la-Transformada-Wavelet


## Fundamentos Teoricos

### Nuestro corazón no late siempre a la misma velocidad; entre un latido y el siguiente se producen pequeñas aceleraciones y desaceleraciones. Estas variaciones, conocidas como Variabilidad de la Frecuencia Cardíaca (HRV), nos indican cómo el cuerpo gestiona el estrés, el descanso y las respuestas al entorno.

## Control autonomo

**Sistema simpático (acelerador):** eleva las pulsaciones cuando hacemos ejercicio, nos asustamos o nos estresamos.

**Sistema parasimpático (freno):** reduce las pulsaciones cuando estamos relajados, descansando o durmiendo.

## ¿Qué mide la HRV?

**La HRV cuantifica las diferencias de tiempo entre latidos sucesivos (intervalos R-R).**

**Una HRV alta sugiere un sistema nervioso autónomo flexible y bien adaptado.**

**Una HRV baja puede reflejar fatiga, estrés prolongado o posibles alteraciones de salud.**

## Métodos de análisis

**Dominio del tiempo:** calculamos la media y la desviación estándar de los intervalos R-R para evaluar su consistencia.

**Dominio tiempo-frecuencia:** aplicamos la Transformada Wavelet —un “microscopio” dinámico— para detectar cómo cambian las frecuencias  a lo largo de los 5 minutos de registro.

# Diagrama de flujo

![image](https://github.com/user-attachments/assets/1d4b497f-e38b-464d-bbc8-1f8433ae6417)


# Adquisicion de la señal 


### La señal ECG fue adquirida utilizando un sensor de ECG de superficie conectado a un sistema de adquisición basado en la placa STM32. La grabación se realizó en un sujeto en estado de reposo, sin movimiento, durante un periodo continuo de 5 minutos.

### Características de la adquisición:

- **Frecuencia de muestreo:** 400 Hz

- **Tiempo total de adquisición:** 300 segundos

- **Cantidad total de muestras:** 120,000

- **Nivel de cuantificación:** 12 bits (valores entre 0 y 4095 ADC)

- **Condiciones:** sujeto en reposo, en ambiente controlado, algun juego o actividad de respiracion para aumentar frecuencias por ciertos periodos

  *La señal fue almacenada en un archivo de texto (.txt) y posteriormente procesada con Python. A continuación se muestra la señal cruda sin filtrar, representando los valores directamente adquiridos del sensor:*

```python
  import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
import pywt
import time as tm

# ========= 1. Cargar los datos =========

with open('DANIEL01.txt', 'r') as file:
    data = file.readlines()

# Convertir datos a números
ecg_signal = np.array([int(x.strip()) for x in data])

# ========= 2. Definir parámetros =========

sampling_rate = 400  # Hz
lowcut = 0.5  # Hz
highcut = 40.0  # Hz
order = 4

time = np.arange(len(ecg_signal)) / sampling_rate

adc_max = 4095
v_ref = 3.3  # voltios
ecg_mv = (ecg_signal / adc_max) * v_ref * 1000  # señal en milivoltios

plt.figure(figsize=(15, 5))
plt.plot(time, ecg_mv, color='gray')
plt.title('ECG ORIGINAL Escala mv')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.grid(True)
plt.show()
```

![image](https://github.com/user-attachments/assets/7a1cd509-b354-4069-a14a-12db32e42009)
![image](https://github.com/user-attachments/assets/3c9db63d-d91d-4b42-bd0e-408eaf12558f)

*Posteriormente, se aplicó un filtro digital pasabanda Butterworth de orden 4, diseñado con las siguientes características:*

- Tipo de filtro: IIR Butterworth (respuesta suave, sin ondulaciones en banda pasante)

- Frecuencia de muestreo (fs): 400 Hz

- Frecuencia de corte inferior (lowcut): 0.5 Hz

- Frecuencia de corte superior (highcut): 40 Hz

- Orden del filtro: n ( Puede variar el orden del filtro, ya que aunque esta definido , se puede cambiar por orden 1,2,3 etc, en este caso es 2)
  
```python
sampling_rate = 400  # Hz
lowcut = 0.5         # Hz
highcut = 40.0       # Hz
order = 2
```
- La frecuencia de muestreo (fs).

- El rango de paso del filtro: 0.5–40 Hz.

- El orden del filtro Butterworth (mayor orden = mayor pendiente del corte).

```python
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
```
- Calcula la frecuencia de Nyquist (mitad del fs).

- Convierte las frecuencias de corte de Hz a la escala normalizada (0 a 1) que exige la función butter() de SciPy.

- Llama a butter() para diseñar el filtro pasabanda Butterworth, y devuelve los coeficientes del filtro:

- b: numerador

- a: denominador

```python
def aplicar_filtro_butterworth(señal, fs, lowcut=0.5, highcut=40.0, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
```
- Esta parte llama a la función anterior para obtener los coeficientes del filtro.
- 
```python
    if order == 1:
        eq = f"y[n] = ({b[0]:.4f} * x[n] + {b[1]:.4f} * x[n-1] - {a[1]:.4f} * y[n-1])"
        print("Ecuación en diferencias del filtro Butterworth:")
        print(eq)
```
- Si el filtro es de orden 1, imprime la ecuación en diferencias 

```python
    else:
        print(f"Filtro Butterworth aplicado (orden {order})")
        print(f"Coeficientes b: {b}")
        print(f"Coeficientes a: {a}")
```
- Si el filtro es de orden mayor, imprime los coeficientes completos
  
```python
    return lfilter(b, a, señal)
```
- Aplica el filtro a la señal usando lfilter(), que ejecuta la ecuación en diferencias usando los coeficientes b y a.
 
```python
filtered_ecg = aplicar_filtro_butterworth(ecg_mv, sampling_rate, lowcut, highcut, order)
```
- filtra la señal que ya fue convertida a milivoltios (ecg_mv) usando todos los parámetros definidos antes.

### Grafica de la señal filtrada

```python

plt.figure(figsize=(15, 5))
plt.plot(time, filtered_ecg, color='teal')
plt.title('ECG Filtrado')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.grid(True)
plt.show()
```
![image](https://github.com/user-attachments/assets/cd2eccd2-5967-42e9-8a07-6d70b83be904)
![image](https://github.com/user-attachments/assets/158e4055-02d6-4874-93dd-37a82aa06cdf)


## Deteccion de los picos R

Antes de todo En un electrocardiograma (ECG), un pico R es el punto más alto de un complejo QRS, que representa la despolarización ventricular, es decir, el momento en que los ventrículos del corazón se contraen. Es el componente más prominente del ECG y por eso se suele usar para analizar la frecuencia cardíaca y la variabilidad del ritmo (HRV).

```python
distance = int(0.2 * sampling_rate)  # 0.2 es el tiempo  entre picos(Tiempo) , entre mayor tiempo menos reconocimiento de picos
min_height = 80   # mV Deteccion de picos desde un minimo de 80mV
max_height = 130  # mV Deteccion de picos hasta un maximo de 130 (Asegurar que capte todos los picos)
```

- **distance:** Define el mínimo número de muestras entre dos picos R detectables,  Esto impone un límite mínimo de 0.2 segundos entre picos, lo que evita detectar múltiples picos dentro de un solo latido.
- **min_height y max_height:** Se establece que un pico debe estar entre 80 mV y 130 mV de altura para ser considerado un pico R, siendo min_height la altura minima y el max la altura maxima

```python
peaks, properties = find_peaks(filtered_ecg, distance=distance, height=(min_height, max_height))
```
- find_peaks() es una función de scipy.signal que detecta máximos locales en la señal.

- **Solo se consideran los picos que cumplan:** - Tener una distancia mínima (distance), - Tener una altura dentro del rango definido (height)

```python
t_peaks = peaks / sampling_rate
```

- Convierte las posiciones de muestra a tiempo en segundos, útil para graficar o calcular intervalos entre latidos.

### Visualizacion de los picos R y cuantos picos R hay

```python
# Visualización
plt.figure(figsize=(15, 5))
plt.plot(time, filtered_ecg, label='ECG Filtrado', color='green')
plt.plot(time[peaks], filtered_ecg[peaks], 'rx', label=f'Picos R detectados ({min_height}-{max_height} mV)')
plt.title('Detección de Picos R con Rango de Amplitud')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.legend()
plt.grid(True)
plt.show()

print(f"Cantidad de picos R detectados: {len(peaks)}")

# Cantidad de picos R detectados: 469
```
![image](https://github.com/user-attachments/assets/2dbea8bc-1cb6-49c5-8c60-1fbaee18cdac)
![image](https://github.com/user-attachments/assets/3eef1763-4693-4d74-b2e4-78908cd48cb9)

**Cantidad de picos R detectados: 469**

*Obtener los picos R puede ayudar con lo siguiente*

- Calcular la frecuencia cardíaca.

- Estimar los intervalos R-R (tiempo entre latidos).

- Realizar análisis de variabilidad (HRV), estrés, fatiga, etc.





![image](https://github.com/user-attachments/assets/271346e6-6ac6-4a10-9a0a-f345e3d83d60)

![image](https://github.com/user-attachments/assets/f4ff73ce-c025-49d7-8a8b-c188aabcdb18)
