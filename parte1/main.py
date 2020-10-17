import gpu

from params import WIDTH, HEIGHT
from .functions import get_line, is_inside


def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """

    r, g, b = [i * 255 for i in color]  # transforma do X3D para o Framebuffer
    int_point = [int(p) for p in point]

    for p in range(0, len(int_point), 2):
        x, y = int_point[p], int_point[p + 1]
        gpu.GPU.set_pixel(x, y, r, g, b)


def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """

    r, g, b = [i * 255 for i in color]  # transforma do X3D para o Framebuffer
    x0, y0, x1, y1 = lineSegments[:5]

    pontos_bresenham = [int(pb) for pb in get_line(int(x0), int(y0), int(x1), int(y1))]

    for p in pontos_bresenham:
        x, y = p[0], p[1]
        gpu.GPU.set_pixel(x, y, r, g, b)


def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """
    r, g, b = [i * 255 for i in color]  # transforma do X3D para o Framebuffer

    for x in range(WIDTH):
        for y in range(HEIGHT):
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
                gpu.GPU.set_pixel(x, y, r * frac, g * frac, b * frac)
