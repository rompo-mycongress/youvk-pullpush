# src/main.py
import os
from dotenv import load_dotenv
from youtube import YouTubeDownloader
from vk import VKUploader

def main():
    # Загружаем настройки
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_raw = os.getenv("VK_GROUP_ID", "").strip()

    if not vk_token:
        print("❌ Ошибка: не задан VK_ACCESS_TOKEN в .env")
        return

    # Парсим group_id (если указан)
    group_id = None
    if vk_group_raw:
        try:
            # Убираем минус, если пользователь ввёл "-123"
            gid = vk_group_raw.lstrip('-')
            group_id = int(gid)
        except ValueError:
            print("❌ Ошибка: VK_GROUP_ID должен быть числом (например, -123456789 или 123456789)")
            return

    # Получаем ссылку
    youtube_url = input("Введите ссылку на YouTube видео: ").strip()
    if not youtube_url:
        print("❌ Ссылка не указана.")
        return

    print("\n📥 Скачиваем видео с YouTube...")
    downloader = YouTubeDownloader()
    video_info = downloader.download(youtube_url)
    print(f"✅ Скачано: {video_info['title']} ({video_info['duration']} сек)")

    print("\n📤 Загружаем в VK...")
    uploader = VKUploader(access_token=vk_token, group_id=group_id)
    result = uploader.upload_video(
        filepath=video_info['filepath'],
        title=video_info['title'],
        description=f"Источник: {video_info['webpage_url']}"
    )

    print(f"\n🎉 Успех! Видео загружено.")
    print(f"🔗 Ссылка: https://vk.com/video{result.get('owner_id')}_{result.get('video_id')}")

    # Опционально: удалить временный файл
    try:
        os.remove(video_info['filepath'])
        print("🗑️ Временный файл удалён.")
    except Exception as e:
        print(f"⚠️ Не удалось удалить временный файл: {e}")

if __name__ == "__main__":
    main()

if input("Нужно получить токен VK? (y/n): ").lower() == 'y':
    from auth import get_vk_token
    get_vk_token()