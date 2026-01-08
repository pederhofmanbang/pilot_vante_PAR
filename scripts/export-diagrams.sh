#!/bin/bash
# Genererar HTML-filer för diagram (Mermaid och PlantUML)
# HTML-filerna har inbyggd export-funktion för PNG/SVG
# Användning: ./scripts/export-diagrams.sh
#
# Stöder:
#   - .mmd (Mermaid) - renderas med mermaid.js
#   - .puml (PlantUML) - renderas via PlantUML server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DIAGRAMS_DIR="$ROOT_DIR/diagrams"
EXPORTS_DIR="$ROOT_DIR/exports"
DOCS_DIR="$ROOT_DIR/docs"

mkdir -p "$EXPORTS_DIR/html"

# ============================================================
# Mermaid HTML generator
# ============================================================
generate_mermaid_html() {
    local file="$1"
    local filename=$(basename "$file" .mmd)
    local subdir=$(dirname "$file" | sed "s|$DIAGRAMS_DIR/||")
    local content=$(cat "$file")

    mkdir -p "$EXPORTS_DIR/html/$subdir"
    mkdir -p "$DOCS_DIR/$subdir"
    local output_file="$EXPORTS_DIR/html/$subdir/$filename.html"

    cat > "$output_file" << 'HTMLHEAD'
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DIAGRAM_TITLE</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .toolbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 100;
        }
        .toolbar-left {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .toolbar-left a {
            color: #6b7280;
            text-decoration: none;
            font-size: 0.9rem;
        }
        .toolbar-left a:hover { color: #2563eb; }
        .toolbar h1 {
            font-size: 1.1rem;
            color: #1f2937;
        }
        .toolbar-right {
            display: flex;
            gap: 10px;
        }
        button {
            padding: 10px 20px;
            font-size: 14px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            background: #10b981;
            color: white;
            transition: background 0.2s;
        }
        button:hover { background: #059669; }
        button.secondary {
            background: #e5e7eb;
            color: #374151;
        }
        button.secondary:hover { background: #d1d5db; }
        .container {
            padding: 80px 20px 40px;
            overflow-x: auto;
        }
        .diagram-wrapper {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-width: fit-content;
        }
        .mermaid {
            display: flex;
            justify-content: center;
        }
        .mermaid svg {
            max-width: 100%;
            height: auto;
        }
        .badge {
            background: #d1fae5;
            color: #065f46;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <div class="toolbar-left">
            <a href="../">← Tillbaka</a>
            <h1>DIAGRAM_TITLE</h1>
            <span class="badge">Mermaid</span>
        </div>
        <div class="toolbar-right">
            <button class="secondary" onclick="exportSVG()">Ladda ner SVG</button>
            <button onclick="exportPNG()">Ladda ner PNG</button>
        </div>
    </div>
    <div class="container">
        <div class="diagram-wrapper">
            <div class="mermaid" id="diagram">
HTMLHEAD

    echo "$content" >> "$output_file"

    cat >> "$output_file" << 'HTMLFOOT'
            </div>
        </div>
    </div>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            sequence: {
                diagramMarginX: 50,
                diagramMarginY: 10,
                actorMargin: 50,
                width: 150,
                height: 65,
                boxMargin: 10,
                boxTextMargin: 5,
                noteMargin: 10,
                messageMargin: 35,
                mirrorActors: false,
                useMaxWidth: true
            }
        });

        function exportSVG() {
            const svg = document.querySelector('.mermaid svg');
            if (!svg) return alert('Diagram ej laddat ännu');

            const svgData = new XMLSerializer().serializeToString(svg);
            const blob = new Blob([svgData], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'DIAGRAM_FILENAME.svg';
            a.click();
            URL.revokeObjectURL(url);
        }

        function exportPNG() {
            const svg = document.querySelector('.mermaid svg');
            if (!svg) return alert('Diagram ej laddat ännu');

            const svgData = new XMLSerializer().serializeToString(svg);
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = function() {
                const scale = 2;
                canvas.width = img.width * scale;
                canvas.height = img.height * scale;
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.scale(scale, scale);
                ctx.drawImage(img, 0, 0);

                const a = document.createElement('a');
                a.href = canvas.toDataURL('image/png');
                a.download = 'DIAGRAM_FILENAME.png';
                a.click();
            };

            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        }
    </script>
</body>
</html>
HTMLFOOT

    sed -i "s/DIAGRAM_TITLE/$filename/g" "$output_file"
    sed -i "s/DIAGRAM_FILENAME/$filename/g" "$output_file"

    # Kopiera till docs för GitHub Pages
    cp "$output_file" "$DOCS_DIR/$subdir/"

    echo "✓ [Mermaid] $filename"
}

# ============================================================
# PlantUML HTML generator
# ============================================================
generate_plantuml_html() {
    local file="$1"
    local filename=$(basename "$file" .puml)
    local subdir=$(dirname "$file" | sed "s|$DIAGRAMS_DIR/||")

    mkdir -p "$EXPORTS_DIR/html/$subdir"
    mkdir -p "$DOCS_DIR/$subdir"

    echo "✓ [PlantUML] $filename"
    echo "  → PlantUML-filer hanteras manuellt eller finns redan i docs/"
}

# ============================================================
# Main
# ============================================================
echo "=========================================="
echo "  Diagram Export Script"
echo "=========================================="
echo ""
echo "Genererar HTML-filer för diagram..."
echo ""

# Process Mermaid files
find "$DIAGRAMS_DIR" -name "*.mmd" 2>/dev/null | while read -r file; do
    generate_mermaid_html "$file"
done

# Note about PlantUML files
find "$DIAGRAMS_DIR" -name "*.puml" 2>/dev/null | while read -r file; do
    generate_plantuml_html "$file"
done

echo ""
echo "=========================================="
echo "  Klart!"
echo "=========================================="
echo ""
echo "Filer exporterade till:"
echo "  - exports/html/  (lokal användning)"
echo "  - docs/          (GitHub Pages)"
echo ""
echo "Öppna HTML-filerna i webbläsare för att:"
echo "  - Visa diagrammet"
echo "  - Exportera till PNG (för PowerPoint)"
echo "  - Exportera till SVG (för web)"
echo ""
