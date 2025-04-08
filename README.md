# Soil API – BGR WMS mit dynamischer BBOX-Skalierung

## Endpunkt:
GET /soil?lat=...&lon=...

## Funktion:
- Führt GetFeatureInfo-Anfragen mit zunehmend größerem Suchradius (BBOX) aus
- Liefert Daten aus BGR BÜK200-WMS zurück
- Gibt JSON-Objekt mit HTML-inhaltlich geparsten Bodenparametern zurück

## Quelle:
https://services.bgr.de/wms/boden/buek200
