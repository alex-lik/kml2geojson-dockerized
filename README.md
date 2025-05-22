# kml2geojson-dockerized
Automated Google My Maps parser: downloads KML, extracts layer and placemark names, outputs clean GeoJSON. Docker-ready, PostGIS-friendly.

Автоматизированный парсер для публичных Google My Maps: скачивает KML, извлекает имена слоёв и полигонов, сохраняет в GeoJSON. Обёрнут в Docker, готов к импорту в PostGIS.
Этот проект загружает публичную карту Google My Maps в формате KML, парсит её и сохраняет как GeoJSON, включая название слоя (`layer_name`) и объекта (`name`).


## 📦 Установка

```
    bash
    docker-compose build
```
# ▶️ Запуск

bash

```
    docker-compose up
```
После выполнения в текущей папке появится файл map.geojson.

# ⚙️ Настройки
URL карты задаётся внутри скрипта parse_kml_to_geojson.py (константа KML_URL). Поддерживается экспорт только публичных карт.

# 🔧 Зависимости
Python 3.11

shapely
requests

# 📁 Структура
parse_kml_to_geojson.py — основной скрипт.
map.kml — загруженный KML-файл.
map.geojson — результат в формате GeoJSON.
docker-compose.yml + Dockerfile — окружение Docker.