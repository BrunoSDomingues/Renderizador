# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 28 de Agosto de 2020

# Para tratar os parâmetros da linha de comando
import argparse

# Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import x3d

# Janela de visualização baseada no Matplotlib
import interface

# Simula os recursos de uma GPU
import gpu

# imports extras
import numpy as np

# Classe para organizar as diferentes matrizes utilizadas
class Matrix:
    def __init__(self):
        self.matrix = np.identity(4)

# Implementação do Algoritmo de Bresenham disponível em http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python (com modificações pontuais)
def get_line(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    steep = abs(dy) > abs(dx)  # Checa se a linha desenhada é íngreme

    if steep:  # Se a linha for íngreme, inverte-se as coordenadas dos pontos 1 e 2
        x1, y1, x2, y2 = y1, x1, y2, x2

    # O algoritmo usa a condição que x1 < x2, caso não seja, basta trocar os pontos
    swap = False  # Armazena se houve troca de pontos
    if x1 > x2:
        x1, x2, y1, y2 = x2, x1, y2, y1
        swap = True

    dx, dy = x2 - x1, y2 - y1  # Refazendo o cálculo dos deltas (em caso de diferenças)

    # Cálculo do erro
    error = int(dx / 2.2)
    ystep = 1 if y1 < y2 else -1

    # Iterando o caminho da linha e gerando os pontos
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Caso tenha ocorrido troca de pontos, é necessário ajustar a lista
    if swap:
        points.reverse()

    return points


def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """
    r, g, b = [i * 255 for i in color]  # transforma do X3D para o Framebuffer

    for p in range(0, len(point), 2):
        x, y = int(point[p]), int(point[p + 1])
        print(f"Pintando o ponto ({x}, {y}) da cor ({r}, {g}, {b})...")

        gpu.GPU.set_pixel(x, y, r, g, b)


def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """
    r, g, b = [i * 255 for i in color]  # transforma do X3D para o Framebuffer
    x0, y0, x1, y1 = lineSegments[:5]

    print(f"Ponto P0: ({x0}, {y0})")
    print(f"Ponto P1: ({x1}, {y1})")
    print(f"Cor: ({r}, {g}, {b})")

    pontos_bresenham = get_line(int(x0), int(y0), int(x1), int(y1))

    for p in pontos_bresenham:
        x, y = int(p[0]), int(p[1])
        gpu.GPU.set_pixel(x, y, r, g, b)


# Calcula se um ponto está abaixo ou acima da linha que liga P1 a P2
def sinal(x, y, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0

    return True if (x - x0) * dy - (y - y0) * dx >= 0 else False


# Checa se o ponto está no interior do triângulo
def is_inside(point, vertices):
    x0, y0, x1, y1, x2, y2 = vertices[:6]
    x, y = point

    s1 = sinal(x, y, x0, y0, x1, y1)
    s2 = sinal(x, y, x1, y1, x2, y2)
    s3 = sinal(x, y, x2, y2, x0, y0)

    return s1 and s2 and s3


def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """
    r, g, b = [i * 255 for i in color]  # transforma do X3D para o Framebuffer
    x_max, y_max = 30, 20

    for x in range(x_max):
        for y in range(y_max):
            n_super = 4  # quantas divisões o supersampling irá fazer
            frac = 0

            points = [
                (x + 0.25, y + 0.25),
                (x + 0.25, y + 0.75),
                (x + 0.75, y + 0.25),
                (x + 0.75, y + 0.75),
            ]

            for p in points:
                if is_inside(p, vertices):
                    frac += 1 / n_super

            if frac > 0:
                gpu.GPU.set_pixel(
                    x, y, r * frac, g * frac, b * frac
                )  # altera um pixel da imagem


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
    triangles = []

    for p in range(len(point)):
        if p % 9 == 0:
            # Matriz transposta
            transposed = np.array([[point[p], point[p+3], point[p+6]],
                                   [point[p+1], point[p+4], point[p+7]],
                                   [point[p+2], point[p+5], point[p+8]],
                                   [1.0, 1.0, 1.0, 1.0]])
            
            # Multiplicando pelas matrizes de transformação, lookat e perspectiva
            r_triangle = np.matmul(t_matrix.matrix, transposed)
            r_triangle = np.matmul(l_matrix.matrix, r_triangle)
            r_triangle = np.matmul(p_matrix.matrix, r_triangle)

            # Normalização
            for i in range(0, 3):
                if r_triangle[3][i] > 0:
                    r_triangle[:, i] /= r_triangle[3][i]

            # Ajuste para o tamanho da tela
            half_w, half_h = LARGURA/2.0, ALTURA/2.0
            s_matrix = np.array([half_w, 0, 0, half_w],
                                [0, -half_h, 0, half_h],
                                [0, 0, 1.0, 0],
                                [0, 0, 0, 1.0])
            triangles.append(np.matmul(s_matrix, r_triangle))

    # Rasterização da matriz
    for t in triangles:
        triangleSet2D([t[0][0], t[1][0], t[0][1], t[1][1], t[0][2], t[1][2]], color)         


def viewpoint(position, orientation, fieldOfView):
    """ Função usada para renderizar (na verdade coletar os dados) de Viewpoint. """
    # Na função de viewpoint você receberá a posição, orientação e campo de visão da
    # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
    # perspectiva para poder aplicar nos pontos dos objetos geométricos.

    l_matrix.matrix = np.identity(4)    # Redefine a matriz lookat
    o_matrix = np.identity(4)           # Matriz de orientação

    top = NEAR * np.tan(fieldOfView)
    right = top * (LARGURA/ALTURA)

    # Refaz a matriz de perspectiva
    p_matrix.matrix = np.array([[NEAR/right, 0, 0, 0],
                                [0, NEAR/top, 0, 0],
                                [0, 0,-(FAR+NEAR)/(FAR-NEAR), -2*(FAR+NEAR)/(FAR-NEAR)],
                                [0, 0, -1.0, 0]])

    # Matriz de posição
    pos_matrix = np.array([[1.0, 0, 0, -position[0]],
                           [0, 1.0, 0, -position[1]],
                           [0, 0, 1.0, -position[2]],
                           [0, 0, 0, 1.0]])
    
    l_matrix.matrix = np.matmul(o_matrix, pos_matrix)


def transform(translation, scale, rotation):
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função transform será chamada quando se entrar em um nó X3D do tipo Transform
    # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
    # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
    # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
    # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
    # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
    # modelos do mundo em alguma estrutura de pilha.

    t_stack = []    # Pilha temporária
    t_matrix = np.identity(4)   # Matriz temporária, será usada posteriormente para formar a pilha final


    if scale:
        t_stack.append(np.array([[scale[0], 0, 0, 0],
                                 [0, scale[1], 0, 0],
                                 [0, 0, scale[2], 0],
                                 [0, 0, 0, 1]]))

    if translation:
        t_stack.append(np.array([[1.0, 0, 0, translation[0]],
                                 [0, 1.0, 0, translation[1]],
                                 [0, 0, 1.0, translation[2]],
                                 [0, 0, 0, 1.0]]))

    if rotation:
        if rotation[0]:
            t_stack.append(np.array([[1.0,0,0,0],
                                     [0,np.cos(rotation[3]),-np.sin(rotation[3]),0],
                                     [0,np.sin(rotation[3]),np.cos(rotation[3]),0],
                                     [0,0,0,1.0]]))

        elif rotation[1]:
            t_stack.append(np.array([[np.cos(rotation[3]),0,np.sin(rotation[3]),0],
                                     [0,1.0,0,0],
                                     [-np.sin(rotation[3]),0,np.cos(rotation[3]),0],
                                     [0,0,0,1.0]]))
        else:
            t_stack.append(np.array([[np.cos(rotation[3]),-np.sin(rotation[3]),0,0],
                                     [np.sin(rotation[3]),np.cos(rotation[3]),0,0],
                                     [0,0,1.0,0],
                                     [0,0,0,1.0]]))

    while (t_stack):
        t_matrix = np.matmul(t_stack.pop(), t_matrix)

    stack.append(t_matrix)


def _transform():
    """ Função usada para renderizar (na verdade coletar os dados) de Transform. """
    # A função _transform será chamada quando se sair em um nó X3D do tipo Transform do
    # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
    # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
    # pilha implementada.

    while (stack):
        t_matrix.matrix = np.matmul(stack.pop(), t_matrix.matrix)


def triangleStripSet(point, stripCount, color):
    """ Função usada para renderizar TriangleStripSet. """
    # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
    # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
    # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
    # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
    # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
    # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
    # em uma lista chamada stripCount (perceba que é uma lista).

    triangles = []

    for p in range(len(point)):
        if (p % 3 == 0) and (p >= 9) and (p < (len(point)-8)):

            # Matriz transposta
            transposed = np.array([[point[p], point[p+3], point[p+6]],
                                   [point[p+1], point[p+4], point[p+7]],
                                   [point[p+2], point[p+5], point[p+8]],
                                   [1.0, 1.0, 1.0, 1.0]])
            
            # Multiplicando pelas matrizes de transformação, lookat e perspectiva
            r_triangle = np.matmul(t_matrix.matrix, transposed)
            r_triangle = np.matmul(l_matrix.matrix, r_triangle)
            r_triangle = np.matmul(p_matrix.matrix, r_triangle)

            # Normalização
            for i in range(0, 3):
                if r_triangle[3][i] > 0:
                    r_triangle[:, i] /= r_triangle[3][i]

            # Ajuste para o tamanho da tela
            half_w, half_h = LARGURA/2.0, ALTURA/2.0
            s_matrix = np.array([half_w, 0, 0, half_w],
                                [0, -half_h, 0, half_h],
                                [0, 0, 1.0, 0],
                                [0, 0, 0, 1.0])
            triangles.append(np.matmul(s_matrix, r_triangle))
    
    # Rasterização da matriz
    for t in triangles:
        triangleSet2D([t[0][0], t[1][0], t[0][1], t[1][1], t[0][2], t[1][2]], color)  



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

    triangles = []

    for p in range(len(point)):
        if (p % 3 == 0) and (p >= 9) and (p < (len(point)-8)):

            # Matriz transposta
            transposed = np.array([[point[p], point[p+3], point[p+6]],
                                   [point[p+1], point[p+4], point[p+7]],
                                   [point[p+2], point[p+5], point[p+8]],
                                   [1.0, 1.0, 1.0, 1.0]])
            
            # Multiplicando pelas matrizes de transformação, lookat e perspectiva
            r_triangle = np.matmul(t_matrix.matrix, transposed)
            r_triangle = np.matmul(l_matrix.matrix, r_triangle)
            r_triangle = np.matmul(p_matrix.matrix, r_triangle)

            # Normalização
            for i in range(0, 3):
                if r_triangle[3][i] > 0:
                    r_triangle[:, i] /= r_triangle[3][i]

            # Ajuste para o tamanho da tela
            half_w, half_h = LARGURA/2.0, ALTURA/2.0
            s_matrix = np.array([half_w, 0, 0, half_w],
                                [0, -half_h, 0, half_h],
                                [0, 0, 1.0, 0],
                                [0, 0, 0, 1.0])
            triangles.append(np.matmul(s_matrix, r_triangle))
    
    # Rasterização da matriz
    for t in triangles:
        triangleSet2D([t[0][0], t[1][0], t[0][1], t[1][1], t[0][2], t[1][2]], color)  


def box(size, color):
    """ Função usada para renderizar Boxes. """
    # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
    # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
    # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
    # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
    # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
    # encontre os vértices e defina os triângulos.

    points = [[size[0]/2,size[1]/2,size[2]/2],
              [size[0]/2,-size[1]/2,size[2]/2],
              [size[0]/2,-size[1]/2,-size[2]/2],
              [size[0]/2,size[1]/2,-size[2]/2],
              [-size[0]/2,-size[1]/2,-size[2]/2],
              [-size[0]/2,size[1]/2,-size[2]/2],
              [-size[0]/2,size[1]/2,size[2]/2],
              [-size[0]/2,-size[1]/2,size[2]/2]]

    render_triangles = [[points[0],points[1],points[2]],
                        [points[0],points[2],points[3]],
                        [points[2],points[3],points[4]],
                        [points[3],points[4],points[5]],
                        [points[4],points[5],points[6]],
                        [points[4],points[6],points[7]],
                        [points[6],points[7],points[1]],
                        [points[6],points[1],points[0]],
                        [points[0],points[6],points[5]],
                        [points[0],points[3],points[5]],
                        [points[1],points[2],points[4]],
                        [points[1],points[7],points[4]]]

    triangles = []

    for r in render_triangles:
        # Matriz de cada triângulo
        matrix = np.array([[r[0][0],r[1][0],r[2][0]],
                           [r[0][1],r[1][1],r[2][1]],
                           [r[0][2],r[1][2],r[2][2]],
                           [1.0, 1.0, 1.0]]))

        # Multiplicando pelas matrizes de transformação, lookat e perspectiva
        r_triangle = np.matmul(t_matrix.matrix, matrix)
        r_triangle = np.matmul(l_matrix.matrix, r_triangle)
        r_triangle = np.matmul(p_matrix.matrix, r_triangle)

        # Normalização
        for i in range(0, 3):
            if r_triangle[3][i] > 0:
                r_triangle[:, i] /= r_triangle[3][i]

        # Ajuste para o tamanho da tela
        half_w, half_h = LARGURA/2.0, ALTURA/2.0
        s_matrix = np.array([half_w, 0, 0, half_w],
                            [0, -half_h, 0, half_h],
                            [0, 0, 1.0, 0],
                            [0, 0, 0, 1.0])
        triangles.append(np.matmul(s_matrix, r_triangle))
    
    # Rasterização da matriz
    for t in triangles:
        triangleSet2D([t[0][0], t[1][0], t[0][1], t[1][1], t[0][2], t[1][2]], color)

def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex, texCoord, texCoordIndex, current_color, current_texture):
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
    
    # O print abaixo é só para vocês verificarem o funcionamento, deve ser removido.
    print("IndexedFaceSet : ")
    if coord:
        print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex)) # imprime no terminal
    if colorPerVertex:
        print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex)) # imprime no terminal
    if texCoord:
        print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex)) # imprime no terminal
    if(current_texture):
        image = gpu.GPU.load_texture(current_texture[0])
        print("\t Matriz com image = {0}".format(image))


LARGURA = 300
ALTURA = 200
NEAR = 0.5
FAR = 100


if __name__ == "__main__":

    stack = []              # Stack original
    t_matrix = Matrix()     # Matriz de transformação
    l_matrix = Matrix()     # Matriz lookat
    p_matrix = Matrix()     # Matriz perspectiva

    # Valores padrão da aplicação
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo9.x3d"
    image_file = "tela.png"

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)  # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    parser.add_argument(
        "-q", "--quiet", help="não exibe janela de visualização", action="store_true"
    )
    args = parser.parse_args()  # parse the arguments
    if args.input:
        x3d_file = args.input
    if args.output:
        image_file = args.output
    if args.width:
        width = args.width
    if args.height:
        height = args.height

    # Iniciando simulação de GPU
    gpu.GPU(width, height, image_file)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)
    scene.set_resolution(width, height)

    # funções que irão fazer o rendering
    x3d.X3D.render["Polypoint2D"] = polypoint2D
    x3d.X3D.render["Polyline2D"] = polyline2D
    x3d.X3D.render["TriangleSet2D"] = triangleSet2D
    x3d.X3D.render["TriangleSet"] = triangleSet
    x3d.X3D.render["Viewpoint"] = viewpoint
    x3d.X3D.render["Transform"] = transform
    x3d.X3D.render["_Transform"] = _transform
    x3d.X3D.render["TriangleStripSet"] = triangleStripSet
    x3d.X3D.render["IndexedTriangleStripSet"] = indexedTriangleStripSet
    x3d.X3D.render["Box"] = box
    x3d.X3D.render["IndexedFaceSet"] = indexedFaceSet

    # Se no modo silencioso não configurar janela de visualização
    if not args.quiet:
        window = interface.Interface(width, height)
        scene.set_preview(window)

    scene.parse()  # faz o traversal no grafo de cena

    # Se no modo silencioso salvar imagem e não mostrar janela de visualização
    if args.quiet:
        gpu.GPU.save_image()  # Salva imagem em arquivo
    else:
        window.image_saver = gpu.GPU.save_image  # pasa a função para salvar imagens
        window.preview(gpu.GPU._frame_buffer)  # mostra janela de visualização
