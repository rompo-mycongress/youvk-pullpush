# src/main_tkinter.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.app_tkinter import YouVkAppTkinter

if __name__ == "__main__":
    app = YouVkAppTkinter()
    app.run()