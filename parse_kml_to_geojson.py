import os
import json
import requests
import xml.etree.ElementTree as ET
import psycopg2
from shapely.geometry import shape, Polygon, mapping, MultiPolygon
from shapely import wkb
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()

# Константы
KML_URL = "https://www.google.com/maps/d/kml?forcekml=1&mid=1QKv2JmSmNklxrlw4MIc-yc60rebgkl8"
KML_FILE = "map.kml"
GEOJSON_FILE = "map.geojson"
NS = {"kml": "http://www.opengis.net/kml/2.2"}

def download_kml(url, output_path):
    print(f"📥 Скачиваем KML из {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"✅ Сохранено: {output_path}")

def parse_kml_to_geojson(input_file, output_file):
    print(f"🔍 Парсинг KML: {input_file}")
    tree = ET.parse(input_file)
    root = tree.getroot()
    doc = root.find("kml:Document", NS)
    features = []

    for folder in doc.findall("kml:Folder", NS):
        layer_name = folder.find("kml:name", NS).text
        for placemark in folder.findall("kml:Placemark", NS):
            name_el = placemark.find("kml:name", NS)
            name = name_el.text if name_el is not None else ""
            polygon = placemark.find(".//kml:Polygon", NS)
            coords_el = polygon.find(".//kml:coordinates", NS) if polygon is not None else None
            if coords_el is None:
                continue
            raw_coords = coords_el.text.strip()
            coords = []
            for pair in raw_coords.split():
                lon, lat, *_ = map(float, pair.split(","))
                coords.append((lon, lat))
            poly = Polygon(coords)
            features.append({
                "type": "Feature",
                "geometry": mapping(poly),
                "properties": {
                    "name": name,
                    "layer_name": layer_name
                }
            })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"✅ Сохранено {len(features)} объектов в {output_file}")

def reset_target_table():
    print("🔄 Очистка таблицы перед импортом...")
    conn = psycopg2.connect(
        dbname=os.getenv("PDB_NAME"),
        user=os.getenv("PDB_USER"),
        password=os.getenv("PDB_PASSWORD"),
        host=os.getenv("PDB_HOST"),
    )
    table = os.getenv("PDB_TABLE")
    cur = conn.cursor()
    cur.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}') THEN
                TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;
            ELSE
                CREATE TABLE {table} (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    layer_name TEXT,
                    city TEXT,
                    geom geometry(Polygon, 4326)
                );
                CREATE INDEX ON {table} USING GIST (geom);
            END IF;
        END
        $$;
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблица проверена и сброшена.")

def import_geojson_to_postgis(geojson_file):
    print("📤 Импорт в PostGIS...")
    conn = psycopg2.connect(
        dbname=os.getenv("PDB_NAME"),
        user=os.getenv("PDB_USER"),
        password=os.getenv("PDB_PASSWORD"),
        host=os.getenv("PDB_HOST"),
    )
    table = os.getenv("PDB_TABLE")
    cur = conn.cursor()

    with open(geojson_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for feature in data["features"]:
        name = feature["properties"].get("name")
        layer_name = feature["properties"].get("layer_name")
        geom = shape(feature["geometry"]).wkb_hex
        cur.execute(f"""
            INSERT INTO {table} (name, layer_name, geom)
            VALUES (%s, %s, ST_GeomFromWKB(decode(%s, 'hex'), 4326))
        """, (name, layer_name, geom))
        count += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Импортировано {count} объектов.")

def assign_city_by_containment():
    print("📌 Обновляем поле city по включённости в слой 'Міста'...")
    conn = psycopg2.connect(
        dbname=os.getenv("PDB_NAME"),
        user=os.getenv("PDB_USER"),
        password=os.getenv("PDB_PASSWORD"),
        host=os.getenv("PDB_HOST"),
    )
    table = os.getenv("PDB_TABLE")
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE {table} AS target
        SET city = city_src.name
        FROM {table} AS city_src
        WHERE
          city_src.layer_name = 'Міста'
          AND target.layer_name != 'Міста'
          AND ST_Within(target.geom, city_src.geom);
    """)
    print("✅ Назначения city выполнены.")

    cur.execute(f"DELETE FROM {table} WHERE layer_name = 'Міста';")
    print("🗑️ Удалены временные полигоны слоя 'Міста'.")

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Обновление и очистка завершены.")

if __name__ == "__main__":
    download_kml(KML_URL, KML_FILE)
    parse_kml_to_geojson(KML_FILE, GEOJSON_FILE)
    reset_target_table()
    import_geojson_to_postgis(GEOJSON_FILE)
    assign_city_by_containment()
