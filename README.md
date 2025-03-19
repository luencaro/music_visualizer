# Visualizador de Audio en Tiempo Real

Este proyecto es un visualizador de audio en tiempo real desarrollado en Python. Utiliza técnicas de procesamiento de señales para transformar el audio en su representación en el dominio de la frecuencia mediante una Transformada de Fourier (FFT) y muestra la visualización utilizando gráficos generados con Pygame.

## Características

- **Visualización Espectral:** Representa las amplitudes de las frecuencias del audio en forma de onda, permitiendo alternar entre escala logarítmica y lineal.
- **Reproducción de Audio en Tiempo Real:** Sincroniza la reproducción del audio con la visualización.
- **Interfaz Interactiva:** Permite pausar, reiniciar y cambiar esquemas de color mediante atajos de teclado.
- **Código Modular y Personalizable:** Fácil de modificar para futuras mejoras.

## Requisitos

- **Python 3.6+**

### Librerías Python:
- `pygame`
- `pyaudio`
- `numpy`
- `librosa`
- `tkinter` (incluido con Python en la mayoría de las instalaciones)

## Instalación

1. **Clona el repositorio o descarga el archivo `main.py`.**

2. **Instala las dependencias necesarias.** Puedes hacerlo utilizando `pip`:

   ```bash
   pip install pygame pyaudio numpy librosa

## Explicación Técnica: Transformada de Fourier

El visualizador utiliza la Transformada de Fourier (FFT) para analizar la señal de audio y convertirla al dominio de la frecuencia. Este proceso se realiza en los siguientes pasos:

1. **Extracción de un Bloque (Chunk):**  
   Se procesa el audio en bloques de tamaño definido (`Config.CHUNK`).

2. **Aplicación de la Ventana de Hann:**  
   Se aplica una ventana de Hann al bloque para minimizar la fuga espectral y mejorar la precisión de la FFT. La ventana suaviza los bordes de la señal, reduciendo los artefactos en la transformación.

3. **Cálculo de la FFT:**  
   Se utiliza `np.fft.fft` para transformar la señal. Se toma la magnitud de los valores complejos con `np.abs` y se considera únicamente la primera mitad del resultado, ya que la FFT de una señal real es simétrica.

4. **Suavizado y Normalización:**  
   Para evitar cambios bruscos en la visualización, los resultados de la FFT se suavizan utilizando un factor configurable (`Config.SMOOTHING`). Además, se normalizan en función de la amplitud máxima obtenida, garantizando una representación visual consistente.

### Teoría de la Transformada de Fourier

La Transformada de Fourier es una técnica matemática fundamental que permite descomponer cualquier señal en una suma de funciones sinusoidales (seno y coseno) con diferentes frecuencias, amplitudes y fases. Esta descomposición facilita el análisis y la manipulación de señales en el dominio de la frecuencia.

En el procesamiento digital, se utiliza la **Transformada Discreta de Fourier (DFT)**, definida por la siguiente fórmula:

$$
X_k = \sum_{n=0}^{N-1} x_n \cdot e^{-i2\pi \frac{kn}{N}}
$$

donde:
- $x_n$ es la señal en el dominio del tiempo.
- $X_k$ representa la magnitud y la fase correspondiente a la frecuencia $k$.
- $N$ es el número total de muestras.

Para optimizar el cálculo de la DFT, se utiliza el algoritmo **FFT (Fast Fourier Transform)**, que reduce significativamente la complejidad computacional de $O(N^2)$ a $O(N \log N)$, permitiendo así el análisis en tiempo real.

Un aspecto crucial en el análisis de señales es la **fuga espectral**, la cual se produce cuando la señal no es periódica en el intervalo de muestreo. Para mitigar este problema, se aplica una **ventana de Hann** a cada bloque de datos antes de calcular la FFT. La ventana de Hann se define como:

$$
w(n) = 0.5 \left(1 - \cos\left(\frac{2\pi n}{N-1}\right)\right)
$$

para $n = 0, 1, \dots, N-1$. Al suavizar los bordes del bloque, la ventana de Hann reduce la discontinuidad en la señal y mejora la exactitud de la transformación.

El resultado es un vector de magnitudes que indica la energía presente en cada frecuencia, lo que se traduce en una representación visual del espectro del audio.


