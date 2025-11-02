# src/core/vk.py
import os
import json
import vk_api
import requests
from typing import Optional

UPLOADS_LOG = os.path.join(os.path.dirname(__file__), "..", "uploads.json")

class VKUploader:
    def __init__(self, access_token: str, group_id: Optional[int] = None):
        self.access_token = access_token
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk = self.vk_session.get_api()

    def upload_video(self, filepath: str, title: str, description: str = "", privacy_view: str = "3", progress_callback=None):
        """
        Загружает видео на VK
        :param progress_callback: Функция для отслеживания прогресса (bytes_uploaded, total_bytes, progress_percent)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не найден: {filepath}")

        safe_title = (title or "").strip()
        if not safe_title:
            safe_title = "Видео с YouTube"

        upload_params = {
            'name': safe_title,
            'description': description,
            'wallpost': 0,
            'is_private': 0,
            'privacy_view': privacy_view,
            'privacy_comment': '0',
        }

        if self.group_id:
            upload_params['group_id'] = self.group_id

        upload_info = self.vk.video.save(**upload_params)

        # Загружаем видео файл напрямую на upload_url через HTTP POST
        upload_url = upload_info['upload_url']
        
        file_size = os.path.getsize(filepath)
        
        # Класс для отслеживания прогресса загрузки
        class ProgressUploadAdapter:
            def __init__(self, file_obj, callback, total_size):
                self.file_obj = file_obj
                self.callback = callback
                self.total_size = total_size
                self.uploaded = 0
            
            def read(self, size=-1):
                chunk = self.file_obj.read(size)
                if chunk and self.callback:
                    self.uploaded += len(chunk)
                    progress = (self.uploaded / self.total_size) * 100 if self.total_size > 0 else 0
                    self.callback(self.uploaded, self.total_size, progress)
                return chunk
        
        with open(filepath, 'rb') as video_file:
            # Используем адаптер для отслеживания прогресса
            progress_file = ProgressUploadAdapter(video_file, progress_callback, file_size)
            files = {'video_file': progress_file}
            upload_response = requests.post(upload_url, files=files, timeout=300)
        
        if upload_response.status_code != 200:
            raise Exception(f"Ошибка загрузки файла: HTTP {upload_response.status_code}")
        
        # После загрузки файла VK возвращает данные о видео
        # Если upload_response содержит JSON с данными о видео, используем его
        # Иначе используем данные из upload_info
        try:
            response_data = upload_response.json()
            if 'owner_id' in response_data and 'video_id' in response_data:
                owner_id = response_data['owner_id']
                video_id = response_data['video_id']
            else:
                # Если в ответе нет данных, используем данные из upload_info
                owner_id = upload_info.get('owner_id')
                video_id = upload_info.get('video_id')
        except:
            # Если ответ не JSON, используем данные из upload_info
            owner_id = upload_info.get('owner_id')
            video_id = upload_info.get('video_id')
        
        # Если owner_id и video_id не найдены, пробуем получить их через video.get
        if not owner_id or not video_id:
            # Пробуем получить видео по имени
            videos = self.vk.video.get(count=1, q=safe_title[:50])
            if videos.get('items'):
                video_item = videos['items'][0]
                owner_id = video_item.get('owner_id')
                video_id = video_item.get('id')
        
        if not owner_id or not video_id:
            raise Exception("Не удалось получить ID загруженного видео")
        
        # Формируем ссылки на видео
        link = f"https://vk.com/video{owner_id}_{video_id}"
        embed_url = f"https://vk.com/video_ext.php?oid={owner_id}&id={video_id}"

        self._log_upload({
            "title": safe_title,
            "description": description,
            "link": link,
            "embed_url": embed_url,
            "owner_id": owner_id,
            "video_id": video_id,
            "filepath": filepath
        })

        return {
            "title": safe_title,
            "description": description,
            "link": link,
            "embed_url": embed_url,
            "owner_id": owner_id,
            "video_id": video_id
        }

    def _log_upload(self, record: dict):
        try:
            if os.path.exists(UPLOADS_LOG):
                with open(UPLOADS_LOG, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
        except Exception:
            data = []

        if not any(item.get("video_id") == record["video_id"] for item in data):
            data.append(record)
            with open(UPLOADS_LOG, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def get_uploaded_videos(self):
        if not os.path.exists(UPLOADS_LOG):
            return []
        try:
            with open(UPLOADS_LOG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    
    def rename_video(self, owner_id: int, video_id: int, new_title: str):
        """Переименовывает видео на ВК"""
        try:
            result = self.vk.video.edit(
                owner_id=owner_id,
                video_id=video_id,
                name=new_title
            )
            # Обновляем локальный лог
            if os.path.exists(UPLOADS_LOG):
                try:
                    with open(UPLOADS_LOG, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for item in data:
                        if item.get("owner_id") == owner_id and item.get("video_id") == video_id:
                            item["title"] = new_title
                            break
                    with open(UPLOADS_LOG, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            return result == 1
        except Exception as e:
            raise Exception(f"Ошибка переименования: {str(e)}")
    
    def change_privacy(self, owner_id: int, video_id: int, privacy_view: str):
        """Изменяет настройки приватности видео на ВК
        privacy_view: "0" - всем, "3" - по ссылке, "2" - только мне
        """
        try:
            result = self.vk.video.edit(
                owner_id=owner_id,
                video_id=video_id,
                privacy_view=privacy_view
            )
            return result == 1
        except Exception as e:
            raise Exception(f"Ошибка изменения приватности: {str(e)}")
    
    def get_all_videos(self, count: int = 200):
        """Получает все видео пользователя/группы с ВК"""
        try:
            videos = []
            offset = 0
            while True:
                params = {
                    'count': min(200, count - offset),
                    'offset': offset
                }
                if self.group_id:
                    params['owner_id'] = -self.group_id
                
                response = self.vk.video.get(**params)
                items = response.get('items', [])
                if not items:
                    break
                
                for item in items:
                    videos.append({
                        'title': item.get('title', 'Без названия'),
                        'link': f"https://vk.com/video{item.get('owner_id')}_{item.get('id')}",
                        'owner_id': item.get('owner_id'),
                        'video_id': item.get('id'),
                        'embed_url': f"https://vk.com/video_ext.php?oid={item.get('owner_id')}&id={item.get('id')}",
                        'privacy_view': item.get('privacy_view', '3')
                    })
                
                offset += len(items)
                if offset >= count or len(items) < 200:
                    break
            
            return videos
        except Exception as e:
            raise Exception(f"Ошибка получения видео: {str(e)}")