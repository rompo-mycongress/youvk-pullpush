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
        self.stop_processing_flag = False  # Флаг для остановки обработки
        self.waiting_for_upload = False  # Флаг ожидания загрузки в раздельном режиме
        
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
        
        # Вкладка всех видео ВК
        all_vk_videos_frame = ttk.Frame(self.notebook)
        self.notebook.add(all_vk_videos_frame, text="Все видео ВК")
        self._build_all_vk_videos_tab(all_vk_videos_frame)
        
        # Вкладка парсинга YouTube канала
        yt_parse_frame = ttk.Frame(self.notebook)
        self.notebook.add(yt_parse_frame, text="Парсинг YouTube")
        self._build_yt_parse_tab(yt_parse_frame)
        
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
        
        # Режимы раздельной закачки и загрузки
        modes_frame = ttk.Frame(parent)
        modes_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.separate_download_var = tk.BooleanVar(value=False)
        separate_download_check = ttk.Checkbutton(modes_frame, text="Раздельная закачка (сначала скачать все, затем загрузить на VK)", 
                                                 variable=self.separate_download_var)
        separate_download_check.pack(side=tk.LEFT, padx=5)
        
        info_label_modes = ttk.Label(modes_frame, 
                                     text="ℹ️ Полезно при использовании VPN/WARP для YouTube", 
                                     foreground=self.text_secondary, font=('Arial', 8))
        info_label_modes.pack(side=tk.LEFT, padx=10)
        
        # Кнопки
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        add_btn = ttk.Button(buttons_frame, text="Добавить в очередь", command=self._add_to_queue)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = ttk.Button(buttons_frame, text="Начать обработку", 
                                  command=self._start_processing, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.continue_btn = ttk.Button(buttons_frame, text="Продолжить выполнение", 
                                       command=self._continue_processing, state=tk.DISABLED)
        self.continue_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="Остановить", 
                                  command=self._stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Информация
        info_frame = ttk.Frame(parent)
        info_frame.pack(pady=5)
        info_label = ttk.Label(info_frame, text="ℹ️ Используйте задержку при ошибках или лимитах VK", 
                              foreground=self.text_secondary, font=('Arial', 9))
        info_label.pack(side=tk.LEFT)
        
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
        ttk.Button(queue_controls, text="Удалить все", command=self._delete_all_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_controls, text="Очистить очередь", command=self._clear_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_controls, text="📁 Открыть папку", command=self._open_temp_folder).pack(side=tk.LEFT, padx=5)
        
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
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Ошибка", f"Ошибка парсинга: {msg}"))
        
        threading.Thread(target=add_thread, daemon=True).start()
        
    def _update_delay(self):
        try:
            delay = int(self.delay_var.get())
            self.dq.set_delay(delay)
        except ValueError:
            pass
        
    def _refresh_queue_ui(self):
        # Сохраняем текущее выделение
        selected_items = self.queue_tree.selection()
        selected_urls = []
        if selected_items:
            for item_id in selected_items:
                item = self.queue_tree.item(item_id)
                values = item["values"]
                if len(values) >= 5:
                    try:
                        idx = int(values[0]) - 1
                        if 0 <= idx < len(self.dq.items):
                            selected_urls.append(self.dq.items[idx]["url"])
                    except:
                        pass
        
        # Очищаем treeview
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        if not self.dq.items:
            self.queue_tree.insert("", "end", values=("", "Очередь пуста", "", "", ""))
            self.start_btn.config(state=tk.DISABLED)
            self.continue_btn.config(state=tk.DISABLED)
        else:
            # Проверяем наличие элементов для обработки
            pending = self.dq.get_pending_urls()
            # Проверяем скачанные элементы по статусу ИЛИ по наличию downloaded_filepath
            downloaded = [item for item in self.dq.items if item.get("status") == "downloaded" or item.get("downloaded_filepath")]
            
            if pending and not self.is_processing:
                self.start_btn.config(state=tk.NORMAL)
            else:
                self.start_btn.config(state=tk.DISABLED)
            
            # Кнопка активна если есть скачанные файлы и не идет обработка
            if len(downloaded) > 0 and not self.is_processing:
                self.continue_btn.config(state=tk.NORMAL)
            else:
                self.continue_btn.config(state=tk.DISABLED)
            
            inserted_items = {}
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
                elif status == "downloaded":
                    status_text = "✅ Скачано, готово к загрузке"
                    progress_text = "100%"
                    progress_value = 100
                elif item.get("downloaded_filepath"):
                    # Проверяем существование файла
                    filepath = item.get("downloaded_filepath")
                    if filepath and os.path.exists(filepath):
                        # Если файл существует, но статус не "downloaded" - обновляем статус
                        status_text = "✅ Скачано, готово к загрузке"
                        progress_text = "100%"
                        progress_value = 100
                        if status != "downloaded":
                            item["status"] = "downloaded"
                            self.dq._save()
                    else:
                        # Файл не найден - показываем как есть
                        status_text = status[:40]
                        progress_text = ""
                elif "📥" in status or "Получение информации" in status:
                    status_text = status[:40]
                    progress_value = item.get("progress", 0)
                    progress_text = f"{progress_value:.0f}%" if progress_value else "0%"
                elif status.startswith("📤") or "Загрузка" in status:
                    # Для загрузки показываем статус с прогрессом
                    status_text = status[:40] if len(status) <= 40 else status[:37] + "..."
                    progress_value = item.get("progress", 0)
                    # Если прогресс в статусе не сохранен, пытаемся извлечь из текста статуса
                    if progress_value == 0 and "%" in status:
                        try:
                            import re
                            match = re.search(r'(\d+\.?\d*)%', status)
                            if match:
                                progress_value = float(match.group(1))
                        except:
                            pass
                    progress_text = f"{progress_value:.1f}%" if progress_value > 0 else "0%"
                elif "🔄" in status or "Конвертация" in status:
                    status_text = status[:40]
                    progress_value = item.get("progress", 95)
                    progress_text = f"{progress_value:.0f}%" if progress_value else "95%"
                elif "⏳" in status and "Пауза" in status:
                    # Обрезаем длинный текст паузы для отображения
                    status_text = status[:50] if len(status) <= 50 else status[:47] + "..."
                    progress_text = ""
                else:
                    status_text = status[:40]
                    progress_text = ""
                
                # Действия - определяем по статусу
                actions = ""
                if status == "done" and item.get("result_link"):
                    actions = "📋 Копировать ссылку|Удалить"
                elif status == "pending":
                    actions = "Удалить|Изменить|📋 Копировать URL"
                elif status == "downloaded":
                    actions = "Продолжить загрузку|Удалить"
                elif status.startswith("error"):
                    actions = "Удалить"
                elif "📤" in status or "Загрузка" in status:
                    # При загрузке показываем только "Сбросить"
                    actions = "Сбросить"
                else:
                    # Для других зависших состояний
                    actions = "Сбросить|Удалить"
                
                item_id = self.queue_tree.insert("", "end", 
                    values=(idx, display_title, status_text, progress_text, actions),
                    tags=(status,))
                
                # Сохраняем связь URL с item_id для восстановления выделения
                inserted_items[item["url"]] = item_id
                
                # Настройка цвета статуса
                if status == "done":
                    self.queue_tree.set(item_id, "status", "✅ Готово")
                elif status.startswith("error"):
                    self.queue_tree.set(item_id, "status", f"❌ Ошибка")
            
            # Восстанавливаем выделение
            if selected_urls:
                items_to_select = []
                for url in selected_urls:
                    if url in inserted_items:
                        items_to_select.append(inserted_items[url])
                if items_to_select:
                    for item_id in items_to_select:
                        self.queue_tree.selection_add(item_id)
        
            
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
        
        # Добавляем переименование для всех статусов (до и после загрузки)
        if status == "done" and queue_item.get("owner_id") and queue_item.get("video_id"):
            # Переименование на VK после загрузки
            menu.add_command(label="✏️ Переименовать на VK", command=lambda: self._rename_vk_video_from_queue(queue_item))
            menu.add_separator()
            menu.add_command(label="📋 Копировать ссылку VK", command=lambda: self._copy_to_clipboard(queue_item.get("result_link", "")))
            menu.add_command(label="Удалить из очереди", command=lambda: self._delete_item(queue_item))
        elif status == "pending":
            menu.add_command(label="Изменить название", command=lambda: self._edit_title_dialog(queue_item))
            menu.add_command(label="✏️ Переименовать на VK", command=lambda: self._rename_vk_video_from_queue(queue_item))
            menu.add_command(label="Удалить", command=lambda: self._delete_item(queue_item))
            menu.add_command(label="📋 Копировать URL", command=lambda: self._copy_to_clipboard(url))
            menu.add_command(label="Переместить вверх", command=lambda: self._move_item_up(queue_item))
            menu.add_command(label="Переместить вниз", command=lambda: self._move_item_down(queue_item))
        elif status == "downloaded":
            menu.add_command(label="Продолжить загрузку", command=lambda: self._continue_processing())
            menu.add_command(label="✏️ Переименовать на VK", command=lambda: self._rename_vk_video_from_queue(queue_item))
            menu.add_command(label="Удалить", command=lambda: self._delete_item(queue_item))
        elif status.startswith("error"):
            menu.add_command(label="Удалить", command=lambda: self._delete_item(queue_item))
            menu.add_command(label="Сбросить в ожидание", command=lambda: self._reset_item_status(queue_item))
        else:
            # Для зависших состояний (98%, загрузка и т.д.)
            menu.add_command(label="Сбросить в ожидание", command=lambda: self._reset_item_status(queue_item))
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
        """Открывает диалог обновления токена с ссылкой на авторизацию"""
        # Ссылка на авторизацию VK
        auth_url = (
            "https://oauth.vk.com/authorize"
            "?client_id=6287487"
            "&redirect_uri=https://oauth.vk.com/blank.html"
            "&display=page"
            "&scope=video"
            "&response_type=token"
        )
        
        # Создаем диалог с кнопками
        dialog = tk.Toplevel(self.root)
        dialog.title("Обновить токен VK")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Позиционируем окно над основным окном
        self.root.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        dialog_width = 550
        dialog_height = 220
        
        dialog_x = main_x + (main_width // 2) - (dialog_width // 2)
        dialog_y = main_y + (main_height // 2) - (dialog_height // 2)
        
        dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")
        dialog.configure(bg=self.bg_primary)
        dialog.resizable(False, False)
        
        result = [None]
        
        # Фрейм для содержимого
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Инструкция
        instruction_label = ttk.Label(content_frame, 
                                    text="1. Нажмите кнопку ниже, чтобы получить токен VK", 
                                    background=self.bg_primary, foreground=self.text_primary)
        instruction_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Кнопки для открытия ссылки
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        def open_auth_url():
            import webbrowser
            webbrowser.open(auth_url)
        
        def copy_auth_url():
            self._copy_to_clipboard(auth_url)
        
        ttk.Button(buttons_frame, text="Открыть в браузере", command=open_auth_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📋 Копировать ссылку", command=copy_auth_url).pack(side=tk.LEFT, padx=5)
        
        # Инструкция 2
        instruction2_label = ttk.Label(content_frame, 
                                       text="2. Скопируйте часть после access_token= и до первого &", 
                                       background=self.bg_primary, foreground=self.text_secondary,
                                       font=('Arial', 9))
        instruction2_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Поле ввода токена
        entry_var = tk.StringVar(value=self.token or "")
        entry = ttk.Entry(content_frame, textvariable=entry_var, width=70, show="*")
        entry.pack(fill=tk.X, pady=(0, 20))
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        # Фрейм для кнопок
        action_buttons_frame = ttk.Frame(content_frame)
        action_buttons_frame.pack(fill=tk.X)
        
        def on_ok():
            token = entry_var.get().strip()
            if not token:
                messagebox.showerror("Ошибка", "Токен не может быть пустым")
                return
            dotenv_path = find_dotenv(usecwd=True) or ".env"
            set_key(dotenv_path, "VK_ACCESS_TOKEN", token)
            self.token = token
            result[0] = token
            dialog.destroy()
            messagebox.showinfo("Успех", "Токен обновлен")
        
        def on_cancel():
            result[0] = None
            dialog.destroy()
        
        def on_enter(event):
            on_ok()
        
        # Кнопки
        ok_btn = ttk.Button(action_buttons_frame, text="Сохранить токен", command=on_ok)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(action_buttons_frame, text="Отмена", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Привязываем Enter
        entry.bind('<Return>', on_enter)
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Ждем закрытия окна
        dialog.wait_window()
        
        return result[0]
    
    def _copy_link(self, queue_item):
        """Копирует ссылку на видео"""
        if queue_item.get("result_link"):
            self._copy_to_clipboard(queue_item["result_link"])
    
    def _reset_item_status(self, queue_item):
        """Сбрасывает статус элемента в pending"""
        queue_item["status"] = "pending"
        queue_item["progress"] = 0
        if "result_link" in queue_item:
            del queue_item["result_link"]
        self.dq._save()
        self._refresh_queue_ui()
    
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
        # Разрешаем удалять любые элементы
        self._delete_item(queue_item)
    
    def _delete_all_queue(self):
        """Удаляет все записи из очереди"""
        if messagebox.askyesno("Подтверждение", "Удалить ВСЕ записи из очереди?"):
            self.dq.items = []
            self.dq._save()
            self._refresh_queue_ui()
    
    def _clear_queue(self):
        """Очищает очередь от завершенных и ошибок, оставляет только pending"""
        if messagebox.askyesno("Подтверждение", "Очистить очередь от завершенных и ошибочных элементов?\nОставятся только ожидающие обработки."):
            self.dq.items = [item for item in self.dq.items if item.get("status") == "pending"]
            self.dq._save()
            self._refresh_queue_ui()
    
    def _open_temp_folder(self):
        """Открывает папку программы во временной директории"""
        import tempfile
        import subprocess
        import platform
        
        # Получаем путь к папке программы
        temp_dir = tempfile.gettempdir()
        app_temp_dir = os.path.join(temp_dir, "youvk-pullpush")
        
        # Создаем папку, если её нет
        os.makedirs(app_temp_dir, exist_ok=True)
        
        try:
            if platform.system() == 'Windows':
                os.startfile(app_temp_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', app_temp_dir])
            else:  # Linux
                subprocess.Popen(['xdg-open', app_temp_dir])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {str(e)}\nПуть: {app_temp_dir}")
    
    def _stop_processing(self):
        """Останавливает обработку очереди"""
        if self.is_processing:
            self.stop_processing_flag = True
            self.is_processing = False
            self.start_btn.config(state=tk.NORMAL, text="Начать обработку")
            self.stop_btn.config(state=tk.DISABLED)
            # Сбрасываем зависшие состояния в pending
            self._reset_stuck_items()
            messagebox.showinfo("Информация", "Обработка остановлена")
    
    def _reset_stuck_items(self):
        """Сбрасывает зависшие состояния (98%, загрузка и т.д.) обратно в pending"""
        reset_count = 0
        for item in self.dq.items:
            status = item.get("status", "")
            # Если статус содержит загрузку или прогресс, но не завершен и не ошибка
            if status not in ("done", "pending") and not status.startswith("error"):
                if any(keyword in status for keyword in ["📥", "📤", "🔄", "Загрузка", "Скачивание", "Конвертация"]):
                    item["status"] = "pending"
                    item["progress"] = 0
                    reset_count += 1
        if reset_count > 0:
            self.dq._save()
            self._refresh_queue_ui()
            messagebox.showinfo("Информация", f"Сброшено {reset_count} зависших элементов в состояние 'Ожидание'")
    
    def _continue_processing(self):
        """Продолжает выполнение после скачивания в раздельном режиме"""
        if self.is_processing:
            return
        
        # Проверяем наличие скачанных файлов
        downloaded_items = [item for item in self.dq.items if item.get("status") == "downloaded" or item.get("downloaded_filepath")]
        if not downloaded_items:
            messagebox.showwarning("Предупреждение", "Нет скачанных видео для загрузки")
            return
        
        self.is_processing = True
        self.waiting_for_upload = False
        self.stop_processing_flag = False
        self.continue_btn.config(state=tk.DISABLED, text="Загрузка...")
        self.stop_btn.config(state=tk.NORMAL)
        
        from core.vk import VKUploader
        
        def progress_hook(url, status, progress=None):
            """Хук для обновления прогресса"""
            # Извлекаем прогресс из статуса, если он не передан явно
            if progress is None and "%" in status:
                try:
                    # Пытаемся извлечь число перед символом %
                    import re
                    match = re.search(r'(\d+\.?\d*)%', status)
                    if match:
                        progress = float(match.group(1))
                except:
                    pass
            
            # Обновляем статус в очереди
            self.dq.update_status(url, status, progress=progress)
            
            # Обновляем UI в главном потоке
            self.root.after(0, self._refresh_queue_ui)
        
        def upload_thread():
            uploader = VKUploader(self.token)
            
            try:
                for item in downloaded_items:
                    if self.stop_processing_flag:
                        break
                    
                    url = item["url"]
                    filepath = item.get("downloaded_filepath")
                    
                    if not filepath or not os.path.exists(filepath):
                        self.dq.update_status(url, "error: Файл не найден")
                        self.root.after(0, self._refresh_queue_ui)
                        continue
                    
                    try:
                        # Начинаем загрузку - устанавливаем начальный статус
                        self.dq.update_status(url, "📤 Загрузка в VK: 0%", progress=0)
                        self.root.after(0, self._refresh_queue_ui)
                        
                        print(f"[VK Upload] Начинаем загрузку видео: {item.get('final_title', 'Без названия')}")
                        
                        # Функция для отслеживания прогресса загрузки
                        def upload_progress(bytes_uploaded, total_bytes, progress_percent):
                            # Обновляем статус и прогресс через единый механизм
                            status_text = f"📤 Загрузка в VK: {progress_percent:.1f}%"
                            self.dq.update_status(url, status_text, progress=progress_percent)
                            # Обновляем UI в главном потоке
                            self.root.after(0, self._refresh_queue_ui)
                        
                        result = uploader.upload_video(
                            filepath=filepath,
                            title=item.get("final_title", "Видео с YouTube"),
                            description=item.get("description", f"Источник: {url}"),
                            privacy_view=item.get("privacy", "3"),
                            progress_callback=upload_progress
                        )
                        
                        print(f"[VK Upload] Видео успешно загружено: {result['link']}")
                        
                        # Сохраняем результат с правильным статусом
                        self.dq.update_status(url, "done", result_link=result["link"], progress=100)
                        # Обновляем UI
                        self.root.after(0, self._refresh_queue_ui)
                        
                        # Сохраняем owner_id и video_id для возможности переименования
                        item["owner_id"] = result.get("owner_id")
                        item["video_id"] = result.get("video_id")
                        
                        # Удаляем временные данные
                        if "downloaded_filepath" in item:
                            del item["downloaded_filepath"]
                        if "final_title" in item:
                            del item["final_title"]
                        if "description" in item:
                            del item["description"]
                        
                    except Exception as e:
                        error_msg = str(e)
                        print(f"[VK Upload] Ошибка при загрузке видео: {error_msg}")
                        self.dq.update_status(url, f"error: {error_msg}")
                        self.root.after(0, self._refresh_queue_ui)
                    
                    # Пауза только между видео (не после последнего и не после ошибок)
                    if self.stop_processing_flag:
                        break
                    
                    # Проверяем, есть ли следующее видео в списке
                    current_index = downloaded_items.index(item)
                    is_last = current_index == len(downloaded_items) - 1
                    
                    # Применяем паузу только если есть следующее видео и загрузка была успешной
                    if not is_last and self.dq.delay > 0:
                        # Проверяем, что загрузка была успешной (status == "done")
                        item_status = None
                        for queue_item in self.dq.items:
                            if queue_item["url"] == url:
                                item_status = queue_item.get("status")
                                break
                        
                        if item_status == "done":
                            # Пауза с счетчиком обратного отсчета
                            for remaining in range(self.dq.delay, 0, -1):
                                if self.stop_processing_flag:
                                    break
                                self.dq.update_status(url, f"⏳ Пауза {self.dq.delay} сек... (осталось {remaining} сек)")
                                self.root.after(0, self._refresh_queue_ui)
                                import time
                                time.sleep(1)
            finally:
                self.is_processing = False
                self.stop_processing_flag = False
                self.waiting_for_upload = False
                self.dq._save()
                self.root.after(0, lambda: self.continue_btn.config(state=tk.DISABLED, text="Продолжить выполнение"))
                self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                self.root.after(0, self._refresh_queue_ui)
                # Обновляем вкладку "Мои видео" после завершения загрузки
                self.root.after(0, self._refresh_videos_tab)
                if not self.stop_processing_flag:
                    self.root.after(0, lambda: messagebox.showinfo("Успех", "Загрузка завершена"))
        
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
        
        # Запускаем автообновление UI
        self._start_auto_refresh()
    
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
    
            self._refresh_queue_ui()
    
    def _move_item_up(self, queue_item):
        """Перемещает элемент вверх"""
        if self.dq.move_item(queue_item["url"], "up"):
            self._refresh_queue_ui()
    
    def _move_item_down(self, queue_item):
        """Перемещает элемент вниз"""
        if self.dq.move_item(queue_item["url"], "down"):
            self._refresh_queue_ui()
            
    def _start_processing(self):
        if self.is_processing:
            return
        
        # Проверяем, есть ли что обрабатывать
        pending = self.dq.get_pending_urls()
        if not pending:
            messagebox.showwarning("Предупреждение", "Нет элементов для обработки")
            return
            
        self.is_processing = True
        self.waiting_for_upload = False
        self.stop_processing_flag = False
        self.start_btn.config(state=tk.DISABLED, text="Обработка...")
        self.stop_btn.config(state=tk.NORMAL)
        self.continue_btn.config(state=tk.DISABLED)
        
        from core.youtube import YouTubeDownloader
        from core.vk import VKUploader
        
        def progress_hook(url, status, progress=None):
            """Хук для обновления прогресса"""
            # Извлекаем прогресс из статуса, если он не передан явно
            if progress is None and "%" in status:
                try:
                    # Пытаемся извлечь число перед символом %
                    import re
                    match = re.search(r'(\d+\.?\d*)%', status)
                    if match:
                        progress = float(match.group(1))
                except:
                    pass
            
            # Обновляем статус в очереди
            self.dq.update_status(url, status, progress=progress)
            
            # Обновляем UI в главном потоке
            self.root.after(0, self._refresh_queue_ui)
            
        def process_thread():
            downloader = YouTubeDownloader(progress_hook=progress_hook)
            uploader = VKUploader(self.token)
            
            separate_mode = self.separate_download_var.get()
            
            try:
                pending = self.dq.get_pending_urls()
                
                # Если включен раздельный режим - сначала скачиваем все
                if separate_mode:
                    for item in pending:
                        if self.stop_processing_flag:
                            break
                        
                        url = item["url"]
                        try:
                            # Получаем информацию о видео
                            self.dq.update_status(url, "📥 Получение информации...", progress=0)
                            self.root.after(0, self._refresh_queue_ui)
                            
                            try:
                                video_info = downloader.get_info(url)
                                extracted_title = video_info.get("title") or "Видео с YouTube"
                                self.dq.update_status(url, "📥 Скачивание...", extracted_title=extracted_title)
                                self.root.after(0, self._refresh_queue_ui)
                            except Exception:
                                extracted_title = None
                            
                            if self.stop_processing_flag:
                                break
                            
                            # Скачиваем видео
                            video_info = downloader.download(url)
                            final_title = item.get("custom_title") or extracted_title or video_info.get("title") or "Видео с YouTube"
                            
                            # Сохраняем информацию о скачанном файле для последующей загрузки
                            item["downloaded_filepath"] = video_info['filepath']
                            item["final_title"] = final_title
                            item["description"] = video_info.get("description") or f"Источник: {video_info.get('webpage_url', url)}"
                            
                            # Ставим статус "downloaded" - готово к загрузке
                            self.dq.update_status(url, "downloaded", progress=100)
                            self.root.after(0, self._refresh_queue_ui)
                            # Сохраняем очередь после каждого скачивания
                            self.dq._save()
                            
                        except Exception as e:
                            self.dq.update_status(url, f"error: {str(e)}")
                            self.root.after(0, self._refresh_queue_ui)
                    
                    # После скачивания всех файлов ставим на паузу
                    if not self.stop_processing_flag:
                        self.waiting_for_upload = True
                        self.dq._save()
                        # Сбрасываем флаги и обновляем UI в главном потоке
                        def finish_download():
                            # ВАЖНО: сначала сбрасываем is_processing, потом обновляем UI
                            self.is_processing = False
                            self.stop_processing_flag = False
                            self.start_btn.config(state=tk.NORMAL, text="Начать обработку")
                            self.stop_btn.config(state=tk.DISABLED)
                            # Проверяем статусы перед обновлением UI
                            downloaded_count = len([item for item in self.dq.items if item.get("status") == "downloaded" or item.get("downloaded_filepath")])
                            print(f"DEBUG finish_download: downloaded_count={downloaded_count}, is_processing={self.is_processing}")
                            # Обновляем UI - это должно активировать кнопку
                            self._refresh_queue_ui()
                            # Дополнительная проверка и активация кнопки на всякий случай
                            if downloaded_count > 0:
                                self.continue_btn.config(state=tk.NORMAL)
                                print("DEBUG: Кнопка активирована явно")
                            messagebox.showinfo("Информация", 
                                "Все видео скачаны!\nПереключите сетевые настройки и нажмите 'Продолжить выполнение' для загрузки на VK")
                        self.root.after(0, finish_download)
                else:
                    # Обычный режим - обрабатываем все сразу
                    for item in pending:
                        if self.stop_processing_flag:
                            break
                        
                        url = item["url"]
                        try:
                            # Получаем информацию о видео
                            self.dq.update_status(url, "📥 Получение информации...", progress=0)
                            self.root.after(0, self._refresh_queue_ui)
                            
                            try:
                                video_info = downloader.get_info(url)
                                extracted_title = video_info.get("title") or "Видео с YouTube"
                                self.dq.update_status(url, "📥 Скачивание...", extracted_title=extracted_title)
                                self.root.after(0, self._refresh_queue_ui)
                            except Exception:
                                extracted_title = None
                            
                            if self.stop_processing_flag:
                                break
                            
                            # Скачиваем видео
                            video_info = downloader.download(url)
                            final_title = item.get("custom_title") or extracted_title or video_info.get("title") or "Видео с YouTube"
                            description = video_info.get("description") or f"Источник: {video_info.get('webpage_url', url)}"

                            if self.stop_processing_flag:
                                break

                            # Загружаем в VK
                            self.dq.update_status(url, "📤 Загрузка в VK: 0%", progress=0)
                            self.root.after(0, self._refresh_queue_ui)
                            
                            print(f"[VK Upload] Начинаем загрузку видео: {final_title}")
                            
                            # Функция для отслеживания прогресса загрузки
                            def upload_progress(bytes_uploaded, total_bytes, progress_percent):
                                # Обновляем статус и прогресс через единый механизм
                                status_text = f"📤 Загрузка в VK: {progress_percent:.1f}%"
                                self.dq.update_status(url, status_text, progress=progress_percent)
                                # Обновляем UI в главном потоке
                                self.root.after(0, self._refresh_queue_ui)
                            
                            result = uploader.upload_video(
                                filepath=video_info['filepath'],
                                title=final_title,
                                description=description,
                                privacy_view=item.get("privacy", "3"),
                                progress_callback=upload_progress
                            )

                            print(f"[VK Upload] Видео успешно загружено: {result['link']}")

                            # Сохраняем результат с правильным статусом
                            self.dq.update_status(url, "done", result_link=result["link"], progress=100)
                            # Обновляем UI
                            self.root.after(0, self._refresh_queue_ui)
                            
                            # Сохраняем owner_id и video_id для возможности переименования
                            item["owner_id"] = result.get("owner_id")
                            item["video_id"] = result.get("video_id")

                        except Exception as e:
                            error_msg = str(e)
                            print(f"[VK Upload] Ошибка при загрузке видео: {error_msg}")
                            self.dq.update_status(url, f"error: {error_msg}")
                            self.root.after(0, self._refresh_queue_ui)

                        if self.stop_processing_flag:
                            break

                        # Пауза только между видео (не после последнего и не после ошибок)
                        # Проверяем, есть ли следующее видео в списке
                        current_index = pending.index(item)
                        is_last = current_index == len(pending) - 1
                        
                        # Применяем паузу только если есть следующее видео и загрузка была успешной
                        if not is_last and self.dq.delay > 0:
                            # Проверяем, что загрузка была успешной (status == "done")
                            item_status = None
                            for queue_item in self.dq.items:
                                if queue_item["url"] == url:
                                    item_status = queue_item.get("status")
                                    break
                            
                            if item_status == "done":
                                # Пауза с счетчиком обратного отсчета
                                for remaining in range(self.dq.delay, 0, -1):
                                    if self.stop_processing_flag:
                                        break
                                    self.dq.update_status(url, f"⏳ Пауза {self.dq.delay} сек... (осталось {remaining} сек)")
                                    self.root.after(0, self._refresh_queue_ui)
                                    import time
                                    time.sleep(1)
            finally:
                # В раздельном режиме уже обновили UI выше в блоке после скачивания
                if not (separate_mode and self.waiting_for_upload):
                    self.is_processing = False
                    self.stop_processing_flag = False
                    self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL, text="Начать обработку"))
                    self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
                    self.root.after(0, self._refresh_queue_ui)
                    if not self.waiting_for_upload and not self.stop_processing_flag:
                        self.root.after(0, lambda: messagebox.showinfo("Успех", "Обработка завершена"))
            
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()
        
        # Запускаем автообновление UI
        self._start_auto_refresh()
        
    def _start_auto_refresh(self):
        """Запускает автообновление UI каждые 200мс для более плавного отображения прогресса"""
        if self.is_processing or self.waiting_for_upload:
            self._refresh_queue_ui()
            self.refresh_timer = self.root.after(200, self._start_auto_refresh)
        else:
            if self.refresh_timer:
                self.root.after_cancel(self.refresh_timer)
                self.refresh_timer = None
            # Финальное обновление UI после остановки обработки
            self._refresh_queue_ui()
            
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
        
        # Подменю для изменения приватности
        privacy_menu = tk.Menu(menu, tearoff=0)
        privacy_menu.add_command(label="Доступно всем", command=lambda: self._change_privacy(owner_id, video_id, "0"))
        privacy_menu.add_command(label="Доступно по ссылке", command=lambda: self._change_privacy(owner_id, video_id, "3"))
        privacy_menu.add_command(label="Только мне", command=lambda: self._change_privacy(owner_id, video_id, "2"))
        menu.add_cascade(label="Приватность", menu=privacy_menu)
        
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
    
    def _change_privacy(self, owner_id, video_id, privacy_view):
        """Изменяет приватность видео"""
        privacy_names = {"0": "Доступно всем", "3": "Доступно по ссылке", "2": "Только мне"}
        try:
            from core.vk import VKUploader
            uploader = VKUploader(self.token)
            if uploader.change_privacy(owner_id, video_id, privacy_view):
                messagebox.showinfo("Успех", f"Приватность изменена на: {privacy_names.get(privacy_view, privacy_view)}")
                self._refresh_videos_tab()
                if hasattr(self, 'all_vk_videos_tree'):
                    self._refresh_all_vk_videos_tab()
            else:
                messagebox.showerror("Ошибка", "Не удалось изменить приватность")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка изменения приватности: {str(e)}")
    
    def _rename_vk_video_from_queue(self, queue_item):
        """Переименовывает видео на VK из очереди"""
        # Если видео уже загружено на VK
        if queue_item.get("owner_id") and queue_item.get("video_id"):
            owner_id = queue_item["owner_id"]
            video_id = queue_item["video_id"]
            current_title = queue_item.get("custom_title") or queue_item.get("extracted_title") or queue_item.get("url", "")
            
            new_title = self._custom_input_dialog(
                "Переименование видео на VK",
                f"Введите новое название для видео:\n{current_title[:50]}",
                current_title[:200]
            )
            
            if new_title:
                try:
                    from core.vk import VKUploader
                    uploader = VKUploader(self.token)
                    success = uploader.rename_video(owner_id, video_id, new_title)
                    
                    if success:
                        # Обновляем название в очереди
                        queue_item["custom_title"] = new_title
                        self.dq._save()
                        self._refresh_queue_ui()
                        messagebox.showinfo("Успех", "Видео успешно переименовано на VK")
                    else:
                        messagebox.showerror("Ошибка", "Не удалось переименовать видео")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка переименования: {str(e)}")
        else:
            # Если видео еще не загружено - просто меняем название для будущей загрузки
            current_title = queue_item.get("custom_title") or queue_item.get("extracted_title") or queue_item.get("url", "")
            
            new_title = self._custom_input_dialog(
                "Изменение названия видео",
                f"Введите новое название для видео:\n{current_title[:50]}",
                current_title[:200]
            )
            
            if new_title:
                queue_item["custom_title"] = new_title
                self.dq._save()
                self._refresh_queue_ui()
                messagebox.showinfo("Успех", "Название изменено. Будет использовано при загрузке на VK")
    
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
        
    def _build_all_vk_videos_tab(self, parent):
        """Создает вкладку для просмотра всех видео с канала ВК"""
        # Заголовок с кнопками
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(header_frame, text="Все видео с канала ВК", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Обновить", command=self._refresh_all_vk_videos_tab).pack(side=tk.RIGHT, padx=5)
        
        # Фрейм для списка видео
        videos_container = ttk.Frame(parent)
        videos_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Создаем Treeview для видео
        columns = ("title", "link", "privacy", "actions")
        self.all_vk_videos_tree = ttk.Treeview(videos_container, columns=columns, show="headings", height=20)
        
        self.all_vk_videos_tree.heading("title", text="Название")
        self.all_vk_videos_tree.heading("link", text="Ссылка VK")
        self.all_vk_videos_tree.heading("privacy", text="Приватность")
        self.all_vk_videos_tree.heading("actions", text="Действия")
        
        self.all_vk_videos_tree.column("title", width=350)
        self.all_vk_videos_tree.column("link", width=250)
        self.all_vk_videos_tree.column("privacy", width=150)
        self.all_vk_videos_tree.column("actions", width=150)
        
        scrollbar_videos = ttk.Scrollbar(videos_container, orient=tk.VERTICAL, command=self.all_vk_videos_tree.yview)
        self.all_vk_videos_tree.configure(yscrollcommand=scrollbar_videos.set)
        
        self.all_vk_videos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_videos.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.all_vk_videos_tree.bind("<Double-1>", self._on_all_vk_video_double_click)
        self.all_vk_videos_tree.bind("<Button-3>", self._on_all_vk_video_right_click)
        
        self._refresh_all_vk_videos_tab()
    
    def _refresh_all_vk_videos_tab(self):
        """Обновляет список всех видео ВК"""
        # Очищаем treeview
        for item in self.all_vk_videos_tree.get_children():
            self.all_vk_videos_tree.delete(item)
        
        try:
            from core.vk import VKUploader
            uploader = VKUploader(self.token)
            videos = uploader.get_all_videos(count=500)
            
            if not videos:
                self.all_vk_videos_tree.insert("", "end", values=("Нет видео", "", "", ""))
            else:
                privacy_names = {"0": "Доступно всем", "3": "Доступно по ссылке", "2": "Только мне"}
                for video in videos:
                    title = video.get('title', 'Без названия')
                    link = video.get('link', '')
                    privacy_view = video.get('privacy_view', '3')
                    privacy_text = privacy_names.get(privacy_view, "Неизвестно")
                    self.all_vk_videos_tree.insert("", "end", values=(title, link, privacy_text, "Действия"))
        except Exception as e:
            self.all_vk_videos_tree.insert("", "end", values=(f"Ошибка загрузки: {str(e)}", "", "", ""))
    
    def _on_all_vk_video_double_click(self, event):
        """Обработка двойного клика по видео из всех видео ВК"""
        selection = self.all_vk_videos_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.all_vk_videos_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 4:
            return
        
        link = values[1]
        if link:
            self._copy_to_clipboard(link)
    
    def _on_all_vk_video_right_click(self, event):
        """Обработка правого клика по видео из всех видео ВК"""
        selection = self.all_vk_videos_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.all_vk_videos_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 4:
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
        
        # Подменю для изменения приватности
        privacy_menu = tk.Menu(menu, tearoff=0)
        privacy_menu.add_command(label="Доступно всем", command=lambda: self._change_privacy_all_vk(owner_id, video_id, "0"))
        privacy_menu.add_command(label="Доступно по ссылке", command=lambda: self._change_privacy_all_vk(owner_id, video_id, "3"))
        privacy_menu.add_command(label="Только мне", command=lambda: self._change_privacy_all_vk(owner_id, video_id, "2"))
        menu.add_cascade(label="Приватность", menu=privacy_menu)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _change_privacy_all_vk(self, owner_id, video_id, privacy_view):
        """Изменяет приватность видео для вкладки всех видео ВК"""
        self._change_privacy(owner_id, video_id, privacy_view)
        self._refresh_all_vk_videos_tab()
    
    def _build_yt_parse_tab(self, parent):
        """Создает вкладку для парсинга канала YouTube"""
        # Заголовок
        title_label = ttk.Label(parent, text="Парсинг канала YouTube", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Поле для URL канала
        url_frame = ttk.Frame(parent)
        url_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(url_frame, text="Ссылка на канал YouTube:").pack(side=tk.LEFT, padx=5)
        self.yt_channel_url_var = tk.StringVar()
        yt_channel_entry = ttk.Entry(url_frame, textvariable=self.yt_channel_url_var, width=60)
        yt_channel_entry.pack(side=tk.LEFT, padx=10)
        yt_channel_entry.bind('<Return>', lambda e: self._parse_yt_channel())
        
        parse_btn = ttk.Button(url_frame, text="Парсить канал", command=self._parse_yt_channel)
        parse_btn.pack(side=tk.LEFT, padx=5)
        
        # Информация
        info_label = ttk.Label(parent, text="Введите ссылку на канал YouTube или плейлист\n(например: https://www.youtube.com/@channel или ссылка с параметром list=...)",
                              foreground=self.text_secondary, font=('Arial', 9))
        info_label.pack(pady=5)
        
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Фрейм для результатов
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(results_frame, text="Видео канала:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Создаем Treeview для результатов
        columns = ("title", "url", "actions")
        self.yt_parse_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)
        
        self.yt_parse_tree.heading("title", text="Название видео")
        self.yt_parse_tree.heading("url", text="URL")
        self.yt_parse_tree.heading("actions", text="Действия")
        
        self.yt_parse_tree.column("title", width=400)
        self.yt_parse_tree.column("url", width=300)
        self.yt_parse_tree.column("actions", width=200)
        
        scrollbar_parse = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.yt_parse_tree.yview)
        self.yt_parse_tree.configure(yscrollcommand=scrollbar_parse.set)
        
        self.yt_parse_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_parse.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.yt_parse_tree.bind("<Double-1>", self._on_yt_parse_double_click)
        self.yt_parse_tree.bind("<Button-3>", self._on_yt_parse_right_click)
        
        # Кнопки управления
        parse_controls = ttk.Frame(results_frame)
        parse_controls.pack(fill=tk.X, pady=10)
        
        ttk.Button(parse_controls, text="Добавить все в очередь", command=self._add_all_parsed_to_queue).pack(side=tk.LEFT, padx=5)
        ttk.Button(parse_controls, text="Очистить список", command=self._clear_yt_parse_results).pack(side=tk.LEFT, padx=5)
        
        # Переменная для хранения распарсенных видео
        self.parsed_yt_videos = []
    
    def _parse_yt_channel(self):
        """Парсит канал YouTube и отображает список видео"""
        url = self.yt_channel_url_var.get().strip()
        if not url:
            messagebox.showwarning("Предупреждение", "Введите ссылку на канал YouTube")
            return
        
        def parse_thread():
            try:
                import yt_dlp
                import re
                
                # Извлекаем ID плейлиста из ссылки, если она содержит параметр list=
                if 'list=' in url:
                    match = re.search(r'list=([^&]+)', url)
                    if match:
                        playlist_id = match.group(1)
                        # Формируем прямую ссылку на плейлист
                        url_to_parse = f"https://www.youtube.com/playlist?list={playlist_id}"
                    else:
                        url_to_parse = url
                else:
                    url_to_parse = url
                
                # Опции для парсинга канала/плейлиста
                ydl_opts = {
                    'quiet': True,
                    'extract_flat': 'playlist',  # Извлекаем плоскую структуру для плейлиста, но получаем информацию о видео
                    'ignoreerrors': True,  # Продолжать при ошибках с отдельными видео
                    'no_warnings': True,
                    'playlistend': 500,  # Ограничиваем количество видео
                    'skip_unavailable_fragments': True,
                }
                
                parsed_videos = []
                errors_count = 0
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Извлекаем информацию о канале/плейлисте
                    try:
                        info = ydl.extract_info(url_to_parse, download=False)
                    except Exception as e:
                        # Если не удалось получить информацию о плейлисте целиком
                        raise Exception(f"Не удалось получить информацию о канале/плейлисте: {str(e)}")
                    
                    if not info:
                        raise Exception("Не удалось получить информацию о канале/плейлисте")
                    
                    # Получаем список видео
                    entries = info.get('entries', [])
                    
                    # Если entries - это генератор или None, конвертируем в список
                    if entries is None:
                        entries = []
                    elif hasattr(entries, '__iter__') and not isinstance(entries, (list, tuple)):
                        entries = list(entries)
                    
                    if not entries:
                        # Если это одно видео, а не канал/плейлист
                        if info.get('webpage_url') or info.get('url'):
                            video_url = info.get('webpage_url') or info.get('url')
                            title = info.get('title') or info.get('fulltitle') or video_url
                            parsed_videos.append({
                                'title': title,
                                'url': video_url
                            })
                        else:
                            raise Exception("Не найдено видео. Проверьте правильность ссылки.")
                    else:
                        # Обрабатываем все видео из канала/плейлиста
                        for entry in entries:
                            if entry:
                                try:
                                    # Получаем URL и название
                                    video_url = entry.get('webpage_url') or entry.get('url')
                                    if not video_url:
                                        # Если есть только ID, формируем URL
                                        video_id = entry.get('id')
                                        if video_id:
                                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                                        else:
                                            errors_count += 1
                                            continue
                                    
                                    if video_url:
                                        # Используем доступные поля для названия
                                        # В режиме extract_flat может не быть title, поэтому используем name или url
                                        title = entry.get('title') or entry.get('fulltitle') or entry.get('name') or video_url
                                        
                                        # Если название не получено, пытаемся получить его отдельно (опционально)
                                        if title == video_url or not title:
                                            try:
                                                # Быстрая попытка получить название без полной загрузки
                                                video_info = ydl.extract_info(video_url, download=False)
                                                title = video_info.get('title') or video_info.get('fulltitle') or title
                                            except:
                                                # Если не удалось, используем URL как название
                                                pass
                                        
                                        parsed_videos.append({
                                            'title': title,
                                            'url': video_url
                                        })
                                except Exception as e:
                                    # Пропускаем проблемные видео, но продолжаем парсинг
                                    errors_count += 1
                                    continue
                
                if not parsed_videos:
                    raise Exception("Не найдено видео. Возможно, канал/плейлист пуст или все видео недоступны.")
                
                self.parsed_yt_videos = parsed_videos
                
                # Формируем сообщение об успехе
                success_msg = f"Найдено {len(parsed_videos)} видео"
                if errors_count > 0:
                    success_msg += f"\nПропущено {errors_count} недоступных видео (возрастные ограничения, не начавшиеся трансляции и т.д.)"
                
                # Обновляем UI в главном потоке
                self.root.after(0, lambda: self._refresh_yt_parse_results())
                self.root.after(0, lambda: messagebox.showinfo("Успех", success_msg))
            except Exception as e:
                import traceback
                error_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка парсинга: {error_msg}"))
        
        threading.Thread(target=parse_thread, daemon=True).start()
    
    def _refresh_yt_parse_results(self):
        """Обновляет список распарсенных видео"""
        # Очищаем treeview
        for item in self.yt_parse_tree.get_children():
            self.yt_parse_tree.delete(item)
        
        if not self.parsed_yt_videos:
            self.yt_parse_tree.insert("", "end", values=("Нет видео", "", ""))
        else:
            for video in self.parsed_yt_videos:
                title = video.get('title', 'Без названия')
                url = video.get('url', '')
                if len(title) > 60:
                    title = title[:57] + "..."
                self.yt_parse_tree.insert("", "end", values=(title, url, "📋 Копировать|Добавить в очередь"))
    
    def _on_yt_parse_double_click(self, event):
        """Обработка двойного клика по распарсенному видео"""
        selection = self.yt_parse_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.yt_parse_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 3:
            return
        
        url = values[1]
        if url:
            self._copy_to_clipboard(url)
    
    def _on_yt_parse_right_click(self, event):
        """Обработка правого клика по распарсенному видео"""
        selection = self.yt_parse_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.yt_parse_tree.item(item_id)
        values = item["values"]
        
        if len(values) < 3:
            return
        
        url = values[1]
        title = values[0]
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📋 Копировать URL", command=lambda: self._copy_to_clipboard(url))
        menu.add_command(label="Добавить в очередь", command=lambda: self._add_parsed_to_queue(url))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _add_parsed_to_queue(self, url):
        """Добавляет одно распарсенное видео в очередь"""
        self.dq.add_url(url, None, "3")
        self._refresh_queue_ui()
        messagebox.showinfo("Успех", "Видео добавлено в очередь")
    
    def _add_all_parsed_to_queue(self):
        """Добавляет все распарсенные видео в очередь"""
        if not self.parsed_yt_videos:
            messagebox.showwarning("Предупреждение", "Нет видео для добавления")
            return
        
        count = 0
        for video in self.parsed_yt_videos:
            url = video.get('url')
            if url:
                self.dq.add_url(url, None, "3")
                count += 1
        
        self._refresh_queue_ui()
        messagebox.showinfo("Успех", f"Добавлено {count} видео в очередь")
    
    def _clear_yt_parse_results(self):
        """Очищает список распарсенных видео"""
        self.parsed_yt_videos = []
        self._refresh_yt_parse_results()
        
    def run(self):
        self.root.mainloop()

def main():
    app = YouVkAppTkinter()
    app.run()

if __name__ == "__main__":
    main()
