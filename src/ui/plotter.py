import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from src.utils import less_square_get_coefficient

def format_log_tick(x, pos):
    """
    Перетворення логарифмічного значення назад у реальне число для підпису осі.
    x: значення на осі (яке є логарифмом)
    return: рядок з реальним числом
    """
    try:
        val = np.exp(x)
        # Якщо число велике, без дробової частини
        if val >= 10:
            return f"{val:.0f}"
        elif val >= 1:
            return f"{val:.1f}"
        else:
            # Для дуже малих чисел (наприклад 1/eps)
            return f"{val:.2f}"
    except OverflowError:
        return str(x)

def plot_graph(points, title_text, y_label_text, x_label_text):
    """
    Графік регресії з перерахунком підписів осей з ln() у реальні числа.
    """
    if not points: return
    
    x_values = np.array([p[0] for p in points])
    y_values = np.array([p[1] for p in points])
    
    # Трохи ширша фігура
    plt.figure(figsize=(9, 6))
    
    # Розрахунок лінії регресії (логарифм)
    k, b = less_square_get_coefficient(points)
    x_line = np.array([min(x_values), max(x_values)])
    y_line = k * x_line + b
    
    # Побудова графіків
    plt.plot(x_line, y_line, color='blue', linewidth=1.5, zorder=1, label=f'Апроксимація (D={k:.4f})')
    plt.scatter(x_values, y_values, color='#ffadad', edgecolors='red', s=50, alpha=0.8, zorder=2, label='Експериментальні дані')
    
    # Налаштування осей
    ax = plt.gca()
    
    # Форматер, який робить exp(x) для підписів
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_log_tick))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_log_tick))
    
    # Cітка
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins='auto', min_n_ticks=5))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins='auto', min_n_ticks=5))

    # Підписи та заголовок
    plt.title(f"{title_text}\nD = {k:.5f}", fontsize=12, fontweight='bold')
    
    # Підписи осей
    plt.xlabel(x_label_text, fontsize=11, fontstyle='italic')
    plt.ylabel(y_label_text, fontsize=11, fontstyle='italic')
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_bar_graph(points, title, y_label, x_label):
    if not points: return
    x_labels = [f"{p[0][0]*1e5:.1f}-{p[0][1]*1e5:.1f}" for p in points]
    y_values = [p[1] for p in points]
    
    plt.figure(figsize=(10, 6))
    plt.bar(x_labels, y_values, color='skyblue', edgecolor='navy')
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label + " (* 10^-5)")
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    plt.show()