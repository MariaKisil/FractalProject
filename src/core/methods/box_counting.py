import math
import numpy as np
from src.utils import less_square_get_coefficient


def calculate_grid_method(image, black_boundary, start_size, end_size, step):
    """
    Box Counting.
    Важливо: start_size має бути більшим за товщину лінії на зображенні,
    інакше результат буде заниженим.
    """

    # Бінаризація
    img_array = np.array(image)

    # Маска (True = чорний піксель)
    if len(img_array.shape) == 3:  # RGB
        mask = (
            (img_array[:, :, 0] <= black_boundary) &
            (img_array[:, :, 1] <= black_boundary) &
            (img_array[:, :, 2] <= black_boundary)
        )
    else:  # Grayscale
        mask = img_array <= black_boundary

    # Координати чорних пікселів
    # y, x = np.where(mask)
    pixels = np.column_stack(np.where(mask))

    if len(pixels) == 0:
        return 0, []

    points = []

    # Валідація параметрів циклу
    if start_size < 1:
        start_size = 1
    if end_size < start_size:
        end_size = start_size + 1
    if step < 1:
        step = 1

    # Основний цикл
    for box_size in range(start_size, end_size + 1, step):
        # Цілочисельне ділення координат пікселів на розмір сітки дає індекс коробки. (x // size, y // size)

        # Оптимізація: ділимо зразу весь масив координат
        scaled_pixels = pixels // box_size

        # Кількість унікальних рядків (коробок)
        unique_boxes = np.unique(scaled_pixels, axis=0)
        count_n = len(unique_boxes)

        if count_n > 0:
            # X = ln(1/eps) = -ln(eps)
            # Y = ln(N)
            ln_inv_eps = math.log(1.0 / box_size)
            ln_n = math.log(count_n)
            points.append((ln_inv_eps, ln_n))

    # Регресія
    k, b = less_square_get_coefficient(points)

    return k, points