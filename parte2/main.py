import gpu
import math as m
import numpy as np

from parte1.main import triangleSet2D
from params import aux_arrays, transform_array, stack
from .functions import (
    make_triangle_array,
    make_screen_array,
    get_vertexes,
    make_triangle_strips_array,
    get_box_faces,
)


def triangleSet(point, color):
    """ Função usada para renderizar TriangleSet. """
    # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
    # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
    # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
    # assim por diante.
    # No TriangleSet os triângulos são informados individualmente, assim os três
    # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
    # triângulo, e assim por diante.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    # print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos

    # Monta a lista de triângulos
    triangles = []

    for i in range(int(len(point)/9)):
        # Cria um triângulo e coloca na lista
        triangles.append(make_triangle_array(point, i))
    
    # Define as matrizes auxiliares utilizadas no processo    
    lookAt_array = aux_arrays[0]                # Matriz lookAt
    perspective_array = aux_arrays[1]           # Matriz perspectiva
    screen_array = make_screen_array()          # Matriz das coordenadas da tela
    
    # Iterando pela lista
    for triangle in triangles:
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
        vertexes = get_vertexes(transformed)
        
        # Por fim, usar o triangleSet2D
        triangleSet2D(vertexes, color)


def viewpoint(position, orientation, fieldOfView):
    """ Função usada para renderizar (na verdade coletar os dados) de Viewpoint. """
    # Na função de viewpoint você receberá a posição, orientação e campo de visão da
    # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
    # perspectiva para poder aplicar nos pontos dos objetos geométricos.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    # print("Viewpoint : position = {0}, orientation = {1}, fieldOfView = {2}".format(position, orientation, fieldOfView)) # imprime no terminal

    # Chama a lista de arrays auxiliares pois ela será editada
    global aux_arrays

    # Matriz de orientação
    ori_array = np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
    )

    # Matriz de posição
    pos_array = np.array(
        [
            [1, 0, 0, -position[0]],
            [0, 1, 0, -position[1]],
            [0, 0, 1, -position[2]],
            [0, 0, 0, 1],
        ]
    )

    # Matriz lookAt
    lookAt_array = np.matmul(ori_array, pos_array)

    # Matriz de projeção perspectiva
    perspective_array = np.array(
        [[0.5, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1.01, -1.005], [0, 0, -1, 0]]
    )

    # Adiciona as matrizes na lista aux_arrays
    aux_arrays.append(lookAt_array)
    aux_arrays.append(perspective_array)


