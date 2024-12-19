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
