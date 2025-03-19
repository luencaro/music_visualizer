import pygame
import pyaudio
import numpy as np
import sys
import tkinter as tk
from tkinter import filedialog
import librosa
from collections import deque
import math

# Configuración actualizada
class Config:
    WIDTH, HEIGHT = 1080, 720
    FPS = 60
    CHUNK = 2048
    RATE = 44100
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    HISTORY_LENGTH = 30
    SMOOTHING = 0.7
    # El parámetro LOG_BASE ya no se utiliza
    SYMMETRICAL = False  # Opción ya no necesaria para modos extra
    PEAK_LINES = 50  # Líneas dinámicas entre picos
    COLOR_SCHEMES = [
        lambda i, n, t: hsl_to_rgb((i/n + t*0.1) % 1, 0.7, 0.6),
        lambda i, n, t: (150 + int(105 * math.sin(t*2 + i/n*5)), 0, 0),
        lambda i, n, t: (int(255 * abs(math.sin(t*3 + i/n*10))), 0, 0),
    ]
    # Nueva opción para escoger entre escala logarítmica y lineal
    USE_LOG_SCALE = False

def hsl_to_rgb(h, s, l):
    # Conversión HSL a RGB para obtener efectos de color suaves
    c = (1 - abs(2*l - 1)) * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = l - c/2
    if h < 1/6:
        r, g, b = c, x, 0
    elif h < 2/6:
        r, g, b = x, c, 0
    elif h < 3/6:
        r, g, b = 0, c, x
    elif h < 4/6:
        r, g, b = 0, x, c
    elif h < 5/6:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

class AudioVisualizer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        self.clock = pygame.time.Clock()
        self.p = pyaudio.PyAudio()
        
        self.audio_data = None
        self.stream = None
        self.pointer = 0
        self.paused = False
        self.color_scheme = 0
        self.history = deque(maxlen=Config.HISTORY_LENGTH)
        self.smoothed = None
        self.max_amplitude = 1
        self.time = 0
        
        self.load_audio()
        self.init_audio_stream()

    def load_audio(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac")])
        root.destroy()
        
        if not file_path:
            sys.exit()
        
        audio, _ = librosa.load(file_path, sr=Config.RATE, mono=True)
        self.audio_data = (audio * 32767).astype(np.int16)
    
    def init_audio_stream(self):
        self.stream = self.p.open(
            format=Config.FORMAT,
            channels=Config.CHANNELS,
            rate=Config.RATE,
            output=True
        )

    def process_audio(self):
        chunk = self.audio_data[self.pointer:self.pointer + Config.CHUNK]
        if len(chunk) < Config.CHUNK:
            chunk = np.pad(chunk, (0, Config.CHUNK - len(chunk)), 'constant')
        
        # Aplicar ventana de Hann para una mejor FFT
        window = np.hanning(len(chunk))
        fft = np.abs(np.fft.fft(chunk * window)[:Config.CHUNK // 2])
        
        # Suavizado no lineal
        if self.smoothed is None:
            self.smoothed = fft
        else:
            self.smoothed = np.maximum(fft, Config.SMOOTHING * self.smoothed)
        
        self.history.append(self.smoothed)
        self.max_amplitude = max(np.max(self.smoothed), self.max_amplitude * 0.99)
        return self.smoothed

    def draw_spectrum_wave(self, amplitudes):
        n = len(amplitudes)
        points = []
        
        # Seleccionar la forma de muestreo según la opción: logarítmica o lineal
        if Config.USE_LOG_SCALE:
            bins = np.logspace(0, np.log10(n), num=Config.WIDTH, base=10)
        else:
            bins = np.linspace(0, n - 1, Config.WIDTH)
        
        for x in range(Config.WIDTH):
            bin_idx = int(bins[x])
            bin_idx = min(bin_idx, n - 1)
            y = Config.HEIGHT / 2 - amplitudes[bin_idx] * Config.HEIGHT / self.max_amplitude * 0.6
            points.append((x, y))
        
        # Dibujar la línea del espectro con gradiente de color
        for i in range(len(points) - 1):
            alpha = int(255 * (i / Config.WIDTH))
            color = (*Config.COLOR_SCHEMES[self.color_scheme](i, Config.WIDTH, self.time), alpha)
            pygame.draw.line(self.screen, color, points[i], points[i + 1], 4)
        
        # Dibujar líneas dinámicas entre picos
        for _ in range(Config.PEAK_LINES):
            i = np.random.randint(0, len(points) - 10)
            j = np.random.randint(i + 5, min(i + 20, len(points) - 1))
            if abs(points[i][1] - points[j][1]) > 50:
                color = Config.COLOR_SCHEMES[self.color_scheme](i, Config.WIDTH, self.time)
                pygame.draw.line(self.screen, color, points[i], points[j], 1)

    def draw_ui(self):
        # Barra de progreso con efecto de onda
        progress = self.pointer / len(self.audio_data)
        for i in range(Config.WIDTH):
            y = Config.HEIGHT - 10 + 5 * math.sin(i / 50 + self.time * 5)
            color = Config.COLOR_SCHEMES[self.color_scheme](i, Config.WIDTH, self.time)
            if i < Config.WIDTH * progress:
                pygame.draw.rect(self.screen, color, (i, int(y), 1, 3))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.pointer = 0
                elif event.key == pygame.K_c:
                    self.color_scheme = (self.color_scheme + 1) % len(Config.COLOR_SCHEMES)
                # Tecla para alternar entre escala logarítmica y lineal
                elif event.key == pygame.K_l:
                    Config.USE_LOG_SCALE = not Config.USE_LOG_SCALE
                elif event.key == pygame.K_ESCAPE:
                    self.quit()
    
    def quit(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.time = pygame.time.get_ticks() / 1000
            self.handle_input()
            # Limpiar pantalla sin fondo (sin efectos adicionales)
            self.screen.fill((0, 0, 0))
            
            if not self.paused and self.pointer < len(self.audio_data):
                chunk = self.audio_data[self.pointer:self.pointer + Config.CHUNK]
                self.stream.write(chunk.tobytes())
                amplitudes = self.process_audio()
                self.pointer += Config.CHUNK
            else:
                amplitudes = np.zeros(Config.CHUNK // 2)
            
            self.draw_spectrum_wave(amplitudes)
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(Config.FPS)

if __name__ == "__main__":
    visualizer = AudioVisualizer()
    visualizer.run()
