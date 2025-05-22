import xml.etree.ElementTree as ET
import json
import requests
from shapely.geometry import Polygon, mapping

# Настройки файлов
KML_URL = "https://www.google.com/maps/d/kml?forcekml=1&mid=1QKv2JmSmNklxrlw4MIc-yc60rebgkl8"
KML_FILE = "map.kml"
GEOJSON_FILE = "map.geojson"

# Пространство имён KML
ns = {"kml": "http://www.opengis.net/kml/2.2"}

def download_kml(url, output_path):
    """
    Загружает KML-файл по указанному URL и сохраняет его в output_path.
    """
    print(f"📥 Скачиваем KML из {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"✅ Файл сохранён: {output_path}")

def parse_kml(input_file, output_file):
    """
    Парсит KML-файл и сохраняет как GeoJSON с включением layer_name и имени полигона.
    """
    print(f"🔍 Парсинг KML-файла: {input_file}")
    tree = ET.parse(input_file)
    root = tree.getroot()
    doc = root.find("kml:Document", ns)
    features = []

    for folder in doc.findall("kml:Folder", ns):
        layer_name = folder.find("kml:name", ns).text
        for placemark in folder.findall("kml:Placemark", ns):
            name_el = placemark.find("kml:name", ns)
            name = name_el.text if name_el is not None else ""

            polygon = placemark.find(".//kml:Polygon", ns)
            coords_el = polygon.find(".//kml:coordinates", ns) if polygon is not None else None

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

if __name__ == "__main__":
    download_kml(KML_URL, KML_FILE)
    parse_kml(KML_FILE, GEOJSON_FILE)
