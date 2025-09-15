
import pygame
import tkinter as tk
from tkinter import colorchooser
import numpy as np
import pygame.sndarray
import os
from datetime import datetime


# (Class definition omitted as it is not used)

# Initialize mixer
print("[INFO] Initializing Pygame mixer...")
pygame.mixer.init(frequency=44100, size=-16, channels=1)
print("[INFO] Mixer initialized.")

# Sound frequencies in Hz
sound_freqs = {
    "#ff0000": 440,    # Red A4
    "#00ff00": 493,   # Green B4
    "#0000ff": 261,   # Blue C4
    "#ffff00": 293,   # Yellow D4
    "#000000": 329,   # Black E4
    "#ffffff": 880    # White A5 (using highest value for white)
}

# Generate sound samples from frequencies
print("[INFO] Generating sound samples for each color...")
sounds = {}
sample_rate = pygame.mixer.get_init()[0]
duration = 0.5  # seconds
num_samples = int(duration * sample_rate)
for color, freq in sound_freqs.items():
    print(f"[DEBUG] Generating sound for color {color} at {freq} Hz")
    arr = np.sin(2 * np.pi * freq * np.arange(num_samples) / sample_rate)
    sound_array = np.int16(arr * 32767)
    sound = pygame.sndarray.make_sound(sound_array)
    sounds[color] = sound
print("[INFO] Sound samples generated.")

# GUI setup
brush_size = 16
current_color = "#ff0000"


def play_sound():
    color_hex = current_color.lower()
    if color_hex in sounds:
        volume = min(1.0, brush_size / 50.0)
        sound = sounds[color_hex]
        sound.set_volume(volume)
        sound.play()
        # Add timestamped log entry
        timestamp = datetime.now().isoformat()
        print({
            "event": "sound_played",
            "color": color_hex,
            "volume": volume,
            "timestamp": timestamp
        })

def choose_color():
    global current_color
    color = colorchooser.askcolor()[1]
    if color:
        current_color = color
        print(f"[INFO] Color chosen: {current_color}")

def draw(event):
    x1, y1 = (event.x - brush_size), (event.y - brush_size)
    x2, y2 = (event.x + brush_size), (event.y + brush_size)
    canvas.create_oval(x1, y1, x2, y2, fill=current_color, outline=current_color)
    play_sound()
    print(f"[DEBUG] Drew at ({event.x}, {event.y}) with color {current_color} and brush size {brush_size}")


print("[INFO] Starting SynestheticSounds application...")
root = tk.Tk()
root.title("SynestheticSounds - Paint with Melody")

canvas = tk.Canvas(root, width=800, height=600, bg="white")
canvas.pack()

canvas.bind("<B1-Motion>", draw)

controls = tk.Frame(root)
controls.pack()

tk.Button(controls, text="Choose Color", command=choose_color).pack(side=tk.LEFT)

size_scale = tk.Scale(controls, from_=1, to=50, orient=tk.HORIZONTAL, label="Brush Size")
size_scale.set(brush_size)
size_scale.pack(side=tk.LEFT)

def update_size(val):
    global brush_size
    brush_size = int(val)
    print(f"[INFO] Brush size updated: {brush_size}")

size_scale.config(command=update_size)

root.mainloop()
