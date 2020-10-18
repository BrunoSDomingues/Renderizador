import numpy as np
from params import WIDTH, HEIGHT

# Cria um triângulo para o triangleSet
def make_triangle_array(p_list, idx):
    i = 9*idx
    
    return np.array(
        [
            [p_list[i], p_list[i + 3], p_list[i + 6]],
            [p_list[i + 1], p_list[i + 4], p_list[i + 7]],
            [p_list[i + 2], p_list[i + 5], p_list[i + 8]],
            [1, 1, 1],
        ]
    )


# Faz a matriz de coordenadas da tela
def make_screen_array():
    global WIDTH, HEIGHT

    # Matriz de escala
    scale_array = np.array(
        [
            [WIDTH / 2, 0, 0, 0],
            [0, HEIGHT / 2, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )

    # Matriz de translação
    translation_array = np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
    )

    # Matriz de espelhamento
    mirror_array = np.array(
        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    )

    # Faz o produto das matrizes
    return np.matmul(np.matmul(scale_array, translation_array), mirror_array)


# Retorna os vértices para serem utilizados no triangleSet2D
def get_vertexes(arr):
    vtx = []
    
    for i in range(3):
        for j in range(2):
            vtx.append(arr[j, i])
            
    return vtx


# Faz o array das tiras do triângulo 
def make_triangle_strips_array(point, idx):
    i = 3*idx
    
    if idx % 2 == 0:
        return np.array(
            [
                [point[i], point[i + 3], point[i + 6]],
                [point[i + 1], point[i + 4], point[i + 7]],
                [point[i + 2], point[i + 5], point[i + 8]],
                [1, 1, 1],
            ]
        )
        
    else:
        return np.array(
            [
                [point[i + 3], point[i], point[i + 6]],
                [point[i + 4], point[i + 1], point[i + 7]],
                [point[i + 5], point[i + 2], point[i + 8]],
                [1, 1, 1],
            ]
        )


# A partir do size e do center, retorna a lista de faces do método box
def get_box_faces(size, c):
    s = [s / 2 for s in size]

    vtx = [
        [c[0] - s[0], c[1] - s[1], c[2] - s[2]],
        [c[0] - s[0], c[1] - s[1], c[2] + s[2]],
        [c[0] - s[0], c[1] + s[1], c[2] - s[2]],
        [c[0] - s[0], c[1] + s[1], c[2] + s[2]],
        [c[0] + s[0], c[1] - s[1], c[2] - s[2]],
        [c[0] + s[0], c[1] - s[1], c[2] + s[2]],
        [c[0] + s[0], c[1] + s[1], c[2] - s[2]],
        [c[0] + s[0], c[1] + s[1], c[2] + s[2]],
    ]

    return [
        [vtx[4], vtx[6], vtx[0], vtx[2]],
        [vtx[2], vtx[3], vtx[6], vtx[7]],
        [vtx[0], vtx[1], vtx[4], vtx[5]],
        [vtx[4], vtx[5], vtx[6], vtx[7]],
        [vtx[0], vtx[1], vtx[2], vtx[3]],
        [vtx[5], vtx[7], vtx[1], vtx[3]],
    ]
