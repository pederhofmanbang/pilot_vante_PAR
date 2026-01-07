#!/bin/bash
# Export alla Mermaid-diagram till PNG och/eller SVG
# Användning: ./scripts/export-diagrams.sh [png|svg|all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DIAGRAMS_DIR="$ROOT_DIR/diagrams"
EXPORTS_DIR="$ROOT_DIR/exports"

FORMAT="${1:-all}"

# Skapa exports-mappar
mkdir -p "$EXPORTS_DIR/png" "$EXPORTS_DIR/svg"

# Hitta alla .mmd-filer
find "$DIAGRAMS_DIR" -name "*.mmd" | while read -r file; do
    filename=$(basename "$file" .mmd)
    subdir=$(dirname "$file" | sed "s|$DIAGRAMS_DIR/||")

    mkdir -p "$EXPORTS_DIR/png/$subdir" "$EXPORTS_DIR/svg/$subdir"

    if [[ "$FORMAT" == "png" || "$FORMAT" == "all" ]]; then
        echo "Exporterar $filename till PNG..."
        npx mmdc -i "$file" -o "$EXPORTS_DIR/png/$subdir/$filename.png" -b transparent -w 2400
    fi

    if [[ "$FORMAT" == "svg" || "$FORMAT" == "all" ]]; then
        echo "Exporterar $filename till SVG..."
        npx mmdc -i "$file" -o "$EXPORTS_DIR/svg/$subdir/$filename.svg" -b transparent
    fi
done

echo "Export klar! Filer i: $EXPORTS_DIR"
