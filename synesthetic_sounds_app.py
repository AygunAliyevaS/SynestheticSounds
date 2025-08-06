
import pygame
import tkinter as tk
from tkinter import colorchooser
import os

# Initialize mixer
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Load sound samples
sound_files = {
    "#ff0000": "A4_piano_mono.wav",   # Red
    "#00ff00": "C5_piano_mono.wav",   # Green
    "#0000ff": "E5_piano_mono.wav",   # Blue
    "#ffff00": "G5_piano_mono.wav",   # Yellow
    "#000000": "D4_piano_mono.wav",   # Black
    "#ffffff": "A5_piano_mono.wav"    # White
}
sounds = {color: pygame.mixer.Sound(file) for color, file in sound_files.items()}

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

def choose_color():
    global current_color
    color = colorchooser.askcolor()[1]
    if color:
        current_color = color

def draw(event):
    x1, y1 = (event.x - brush_size), (event.y - brush_size)
    x2, y2 = (event.x + brush_size), (event.y + brush_size)
    canvas.create_oval(x1, y1, x2, y2, fill=current_color, outline=current_color)
    play_sound()

root = tk.Tk()
root.title("SynestheticSounds - Paint with Piano")

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

size_scale.config(command=update_size)

root.mainloop()
