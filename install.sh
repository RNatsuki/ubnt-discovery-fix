#!/usr/bin/env bash
# ==============================================================================
# Instalador automático para Ubiquiti Discovery Tool (Extensión Chrome + Host UDP)
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_DIR="$DIR/chrome-extension"
HOST_SCRIPT="$EXT_DIR/ubnt_host.py"
HOST_NAME="com.ubnt.discovery"
EXTENSION_ID="mnhadifepcgolnghpnknpnkfleiogebl"

echo "======================================================================"
echo " Instalando conector nativo para Ubiquiti Discovery en Google Chrome"
echo "======================================================================"

# 1. Asegurar permisos de ejecucion
chmod +x "$HOST_SCRIPT"
chmod +x "$DIR/run.sh" 2>/dev/null || true
chmod +x "$DIR/patch_discovery.py" 2>/dev/null || true

# 2. Generar el manifiesto con la ruta absoluta real
HOST_MANIFEST="$EXT_DIR/$HOST_NAME.json"
cat > "$HOST_MANIFEST" <<EOF
{
  "name": "$HOST_NAME",
  "description": "Ubiquiti Device Discovery Native Messaging Host",
  "path": "$HOST_SCRIPT",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://$EXTENSION_ID/"
  ]
}
EOF

# 3. Directorios de destino para navegadores basados en Chromium
TARGET_DIRS=(
  "$HOME/.config/google-chrome/NativeMessagingHosts"
  "$HOME/.config/chromium/NativeMessagingHosts"
  "$HOME/.config/BraveSoftware/Brave-Browser/NativeMessagingHosts"
  "$HOME/.config/microsoft-edge/NativeMessagingHosts"
  "$HOME/.config/vivaldi/NativeMessagingHosts"
)

INSTALLED_COUNT=0
for target in "${TARGET_DIRS[@]}"; do
  parent_browser="$(dirname "$target")"
  if [ -d "$parent_browser" ] || [ -d "$(dirname "$parent_browser")" ] || [ "$target" == "$HOME/.config/google-chrome/NativeMessagingHosts" ]; then
    mkdir -p "$target"
    cp -f "$HOST_MANIFEST" "$target/$HOST_NAME.json"
    echo " [OK] Registrado en: $target/$HOST_NAME.json"
    INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
  fi
done

# 4. Probar escaneo de red en vivo
echo ""
echo ">> Probando conector UDP en puerto 10001..."
python3 "$HOST_SCRIPT" --test

echo ""
echo "======================================================================"
echo " ¡INSTALACIÓN COMPLETADA CON ÉXITO!"
echo "======================================================================"
echo ""
echo "Para activar la extensión en Google Chrome (sólo la primera vez):"
echo "  1. Abre Chrome y ve a: chrome://extensions"
echo "  2. Activa el interruptor 'Modo de desarrollador' (arriba a la derecha)."
echo "  3. Haz clic en 'Cargar descomprimida' (Load unpacked)."
echo "  4. Selecciona la carpeta:"
echo "     $EXT_DIR"
echo ""
echo "¡Y listo! Tendrás el icono azul de Ubiquiti Discovery en tu barra de extensiones."
echo "======================================================================"

# Si el usuario tiene google-chrome instalado, ofrecer abrir la pagina de extensiones
if which google-chrome &>/dev/null; then
  read -p "¿Deseas abrir Chrome ahora para cargar la extensión? (s/N): " -n 1 -r || true
  echo ""
  if [[ $REPLY =~ ^[Ss]$ ]]; then
    google-chrome --load-extension="$EXT_DIR" "chrome://extensions" &>/dev/null &
    disown
  fi
elif which chromium &>/dev/null; then
  read -p "¿Deseas abrir Chromium ahora para cargar la extensión? (s/N): " -n 1 -r || true
  echo ""
  if [[ $REPLY =~ ^[Ss]$ ]]; then
    chromium --load-extension="$EXT_DIR" "chrome://extensions" &>/dev/null &
    disown
  fi
fi
