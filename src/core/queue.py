# src/core/queue.py
import os
import json
import time
import yt_dlp
from typing import List, Callable, Optional

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "..", "queue.json")

class DownloadQueue:
    def __init__(self):
        self.items = []
        self.delay = 10
        self._load()

    def _load(self):
        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.delay = data.get("delay_between_videos_sec", 10)
                    self.items = data.get("items", [])
            except Exception:
                pass

    def _save(self):
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "delay_between_videos_sec": self.delay,
                "items": self.items
            }, f, ensure_ascii=False, indent=2)

    def add_url(self, url: str, custom_title: Optional[str] = None, privacy: str = "3"):
        url = url.strip()
        if not url:
            return
        for item in self.items:
            if item["url"] == url:
                return
        self.items.append({
            "url": url,
            "custom_title": custom_title,
            "privacy": privacy,
            "status": "pending",
            "result_link": None
        })
        self._save()

    def add_channel_or_playlist(self, url: str, privacy: str = "3"):
        """Добавляет все видео из канала или плейлиста в очередь"""
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,  # Изменено на False для получения полной информации
            'force_generic_extractor': False,
            'ignoreerrors': True,  # Продолжать при ошибках с отдельными видео
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Не удалось получить информацию о канале/плейлисте")
                
                # Обрабатываем плейлист или канал
                entries = info.get('entries', [])
                if not entries:
                    # Если это одно видео, добавляем его
                    if info.get('url') or info.get('webpage_url'):
                        video_url = info.get('webpage_url') or info.get('url')
                        if video_url:
                            self.add_url(video_url, privacy=privacy)
                            return 1
                    return 0
                else:
                    # Обрабатываем все видео из плейлиста/канала
                    added_count = 0
                    for entry in entries:
                        if entry:
                            # Получаем URL видео
                            video_url = entry.get('webpage_url') or entry.get('url') or entry.get('id')
                            if video_url:
                                # Если это ID, конвертируем в полный URL
                                if not video_url.startswith('http'):
                                    video_url = f"https://www.youtube.com/watch?v={video_url}"
                                self.add_url(video_url, privacy=privacy)
                                added_count += 1
                    return added_count
        except Exception as e:
            raise Exception(f"Ошибка парсинга канала/плейлиста: {str(e)}")

    def set_delay(self, seconds: int):
        self.delay = max(0, int(seconds))
        self._save()

    def get_pending_urls(self) -> List[dict]:
        return [item for item in self.items if item["status"] == "pending"]

    def update_status(self, url: str, status: str, result_link: Optional[str] = None, progress: Optional[float] = None, extracted_title: Optional[str] = None):
        for item in self.items:
            if item["url"] == url:
                item["status"] = status
                if result_link:
                    item["result_link"] = result_link
                if progress is not None:
                    item["progress"] = progress
                if extracted_title:
                    item["extracted_title"] = extracted_title
                break
        self._save()
    
    def move_item(self, url: str, direction: str):
        """Перемещает элемент в очереди (up/down)"""
        for i, item in enumerate(self.items):
            if item["url"] == url:
                if direction == "up" and i > 0:
                    self.items[i], self.items[i-1] = self.items[i-1], self.items[i]
                    self._save()
                    return True
                elif direction == "down" and i < len(self.items) - 1:
                    self.items[i], self.items[i+1] = self.items[i+1], self.items[i]
                    self._save()
                    return True
        return False
    
    def remove_item(self, url: str):
        """Удаляет элемент из очереди"""
        self.items = [item for item in self.items if item["url"] != url]
        self._save()

    def process_all(self, on_progress: Callable[[str, str, float], None], downloader, uploader):
        pending = self.get_pending_urls()
        for item in pending:
            url = item["url"]
            try:
                # Сначала получаем информацию о видео
                self.update_status(url, "📥 Получение информации...", progress=0)
                on_progress(url, "📥 Получение информации...", 0)
                
                try:
                    video_info = downloader.get_info(url)
                    extracted_title = video_info.get("title") or "Видео с YouTube"
                    self.update_status(url, "📥 Скачивание...", extracted_title=extracted_title)
                except Exception:
                    extracted_title = None
                
                # Скачиваем видео
                video_info = downloader.download(url)
                final_title = item.get("custom_title") or extracted_title or video_info.get("title") or "Видео с YouTube"
                description = video_info.get("description") or f"Источник: {video_info.get('webpage_url', url)}"

                # Загружаем в VK
                self.update_status(url, "📤 Загрузка в VK...", progress=98)
                on_progress(url, "📤 Загрузка в VK...", 98)
                result = uploader.upload_video(
                    filepath=video_info['filepath'],
                    title=final_title,
                    description=description,
                    privacy_view=item.get("privacy", "3")
                )

                self.update_status(url, "done", result["link"], progress=100)
                on_progress(url, f"✅ Готово: {result['link']}", 100)

            except Exception as e:
                self.update_status(url, f"error: {str(e)}")
                on_progress(url, f"❌ Ошибка: {str(e)}", None)

            if self.delay > 0:
                on_progress(url, f"⏳ Пауза {self.delay} сек...", None)
                time.sleep(self.delay)