# Variabilidad-de-la-Frecuencia-Cardiaca-usando-la-Transformada-Wavelet

# Objetivo

Estudiar la variabilidad del ritmo cardíaco (HRV) aplicando la transformada wavelet, con el objetivo de detectar alteraciones en sus patrones frecuenciales y examinar cómo evoluciona la señal cardiaca en el tiempo.

# Requisitos
* Computador con Pyhton
* Librerias: Pywavelets

  
## Fundamentos Teoricos

### Nuestro corazón no late siempre a la misma velocidad; entre un latido y el siguiente se producen pequeñas aceleraciones y desaceleraciones. Estas variaciones, conocidas como Variabilidad de la Frecuencia Cardíaca (HRV), nos indican cómo el cuerpo gestiona el estrés, el descanso y las respuestas al entorno.



## Control autonomo

**Sistema simpático (acelerador):** eleva las pulsaciones cuando hacemos ejercicio, nos asustamos o nos estresamos.

**Sistema parasimpático (relajación y digestion):** reduce las pulsaciones cuando estamos relajados, descansando o durmiendo.

## ¿Qué mide la HRV?

**La HRV cuantifica las diferencias de tiempo entre latidos sucesivos (intervalos R-R).**

**Una HRV alta sugiere un sistema nervioso autónomo, sano flexible y bien adaptado.**

**Una HRV baja puede reflejar fatiga, estrés prolongado o posibles alteraciones de salud.**

## Métodos de análisis

**Dominio del tiempo:** calculamos la media y la desviación estándar de los intervalos R-R para evaluar su consistencia.

**Dominio tiempo-frecuencia:** aplicamos la Transformada Wavelet —un “microscopio” dinámico— para detectar cómo cambian las frecuencias  a lo largo de los 5 minutos de registro.

# Diagrama de flujo

