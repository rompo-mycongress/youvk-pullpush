# src/gui/app_tkinter.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import sys
import threading
from dotenv import set_key, load_dotenv, find_dotenv

# Добавляем путь к родительской директории для импорта модулей core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(find_dotenv(usecwd=True))

class YouVkAppTkinter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("youvk-pullpush")
        self.root.geometry("1000x700")
        # Мягкая темная цветовая схема
        self.bg_primary = "#2d2d30"      # Основной фон (темно-серый)
        self.bg_secondary = "#3e3e42"    # Вторичный фон
        self.bg_input = "#404040"        # Фон полей ввода
        self.bg_button = "#4a4a4a"       # Фон кнопок
        self.bg_hover = "#505050"        # Фон при наведении
        self.text_primary = "#e0e0e0"    # Основной текст
        self.text_secondary = "#b0b0b0"   # Вторичный текст
        self.accent = "#5a9eff"          # Акцентный цвет
        
        self.root.configure(bg=self.bg_primary)
        
        # Стиль
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_primary)
        self.style.configure('TLabel', background=self.bg_primary, foreground=self.text_primary)
        self.style.configure('TButton', background=self.bg_button, foreground=self.text_primary)
        self.style.map('TButton', background=[('active', self.bg_hover), ('pressed', self.bg_secondary)])
        self.style.configure('TEntry', fieldbackground=self.bg_input, foreground=self.text_primary, 
                           bordercolor=self.bg_secondary, lightcolor=self.bg_secondary, darkcolor=self.bg_secondary)
        self.style.configure('TCombobox', fieldbackground=self.bg_input, foreground=self.text_primary,
                           bordercolor=self.bg_secondary, arrowcolor=self.text_secondary)
        self.style.configure('TNotebook', background=self.bg_primary, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.bg_secondary, foreground=self.text_primary,
                           padding=[12, 8])
        self.style.map('TNotebook.Tab', background=[('selected', self.bg_primary)], 
                      expand=[('selected', [1, 1, 1, 0])])
        self.style.configure('TProgressbar', background=self.accent, troughcolor=self.bg_secondary,
                           borderwidth=0, lightcolor=self.accent, darkcolor=self.accent)
        
        # Стили для Treeview
        self.style.configure('Treeview', background=self.bg_secondary, foreground=self.text_primary,
                           fieldbackground=self.bg_secondary, borderwidth=0)
        self.style.configure('Treeview.Heading', background=self.bg_button, foreground=self.text_primary,
                           borderwidth=1, relief='flat')
        self.style.map('Treeview.Heading', background=[('active', self.bg_hover)])
        self.style.map('Treeview', background=[('selected', self.accent)], 
                      foreground=[('selected', '#ffffff')])
        
        # Стили для Scrollbar
        self.style.configure('TScrollbar', background=self.bg_button, troughcolor=self.bg_secondary,
                           borderwidth=0, arrowcolor=self.text_secondary)
        self.style.map('TScrollbar', background=[('active', self.bg_hover)])
        
        # Стили для Separator
        self.style.configure('TSeparator', background=self.bg_secondary)
        
        # Мягкие цвета для статусов
        self.color_success = "#6bc97f"      # Мягкий зеленый
        self.color_error = "#e87676"        # Мягкий красный
        self.color_warning = "#d4a574"      # Мягкий оранжевый
        
        self.token = os.getenv("VK_ACCESS_TOKEN")
        self.is_processing = False
        self.refresh_timer = None
        
        self.build_ui()
        
    def build_ui(self):
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if not self.token:
            self.show_token_screen()
        else:
            self.show_main_screen()
            
    def show_token_screen(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="youvk-pullpush", font=('Arial', 20, 'bold'))
        title_label.pack(pady=10)
        
        instruction1 = ttk.Label(main_frame, text="1. Нажмите на кнопку ниже, чтобы получить токен:", font=('Arial', 12))
        instruction1.pack(pady=5)
        
        # Ссылка на авторизацию VK
        auth_url = (
            "https://oauth.vk.com/authorize"
            "?client_id=6287487"
            "&redirect_uri=https://oauth.vk.com/blank.html"
            "&display=page"
            "&scope=video"
            "&response_type=token"
        )
        
        def open_auth_url():
            import webbrowser
            webbrowser.open(auth_url)
            
        auth_btn = ttk.Button(main_frame, text="Получить токен VK", command=open_auth_url)
        auth_btn.pack(pady=10)
        
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        self.token_var = tk.StringVar()
        token_entry = ttk.Entry(main_frame, textvariable=self.token_var, show="*", width=60)
        token_entry.pack(pady=10)
        
        def on_save_token():
            token = self.token_var.get().strip()
            if not token:
                messagebox.showerror("Ошибка", "Токен не может быть пустым")
                return
                
            dotenv_path = find_dotenv(usecwd=True) or ".env"
            set_key(dotenv_path, "VK_ACCESS_TOKEN", token)
            self.token = token
            self.build_ui()
            
        save_btn = ttk.Button(main_frame, text="Сохранить токен", command=on_save_token)
        save_btn.pack(pady=10)
        
        instruction2 = ttk.Label(main_frame, 
                               text="2. Скопируйте часть после access_token= и до первого &\n3. Вставьте её выше и нажмите «Сохранить»",
                               font=('Arial', 10),
                               foreground=self.text_secondary)
        instruction2.pack(pady=10)
        
    def show_main_screen(self):
        # Заголовок с кнопкой обновления токена
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="youvk-pullpush", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Обновить токен", command=self._update_token).pack(side=tk.RIGHT, padx=5)
        
        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка загрузки
        upload_frame = ttk.Frame(self.notebook)
        self.notebook.add(upload_frame, text="Загрузить")
        self._build_upload_tab(upload_frame)
        
        # Вкладка моих видео
        videos_frame = ttk.Frame(self.notebook)
        self.notebook.add(videos_frame, text="Мои видео")
        self._build_videos_tab(videos_frame)
        
    def _build_upload_tab(self, parent):
        # Заголовок
        title_label = ttk.Label(parent, text="Очередь загрузки", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Поле для URL
        url_frame = ttk.Frame(parent)
        url_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(url_frame, text="Ссылка на YouTube:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.pack(side=tk.LEFT, padx=10)
        self.url_entry.bind('<Return>', lambda e: self._add_to_queue())
        
        # Кнопка добавления канала/плейлиста
        add_playlist_btn = ttk.Button(url_frame, text="Добавить канал/плейлист", command=self._add_playlist)
        add_playlist_btn.pack(side=tk.LEFT, padx=5)
        
        # Настройки
        settings_frame = ttk.Frame(parent)
        settings_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(settings_frame, text="Приватность:").pack(side=tk.LEFT)
        self.privacy_var = tk.StringVar(value="3")
        privacy_combo = ttk.Combobox(settings_frame, textvariable=self.privacy_var, 
                                   values=["3 - Только по ссылке", "0 - Публичное"],
                                   state="readonly", width=20)
        privacy_combo.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(settings_frame, text="Пауза (сек):").pack(side=tk.LEFT, padx=(20, 0))
        self.delay_var = tk.StringVar(value="10")
        delay_entry = ttk.Entry(settings_frame, textvariable=self.delay_var, width=8)
        delay_entry.pack(side=tk.LEFT, padx=5)
        delay_entry.bind('<FocusOut>', lambda e: self._update_delay())
        
        # Кнопки
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_btn = ttk.Button(buttons_frame, text="Добавить в очередь", command=self._add_to_queue)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = ttk.Button(buttons_frame, text="Начать обработку", 
                                  command=self._start_processing, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Информация с возможностью копирования
        info_frame = ttk.Frame(parent)
        info_frame.pack(pady=5)
        info_label = ttk.Label(info_frame, text="ℹ️ Используйте задержку при ошибках или лимитах VK", 
                              foreground=self.text_secondary, font=('Arial', 9))
        info_label.pack(side=tk.LEFT)
        info_copy_btn = ttk.Button(info_frame, text="📋", width=3, 
                                  command=lambda: self._copy_to_clipboard("Используйте задержку при ошибках или лимитах VK"))
        info_copy_btn.pack(side=tk.LEFT, padx=5)
        
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Фрейм для очереди с кнопками управления
        queue_container = ttk.Frame(parent)
        queue_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(queue_container, text="Очередь:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Кнопки управления очередью
        queue_controls = ttk.Frame(queue_container)
        queue_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(queue_controls, text="↑", width=3, command=self._move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(queue_controls, text="↓", width=3, command=self._move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(queue_controls, text="Удалить", command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_controls, text="Очистить очередь", command=self._clear_queue).pack(side=tk.LEFT, padx=5)
        
        # Создаем Treeview для отображения очереди с прогресс-барами
        columns = ("order", "title", "status", "progress", "actions")
        self.queue_tree = ttk.Treeview(queue_container, columns=columns, show="headings", height=15)
        
        self.queue_tree.heading("order", text="#")
        self.queue_tree.heading("title", text="Название / URL")
        self.queue_tree.heading("status", text="Статус")
        self.queue_tree.heading("progress", text="Прогресс")
        self.queue_tree.heading("actions", text="Действия")
        
        self.queue_tree.column("order", width=30, anchor=tk.CENTER)
        self.queue_tree.column("title", width=350)
        self.queue_tree.column("status", width=180)
        self.queue_tree.column("progress", width=150)
        self.queue_tree.column("actions", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(queue_container, orient=tk.VERTICAL, command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=scrollbar.set)
        
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Инициализируем очередь
        from core.queue import DownloadQueue
        self.dq = DownloadQueue()
        self.delay_var.set(str(self.dq.delay))
        self._refresh_queue_ui()
        
        # Настройка drag-and-drop (имитация через выделение)
        self.queue_tree.bind("<Button-1>", self._on_select)
        self.queue_tree.bind("<Double-1>", self._on_queue_item_double_click)
        self.queue_tree.bind("<Button-3>", self._on_right_click)  # Правый клик для меню
        
    def _add_to_queue(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Предупреждение", "Введите URL видео")
            return
        
        # Проверяем, является ли это каналом или плейлистом
        if "playlist" in url.lower() or "channel" in url.lower() or "@" in url:
            self._add_playlist(url)
        else:
            privacy = self.privacy_var.get().split()[0]  # Извлекаем число из строки
            self.dq.add_url(url, None, privacy)
            self._refresh_queue_ui()
            self.start_btn.config(state=tk.NORMAL)
            self.url_var.set("")
            messagebox.showinfo("Успех", "Видео добавлено в очередь")
        
    def _add_playlist(self, url=None):
        if not url:
            url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Предупреждение", "Введите URL канала или плейлиста")
            return
        
        privacy = self.privacy_var.get().split()[0]
        
        def add_thread():
            try:
                count = self.dq.add_channel_or_playlist(url, privacy)
                self.root.after(0, lambda: messagebox.showinfo("Успех", f"Добавлено {count} видео в очередь"))
                self.root.after(0, self._refresh_queue_ui)
                self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка парсинга: {str(e)}"))
        
        threading.Thread(target=add_thread, daemon=True).start()
        
    def _update_delay(self):
        try:
            delay = int(self.delay_var.get())
            self.dq.set_delay(delay)
        except ValueError:
            pass
        
    def _refresh_queue_ui(self):
        # Очищаем treeview
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        if not self.dq.items:
            self.queue_tree.insert("", "end", values=("", "Очередь пуста", "", "", ""))
            self.start_btn.config(state=tk.DISABLED)
        else:
            for idx, item in enumerate(self.dq.items, 1):
                status = item.get("status", "pending")
                
                # Определяем отображаемое название
                extracted_title = item.get("extracted_title")
                custom_title = item.get("custom_title")
                display_title = custom_title or extracted_title or item["url"]
                if len(display_title) > 50:
                    display_title = display_title[:47] + "..."
                
                # Статус и прогресс
                status_text = status
                progress_text = ""
                progress_value = 0
                
                if status == "done":
                    status_text = "✅ Готово"
                    progress_text = "100%"
                    progress_value = 100
                elif status.startswith("error"):
                    status_text = f"❌ {status.split(':', 1)[-1][:30]}"
                    progress_text = "Ошибка"
                elif status == "pending":
                    status_text = "⏳ Ожидание"
                    progress_text = "0%"
                elif "📥" in status or "Получение информации" in status:
                    status_text = status[:40]
                    progress_value = item.get("progress", 0)
                    progress_text = f"{progress_value:.0f}%" if progress_value else "0%"
                elif "📤" in status or "Загрузка" in status:
                    status_text = status[:40]
                    progress_value = item.get("progress", 98)
                    progress_text = f"{progress_value:.0f}%" if progress_value else "98%"
                elif "🔄" in status or "Конвертация" in status:
                    status_text = status[:40]
                    progress_value = item.get("progress", 95)
                    progress_text = f"{progress_value:.0f}%" if progress_value else "95%"
                else:
                    status_text = status[:40]
                    progress_text = ""
                
                # Действия
                actions = ""
                if status == "done" and item.get("result_link"):
                    actions = "📋 Копировать ссылку"
                elif status == "pending":
                    actions = "Удалить|Изменить|📋 Копировать URL"
                elif status.startswith("error"):
                    actions = "Удалить"
                
                item_id = self.queue_tree.insert("", "end", 
                    values=(idx, display_title, status_text, progress_text, actions),
                    tags=(status,))
                
                # Настройка цвета статуса
                if status == "done":
                    self.queue_tree.set(item_id, "status", "✅ Готово")
                elif status.startswith("error"):
                    self.queue_tree.set(item_id, "status", f"❌ Ошибка")
        
        # Обновляем кнопку запуска
        if self.dq.get_pending_urls():
            self.start_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.DISABLED)
            
    def _on_select(self, event):
        """Обработка выбора элемента"""
        pass
        
    def _on_queue_item_double_click(self, event):
        """Обработка двойного клика по элементу очереди"""
        selection = self.queue_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.queue_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 5:
            return
        
        idx = int(values[0]) - 1
        if idx < 0 or idx >= len(self.dq.items):
            return
        
        queue_item = self.dq.items[idx]
        url = queue_item["url"]
        status = queue_item.get("status", "pending")
        
        # Если готово - копируем ссылку
        if status == "done" and queue_item.get("result_link"):
            self._copy_to_clipboard(queue_item["result_link"])
            messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена")
        
        # Если pending - открываем диалог редактирования названия
        elif status == "pending":
            self._edit_title_dialog(queue_item)
    
    def _on_right_click(self, event):
        """Обработка правого клика - контекстное меню"""
        selection = self.queue_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.queue_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 5:
            return
        
        idx = int(values[0]) - 1
        if idx < 0 or idx >= len(self.dq.items):
            return
        
        queue_item = self.dq.items[idx]
        url = queue_item["url"]
        status = queue_item.get("status", "pending")
        
        # Создаем контекстное меню
        menu = tk.Menu(self.root, tearoff=0)
        
        if status == "pending":
            menu.add_command(label="Изменить название", command=lambda: self._edit_title_dialog(queue_item))
            menu.add_command(label="Удалить", command=lambda: self._delete_item(queue_item))
            menu.add_command(label="📋 Копировать URL", command=lambda: self._copy_to_clipboard(url))
            menu.add_command(label="Переместить вверх", command=lambda: self._move_item_up(queue_item))
            menu.add_command(label="Переместить вниз", command=lambda: self._move_item_down(queue_item))
        elif status == "done":
            menu.add_command(label="📋 Копировать ссылку VK", command=lambda: self._copy_to_clipboard(queue_item.get("result_link", "")))
            menu.add_command(label="Удалить из очереди", command=lambda: self._delete_item(queue_item))
        elif status.startswith("error"):
            menu.add_command(label="Удалить", command=lambda: self._delete_item(queue_item))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _edit_title_dialog(self, queue_item):
        """Диалог редактирования названия"""
        current_title = queue_item.get("custom_title") or queue_item.get("extracted_title") or ""
        new_title = self._custom_input_dialog("Изменить название", "Введите новое название:", current_title)
        if new_title:
            queue_item["custom_title"] = new_title.strip()
            self.dq._save()
            self._refresh_queue_ui()
    
    def _copy_to_clipboard(self, text):
        """Копирует текст в буфер обмена"""
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(text))
            messagebox.showinfo("Успех", "Текст скопирован в буфер обмена")
    
    def _update_token(self):
        """Открывает диалог обновления токена"""
        # Сохраняем текущий токен для предзаполнения
        current_token = self.token or ""
        new_token = self._custom_input_dialog("Обновить токен VK", "Введите новый токен:", current_token)
        if new_token:
            dotenv_path = find_dotenv(usecwd=True) or ".env"
            set_key(dotenv_path, "VK_ACCESS_TOKEN", new_token)
            self.token = new_token
            messagebox.showinfo("Успех", "Токен обновлен")
    
    def _copy_link(self, queue_item):
        """Копирует ссылку на видео"""
        if queue_item.get("result_link"):
            self._copy_to_clipboard(queue_item["result_link"])
    
    def _delete_item(self, queue_item):
        """Удаляет элемент из очереди"""
        if messagebox.askyesno("Подтверждение", "Удалить из очереди?"):
            self.dq.remove_item(queue_item["url"])
            self._refresh_queue_ui()
    
    def _delete_selected(self):
        """Удаляет выбранный элемент"""
        selection = self.queue_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите элемент для удаления")
            return
        
        item_id = selection[0]
        item = self.queue_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 5:
            return
        
        idx = int(values[0]) - 1
        if idx < 0 or idx >= len(self.dq.items):
            return
        
        queue_item = self.dq.items[idx]
        if queue_item.get("status") == "pending" or queue_item.get("status", "").startswith("error"):
            self._delete_item(queue_item)
        else:
            messagebox.showwarning("Предупреждение", "Можно удалять только элементы со статусом 'Ожидание' или 'Ошибка'")
    
    def _clear_queue(self):
        """Очищает всю очередь от pending элементов"""
        if messagebox.askyesno("Подтверждение", "Очистить очередь от всех элементов со статусом 'Ожидание'?"):
            self.dq.items = [item for item in self.dq.items if item.get("status") != "pending"]
            self.dq._save()
            self._refresh_queue_ui()
    
    def _move_up(self):
        """Перемещает выделенный элемент вверх"""
        selection = self.queue_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.queue_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 5:
            return
        
        idx = int(values[0]) - 1
        if idx > 0:
            url = self.dq.items[idx]["url"]
            if self.dq.move_item(url, "up"):
                self._refresh_queue_ui()
                # Выделяем перемещенный элемент
                new_idx = idx - 1
                children = self.queue_tree.get_children()
                if new_idx < len(children):
                    self.queue_tree.selection_set(children[new_idx])
    
    def _move_down(self):
        """Перемещает выделенный элемент вниз"""
        selection = self.queue_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.queue_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 5:
            return
        
        idx = int(values[0]) - 1
        if idx < len(self.dq.items) - 1:
            url = self.dq.items[idx]["url"]
            if self.dq.move_item(url, "down"):
                self._refresh_queue_ui()
                # Выделяем перемещенный элемент
                new_idx = idx + 1
                children = self.queue_tree.get_children()
                if new_idx < len(children):
                    self.queue_tree.selection_set(children[new_idx])
    
    def _move_item_up(self, queue_item):
        """Перемещает элемент вверх"""
        if self.dq.move_item(queue_item["url"], "up"):
            self._refresh_queue_ui()
    
    def _move_item_down(self, queue_item):
        """Перемещает элемент вниз"""
        if self.dq.move_item(queue_item["url"], "down"):
            self._refresh_queue_ui()
            
    def _start_processing(self):
        if self.is_processing or not self.dq.get_pending_urls():
            return
            
        self.is_processing = True
        self.start_btn.config(state=tk.DISABLED, text="Обработка...")
        
        from core.youtube import YouTubeDownloader
        from core.vk import VKUploader
        
        def progress_hook(url, status, progress=None):
            """Хук для обновления прогресса"""
            if progress is not None:
                self.dq.update_status(url, status, progress=progress)
            else:
                # Извлекаем прогресс из статуса, если возможно
                if "%" in status:
                    try:
                        progress = float(status.split("%")[0].split()[-1])
                        self.dq.update_status(url, status, progress=progress)
                    except:
                        self.dq.update_status(url, status)
                else:
                    self.dq.update_status(url, status)
            
            self.root.after(0, self._refresh_queue_ui)
            
        def update_status(url, status, progress=None):
            """Обновление статуса через очередь"""
            progress_hook(url, status, progress)
            
        def process_thread():
            downloader = YouTubeDownloader(progress_hook=progress_hook)
            uploader = VKUploader(self.token)
            self.dq.process_all(update_status, downloader, uploader)
            self.is_processing = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL, text="Начать обработку"))
            self.root.after(0, lambda: messagebox.showinfo("Успех", "Обработка завершена"))
            
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()
        
        # Запускаем автообновление UI
        self._start_auto_refresh()
        
    def _start_auto_refresh(self):
        """Запускает автообновление UI каждые 500мс"""
        if self.is_processing:
            self._refresh_queue_ui()
            self.refresh_timer = self.root.after(500, self._start_auto_refresh)
        else:
            if self.refresh_timer:
                self.root.after_cancel(self.refresh_timer)
                self.refresh_timer = None
            
    def _build_videos_tab(self, parent):
        # Заголовок с кнопками
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Мои видео", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Обновить", command=self._refresh_videos_tab).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text="Очистить историю", command=self._clear_history).pack(side=tk.RIGHT, padx=5)
        
        # Фрейм для списка видео
        videos_container = ttk.Frame(parent)
        videos_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Создаем Treeview для видео
        columns = ("title", "link", "actions")
        self.videos_tree = ttk.Treeview(videos_container, columns=columns, show="headings", height=20)
        
        self.videos_tree.heading("title", text="Название")
        self.videos_tree.heading("link", text="Ссылка VK")
        self.videos_tree.heading("actions", text="Действия")
        
        self.videos_tree.column("title", width=400)
        self.videos_tree.column("link", width=300)
        self.videos_tree.column("actions", width=200)
        
        scrollbar_videos = ttk.Scrollbar(videos_container, orient=tk.VERTICAL, command=self.videos_tree.yview)
        self.videos_tree.configure(yscrollcommand=scrollbar_videos.set)
        
        self.videos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_videos.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.videos_tree.bind("<Double-1>", self._on_video_double_click)
        self.videos_tree.bind("<Button-3>", self._on_video_right_click)
        
        self._refresh_videos_tab()
        
    def _refresh_videos_tab(self):
        """Обновляет список видео"""
        # Очищаем treeview
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        try:
            from core.vk import VKUploader
            videos = VKUploader(self.token).get_uploaded_videos()
            
            if not videos:
                self.videos_tree.insert("", "end", values=("Нет загруженных видео", "", ""))
            else:
                for video in videos:
                    title = video.get('title', 'Без названия')
                    link = video.get('link', '')
                    self.videos_tree.insert("", "end", values=(title, link, "Копировать|Переименовать|Удалить"))
        except Exception as e:
            self.videos_tree.insert("", "end", values=(f"Ошибка загрузки: {str(e)}", "", ""))
    
    def _on_video_double_click(self, event):
        """Обработка двойного клика по видео"""
        selection = self.videos_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.videos_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 3:
            return
        
        link = values[1]
        if link:
            self.root.clipboard_clear()
            self.root.clipboard_append(link)
            messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена")
    
    def _on_video_right_click(self, event):
        """Обработка правого клика по видео"""
        selection = self.videos_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.videos_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 3:
            return
        
        title = values[0]
        link = values[1]
        
        if not link:
            return
        
        # Извлекаем owner_id и video_id из ссылки
        try:
            parts = link.split("/video")[-1].split("_")
            owner_id = int(parts[0])
            video_id = int(parts[1])
        except:
            messagebox.showerror("Ошибка", "Не удалось определить ID видео")
            return
        
        # Создаем контекстное меню
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать ссылку VK", command=lambda: self._copy_vk_link(link))
        menu.add_command(label="Копировать iframe код", command=lambda: self._copy_iframe(owner_id, video_id))
        menu.add_command(label="Переименовать", command=lambda: self._rename_video(owner_id, video_id, title))
        menu.add_command(label="Удалить из истории", command=lambda: self._delete_from_history(owner_id, video_id))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _copy_vk_link(self, link):
        """Копирует ссылку VK"""
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена")
    
    def _copy_iframe(self, owner_id, video_id):
        """Копирует код iframe"""
        embed_url = f"https://vk.com/video_ext.php?oid={owner_id}&id={video_id}"
        iframe_code = f'<iframe src="{embed_url}" width="640" height="360" frameborder="0" allowfullscreen></iframe>'
        self.root.clipboard_clear()
        self.root.clipboard_append(iframe_code)
        messagebox.showinfo("Успех", "Код iframe скопирован в буфер обмена")
    
    
    def _custom_input_dialog(self, title, prompt, initial_value=""):
        """Кастомный диалог ввода с правильным позиционированием и расширенным полем"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)  # Делаем окно модальным относительно основного окна
        dialog.grab_set()  # Блокируем взаимодействие с другими окнами
        
        # Позиционируем окно над основным окном приложения
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        dialog_width = 500
        dialog_height = 150
        
        # Центрируем над основным окном
        dialog_x = main_x + (main_width // 2) - (dialog_width // 2)
        dialog_y = main_y + (main_height // 2) - (dialog_height // 2)
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")
        dialog.configure(bg=self.bg_primary)
        dialog.resizable(False, False)
        
        result = [None]  # Используем список для изменения значения из замыкания
        
        # Фрейм для содержимого
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Метка с подсказкой
        label = ttk.Label(content_frame, text=prompt, background=self.bg_primary, foreground=self.text_primary)
        label.pack(anchor=tk.W, pady=(0, 10))
        
        # Поле ввода (расширенное для 7 слов по 6 букв)
        entry_var = tk.StringVar(value=initial_value)
        entry = ttk.Entry(content_frame, textvariable=entry_var, width=70)  # Ширина для ~60-70 символов
        entry.pack(fill=tk.X, pady=(0, 20))
        entry.focus_set()
        entry.select_range(0, tk.END)  # Выделяем весь текст для удобства редактирования
        
        # Фрейм для кнопок
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X)
        
        def on_ok():
            result[0] = entry_var.get().strip()
            dialog.destroy()
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        def on_enter(event):
            on_ok()
        
        # Кнопки
        ok_btn = ttk.Button(buttons_frame, text="ОК", command=on_ok)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(buttons_frame, text="Отмена", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Привязываем Enter к кнопке OK
        entry.bind('<Return>', on_enter)
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Ждем закрытия окна
        dialog.wait_window()
        
        return result[0]
            
    def _start_processing(self):
        if self.is_processing or not self.dq.get_pending_urls():
            return
            
        self.is_processing = True
        self.start_btn.config(state=tk.DISABLED, text="Обработка...")
        
        from core.youtube import YouTubeDownloader
        from core.vk import VKUploader
        
        def progress_hook(url, status, progress=None):
            """Хук для обновления прогресса"""
            if progress is not None:
                self.dq.update_status(url, status, progress=progress)
            else:
                # Извлекаем прогресс из статуса, если возможно
                if "%" in status:
                    try:
                        progress = float(status.split("%")[0].split()[-1])
                        self.dq.update_status(url, status, progress=progress)
                    except:
                        self.dq.update_status(url, status)
                else:
                    self.dq.update_status(url, status)
            
            self.root.after(0, self._refresh_queue_ui)
            
        def update_status(url, status, progress=None):
            """Обновление статуса через очередь"""
            progress_hook(url, status, progress)
            
        def process_thread():
            downloader = YouTubeDownloader(progress_hook=progress_hook)
            uploader = VKUploader(self.token)
            self.dq.process_all(update_status, downloader, uploader)
            self.is_processing = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL, text="Начать обработку"))
            self.root.after(0, lambda: messagebox.showinfo("Успех", "Обработка завершена"))
            
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()
        
        # Запускаем автообновление UI
        self._start_auto_refresh()
        
    def _start_auto_refresh(self):
        """Запускает автообновление UI каждые 500мс"""
        if self.is_processing:
            self._refresh_queue_ui()
            self.refresh_timer = self.root.after(500, self._start_auto_refresh)
        else:
            if self.refresh_timer:
                self.root.after_cancel(self.refresh_timer)
                self.refresh_timer = None
            
    def _build_videos_tab(self, parent):
        # Заголовок с кнопками
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Мои видео", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Обновить", command=self._refresh_videos_tab).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text="Очистить историю", command=self._clear_history).pack(side=tk.RIGHT, padx=5)
        
        # Фрейм для списка видео
        videos_container = ttk.Frame(parent)
        videos_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Создаем Treeview для видео
        columns = ("title", "link", "actions")
        self.videos_tree = ttk.Treeview(videos_container, columns=columns, show="headings", height=20)
        
        self.videos_tree.heading("title", text="Название")
        self.videos_tree.heading("link", text="Ссылка VK")
        self.videos_tree.heading("actions", text="Действия")
        
        self.videos_tree.column("title", width=400)
        self.videos_tree.column("link", width=300)
        self.videos_tree.column("actions", width=200)
        
        scrollbar_videos = ttk.Scrollbar(videos_container, orient=tk.VERTICAL, command=self.videos_tree.yview)
        self.videos_tree.configure(yscrollcommand=scrollbar_videos.set)
        
        self.videos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_videos.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.videos_tree.bind("<Double-1>", self._on_video_double_click)
        self.videos_tree.bind("<Button-3>", self._on_video_right_click)
        
        self._refresh_videos_tab()
        
    def _refresh_videos_tab(self):
        """Обновляет список видео"""
        # Очищаем treeview
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        try:
            from core.vk import VKUploader
            videos = VKUploader(self.token).get_uploaded_videos()
            
            if not videos:
                self.videos_tree.insert("", "end", values=("Нет загруженных видео", "", ""))
            else:
                for video in videos:
                    title = video.get('title', 'Без названия')
                    link = video.get('link', '')
                    self.videos_tree.insert("", "end", values=(title, link, "Копировать|Переименовать|Удалить"))
        except Exception as e:
            self.videos_tree.insert("", "end", values=(f"Ошибка загрузки: {str(e)}", "", ""))
    
    def _on_video_double_click(self, event):
        """Обработка двойного клика по видео"""
        selection = self.videos_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.videos_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 3:
            return
        
        link = values[1]
        if link:
            self.root.clipboard_clear()
            self.root.clipboard_append(link)
            messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена")
    
    def _on_video_right_click(self, event):
        """Обработка правого клика по видео"""
        selection = self.videos_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.videos_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 3:
            return
        
        title = values[0]
        link = values[1]
        
        if not link:
            return
        
        # Извлекаем owner_id и video_id из ссылки
        try:
            parts = link.split("/video")[-1].split("_")
            owner_id = int(parts[0])
            video_id = int(parts[1])
        except:
            messagebox.showerror("Ошибка", "Не удалось определить ID видео")
            return
        
        # Создаем контекстное меню
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать ссылку VK", command=lambda: self._copy_vk_link(link))
        menu.add_command(label="Копировать iframe код", command=lambda: self._copy_iframe(owner_id, video_id))
        menu.add_command(label="Переименовать", command=lambda: self._rename_video(owner_id, video_id, title))
        menu.add_command(label="Удалить из истории", command=lambda: self._delete_from_history(owner_id, video_id))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _copy_vk_link(self, link):
        """Копирует ссылку VK"""
        self.root.clipboard_clear()
        self.root.clipboard_append(link)
        messagebox.showinfo("Успех", "Ссылка скопирована в буфер обмена")
    
    def _copy_iframe(self, owner_id, video_id):
        """Копирует код iframe"""
        embed_url = f"https://vk.com/video_ext.php?oid={owner_id}&id={video_id}"
        iframe_code = f'<iframe src="{embed_url}" width="640" height="360" frameborder="0" allowfullscreen></iframe>'
        self.root.clipboard_clear()
        self.root.clipboard_append(iframe_code)
        messagebox.showinfo("Успех", "Код iframe скопирован в буфер обмена")
    
    def _rename_video(self, owner_id, video_id, current_title):
        """Переименовывает видео на ВК"""
        new_title = self._custom_input_dialog("Переименовать видео", "Введите новое название:", current_title)
        if new_title:
            try:
                from core.vk import VKUploader
                uploader = VKUploader(self.token)
                if uploader.rename_video(owner_id, video_id, new_title):
                    messagebox.showinfo("Успех", "Видео переименовано")
                    self._refresh_videos_tab()
                else:
                    messagebox.showerror("Ошибка", "Не удалось переименовать видео")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка переименования: {str(e)}")
    
    def _delete_from_history(self, owner_id, video_id):
        """Удаляет видео из истории"""
        if messagebox.askyesno("Подтверждение", "Удалить видео из истории?"):
            import json
            uploads_log = os.path.join(os.path.dirname(__file__), "..", "uploads.json")
            try:
                if os.path.exists(uploads_log):
                    with open(uploads_log, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    data = [item for item in data if not (item.get("owner_id") == owner_id and item.get("video_id") == video_id)]
                    with open(uploads_log, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    self._refresh_videos_tab()
                    messagebox.showinfo("Успех", "Видео удалено из истории")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления: {str(e)}")
    
    def _clear_history(self):
        """Очищает всю историю"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю загрузок?"):
            uploads_log = os.path.join(os.path.dirname(__file__), "..", "uploads.json")
            try:
                with open(uploads_log, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                self._refresh_videos_tab()
                messagebox.showinfo("Успех", "История очищена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка очистки: {str(e)}")
        
    def run(self):
        self.root.mainloop()

def main():
    app = YouVkAppTkinter()
    app.run()

if __name__ == "__main__":
    main()
