import numpy as np
import gpu

from params import WIDTH, HEIGHT, aux_arrays, transform_array
from parte1.functions import is_inside
from parte2.functions import make_screen_array, get_vertexes


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
    print("Entrei IndexedFaceSet!")
    if coord:
        # Criando lista de pontos
        points = []
        for p in range(int(len(coord)/3)):
            points.append(coord[3 * p : 3 * p + 3])

        # Criando lista de triângulos e de vértices
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
                                [1, 1, 1],
                            ]
                        )
                    )

            else:
                vertexes = []

    if colorPerVertex:
        # Criando lista de pontos e de cores
        points = []
        for p in range(int(len(coord)/3)):
            points.append(coord[3 * p : 3 * p + 3])
        
        colors = []
        for c in range(int(len(color)/3)):
            colors.append(color[3 * c : 3 * c + 3])
        
        # Criando lista de triângulos e de cores dos triângulos
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
                        [1, 1, 1],
                    ]
                )
            )

            # Faz as cores dos triângulos
            c0, c1, c2 = colorIndex[2 * i : 2 * i + 3]
            c_triangles.append([colors[c0], colors[c1], colors[c2]])

    if texCoord:
        print(coordIndex)
        print('\n')
        image = gpu.GPU.load_texture(current_texture[0])
        
        # Criando lista de pontos e de texturas
        points = []
        for p in range(int(len(coord)/3)):
            points.append(coord[3 * p : 3 * p + 3])
        
        t_points = []
        for tp in range(int(len(texCoord)/2)):
            t_points.append(texCoord[2 * tp : 2 * tp + 2])

        # Criando lista de triângulos e de texturas dos triângulos
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
                        [1, 1, 1],
                    ]
                )
            )

            # Faz as texturas
            vt0, vt1, vt2 = texCoordIndex[2 * i : 2 * i + 3]
            t_triangles.append([t_points[vt0], t_points[vt1], t_points[vt2]])

    if current_texture:
        image = gpu.GPU.load_texture(current_texture[0])
        
    # Define as matrizes auxiliares utilizadas no processo    
    lookAt_array = aux_arrays[0]                # Matriz lookAt
    perspective_array = aux_arrays[1]           # Matriz perspectiva
    screen_array = make_screen_array() 

    for i in range(len(triangles)):
        triangle = triangles[i]
        
        # Transformações do triângulo
        
        # 1a transformação: das coordenadas do objeto para as do mundo
        t1 = np.matmul(transform_array, triangle)
        
        # 2a transformação: das coordenadas do mundo para as da câmera
        t2 = np.matmul(lookAt_array, t1)

        # 3a transformação: das coordenadas da câmera para perspectiva
        t3 = np.matmul(perspective_array, t2)
        
        # Normalizando t3
        normalized = np.array(np.zeros((4, 3)))
        
        for i in range(3):
            normalized[:, i] = t3[:, i]/t3[-1, i]
            
        # Última transformação: da perspectiva para as coordenadas da tela
        transformed = np.matmul(screen_array, normalized)

        # Não sei porque, mas sem este adder, as coordenadas estão saindo da tela de desenho.
        for i in range(2):
            adder = 200/(i+1)
            transformed[i,:] = [t+adder for t in transformed[i, :]]        
        
        # O método get_vertexes gera a lista de vértices do triângulo transformado
        vtx = get_vertexes(transformed)
        
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if is_inside((x, y), vtx):
                    if coord:
                        gpu.GPU.set_pixel(x, y, 255, 255, 255)

                    if colorPerVertex:
                        ct = c_triangles[i]
                        
                        a_num = ((y - vtx[3]) * (vtx[4] - vtx[2])) - ((x - vtx[2]) * (vtx[5] - vtx[3]))
                        a_den = ((vtx[1] - vtx[3]) * (vtx[4] - vtx[2])) - ((vtx[0] - vtx[2]) * (vtx[5] - vtx[3]))
                        if a_den != 0:
                            alpha = a_num/a_den
                        else:
                            alpha = 0
                        
                        b_num = (y - vtx[5]) * (vtx[0] - vtx[4]) - (x - vtx[4]) * (vtx[1] - vtx[5])
                        b_den = (vtx[3] - vtx[5]) * (vtx[0] - vtx[4]) - (vtx[2] - vtx[4]) * (vtx[1] - vtx[5])
                        if b_den != 0:
                            beta = b_num/b_den
                        else:
                            beta = 0
                            
                        gamma = 1 - alpha - beta

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
                        
                        a_num = ((y - vtx[3]) * (vtx[4] - vtx[2])) - ((x - vtx[2]) * (vtx[5] - vtx[3]))
                        a_den = ((vtx[1] - vtx[3]) * (vtx[4] - vtx[2])) - ((vtx[0] - vtx[2]) * (vtx[5] - vtx[3]))
                        if a_den != 0:
                            alpha = a_num/a_den
                        else:
                            alpha = 0
                        
                        b_num = (y - vtx[5]) * (vtx[0] - vtx[4]) - (x - vtx[4]) * (vtx[1] - vtx[5])
                        b_den = (vtx[3] - vtx[5]) * (vtx[0] - vtx[4]) - (vtx[2] - vtx[4]) * (vtx[1] - vtx[5])
                        if b_den != 0:
                            beta = b_num/b_den
                        else:
                            beta = 0
                            
                        gamma = 1 - alpha - beta

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
