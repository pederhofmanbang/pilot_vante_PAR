# Pilot Väntetider/PAR

Diagram, modeller och verktyg för Väntetider/PAR-piloten.

## Struktur

```
├── diagrams/           # Mermaid-diagram (.mmd)
│   ├── sequences/      # Sekvensdiagram
│   ├── flows/          # Flödesscheman
│   └── models/         # ER-diagram, datamodeller
├── exports/            # Genererade bilder (PNG/SVG)
├── docs/               # Dokumentation
├── scripts/            # Hjälpscript
├── web/                # (framtida) Vite frontend
└── python/             # (framtida) Python-kod
```

## Kom igång

### Installera beroenden

```bash
npm install
```

### Exportera diagram till bilder

```bash
# Exportera alla diagram till PNG och SVG
npm run export

# Endast PNG (bra för PowerPoint)
npm run export:png

# Endast SVG (bra för web)
npm run export:svg
```

### Redigera diagram

1. Öppna `.mmd`-filer i VS Code med [Mermaid-tillägget](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
2. Eller förhandsgranska på [mermaid.live](https://mermaid.live)

## Diagram

### Sekvensdiagram

| Diagram | Beskrivning |
|---------|-------------|
| [vantetider-par-flode](diagrams/sequences/vantetider-par-flode.mmd) | Huvudflöde för Väntetider/PAR: paketering, ETL, DQ, export till SoS |

## Användning i presentationer

1. Kör `npm run export:png` för att generera högupplösta PNG-bilder
2. Bilderna hamnar i `exports/png/`
3. Dra in bilderna i PowerPoint

## Licens

Internt projekt - VGR
