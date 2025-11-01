# src/gui/app.py
# Импортируем новый улучшенный интерфейс
import sys
import os

# Добавляем путь к родительской директории для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.app_tkinter import YouVkAppTkinter

def main():
    app = YouVkAppTkinter()
    app.run()

if __name__ == "__main__":
    main()
