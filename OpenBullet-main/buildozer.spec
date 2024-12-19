!pip install buildozer
!pip install cython

# Instalar dependencias necesarias
!apt-get update
!apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

# Crear directorio de trabajo
!mkdir openbullet
%cd openbullet

# Crear buildozer.spec
%%writefile buildozer.spec
[app]
title = OpenBullet Checker
package.name = openbullet_checker
package.domain = org.openbullet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,loli
version = 1.0
requirements = python3,kivy,requests,plyer

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 31
android.minapi = 21
android.ndk = 23b
android.arch = arm64-v8a
android.presplash_color = #121212

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1

# Crear main.py
%%writefile main.py
# Pega aquí el contenido de tu main.py

# Crear checker.kv
%%writefile checker.kv
# Pega aquí el contenido de tu checker.kv

# Crear OpenBullet.py
%%writefile OpenBullet.py
# Pega aquí el contenido de tu OpenBullet.py

# Construir APK
!buildozer android debug
