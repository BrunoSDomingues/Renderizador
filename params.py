import numpy as np

WIDTH, HEIGHT = 400, 200  # Tamanho da tela

aux_arrays = []  # Lista de arrays auxiliares, como lookAt e perspective

# Matriz de transformação, inicia como matriz identidade mas pode ser alterada
transform_array = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]
)

stack = []  # Pilha para armazenar os valores da matriz de transformação
