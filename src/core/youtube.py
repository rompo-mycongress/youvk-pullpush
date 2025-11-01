# src/core/youtube.py
import os
import sys
import tempfile
import yt_dlp

def get_ffmpeg_path():
    """Возвращает путь к ffmpeg.exe в зависимости от среды выполнения."""
    if getattr(sys, 'frozen', False):
        # Запущено как скомпилированный .exe (PyInstaller)
        base_path = sys._MEIPASS
    else:
        # Запущено как обычный Python-скрипт
        base_path = os.path.dirname(__file__)
    ffmpeg_exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    return os.path.join(base_path, "..", "bin", ffmpeg_exe)

class YouTubeDownloader:
    def __init__(self, output_dir: str = None, progress_hook=None):
        """
        :param output_dir: Каталог для сохранения видео. Если None — используется временная папка.
        :param progress_hook: Функция для отслеживания прогресса (url, status, progress)
        """
        self.output_dir = output_dir or tempfile.gettempdir()
        self.progress_hook = progress_hook
        self.current_url = None

    def _progress_hook(self, d):
        """Хук для отслеживания прогресса загрузки"""
        if self.progress_hook and self.current_url:
            if d['status'] == 'downloading':
                if 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                    self.progress_hook(self.current_url, f"📥 Скачивание: {progress:.1f}%", progress)
                elif 'total_bytes_estimate' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                    self.progress_hook(self.current_url, f"📥 Скачивание: {progress:.1f}%", progress)
            elif d['status'] == 'finished':
                self.progress_hook(self.current_url, "🔄 Конвертация...", 95)

    def get_info(self, url: str):
        """Получает информацию о видео без скачивания"""
        ffmpeg_path = get_ffmpeg_path()
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'ffmpeg_location': ffmpeg_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title') or info.get('fulltitle') or 'Видео с YouTube',
                'description': info.get('description', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', ''),
                'webpage_url': info.get('webpage_url', url)
            }

    def download(self, url: str):
        """
        Скачивает видео с YouTube.
        :param url: Ссылка на видео
        :return: dict с ключами 'filepath', 'title', 'duration'
        """
        self.current_url = url
        output_template = os.path.join(self.output_dir, "youvk_video_%(id)s.%(ext)s")

        ffmpeg_path = get_ffmpeg_path()
        if not os.path.isfile(ffmpeg_path):
            raise FileNotFoundError(
                f"ffmpeg не найден по пути: {ffmpeg_path}\n"
                "Поместите ffmpeg.exe в папку src/bin/"
            )

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_template,
            'quiet': False,
            'noplaylist': True,
            'no_warnings': False,
            'ffmpeg_location': ffmpeg_path,
        }

        if self.progress_hook:
            ydl_opts['progress_hooks'] = [self._progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)

            # Убедимся, что файл имеет расширение .mp4
            if not filepath.endswith('.mp4'):
                new_filepath = filepath + '.mp4'
                if os.path.exists(filepath):
                    os.rename(filepath, new_filepath)
                    filepath = new_filepath

            return {
                'filepath': filepath,
                'title': info.get('title') or info.get('fulltitle') or 'Видео с YouTube',
                'description': info.get('description', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', ''),
                'webpage_url': info.get('webpage_url', url)
            }