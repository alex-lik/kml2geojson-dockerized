FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parse_kml_to_geojson.py .

ENTRYPOINT ["python", "parse_kml_to_geojson.py"]