def transform(translation, scale, rotation):
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função transform será chamada quando se entrar em um nó X3D do tipo Transform
    # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
    # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
    # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
    # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
    # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
    # modelos do mundo em alguma estrutura de pilha.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    # print("Transform : ", end = '')

    # Chama a pilha e a matriz de transformação
    global stack
    global transform_array

    if translation:
        # Adiciona-se a matriz de transformação na pilha pois ela irá sofrer alterações
        stack.append(transform_array)

        # Matriz de translação
        translation_array = np.array(
            [
                [1, 0, 0, translation[0]],
                [0, 1, 0, translation[1]],
                [0, 0, 1, translation[2]],
                [0, 0, 0, 1],
            ]
        )

        # Novo valor da matriz de transformação
        transform_array = np.matmul(translation_array, transform_array)

    if scale:
        # Adiciona-se a matriz de transformação na pilha pois ela irá sofrer alterações
        stack.append(transform_array)

        # Matriz de escala
        scale_array = np.array(
            [
                [scale[0], 0, 0, 0],
                [0, scale[1], 0, 0],
                [0, 0, scale[2], 0],
                [0, 0, 0, 1],
            ]
        )

        # Novo valor da matriz de transformação
        transform_array = np.matmul(scale_array, transform_array)

    if rotation:
        # rotation[3] é o ângulo de rotação em radianos
        if rotation[0]:
            # Adiciona-se a matriz de transformação na pilha pois ela irá sofrer alterações
            stack.append(transform_array)

            # Matriz de rotação no eixo x
            rotation_array = np.array(
                [
                    [1, 0, 0, 0],
                    [0, m.cos(rotation[3]), -m.sin(rotation[3]), 0],
                    [0, m.sin(rotation[3]), m.cos(rotation[3]), 0],
                    [0, 0, 0, 1],
                ]
            )

            # Novo valor da matriz de transformação
            transform_array = np.matmul(rotation_array, transform_array)

        elif rotation[1]:
            # Adiciona-se a 1.0matriz de transformação na pilha pois ela irá sofrer alterações
            stack.append(transform_array)

            # Matriz de rotação no eixo y
            rotation_array = np.array(
                [
                    [m.cos(rotation[3]), 0, m.sin(rotation[3]), 0],
                    [0, 1, 0, 0],
                    [-m.sin(rotation[3]), 0, m.cos(rotation[3]), 0],
                    [0, 0, 0, 1],
                ]
            )

            # Novo valor da matriz de transformação
            transform_array = np.matmul(rotation_array, transform_array)

        elif rotation[2]:
            # Adiciona-se a matriz de transformação na pilha pois ela irá sofrer alterações
            stack.append(transform_array)

            # Matriz de rotação no eixo z
            rotation_array = np.array(
                [
                    [m.cos(rotation[3]), -m.sin(rotation[3]), 0, 0],
                    [m.sin(rotation[3]), m.cos(rotation[3]), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ]
            )

            # Novo valor da matriz de transformação
            transform_array = np.matmul(rotation_array, transform_array)


def _transform():
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função _transform será chamada quando se sair em um nó X3D do tipo Transform do
    # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
    # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
    # pilha implementada.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    # print("Saindo de Transform")

    # Chama a pilha e a matriz de transformação
    global stack
    global transform_array

    # transform_array recebe o valor da última matriz inserida na pilha
    transform_array = stack[-1]
    
    # Remove a última matriz que foi inserida na pilha
    del stack[-1]
    

def triangleStripSet(point, stripCount, color):
    """ Função usada para renderizar TriangleStripSet. """
    # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
    # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
    # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
    # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
    # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
    # em uma lista chamada stripCount (perceba que é uma lista).
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    # print("TriangleStripSet : pontos = {0} ".format(point), end = '') # imprime no terminal pontos
    # for i, strip in enumerate(stripCount):
    #    print("strip[{0}] = {1} ".format(i, strip), end = '') # imprime no terminal

    # Chama a matriz de transformação e a lista de arrays auxiliares (para obter matriz lookAt e matriz perspectiva)
    global transform_array, aux_arrays
    
    # Monta a lista com os arrays das tiras dos triângulos
    triangle_strips = []
    
    for i in range(int(stripCount[0] - 2)):
        triangle_strips.append(make_triangle_strips_array(point, i))

    # Define as matrizes auxiliares utilizadas no processo    
    lookAt_array, perspective_array = aux_arrays[0], aux_arrays[1]
    screen_array = make_screen_array()
    
    # Iterando pela lista
    for strip in triangle_strips:
        # Transformações da tira
        
        # 1a transformação: das coordenadas do objeto para as do mundo
        t1 = np.matmul(transform_array, strip)

        # 2a transformação: das coordenadas do mundo para as da câmera
        t2 = np.matmul(lookAt_array, t1)

        # 3a transformação: das coordenadas da câmera para perspectiva
        t3 = np.matmul(perspective_array, t2)

        # Normalizando t3
        normalized = np.zeros((4, 3))
        
        for i in range(3):
            normalized[:, i] = t3[:, i]/t3[-1, i]

        # Última transformação: da perspectiva para as coordenadas da tela
        transformed = np.matmul(screen_array, normalized)
        
        # Não sei porque, mas sem este adder, as coordenadas estão saindo da tela de desenho.
        for i in range(2):
            adder = 200/(i+1)
            transformed[i,:] = [t+adder for t in transformed[i, :]]      
        
        # O método get_vertexes gera a lista de vértices da tira transformada
        triangleSet2D(get_vertexes(transformed), color)

def indexedTriangleStripSet(point, index, color):
    """ Função usada para renderizar IndexedTriangleStripSet. """
    # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
    # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
    # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
    # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
    # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
    # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
    # como conectar os vértices é informada em index, o valor -1 indica que a lista
    # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
    # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
    # depois 2, 3 e 4, e assim por diante.
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    # print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index)) # imprime no terminal pontos

    # Chama a matriz de transformação e a lista de arrays auxiliares (para obter matriz lookAt e matriz perspectiva)
    global transform_array, aux_arrays

    # Monta a lista com os arrays das tiras indexadas dos triângulos
    indexed_strips = []
    
    for i in range(int(max(index) - 1)):
        indexed_strips.append(make_triangle_strips_array(point, i))

    # Define as matrizes auxiliares utilizadas no processo    
    lookAt_array, perspective_array = aux_arrays[0], aux_arrays[1]
    screen_array = make_screen_array()
    
    # Iterando pela lista
    for indexed in indexed_strips:
        # Transformações da tira indexada
        
        # 1a transformação: das coordenadas do objeto para as do mundo
        t1 = np.matmul(transform_array, indexed)

        # 2a transformação: das coordenadas do mundo para as da câmera
        t2 = np.matmul(lookAt_array, t1)

        # 3a transformação: das coordenadas da câmera para perspectiva
        t3 = np.matmul(perspective_array, t2)

        # Normalizando t3
        normalized = np.zeros((4, 3))
        
        for i in range(3):
            normalized[:, i] = t3[:, i]/t3[-1, i]

        # Última transformação: da perspectiva para as coordenadas da tela
        transformed = np.matmul(screen_array, normalized)
        
        # Não sei porque, mas sem este adder, as coordenadas estão saindo da tela de desenho.
        for i in range(2):
            adder = 200/(i+1)
            transformed[i,:] = [t+adder for t in transformed[i, :]]    
        
        # O método get_vertexes gera a lista de vértices da tira indexada transformada
        triangleSet2D(get_vertexes(transformed), color)


def box(size, color):
    """ Função usada para renderizar Boxes. """
    # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
    # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
    # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
    # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
    # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
    # encontre os vértices e defina os triângulos.

    # Iterando por cada face
    for face in get_box_faces(size, [0, 0, 0]):
        points = []
        # Iterando por vértice da face
        for vertexes in face:
            # Iterando por coordenadas do vértice
            for coord in vertexes:
                points.append(coord)

        triangleStripSet(points, [4], color)
