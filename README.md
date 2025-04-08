# Agrar GPT API – mit echter Bodenanbindung (BGR)

## Endpunkt
- `/soil?lat=...&lon=...`

## Quelle
- BÜK200 & BODEN-DÜS via BGR WMS

## Validierung
- Fehleingaben (außerhalb Deutschlands) → 400
- Kein Bodeneintrag an Punkt → 404
