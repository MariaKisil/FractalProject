import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import numpy as np
from src.core.fractal_manager import FractalManager
import src.ui.plotter as plotter

class FractalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Фрактальний аналіз МРТ")
        self.root.geometry("1100x950")
        
        self.fractal_manager = FractalManager()
        self.image_path = None
        self.image_tk = None

        # Налаштування шляху до бази даних
        self.dataset_path = os.path.join(os.getcwd(), 'data', 'kaggle_mri')
        if not os.path.exists(self.dataset_path):
            self.dataset_path = os.getcwd()

        # Кольори
        self.btn_stat_color = "#E1BEE7"  # Статистика
        self.btn_load_color = "#E3F2FD"  # Завантаження та метод
        self.btn_calc_color = "#B0BEC5"  # Папки та розрахунки
        self.btn_default_color = "#f0f0f0" 
        self.text_color = "black"

        self.create_widgets()

    def create_widgets(self):
        # Ліва панель (Параметри)
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side="left", fill="y", expand=False)

        # Права панель (Зображення)
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="right", fill="both", expand=True)

        self.image_label = tk.Label(right_frame, bg="#e0e0e0")
        self.image_label.pack(fill="both", expand=True)

        # Статистичний аналіз
        tk.Button(left_frame, text="Статистичний аналіз", 
                  command=self.run_statistical_analysis, height=2, 
                  bg=self.btn_stat_color, font=("Arial", 10, "bold")).pack(pady=(0, 15), fill="x")

        # Завантаження зображення та налаштування параметрів
        load_frame = tk.LabelFrame(left_frame, text="Завантаження", font=("Arial", 9, "bold"))
        load_frame.pack(pady=(0, 10), fill="x")

        tk.Button(load_frame, text="Вибрати зображення", command=self.load_any_image, height=2, bg=self.btn_load_color).pack(pady=5, padx=5, fill="x")
        tk.Button(load_frame, text="Вибрати МРТ з бази", command=self.load_database_image, height=2, bg=self.btn_load_color).pack(pady=5, padx=5, fill="x")

        # Метод підрахунку квадратів (Box-Counting)
        grid_panel = tk.LabelFrame(left_frame, text="1. Метод підрахунку квадратів", font=("Arial", 9, "bold"))
        grid_panel.pack(pady=5, fill="both", expand=True, ipady=2)

        tk.Label(grid_panel, text="Поріг бінаризації:").pack(anchor="w", padx=5)
        self.threshold_entry = tk.Entry(grid_panel); self.threshold_entry.pack(fill="x", padx=5)
        self.threshold_entry.insert(0, "40") # Дефолт 40 для МРТ

        row_g = tk.Frame(grid_panel)
        row_g.pack(fill="x", padx=5, pady=5)
        tk.Label(row_g, text="Start:").pack(side="left")
        self.start_size_entry = tk.Entry(row_g, width=5); self.start_size_entry.insert(0, "5"); self.start_size_entry.pack(side="left", padx=2)
        tk.Label(row_g, text="End:").pack(side="left")
        self.end_size_entry = tk.Entry(row_g, width=5); self.end_size_entry.insert(0, "60"); self.end_size_entry.pack(side="left", padx=2)
        tk.Label(row_g, text="Step:").pack(side="left")
        self.step_entry = tk.Entry(row_g, width=5); self.step_entry.insert(0, "2"); self.step_entry.pack(side="left", padx=2)

        tk.Button(grid_panel, text="Показати ч/б", command=self.apply_threshold, bg=self.btn_default_color).pack(pady=2, fill="x", padx=5)
        tk.Button(grid_panel, text="Розрахувати", command=self.calculate_grid_action, bg=self.btn_calc_color).pack(pady=5, fill="x", padx=5)
        self.grid_result_label = tk.Label(grid_panel, text="D = ...", fg=self.text_color, font=("Arial", 10, "bold"))
        self.grid_result_label.pack(side="bottom", pady=5)

        # Розмірність Гаусдорфа (Covering)
        haus_panel = tk.LabelFrame(left_frame, text="2. Розмірність Гаусдорфа", font=("Arial", 9, "bold"))
        haus_panel.pack(pady=5, fill="both", expand=True, ipady=2)

        row_h = tk.Frame(haus_panel)
        row_h.pack(fill="x", padx=5, pady=5)
        tk.Label(row_h, text="R Start:").pack(side="left")
        self.haus_start_entry = tk.Entry(row_h, width=5); self.haus_start_entry.insert(0, "5"); self.haus_start_entry.pack(side="left", padx=2)
        tk.Label(row_h, text="R End:").pack(side="left")
        self.haus_end_entry = tk.Entry(row_h, width=5); self.haus_end_entry.insert(0, "50"); self.haus_end_entry.pack(side="left", padx=2)
        tk.Label(row_h, text="Step:").pack(side="left")
        self.haus_step_entry = tk.Entry(row_h, width=5); self.haus_step_entry.insert(0, "2"); self.haus_step_entry.pack(side="left", padx=2)

        tk.Button(haus_panel, text="Розрахувати", command=self.calculate_hausdorff_action, bg=self.btn_calc_color).pack(pady=5, fill="x", padx=5)
        self.haus_result_label = tk.Label(haus_panel, text="D = ...", fg=self.text_color, font=("Arial", 10, "bold"))
        self.haus_result_label.pack(side="bottom", pady=5)

        # Метод Маса-Радіус (Sandbox)
        mass_panel = tk.LabelFrame(left_frame, text="3. Метод Маса-Радіус", font=("Arial", 9, "bold"))
        mass_panel.pack(pady=5, fill="both", expand=True, ipady=2)

        row_m = tk.Frame(mass_panel)
        row_m.pack(fill="x", padx=5, pady=5)
        tk.Label(row_m, text="R Start:").pack(side="left")
        self.mass_start_entry = tk.Entry(row_m, width=5); self.mass_start_entry.insert(0, "2"); self.mass_start_entry.pack(side="left", padx=2)
        tk.Label(row_m, text="R Max:").pack(side="left")
        self.mass_end_entry = tk.Entry(row_m, width=5); self.mass_end_entry.insert(0, "100"); self.mass_end_entry.pack(side="left", padx=2)
        tk.Label(row_m, text="Step:").pack(side="left")
        self.mass_step_entry = tk.Entry(row_m, width=5); self.mass_step_entry.insert(0, "2"); self.mass_step_entry.pack(side="left", padx=2)

        tk.Button(mass_panel, text="Розрахувати", command=self.calculate_mass_radius_action, bg=self.btn_calc_color).pack(pady=5, fill="x", padx=5)
        self.mass_result_label = tk.Label(mass_panel, text="D = ...", fg=self.text_color, font=("Arial", 10, "bold"))
        self.mass_result_label.pack(side="bottom", pady=5)

        # Метод дилатації пікселів (Dilation)

        dilation_panel = tk.LabelFrame(left_frame, text="4. Спосіб дилатації пікселів", font=("Arial", 9, "bold"))
        dilation_panel.pack(pady=5, fill="both", expand=True, ipady=2)

        row_d = tk.Frame(dilation_panel)
        row_d.pack(fill="x", padx=5, pady=5)
        
        tk.Label(row_d, text="Min Розмір (px):").pack(side="left")
        self.dilation_min_entry = tk.Entry(row_d, width=5)
        self.dilation_min_entry.insert(0, "4") 
        self.dilation_min_entry.pack(side="left", padx=2)

        tk.Button(dilation_panel, text="Розрахувати", command=self.calculate_dilation_action, bg=self.btn_calc_color).pack(pady=5, fill="x", padx=5)
        self.dilation_result_label = tk.Label(dilation_panel, text="D = ...", fg=self.text_color, font=("Arial", 10, "bold"))
        self.dilation_result_label.pack(side="bottom", pady=5)


    def run_statistical_analysis(self):
        """Статистичний аналіз"""
        
        # Вибір методу (один раз для всього дослідження)
        method_dict = self._ask_method_dialog()
        if not method_dict: return
        method_id = method_dict['id']
        method_name = method_dict['name']

        # База БЕЗ дефекту
        folder_healthy = self._ask_folder_dialog("Оберіть базу даних без дефекту", "Вибрати папку без дефекту")
        if not folder_healthy: return
        
        # Обробка бази без дефекту
        results_healthy = self._process_batch(folder_healthy, method_id, "бази без дефекту")
        if not results_healthy: return

        # База З дефектом
        folder_defect = self._ask_folder_dialog("Оберіть базу даних з дефектом", "Вибрати папку з дефектом")
        if not folder_defect: return
        
        # Обробка бази з дефектом
        results_defect = self._process_batch(folder_defect, method_id, "бази з дефектом")
        if not results_defect: return

        # Вивід усіх результатів
        self._show_results_table("Результати: База без дефекту", results_healthy)
        self._show_results_table("Результати: База з дефектом", results_defect)
        self._show_summary(results_healthy, results_defect, method_name)


    def _ask_method_dialog(self):
        """Вікно вибору методу обчислення """
        dialog = tk.Toplevel(self.root)
        dialog.title("Крок 1: Вибір алгоритму")
        dialog.geometry("380x280")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.config(bg="white")

        tk.Label(dialog, text="Оберіть метод для підрахунку розмірності:", font=("Arial", 11, "bold"), bg="white").pack(pady=15)

        selected_method = tk.StringVar(value="grid")
        methods = [
            ("Метод підрахунку квадратів (Box Counting)", "grid"),
            ("Розмірність Гаусдорфа (Covering)", "hausdorff"),
            ("Метод Маса-Радіус (Sandbox)", "mass_radius"),
            ("Спосіб дилатації пікселів (Dilation)", "dilation")
        ]

        for text, val in methods:
            tk.Radiobutton(dialog, text=text, variable=selected_method, value=val, font=("Arial", 10), bg="white").pack(anchor="w", padx=30, pady=2)

        result_dict = {}

        def on_ok():
            result_dict['id'] = selected_method.get()
            result_dict['name'] = dict((v, k) for k, v in methods)[result_dict['id']]
            dialog.destroy()

        tk.Button(dialog, text="Обрати метод", command=on_ok, bg=self.btn_load_color, font=("Arial", 10, "bold"), width=20, height=2).pack(pady=20)
        
        self.root.wait_window(dialog)
        return result_dict if result_dict else None


    def _ask_folder_dialog(self, title_text, btn_text):
        """Вікно вибору папки """
        dialog = tk.Toplevel(self.root)
        dialog.title("Вибір бази даних")
        dialog.geometry("350x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.config(bg="white")

        tk.Label(dialog, text=title_text, font=("Arial", 12, "bold"), bg="white").pack(pady=20)

        folder_path = []

        def choose_folder():
            path = filedialog.askdirectory(title=title_text, initialdir=self.dataset_path)
            if path:
                folder_path.append(path)
                dialog.destroy()

        tk.Button(dialog, text=f"{btn_text}", command=choose_folder, bg=self.btn_calc_color, font=("Arial", 10, "bold"), width=25, height=2).pack()
        
        self.root.wait_window(dialog)
        return folder_path[0] if folder_path else None


    def _process_batch(self, folder_path, method_id, db_name):
        """Обробка всіх файлів в папці обраним методом (Вікно очікування)"""
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tif')
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_exts)]
        
        if not files:
            messagebox.showwarning("Увага", f"У папці не знайдено зображень!\n{folder_path}")
            return None

        self._sync_params_from_ui()

        wait_win = tk.Toplevel(self.root)
        wait_win.title("Обробка...")
        wait_win.geometry("450x150")
        wait_win.transient(self.root)
        wait_win.config(bg="white")
        
        tk.Label(wait_win, text=f"Виконується обчислення розмірності для\n{db_name}...", font=("Arial", 11, "bold"), bg="white").pack(pady=15)
        progress_lbl = tk.Label(wait_win, text="Ініціалізація...", font=("Arial", 10), bg="white")
        progress_lbl.pack()
        
        wait_win.update()

        results = []
        total = len(files)

        for i, filename in enumerate(files, 1):
            progress_lbl.config(text=f"Обробка файлу ({i}/{total}): {filename}")
            wait_win.update()

            full_path = os.path.join(folder_path, filename)
            
            try:
                if method_id == "grid":
                    d = self.fractal_manager.calculate_grid_dimension(full_path)
                elif method_id == "hausdorff":
                    d = self.fractal_manager.calculate_hausdorff_dimension(full_path)
                elif method_id == "mass_radius":
                    d = self.fractal_manager.calculate_mass_radius_dimension(full_path)
                elif method_id == "dilation":
                    d = self.fractal_manager.calculate_dilation_dimension(full_path)
                
                if d is not None:
                    results.append((filename, d))
                else:
                    results.append((filename, 0.0))
            except Exception as e:
                print(f"Помилка обробки {filename}: {e}")
                results.append((filename, 0.0))

        wait_win.destroy()
        return results


    def _sync_params_from_ui(self):
        """Зчитування поточних параметрів з полів вводу"""
        try:
            self.fractal_manager.black_boundary = int(self.threshold_entry.get())
            self.fractal_manager.box_start = int(self.start_size_entry.get())
            self.fractal_manager.box_end = int(self.end_size_entry.get())
            self.fractal_manager.box_step = int(self.step_entry.get())
            self.fractal_manager.haus_start = int(self.haus_start_entry.get())
            self.fractal_manager.haus_end = int(self.haus_end_entry.get())
            self.fractal_manager.haus_step = int(self.haus_step_entry.get())
            self.fractal_manager.mass_start = int(self.mass_start_entry.get())
            self.fractal_manager.mass_end = int(self.mass_end_entry.get())
            self.fractal_manager.mass_step = int(self.mass_step_entry.get())
            self.fractal_manager.dilation_min_size = int(self.dilation_min_entry.get())
        except ValueError:
            pass


    def _show_results_table(self, title, results_list):
        """Відображення таблиці з результатами для однієї бази"""
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("450x400")

        columns = ("file", "dimension")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        tree.heading("file", text="Назва файлу")
        tree.heading("dimension", text="Розмірність (D)")
        
        tree.column("file", width=250, anchor="w")
        tree.column("dimension", width=150, anchor="center")

        for filename, d in results_list:
            d_str = f"{d:.5f}" if d > 0 else "Помилка"
            tree.insert("", tk.END, values=(filename, d_str))

        scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)


    def _show_summary(self, res_healthy, res_defect, method_name):
        """Відображення вікна зі статистикою та аналізом точності методу"""
        win = tk.Toplevel(self.root)
        win.title("Загальна статистика та Аналіз")
        win.geometry("650x550")
        win.config(bg="white")

        valid_healthy = [d for _, d in res_healthy if d > 0]
        valid_defect = [d for _, d in res_defect if d > 0]

        if not valid_healthy or not valid_defect:
            tk.Label(win, text="Недостатньо даних для статистики.", font=("Arial", 12), bg="white").pack(pady=20)
            return

        mean_h = np.mean(valid_healthy)
        mean_d = np.mean(valid_defect)

        # Визначення оптимального порогу (середина між двома середніми)
        threshold = (mean_h + mean_d) / 2

        # Визначення правила: Зазвичай здорові тканини мають більшу розмірність, ніж пухлини
        if mean_h > mean_d:
            rule_text = f"D >= {threshold:.4f} (Здорові)  |  D < {threshold:.4f} (З дефектом)"
            correct_h = sum(1 for d in valid_healthy if d >= threshold)
            correct_d = sum(1 for d in valid_defect if d < threshold)
        else:
            rule_text = f"D < {threshold:.4f} (Здорові)  |  D >= {threshold:.4f} (З дефектом)"
            correct_h = sum(1 for d in valid_healthy if d < threshold)
            correct_d = sum(1 for d in valid_defect if d >= threshold)

        total_h = len(valid_healthy)
        total_d = len(valid_defect)
        accuracy = ((correct_h + correct_d) / (total_h + total_d)) * 100

        # Інтерфейс виводу статистики
        
        tk.Label(win, text="Звіт про класифікацію МРТ", font=("Arial", 15, "bold"), bg="white", fg="#2C3E50").pack(pady=(15, 5))
        tk.Label(win, text=f"Використаний алгоритм: {method_name}", font=("Arial", 11, "italic"), bg="white").pack(pady=(0, 10))
        
        # Загальні дані
        frame_means = tk.LabelFrame(win, text="1. Середні показники фрактальної розмірності (D)", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        frame_means.pack(fill="x", padx=20, pady=5)
        
        tk.Label(frame_means, text=f"• База без дефекту (Здорові). Проскановано: {total_h}.  D середня = {mean_h:.5f}", font=("Arial", 11), bg="white").pack(anchor="w")
        tk.Label(frame_means, text=f"• База з дефектом (Пухлини). Проскановано: {total_d}.  D середня = {mean_d:.5f}", font=("Arial", 11), bg="white").pack(anchor="w")

        # Визначений критерій
        frame_rule = tk.LabelFrame(win, text="2. Автоматично визначений роздільний критерій", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        frame_rule.pack(fill="x", padx=20, pady=5)
        
        tk.Label(frame_rule, text=f"Оптимальний поріг розділення: D = {threshold:.4f}", font=("Arial", 11, "bold"), fg="#D35400", bg="white").pack(anchor="w")
        tk.Label(frame_rule, text=f"Сформоване правило: {rule_text}", font=("Arial", 10, "italic"), bg="white").pack(anchor="w", pady=(5,0))

        # Результати розпізнавання
        frame_results = tk.LabelFrame(win, text="3. Ефективність методу за цим критерієм", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        frame_results.pack(fill="x", padx=20, pady=5)
        
        tk.Label(frame_results, text=f"• Зображень без дефекту правильно класифіковано: {correct_h} з {total_h}", font=("Arial", 11), bg="white").pack(anchor="w")
        tk.Label(frame_results, text=f"• Зображень з дефектом правильно класифіковано: {correct_d} з {total_d}", font=("Arial", 11), bg="white").pack(anchor="w")
        
        # Точність
        acc_color = "#27AE60" if accuracy > 75 else "#C0392B"
        tk.Label(win, text=f"Загальна точність алгоритму: {accuracy:.1f}%", font=("Arial", 14, "bold"), fg=acc_color, bg="white").pack(pady=15)
        
        tk.Button(win, text="Закрити звіт", command=win.destroy, bg=self.btn_default_color, width=15).pack(pady=5)



    def _process_image_loading(self, filepath):
        if filepath:
            try:
                self.image_path = filepath
                image = Image.open(self.image_path)
                image.thumbnail((600, 600))
                self.image_tk = ImageTk.PhotoImage(image)
                self.image_label.config(image=self.image_tk)
                self.image_label.image = self.image_tk
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")

    def load_any_image(self):
        path = filedialog.askopenfilename(
            title="Оберіть будь-яке зображення",
            filetypes=[("Image files", "*.bmp;*.jpg;*.gif;*.png;*.jpeg;*.tif")]
        )
        self._process_image_loading(path)

    def load_database_image(self):
        path = filedialog.askopenfilename(
            initialdir=self.dataset_path,
            title="Оберіть МРТ знімок з бази",
            filetypes=[("Image files", "*.bmp;*.jpg;*.gif;*.png;*.jpeg;*.tif")]
        )
        self._process_image_loading(path)


    # Додаткові функції для роботи з зображенням та розрахунками

    def apply_threshold(self):
        if self.image_path:
            try:
                threshold = int(self.threshold_entry.get())
                self.fractal_manager.black_boundary = threshold
                original = Image.open(self.image_path).convert('L')
                img_arr = np.array(original)
                mask = img_arr > threshold
                preview_arr = (mask * 255).astype(np.uint8)
                new_image = Image.fromarray(preview_arr)
                new_image.thumbnail((600, 600))
                self.image_tk = ImageTk.PhotoImage(new_image)
                self.image_label.config(image=self.image_tk)
                self.image_label.image = self.image_tk
            except ValueError: messagebox.showerror("Помилка", "Перевірте поріг")

    def calculate_grid_action(self):
        if self.image_path:
            try:
                self._sync_params_from_ui()
                result = self.fractal_manager.calculate_grid_dimension(self.image_path)
                if result:
                    self.grid_result_label.config(text=f"D = {result:.4f}")
                    plotter.plot_graph(
                        self.fractal_manager.cd_points, 
                        "Метод підрахунку квадратів", 
                        r"$\ln N(\varepsilon)$ (Логарифм кількості комірок)", 
                        r"$\ln(1/\varepsilon)$ (Логарифм оберненого розміру комірки)"
                    )
            except ValueError: pass

    def calculate_hausdorff_action(self):
        if self.image_path:
            try:
                self._sync_params_from_ui()
                result = self.fractal_manager.calculate_hausdorff_dimension(self.image_path)
                if result:
                    self.haus_result_label.config(text=f"D = {result:.4f}")
                    plotter.plot_graph(
                        self.fractal_manager.haus_points, 
                        "Розмірність Гаусдорфа (Метод покриття)", 
                        r"$\ln N(r)$ (Логарифм кількості покриваючих фігур)", 
                        r"$\ln(1/r)$ (Логарифм оберненого радіуса)"
                    )
            except ValueError: pass

    def calculate_mass_radius_action(self):
        if self.image_path:
            try:
                self._sync_params_from_ui()
                result = self.fractal_manager.calculate_mass_radius_dimension(self.image_path)
                if result is not None:
                    self.mass_result_label.config(text=f"D = {result:.4f}")
                    plotter.plot_graph(
                        self.fractal_manager.mr_points, 
                        "Метод Маса-Радіус (Sandbox)", 
                        r"$\ln M(r)$ (Логарифм маси об'єкта)", 
                        r"$\ln(r)$ (Логарифм радіуса)"
                    )
                else: messagebox.showwarning("Увага", "Результат невизначений")
            except ValueError: messagebox.showerror("Помилка", "Перевірте параметри")
        else: messagebox.showinfo("Інфо", "Виберіть зображення")

    def calculate_dilation_action(self):
        if self.image_path:
            try:
                self._sync_params_from_ui()
                result = self.fractal_manager.calculate_dilation_dimension(self.image_path)
                
                if result is not None:
                    self.dilation_result_label.config(text=f"D = {result:.4f}")
                    plotter.plot_graph(
                        self.fractal_manager.dilation_points, 
                        "Спосіб дилатації пікселів", 
                        r"$\ln A(\varepsilon)$ (Логарифм площі дилатованої оболонки)", 
                        r"$\ln(\varepsilon)$ (Логарифм радіуса дилатації)"
                    )
                else:
                    messagebox.showwarning("Увага", "Не вдалося розрахувати")
            except ValueError:
                messagebox.showerror("Помилка", "Перевірте параметр")
        else:
             messagebox.showinfo("Інфо", "Спочатку виберіть зображення")