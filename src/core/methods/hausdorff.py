import numpy as np
import math
from src.utils import less_square_get_coefficient

def calculate_hausdorff_method(image, black_boundary, r_start, r_end, step):
    """
    Розмірність Гаусдорфа.
    Використовує матричні маски для миттєвого розрахунку складних фракталів.
    """
    # Конвертація зображення в булеву матрицю (True = чорний піксель)
    img_array = np.array(image.convert('L'))
    
    # Створення сітки: True там, де є об'єкт
    grid = img_array <= black_boundary
    
    # Якщо зображення пусте
    if not np.any(grid):
        return 0, []

    h, w = grid.shape
    results = []

    # Валідація
    if r_start < 1: r_start = 1
    if r_end < r_start: r_end = r_start + 1
    if step < 1: step = 1

    # Основний цикл зміни радіуса
    for r in range(r_start, r_end + 1, step):
        # Копіюємо сітку
        temp_grid = grid.copy()
        n_circles = 0
        
        # Створення шаблону кола (маски) один раз для поточного радіуса
        y_idx, x_idx = np.ogrid[-r:r+1, -r:r+1]
        circle_mask = x_idx**2 + y_idx**2 <= r**2
        
        # Жадібний алгоритм: Поки на сітці лишилися чорні пікселі
        while np.any(temp_grid):
            n_circles += 1
            
            # Знаходимо координати першого чорного пікселя
            flat_idx = np.argmax(temp_grid)
            cy, cx = np.unravel_index(flat_idx, (h, w))
            
            # Визначення координат квадрата для вирізання (враховуючи межі зображення)
            y_start = max(0, cy - r)
            y_end = min(h, cy + r + 1)
            x_start = max(0, cx - r)
            x_end = min(w, cx + r + 1)
            
            # Визначення, яку частину маски кола застосувати (якщо біля краю)
            mask_y_start = r - (cy - y_start)
            mask_y_end = mask_y_start + (y_end - y_start)
            mask_x_start = r - (cx - x_start)
            mask_x_end = mask_x_start + (x_end - x_start)
            
            # Видаляємо пікселі, що потрапили під маску
            # Grid and (not Circle)
            temp_grid[y_start:y_end, x_start:x_end] &= ~circle_mask[mask_y_start:mask_y_end, mask_x_start:mask_x_end]

        if n_circles > 0:
            # X = ln(1/r), Y = ln(N)
            ln_inv_r = math.log(1.0 / r)
            ln_n = math.log(n_circles)
            results.append((ln_inv_r, ln_n))

    # Регресія
    k, b = less_square_get_coefficient(results)
    
    return k, results