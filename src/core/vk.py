# src/core/vk.py
import os
import json
import vk_api
from typing import Optional

UPLOADS_LOG = os.path.join(os.path.dirname(__file__), "..", "uploads.json")

class VKUploader:
    def __init__(self, access_token: str, group_id: Optional[int] = None):
        self.access_token = access_token
        self.group_id = group_id
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk = self.vk_session.get_api()

    def upload_video(self, filepath: str, title: str, description: str = "", privacy_view: str = "3"):
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

        uploader = vk_api.VkUpload(self.vk_session)
        # Название и описание уже переданы через video.save()
        # Теперь загружаем файл на полученный upload_url
        response = uploader.video(
            video_file=filepath,
            upload_url=upload_info['upload_url']
        )

        # 🔥 ИСПРАВЛЕНО: убраны пробелы!
        owner_id = response['owner_id']
        video_id = response['video_id']
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