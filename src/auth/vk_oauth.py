# src/auth/vk_oauth.py
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os
from dotenv import set_key

APP_ID = "54287174"
REDIRECT_URI = "http://localhost:8008"
SCOPE = "video"

# Глобальная переменная для передачи токена обратно в Flet
_token_callback = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # HTML-страница, которая извлекает access_token из URL и отправляет его на /token
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>Авторизация VK</title></head>
            <body>
                <p>Авторизация прошла успешно. Перенаправление...</p>
                <script>
                    var hash = window.location.hash.substring(1);
                    if (hash) {
                        fetch('/token?' + hash)
                            .then(() => window.close());
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        elif self.path.startswith("/token"):
            # Извлекаем токен из query string
            query = self.path.split('?', 1)[1]
            params = urllib.parse.parse_qs(query)
            access_token = params.get('access_token', [None])[0]

            if access_token:
                # Сохраняем в .env
                dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
                os.makedirs(os.path.dirname(dotenv_path), exist_ok=True)
                set_key(dotenv_path, "VK_ACCESS_TOKEN", access_token)

                # Вызываем callback (если задан)
                if _token_callback:
                    _token_callback(access_token)

            # Отправляем ответ
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("✅ Авторизация завершена. Можете закрыть это окно.".encode("utf-8"))

            # Останавливаем сервер
            threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        return  # отключаем логи

def start_vk_auth(callback=None):
    """Запускает OAuth-сервер и открывает браузер."""
    global _token_callback
    _token_callback = callback

    server = HTTPServer(("localhost", 8008), OAuthHandler)
    server.allow_reuse_address = True

    auth_url = (
        f"https://oauth.vk.com/authorize?"
        f"client_id={APP_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=token&"
        f"scope={SCOPE}&"
        f"display=page"
    )

    webbrowser.open(auth_url)
    server.serve_forever()