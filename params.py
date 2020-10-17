import numpy as np

WIDTH, HEIGHT = 400, 200  # Tamanho da tela

aux_arrays = []  # Lista de arrays auxiliares, como lookAt e perspective
t_array = np.identity(
    4
)  # Matriz de transformação, inicia como matriz identidade mas pode ser

stack = []  # Pilha para armazenar os valores de t_array