![image](https://github.com/user-attachments/assets/1d4b497f-e38b-464d-bbc8-1f8433ae6417)


# Adquisicion de la señal 


### La señal ECG fue adquirida utilizando un sensor de ECG de superficie (electrodos) conectado a un sistema de adquisición con la placa STM32. La grabación se realizó en un sujeto en estado de reposo, sin movimiento, durante un periodo continuo de 5 minutos.

### Características de la adquisición:

- **Frecuencia de muestreo:** 400 Hz

- **Tiempo total de adquisición:** 300 segundos

- **Cantidad total de muestras:** 120,000

- **Nivel de cuantificación:** 12 bits (valores entre 0 y 4095 ADC)

- **Condiciones:** sujeto en reposo, en ambiente controlado, algun juego o actividad de respiracion para aumentar frecuencias por ciertos periodos

# Para el analisis de la señal y el HRV con Python se hizo

conversión de unidades, filtrado digital, detección de picos R, análisis de intervalos R-R y análisis de HRV con transformada wavelet.

---

## 1. Lectura y conversión de datos

```python
with open('DANIEL01.txt', 'r') as file:
    data = file.readlines()
senal_ecg = np.array([int(x.strip()) for x in data])
```

Lee los valores de un archivo `.txt` donde cada línea representa una muestra de ECG adquirida por un ADC. Luego los convierte a una lista de enteros y la transforma en un arreglo de `numpy`.

---
### Gráfica 1: Señal original en milivoltios

```python
plt.plot(time, ecg_mv)
```


![image](https://github.com/user-attachments/assets/7a1cd509-b354-4069-a14a-12db32e42009)
![image](https://github.com/user-attachments/assets/3c9db63d-d91d-4b42-bd0e-408eaf12558f)

## 2. Parámetros de adquisición

```python
frecuenciamuestreo = 400  # Hz
lowcut = 0.5  # Hz
highcut = 40.0  # Hz
order = 2
```

- `frecuenciamuestreo`: 400 muestras por segundo.
- `lowcut`, `highcut`: define un filtro pasa banda útil para eliminar artefactos de baja y alta frecuencia.
- `order`: orden del filtro (mayor orden = respuesta más selectiva).

---

## 3. Conversión de señal a milivoltios

```python
adc_max = 4095
v_ref = 3.3
ecg_mv = (senal_ecg / adc_max) * v_ref * 1000
```

Convierte la señal digital (12 bits, 0–4095) a milivoltios. Este paso es fundamental para que la señal sea fisiológicamente interpretable.

---

## 4. Filtrado Butterworth

```python
filtered_ecg = aplicar_filtro_butterworth(ecg_mv, frecuenciamuestreo, lowcut, highcut, order)
```

Se usa un filtro digital Butterworth para eliminar el ruido y artefactos, preservando las frecuencias del ECG clínicamente relevantes (0.5–40 Hz).



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

### Gráfica 2: Señal ECG filtrada


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


## 5. Deteccion de los picos R

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

### 6. Visualizacion de los picos R y cuantos picos R hay

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
### Gráfica 3: Detección de picos R


![image](https://github.com/user-attachments/assets/2dbea8bc-1cb6-49c5-8c60-1fbaee18cdac)
![image](https://github.com/user-attachments/assets/3eef1763-4693-4d74-b2e4-78908cd48cb9)

**Cantidad de picos R detectados: 469**

*Obtener los picos R ayuda con la frecuencia cardíaca, los intervalos R-R (tiempo entre latidos) y lo más importante ealizar análisis de variabilidad (HRV), estrés, fatiga, etc.
### Gráfica 4: Intervalos R-R

```python
rr_intervalos = np.diff(peaks) / frecuenciamuestreo  # en segundos

plt.plot(rr_intervalos, marker='o')
```
- peaks contiene los índices (en muestras) de los picos detectados en la señal.

- np.diff(peaks) calcula la diferencia entre cada pico consecutivo → da la cantidad de muestras entre latidos.

- Dividir por frecuenciamuestreo (en Hz) convierte esas diferencias de muestras a segundos.

```python
mean_rr = np.mean(rr_intervalos)
std_rr = np.std(rr_intervalos)
print(f"Media de Intervalos R-R: {mean_rr:.4f} s")
print(f"Desviación estándar de R-R: {std_rr:.4f} s")

#Media de Intervalos R-R: 0.6405 s
#Desviación estándar de R-R: 0.0686 s

```
Se calcula la media (mean_rr) y la desviación estándar (std_rr) de los intervalos R-R.

- La media indica el promedio de tiempo entre latidos → permite estimar la frecuencia cardíaca media.

- La desviación estándar muestra cuánto varían esos intervalos → es una medida simple de HRV.

- Muestra los valores numéricos de la media y la variabilidad de los intervalos R-R en consola.

Se calcularon los intervalos R-R a partir de los picos detectados y se representaron gráficamente para observar su comportamiento a lo largo del tiempo. A partir de estos datos, se obtuvo la media y la desviación estándar,  identificando posibles patrones de regularidades o fluctuaciones relevantes.

![image](https://github.com/user-attachments/assets/806bcd0d-0361-4b46-9fb3-86780dd50815)


Representa la duración de cada intervalo R-R. Ideal para detectar irregularidades en el ritmo cardíaco.

## 7. Análisis de HRV con Wavelet
En primer lugar la transformada wavelet analiza señales en tiempo y frecuencia a la vez, detecta cambios temporales en frecuencias, y es ideal para estudiar patrones VARIABLES como los latidos cardíacos.
```python
wavelet_type = 'morl'
scales = np.arange(1, 1000)  # Más escalas , mayor resolución en la frecuencia es decir aumentar los valores (b)
sampling_period = 1  

coeffs, freqs = pywt.cwt(rr_intervalos, scales=np.arange(1, 1000), wavelet='morl', sampling_period=1)
```
- Define las escalas (inversas de frecuencia) que usará la transformada.

- Cuanto más amplio sea este rango, mayor será la resolución en frecuencia del espectrograma.

- Este rango cubre tanto frecuencias altas como bajas.


## Se aplica la transformada wavelet continua (CWT):
- Se usan muchas escalas (`np.arange(1, 1000)`) para obtener buena resolución en frecuencia.
- La wavelet Morlet (`'morl'`) es una buena elección para análisis fisiológico.

El espectrograma resultante permite observar la distribución de energía de los intervalos R-R a lo largo del tiempo y en distintas bandas de frecuencia:
- **LF (0.04 - 0.15 Hz)**: refleja regulación simpática y parasimpática.
- **HF (0.15 - 0.4 Hz)**: asociada a respiración y tono vagal.


### Gráfica 5: Espectrograma de HRV (Wavelet)
```python
plt.imshow(np.abs(coeffs), extent=[0, len(rr_intervalos), freqs[-1], freqs[0]], aspect='auto')
```

![image](https://github.com/user-attachments/assets/f4ff73ce-c025-49d7-8a8b-c188aabcdb18)


nos muestra cómo varía la energía en diferentes frecuencias del HRV a lo largo del tiempo.ahora además tenemos bandas fisiológicas clave:
- **LF** (0.04–0.15 Hz): modulación simpática y parasimpática.
- **HF** (0.15–0.4 Hz): control vagal (respiratorio).


*En el análisis de la variabilidad de la frecuencia cardíaca (HRV) se aplicó la Transformada Wavelet Continua (CWT) con la wavelet Morlet, permitiendo observar cómo varía la potencia espectral de los intervalos R-R a lo largo del tiempo. El espectrograma resultante mostró información  en diferentes escalas de frecuencia, incluyendo las bandas fisiológicas LF (0.04–0.15 Hz) y HF (0.15–0.4 Hz), lo que facilita identificar momentos donde se producen cambios significativos en la actividad autónoma. Se incluyeron líneas guía para delimitar dichas bandas y  proporcionando una visualización  completa del comportamiento dinámico del sistema nervioso autónomo.*

---


## Conclusión

Estea practica nos es una herramienta completa para el análisis de señales ECG ya que nnos da desde la adquisición hasta el análisis espectral, aplica técnicas fundamentales de procesamiento digital de señales y la fisiología . Es especialmente útil para estudiar la variabilidad de la frecuencia cardíaca (HRV), un marcador importante en salud cardiovascular.

## Preguntas
- ¿Qué diferencias se observan entre los análisis en el dominio del tiempo y el 
dominio tiempo-frecuencia?
---
R\ En el análisis en el dominio del tiempo, solo vemos cómo cambian los valores con respecto al tiempo. Por ejemplo, en nuestro caso, vimos los intervalos R-R y cómo varía la frecuencia cardíaca con el tiempo. lo cual es útil para detectar si n los latidos, están muy juntos o separados, pero no nos dice en qué frecuencias está variando la señal.
En cambio, el análisis en el dominio tiempo-frecuencia, como el que hicimos con la transformada wavelet, nos deja ver cómo cambian las frecuencias a lo largo del tiempo. Esto es muy útil para señales como el ECG, porque la variabilidad del corazón no es constante. Con este análisis, podemos ver por ejemplo si en cierto momento hay más actividad en frecuencias bajas (lo que se asocia a relajación) o en frecuencias altas (lo que se asocia a estrés o actividad simpática).

- ¿Qué efecto tiene el uso de diferentes funciones wavelet en los resultados del 
análisis?
---
R\ Las wavelets nos dejan ver detalles de la señal en distintas escalas, cambiar el wavelet cambia esa "escala" en nuestro caso usamos la wavelet Morlet, que es buena para ver patrones suaves y continuos como los de la frecuencia cardíaca. Si usáramos otra wavelet,.

- ¿Qué aplicaciones reales tiene esta práctica?
---
R\Esta practica de laboratorio puede tener aplicaciones precisamente en el campo de la cardiologia determinando si hay alguna sobre fatiga, sin embargo también puede tener aplicaciones en el campo de la psicologia determinando como reacción una persona a cierto estimulo psicologico o incluso en deportes para ver la fatoga del atleta.



- *Daniel Herrera* est.daniela.herreraa@unimilitar.edu.co
- *Juan Ortiz*    est.juan.ortiz4@unimilitar.edu.co

 








