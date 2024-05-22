import tkinter as tk
from collections import deque
import numpy as np
import random
import pygame
from colorama import init, Fore, Style
from art import *
from pprint import pformat

init()

# Definir movimientos posibles (arriba, abajo, izquierda, derecha)
moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

def is_valid_move(maze, row, col):
    # Verificar si la celda esta dentro de los limites del laberinto y si es un pasillo
    return 0 <= row < len(maze) and 0 <= col < len(maze[0]) and maze[row][col] == 0

def bfs(maze, start, end, canvas):
    queue = deque([(start, 0)])  # Cola para BFS (celda y distancia desde el inicio)
    visited = set()  # Conjunto para registrar celdas visitadas
    visited.add(start)
    parents = {}  # Diccionario para almacenar los padres de cada celda

    while queue:
        (row, col), distance = queue.popleft()
        color = 'lightblue' if maze[row][col] == 0 else 'black'
        canvas.create_rectangle(col*cell_size, row*cell_size, (col+1)*cell_size, (row+1)*cell_size, fill=color)
        canvas.create_rectangle(start[1]*cell_size, start[0]*cell_size, (start[1]+1)*cell_size, (start[0]+1)*cell_size, fill='yellow')
        canvas.create_rectangle(end[1]*cell_size, end[0]*cell_size, (end[1]+1)*cell_size, (end[0]+1)*cell_size, fill='red')
        if (row, col) == end:
            return distance, parents  # Hemos llegado a la celda de salida, retornar la distancia y los padres

        for dr, dc in moves:  # Iterar sobre movimientos posibles
            new_row, new_col = row + dr, col + dc
            if is_valid_move(maze, new_row, new_col) and (new_row, new_col) not in visited:
                queue.append(((new_row, new_col), distance + 1))
                visited.add((new_row, new_col))  # Marcar celda como visitada
                parents[(new_row, new_col)] = (row, col)  # Almacenar el padre de la celda

        canvas.update()
        canvas.after(100)

    return -1, None  # No se encontro ruta hasta la celda de salida

def reconstruct_path(parents, start, end):
    # Reconstruir la ruta desde la celda de inicio hasta la celda de salida
    path = []
    current = end
    while current != start:
        path.append(current)
        current = parents[current]
    path.append(start)
    return path[::-1]

def find_shortest_path(maze, start, end, canvas):
    # Ejecutar BFS para encontrar la distancia más corta desde la celda de inicio hasta la celda de salida
    distance, parents = bfs(maze, start, end, canvas)
    if distance == -1:
        return None, -1  # No se encontro una ruta válida
    else:
        return reconstruct_path(parents, start, end), distance

def generate_maze(rows, cols, p):
    maze = np.random.choice([0, 1], size=(rows, cols), p=[p, 1-p])
    return maze

def start_bfs():
    global path, distance, maze, start, end, canvas
    # Generar laberinto aleatorio
    rows, cols = 15, 15
    cell_size = 40
    maze = generate_maze(rows, cols, p=0.7)

    # Randomizar el punto de partida y el final
    start = (random.randint(0, rows-1), random.randint(0, cols-1))
    end = (random.randint(0, rows-1), random.randint(0, cols-1))
    while start == end or maze[start] == 1 or maze[end] == 1:
        start = (random.randint(0, rows-1), random.randint(0, cols-1))
        end = (random.randint(0, rows-1), random.randint(0, cols-1))

    # Dibujar el laberinto
    canvas.delete("all")
    for row in range(rows):
        for col in range(cols):
            color = 'black' if maze[row][col] == 1 else 'white'
            canvas.create_rectangle(col*cell_size, row*cell_size, (col+1)*cell_size, (row+1)*cell_size, fill=color)

    # Marcar inicio y fin
    canvas.create_rectangle(start[1]*cell_size, start[0]*cell_size, (start[1]+1)*cell_size, (start[0]+1)*cell_size, fill='yellow')
    canvas.create_rectangle(end[1]*cell_size, end[0]*cell_size, (end[1]+1)*cell_size, (end[0]+1)*cell_size, fill='red')

    # Encontrar la ruta mas corta
    path, distance = find_shortest_path(maze, start, end, canvas)
    if path is not None:
        pathPretty = pformat([path], indent=4)
        distancePretty = pformat(distance, indent=4)
        print(f"{Fore.GREEN}{Style.BRIGHT}Ruta más corta:\n{Style.RESET_ALL}  {Fore.CYAN}{Style.BRIGHT}{pathPretty}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}Distancia:{Style.RESET_ALL} {Fore.CYAN}{Style.BRIGHT}{distancePretty}{Style.RESET_ALL}")
        # Marcar el camino óptimo
        for row, col in path[1:-1]:
            canvas.create_rectangle(col*cell_size, row*cell_size, (col+1)*cell_size, (row+1)*cell_size, fill='darkgreen')
            canvas.create_rectangle(start[1]*cell_size, start[0]*cell_size, (start[1]+1)*cell_size, (start[0]+1)*cell_size, fill='yellow')
            canvas.create_rectangle(end[1]*cell_size, end[0]*cell_size, (end[1]+1)*cell_size, (end[0]+1)*cell_size, fill='red')

        pygame.mixer.init()
        pygame.mixer.music.load("sounds/success.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        root.after(10000, start_bfs)
    else:
        for row in range(len(maze)):
            for col in range(len(maze[0])):
                if maze[row][col] == 1:  # Si la celda fue explorada
                    canvas.create_rectangle(col*cell_size, row*cell_size, (col+1)*cell_size, (row+1)*cell_size, fill='purple')
        
        pygame.mixer.init()
        pygame.mixer.music.load("sounds/Fail.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

        root.after(5000, start_bfs)

# Configuración de la ventana
rows, cols = 15, 15
cell_size = 40
start = (0, 0)
end = (rows-1, cols-1)
maze = generate_maze(rows, cols, p=0.7)

# Crear ventana y lienzo
root = tk.Tk()
root.title("Laberinto con BFS")
root.geometry('{}x{}'.format((cols+1)*cell_size, (rows+2)*cell_size))  # Ajustar size de ventana
root.resizable(False, False)  # Impedir que la ventana se pueda redimensionar
canvas = tk.Canvas(root, width=cols*cell_size, height=rows*cell_size)
canvas.pack()

# Botón para salir
exit_button = tk.Button(root, text="Salir", command=root.destroy)
exit_button.pack()

# Botón para iniciar BFS
start_bfs_button = tk.Button(root, text="Iniciar BFS", command=start_bfs)
start_bfs_button.pack()

tprint("AgentesPy", "rnd-xlarge")

start_bfs()
root.mainloop()
