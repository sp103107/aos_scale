#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VER=$(tr -d '\r' < "$ROOT/VERSION")
PKGROOT="${TMPDIR:-/tmp}/best-buds-weight-station-debian-root"
OUT="$ROOT/dist/debian/best-buds-weight-station_${VER}_amd64.deb"
rm -rf "$PKGROOT"; mkdir -p "$PKGROOT/DEBIAN" "$PKGROOT/opt/best-buds-weight-station/app" "$PKGROOT/usr/bin" "$PKGROOT/usr/share/applications" "$PKGROOT/usr/share/icons/hicolor/scalable/apps"
cp -a "$ROOT/app/best_buds_weight_station" "$PKGROOT/opt/best-buds-weight-station/app/"
cp "$ROOT/VERSION" "$PKGROOT/opt/best-buds-weight-station/VERSION"
# The installed stage/bootstrap entry points resolve /opt/best-buds-weight-station
# as their repository root. Preserve the executable validation and contract
# surfaces they actually call rather than shipping a source-presence-only CLI.
for dir in backend catalogs context contracts cursor docs entrypoints frontend manifests packaging pipeline pods registry release_candidate reports runtime scripts tests validation; do
  if [ -d "$ROOT/$dir" ]; then cp -a "$ROOT/$dir" "$PKGROOT/opt/best-buds-weight-station/"; fi
done
for file in README.md CHANGELOG.md repo_release_state.json guide_pack.json pyproject.toml; do
  if [ -f "$ROOT/$file" ]; then cp "$ROOT/$file" "$PKGROOT/opt/best-buds-weight-station/$file"; fi
done
rm -rf "$PKGROOT/opt/best-buds-weight-station/validation/receipts/stages" \
       "$PKGROOT/opt/best-buds-weight-station/validation/checkpoints"
OPENPYXL_DIR=$(python3 -c 'import openpyxl; print(openpyxl.__path__[0])')
ETXML_DIR=$(python3 -c 'import et_xmlfile; print(et_xmlfile.__path__[0])')
cp -a "$OPENPYXL_DIR" "$PKGROOT/opt/best-buds-weight-station/app/"
cp -a "$ETXML_DIR" "$PKGROOT/opt/best-buds-weight-station/app/"
chmod 755 "$PKGROOT/DEBIAN"
cat > "$PKGROOT/DEBIAN/control" <<EOF
Package: best-buds-weight-station
Version: $VER
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Best Buds <local@bestbuds.invalid>
Depends: python3 (>= 3.11), python3-tk, python3-serial, python3-jsonschema, python3-pytest
Description: Local-first cultivation barcode weight station
 Windows-first PySide6 source is included; Tk is the guaranteed Debian fallback. Physical serial requires python3-serial.
EOF
cat > "$PKGROOT/usr/bin/best-buds-weight-station" <<'EOF'
#!/bin/sh
export PYTHONPATH=/opt/best-buds-weight-station/app${PYTHONPATH:+:$PYTHONPATH}
exec python3 -m best_buds_weight_station "$@"
EOF
chmod 755 "$PKGROOT/usr/bin/best-buds-weight-station"
cat > "$PKGROOT/usr/bin/best-buds-weight-station-validation" <<'EOF'
#!/bin/sh
export PYTHONPATH=/opt/best-buds-weight-station/app${PYTHONPATH:+:$PYTHONPATH}
exec python3 -m best_buds_weight_station.validation "$@"
EOF
chmod 755 "$PKGROOT/usr/bin/best-buds-weight-station-validation"
cat > "$PKGROOT/usr/bin/best-buds-weight-station-bootstrap" <<'EOF'
#!/bin/sh
export PYTHONPATH=/opt/best-buds-weight-station/app${PYTHONPATH:+:$PYTHONPATH}
exec python3 -m best_buds_weight_station.bootstrap "$@"
EOF
chmod 755 "$PKGROOT/usr/bin/best-buds-weight-station-bootstrap"

cat > "$PKGROOT/usr/bin/best-buds-weight-station-stage" <<'EOF'
#!/bin/sh
export PYTHONPATH=/opt/best-buds-weight-station/app${PYTHONPATH:+:$PYTHONPATH}
exec python3 -m best_buds_weight_station.stage_runner "$@"
EOF
chmod 755 "$PKGROOT/usr/bin/best-buds-weight-station-stage"
cp "$ROOT/packaging/debian/best-buds-weight-station.desktop" "$PKGROOT/usr/share/applications/"
cp "$ROOT/frontend/assets/best-buds-weight-station.svg" "$PKGROOT/usr/share/icons/hicolor/scalable/apps/"
find "$PKGROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
mkdir -p "$(dirname "$OUT")"; dpkg-deb --root-owner-group --build "$PKGROOT" "$OUT" >/dev/null
printf '%s\n' "$OUT"
