import cv2
import numpy as np
from PIL import Image, ImageFilter
from src.core.methods import box_counting, hausdorff, mass_radius, dilation

class FractalManager:
    def __init__(self):
        self.black_boundary = 40 
        
        self.box_start = 5
        self.box_end = 60
        self.box_step = 2

        self.haus_start = 5
        self.haus_end = 50
        self.haus_step = 2

        self.mass_start = 2
        self.mass_end = 100
        self.mass_step = 2
        
        self.dilation_min_size = 4 
        
        self.cd_points = []   
        self.haus_points = [] 
        self.mr_points = []   
        self.dilation_points = [] 
        
        self.image = None

    def load_image(self, image_path):
        try:
            self.image = Image.open(image_path).convert('RGB')
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Помилка завантаження файлу: {e}")
            return False

    # Підготовка для контурів (Box-Counting, Hausdorff, Dilation)
    def _preprocess_for_boundaries(self):
        """
        Використовується детектор меж Canny для отримання тонкого 
        контуру (1 піксель).
        """
        gray_image = np.array(self.image.convert('L'))
        
        # Застосовуання алгоритму Canny (пороги 50 і 150 для чітких меж)
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Інвертація кольорів, якщо алгоритм очікує чорні контури на білому тлі.
        # Або як є (Canny дає білі контури на чорному тлі). 
        # Методи мають автоінверсію, поверенення результату.
        return Image.fromarray(edges)

    # Підготовка для маси (Mass-Radius)
    def _preprocess_for_mass(self):
        """
        Повертання суцільної маси об'єкта, очищеної від шуму.
        """
        gray_image = self.image.convert('L')
        smoothed_image = gray_image.filter(ImageFilter.MedianFilter(size=3))
        img_array = np.array(smoothed_image)
        
        # Жорстка бінаризація суцільної маси
        mask = img_array > self.black_boundary
        clean_img_array = np.where(mask, 255, 0).astype(np.uint8)
        return Image.fromarray(clean_img_array)

    # Виклики методів для обчислення фрактальних розмірностей

    def calculate_grid_dimension(self, image_path):
        if self.load_image(image_path):
            # Box-Counting рахує складність контуру
            clean_image = self._preprocess_for_boundaries()
            k, points = box_counting.calculate_grid_method(
                clean_image, 127, self.box_start, self.box_end, self.box_step
            )
            self.cd_points = points
            return k
        return None
    
    def calculate_hausdorff_dimension(self, image_path):
        if self.load_image(image_path):
            # Гаусдорф рахує складність контуру
            clean_image = self._preprocess_for_boundaries()
            k, points = hausdorff.calculate_hausdorff_method(
                clean_image, 127, self.haus_start, self.haus_end, self.haus_step
            )
            self.haus_points = points
            return k
        return None

    def calculate_dilation_dimension(self, image_path):
        if self.load_image(image_path):
            # Дилатація з контуром щоб уникнути топологічного злиття
            clean_image = self._preprocess_for_boundaries()
            k, points = dilation.calculate_dilation_method(
                clean_image, 127, min_size=self.dilation_min_size
            )
            self.dilation_points = points
            return k
        return None

    def calculate_mass_radius_dimension(self, image_path):
        if self.load_image(image_path):
            # Маса-радіус з суцільною масою щоб уникнути проблеми порожнього ядра
            clean_image = self._preprocess_for_mass()
            k, points = mass_radius.calculate_mass_radius_method(
                clean_image, 127, self.mass_start, self.mass_end, self.mass_step
            )
            self.mr_points = points
            return k
        return None

    def calculate_caliper_dimension(self, path): 
        pass
        
    def calculate_multifractal_with_local_density_function(self): 
        pass