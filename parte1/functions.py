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

    # Refazendo o cálculo dos deltas (em caso de diferenças)
    dx, dy = x2 - x1, y2 - y1

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
