import tkinter as tk
from src.ui.window import FractalGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = FractalGUI(root)
    root.mainloop()