import numpy as np
import gpu

from params import WIDTH, HEIGHT
from parte1.functions import is_inside
from parte2.functions import get_vertexes


def indexedFaceSet(
    coord,
    coordIndex,
    colorPerVertex,
    color,
    colorIndex,
    texCoord,
    texCoordIndex,
    current_color,
    current_texture,
):
    """ Função usada para renderizar IndexedFaceSet. """
    # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
    # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
    # Você receberá as coordenadas dos pontos no parâmetro cord, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedFaceSet uma lista informando
    # como conectar os vértices é informada em coordIndex, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.
    # Adicionalmente essa implementação do IndexedFace suport cores por vértices, assim
    # a se a flag colorPerVertex estiver habilidades, os vértices também possuirão cores
    # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
    # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
    # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
    # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
    # implementadado um método para a leitura de imagens.

    if coord:
        points = [coord[3 * p : 3 * p + 3] for p in range(int(len(coord) / 3))]

        triangles = []
        vertexes = []

        for v in coordIndex:
            if v != -1:
                vertexes.append(v)

                if len(vertexes) == 3:
                    v0, v1, v2 = [v - 1 for v in vertexes]

                    # Monta o triângulo e coloca na lista
                    triangles.append(
                        np.array(
                            [
                                [points[v0][0], points[v1][0], points[v2][0]],
                                [points[v0][1], points[v1][1], points[v2][1]],
                                [points[v0][2], points[v1][2], points[v2][2]],
                                [1.0, 1.0, 1.0],
                            ]
                        )
                    )

            else:
                vertexes = []

    if colorPerVertex:
        points = [coord[3 * p : 3 * p + 3] for p in range(int(len(coord) / 3))]
        colors = [color[3 * c : 3 * c + 3] for c in range(int(len(color) / 3))]

        triangles = []
        c_triangles = []

        for i in range(int(len(coordIndex) / 2 - 1)):
            # Faz os triângulos
            v0, v1, v2 = coordIndex[2 * i : 2 * i + 3]
            triangles.append(
                np.array(
                    [
                        [points[v0][0], points[v1][0], points[v2][0]],
                        [points[v0][1], points[v1][1], points[v2][1]],
                        [points[v0][2], points[v1][2], points[v2][2]],
                        [1.0, 1.0, 1.0],
                    ]
                )
            )

            # Faz as cores dos triângulos
            c0, c1, c2 = colorIndex[2 * i : 2 * i + 3]
            c_triangles.append([colors[c0], colors[c1], colors[c2]])

    if texCoord:
        image = gpu.GPU.load_texture(current_texture[0])

        points = [coord[3 * p : 3 * p + 3] for p in range(int(len(coord) / 3))]
        t_points = [
            texCoord[2 * tp : 2 * tp + 2] for tp in range(int(len(texCoord) / 2))
        ]

        triangles = []
        t_triangles = []

        for i in range(int(len(coordIndex) / 2 - 1)):
            # Faz os triângulos
            v0, v1, v2 = coordIndex[2 * i : 2 * i + 3]
            triangles.append(
                np.array(
                    [
                        [points[v0][0], points[v1][0], points[v2][0]],
                        [points[v0][1], points[v1][1], points[v2][1]],
                        [points[v0][2], points[v1][2], points[v2][2]],
                        [1.0, 1.0, 1.0],
                    ]
                )
            )

            # Faz as texturas
            vt0, vt1, vt2 = texCoordIndex[2 * i : 2 * i + 3]
            t_triangles.append([t_points[vt0], t_points[vt1], t_points[vt2]])

    if current_texture:
        image = gpu.GPU.load_texture(current_texture[0])

    for i in range(len(triangles)):
        # O método get_vertexes faz as transformações para o triângulo e gera a lista de vértices
        # do triângulo transformado. Separou-se a lista em seis variáveis de modo a obter alfa, beta e gamma.
        x1, y1, x2, y2, x3, y3 = get_vertexes(triangles[i])

        for x in range(WIDTH):
            for y in range(HEIGHT):
                if is_inside((x, y), [x1, y1, x2, y2, x3, y3]):
                    alpha = (-(x - x2) * (y3 - y2) + (y - y2) * (x3 - x2)) / (
                        -(x1 - x2) * (y3 - y2) + (y1 - y2) * (x3 - x2)
                    )
                    beta = (-(x - x3) * (y1 - y3) + (y - y3) * (x1 - x3)) / (
                        -(x2 - x3) * (y1 - y3) + (y2 - y3) * (x1 - x3)
                    )
                    gamma = 1 - alpha - beta

                    if coord:
                        gpu.GPU.set_pixel(x, y, 255, 255, 255)

                    if colorPerVertex:
                        ct = c_triangles[i]

                        r = (
                            alpha * ct[0][0] + beta * ct[1][0] + gamma * ct[2][0]
                        ) * 255
                        g = (
                            alpha * ct[0][1] + beta * ct[1][1] + gamma * ct[2][1]
                        ) * 255
                        b = (
                            alpha * ct[0][2] + beta * ct[1][2] + gamma * ct[2][2]
                        ) * 255

                        gpu.GPU.set_pixel(x, y, r, g, b)

                    if texCoord:
                        t0, t1, t2 = t_triangles[i]

                        u = int(
                            alpha * t0[0] * 199
                            + beta * t1[0] * 199
                            + gamma * t2[0] * 199
                        )
                        v = int(
                            alpha * t0[1] * 199
                            + beta * t1[1] * 199
                            + gamma * t2[1] * 199
                        )

                        gpu.GPU.set_pixel(
                            x, y, image[-v][u][0], image[-v][u][1], image[-v][u][2]
                        )
