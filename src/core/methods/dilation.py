import numpy as np
import math
from PIL import Image
from scipy.ndimage import binary_dilation
from src.utils import less_square_get_coefficient

def calculate_dilation_method(image, black_boundary=128, **kwargs):
    """
    Класичний спосіб дилатації пікселів.
    З автоінверсією фону та математичною адаптацією.
    """
    current_image = image.convert('L')
    img_arr = np.array(current_image)
    
    # Детект фону: перевірка кутів зображення
    corners = [img_arr[0,0], img_arr[0,-1], img_arr[-1,0], img_arr[-1,-1]]
    bg_color = np.mean(corners)
    
    if bg_color < 127:
        # Темний фон -> пошук світлого фракталу
        fractal_mask = img_arr > black_boundary
    else:
        # Світлий фон -> пошук темного фракталу
        fractal_mask = img_arr <= black_boundary
    
    results = []
    max_radius = 30
    step = 2
    
    # Ітеративна дилатація
    for r in range(1, max_radius + 1, step):
        dilated_mask = binary_dilation(fractal_mask, iterations=r)
        area = np.sum(dilated_mask)
        
        if area > 0:
            ln_r = math.log(r)
            ln_a = math.log(area)
            
            # Математична адаптація 
            # Перерахунок площі A  в еквівалентну кількість структурних блоків: Y = 2*ln(r) - ln(A)
            transformed_y = 2 * ln_r - ln_a
            
            results.append((ln_r, transformed_y))
            
    # Обчислення коефіцієнта
    k, b = less_square_get_coefficient(results)
    
    # Повернення k (координати трансформовані, k = D)
    return k, results