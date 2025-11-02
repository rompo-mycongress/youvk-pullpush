# src/gui/app.py
# Импортируем новый улучшенный интерфейс
import sys
import os

# Добавляем путь к директории src для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Это будет src/
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from gui.app_tkinter import YouVkAppTkinter

def main():
    app = YouVkAppTkinter()
    app.run()

if __name__ == "__main__":
    main()
