import numpy as np
import math
from src.utils import less_square_get_coefficient

def calculate_mass_radius_method(image, black_boundary, r_start, r_end, step):
    """
    Метод Маса-Радіус (Sandbox Method).
    Центр кіл прив'язується до частини об'єкта.
    """
    # Підготовка
    img_array = np.array(image.convert('L'))
    y_idxs, x_idxs = np.where(img_array <= black_boundary)
    
    if len(x_idxs) == 0:
        return 0, []

    # Знаходження геометричного центру мас
    mean_y = np.mean(y_idxs)
    mean_x = np.mean(x_idxs)

    # Пошук найближчого чорного пікселя до центру мас і фіксація йогояк центру.
    
    # Квадрати відстаней від геометричного центру до всіх чорних точок
    dists_to_mean = (x_idxs - mean_x)**2 + (y_idxs - mean_y)**2
    
    # Знаходження індексу точки з мінімальною відстанню
    nearest_idx = np.argmin(dists_to_mean)
    
    center_y = y_idxs[nearest_idx]
    center_x = x_idxs[nearest_idx]

    # Розрахунок відстаней від нового центру
    distances = np.sqrt((x_idxs - center_x)**2 + (y_idxs - center_y)**2)
    
    results = []

    # Валідація
    if r_start < 1: r_start = 1
    if r_end < r_start: r_end = r_start + 1
    if step < 1: step = 1

    for r in range(r_start, r_end + 1, step):
        mass = np.sum(distances <= r)
        
        if mass > 0:
            ln_r = math.log(r)
            ln_m = math.log(mass)
            results.append((ln_r, ln_m))

    k, b = less_square_get_coefficient(results)
    
    return k, results