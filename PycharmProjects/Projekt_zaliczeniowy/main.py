import tkinter as tk
from gui.app import AirQualityApp

if __name__ == "__main__":
    root = tk.Tk()
    app = AirQualityApp(root)
    root.mainloop()