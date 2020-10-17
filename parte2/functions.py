import numpy as np
from params import t_array, aux_arrays, WIDTH, HEIGHT

# Cria a lista de triângulos para o triangleSet
def make_triangle_set_array(p_list):
    triangles = []

    for p in range(0, len(p_list), 9):
        triangles.append(
            np.array(
                [
                    [p_list[p], p_list[p + 3], p_list[p + 6]],
                    [p_list[p + 1], p_list[p + 4], p_list[p + 7]],
                    [p_list[p + 2], p_list[p + 5], p_list[p + 8]],
                    [1.0, 1.0, 1.0],
                ]
            )
        )

    return triangles


# Faz a matriz de coordenadas da tela
def make_screen_array():

    # Matriz de escala
    scale_array = np.array(
        [
            [WIDTH / 2.0, 0, 0, 0],
            [0, HEIGHT / 2.0, 0, 0],
            [0, 0, 1.0, 0],
            [0, 0, 0, 1.0],
        ]
    )

    # Matriz de translação
    translation_array = np.identity(4)

    # Matriz de espelhamento
    mirror_array = np.array(
        [[1.0, 0, 0, 0], [0, -1.0, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]]
    )

    # Faz o produto das matrizes
    return np.matmul(np.matmul(scale_array, translation_array), mirror_array)


# Faz as transformações de um triângulo
def transform_triangle(arr):
    l_array, p_array = aux_arrays[0], aux_arrays[1]
    s_array = make_screen_array()

    # 1a transformação: das coordenadas do objeto para as do mundo
    t1 = np.matmul(t_array, arr)

    # 2a transformação: das coordenadas do mundo para as da câmera
    t2 = np.matmul(l_array, t1)

    # 3a transformação: das coordenadas da câmera para perspectiva
    t3 = np.matmul(p_array, t2)

    # Normalizando t3
    for i in range(3):
        if t3[-1, i] > 0:
            t3[:, i] /= t3[-1, i]

    # Última transformação: da perspectiva para as coordenadas da tela
    return np.matmul(s_array, t3)


# Retorna os vértices para serem utilizados no triangleSet2D
def get_vertexes(arr):
    t_arr = transform_triangle(arr)
    return [t_arr[i, j] for j in range(3) for i in range(2)]


# Faz a lista de tiras do triangleStripSet
def make_strips_array(point, lim):
    for i in range(lim):
        if i % 2 == 0:
            return np.array(
                [
                    [point[3 * i], point[3 * i + 3], point[3 * i + 6]],
                    [point[3 * i + 1], point[3 * i + 4], point[3 * i + 7]],
                    [point[3 * i + 2], point[3 * i + 5], point[3 * i + 8]],
                    [1.0, 1.0, 1.0],
                ]
            )
    else:
        return np.array(
            [
                [point[3 * i + 3], point[3 * i + 0], point[3 * i + 6]],
                [point[3 * i + 4], point[3 * i + 1], point[3 * i + 7]],
                [point[3 * i + 5], point[3 * i + 2], point[3 * i + 8]],
                [1.0, 1.0, 1.0],
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
