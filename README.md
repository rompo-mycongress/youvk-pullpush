# YouVK PullPush

Программа для автоматической загрузки видео с YouTube на VK (ВКонтакте).

## Возможности

- Скачивание видео с YouTube
- Автоматическая загрузка на VK
- Парсинг каналов и плейлистов YouTube
- Управление очередью загрузок
- Отслеживание прогресса загрузки
- Переименование видео на VK
- Управление настройками приватности видео

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/rompo-mycongress/youvk-pullpush.git
cd youvk-pullpush
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Настройте токен VK в файле `.env`:
```
VK_ACCESS_TOKEN=your_token_here
```

## Запуск

### Из исходников:
```bash
python src/gui/app.py
```

### Из собранного EXE:
Скачайте готовый `youvk-pullpush.exe` из раздела [Releases](https://github.com/rompo-mycongress/youvk-pullpush/releases) или соберите самостоятельно (см. раздел "Сборка EXE").

## Сборка EXE

Для сборки исполняемого файла используется PyInstaller:

1. Установите PyInstaller:
```bash
pip install pyinstaller
```

2. Соберите EXE:
```bash
pyinstaller youvk-pullpush.spec --clean
```

Готовый файл будет в папке `dist/youvk-pullpush.exe`.

**Примечание:** В собранный exe включен `ffmpeg.exe` для обработки видео. При первом запуске программа создаст папку для временных файлов в системной временной директории.

## Лицензия

Этот проект распространяется под лицензией MIT с дополнительными требованиями об атрибуции.

**При использовании, модификации или распространении этого программного обеспечения вы обязаны:**

1. Включить ссылку на оригинальный репозиторий: https://github.com/rompo-mycongress/youvk-pullpush
2. Указать автора (rompo-mycongress) в документации, титрах или разделе "О программе"
3. Сохранить оригинальное уведомление об авторских правах и лицензию во всех копиях

Подробности см. в файле [LICENSE](LICENSE).

## Автор

**rompo-mycongress**

- GitHub: [@rompo-mycongress](https://github.com/rompo-mycongress)
- Репозиторий: https://github.com/rompo-mycongress/youvk-pullpush

## Вклад в проект

Приветствуются любые улучшения и исправления! Пожалуйста, создавайте Issues и Pull Requests.

