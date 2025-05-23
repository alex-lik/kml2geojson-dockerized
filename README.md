# kml2geojson-dockerized

🇷🇺 Автоматизированный парсер для Google My Maps → PostGIS  
🇬🇧 Automated parser from Google My Maps to PostGIS  
🇩🇪 Automatischer Parser von Google My Maps nach PostGIS

---

## 📦 Установка / Installation / Installation

```bash
docker-compose build
```

---

## ▶️ Запуск / Run / Starten

```bash
docker-compose up
```

После выполнения / After execution / Nach dem Ausführen:
- 📥 Скачивается `map.kml` / Downloads `map.kml` / Lädt `map.kml` herunter
- 📄 Создаётся `map.geojson` / Creates `map.geojson` / Erstellt `map.geojson`
- 🗑️ Очищается таблица / Resets table / Setzt Tabelle zurück
- 📤 Импортируется в PostGIS / Imports to PostGIS / Importiert in PostGIS

---

## ⚙️ Переменные / Environment / Umgebungsvariablen

Файл `.env` (см. [.env.example](.env.example)):

```dotenv
PDB_NAME=geodb
PDB_USER=user
PDB_PASSWORD=password
PDB_HOST=postgres
PDB_TABLE=city_sectors
```

🌐 URL карты задаётся в `parse_kml_to_geojson.py`.

---

## 🧠 Обработка `city` / City assignment / Stadtnamen-Zuweisung

🇷🇺  
Если полигон из других слоёв входит в полигон слоя `Міста`,  
то в поле `city` будет записано имя этого полигона.

🇬🇧  
If any polygon from other layers is within a polygon from layer `Міста`,  
the field `city` will be set to its name.

🇩🇪  
Wenn ein Polygon aus einem anderen Layer im Layer `Міста` enthalten ist,  
wird das Feld `city` mit dessen Namen befüllt.

---

## 🗑️ Удаление временных данных / Cleanup / Entfernen temporärer Daten

Все объекты из слоя `Міста` автоматически удаляются после назначения `city`.

---

## 📁 Структура проекта / Project structure / Projektstruktur

- `parse_kml_to_geojson.py` – основной скрипт / main script / Hauptskript  
- `map.kml`, `map.geojson` – промежуточные файлы / intermediate files  
- `Dockerfile`, `docker-compose.yml` – окружение / environment  
- `.env`, `.env.example` – переменные среды / env variables

---

## 🛠 Зависимости / Dependencies / Abhängigkeiten

Установлены через `requirements.txt`:

```
shapely
requests
psycopg2-binary
python-dotenv
```

---

## 📜 Лицензия / License / Lizenz

MIT – см. файл [LICENSE](LICENSE)