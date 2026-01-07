# Pilot Väntetider/PAR

Diagram, modeller och verktyg för Väntetider/PAR-piloten.

## Struktur

```
├── diagrams/           # Mermaid-diagram (.mmd)
│   ├── sequences/      # Sekvensdiagram
│   ├── flows/          # Flödesscheman
│   └── models/         # ER-diagram, datamodeller
├── exports/            # Genererade HTML-filer med export
├── docs/               # Dokumentation
├── scripts/            # Hjälpscript
├── web/                # (framtida) Vite frontend
└── python/             # (framtida) Python-kod
```

## Kom igång

### Generera exporterbara HTML-filer

```bash
./scripts/export-diagrams.sh
```

Detta skapar HTML-filer i `exports/html/` som du kan:
1. Öppna i webbläsaren för att visa diagrammet
2. Klicka på **"Ladda ner PNG"** för PowerPoint (högupplöst 2x)
3. Klicka på **"Ladda ner SVG"** för web/skalbar grafik

### Redigera diagram

1. Öppna `.mmd`-filer i VS Code med [Mermaid-tillägget](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
2. Eller förhandsgranska på [mermaid.live](https://mermaid.live)

## Diagram

### Sekvensdiagram

| Diagram | Beskrivning | Visa |
|---------|-------------|------|
| [vantetider-par-flode](diagrams/sequences/vantetider-par-flode.mmd) | Huvudflöde: paketering, ETL, DQ, export till SoS | [HTML](exports/html/sequences/vantetider-par-flode.html) |

## Användning i presentationer

1. Kör `./scripts/export-diagrams.sh`
2. Öppna HTML-filen i `exports/html/` i din webbläsare
3. Klicka **"Ladda ner PNG"** för en högupplöst bild
4. Dra in PNG-filen i PowerPoint

## Online-redigering

Kopiera innehållet från en `.mmd`-fil och klistra in på [mermaid.live](https://mermaid.live) för att:
- Redigera interaktivt
- Exportera direkt till PNG/SVG
- Dela via länk

## Licens

Internt projekt - VGR
