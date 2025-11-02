# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['src/gui/app.py'],
    pathex=['src'],  # Добавляем src в путь поиска модулей
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'dotenv',
        'vk_api',
        'yt_dlp',
        'requests',
        'core.queue',
        'core.vk',
        'core.youtube',
        'gui.app_tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Добавляем ffmpeg.exe как бинарный файл
ffmpeg_path = os.path.join('src', 'bin', 'ffmpeg.exe')
if os.path.exists(ffmpeg_path):
    a.binaries += [('bin/ffmpeg.exe', ffmpeg_path, 'BINARY')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='youvk-pullpush',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Не показывать консольное окно
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

