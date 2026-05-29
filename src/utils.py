import math


def less_square_get_coefficient(points):
    """
    Апроксимація методом найменших квадратів (Normal Equations).
    
    Повертає:
    k - нахил прямої (Фрактальна розмірність)
    b - зсув (intercept)
    """

    if not points or len(points) < 2:
        return 0, 0

    # Підготовка даних
    # X = ln(1/size), Y = ln(N)
    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]
    N = len(points)

    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_xx = sum(x * x for x in x_vals)
    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
    
    # Визначальник матриці
    # Формула для матриці 2x2: det = ad - bc
    denominator = (N * sum_xx - sum_x * sum_x)
    
    if denominator == 0:
        return 0, 0

    # Розрахунок коефіцієнтів за методом Крамера
    # k (slope) = (N * sum_xy - sum_x * sum_y) / det
    # b (intercept) = (sum_y * sum_xx - sum_x * sum_xy) / det
    k = (N * sum_xy - sum_x * sum_y) / denominator
    b = (sum_y * sum_xx - sum_x * sum_xy) / denominator
    
    return k, b
