"""
BBWS SR4 design tokens extracted from salvage front_end_graphics CSS.

Source (cite-only, no React import):
  M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43
  repo_scaffold/professional_business_components/professional-business-components.css

These tokens drive PySide QSS and Tk color/font parity. They do not claim
legal-for-trade, Metrc, or Arc Launcher runtime ownership.
"""
from __future__ import annotations

# --- Color palette (salvage-aligned) ---
COLOR_TEXT = "#172033"
COLOR_TEXT_STRONG = "#122033"
COLOR_TEXT_MUTED = "#667085"
COLOR_TEXT_SECONDARY = "#475467"
COLOR_BG_APP = "#F3F6F8"
COLOR_BG_CARD = "#FFFFFF"
COLOR_BG_LIST = "#FAFBFC"
COLOR_BORDER = "#D8DEE8"
COLOR_BORDER_STRONG = "#1A2330"
COLOR_FOCUS = "#1B69D2"
COLOR_FOCUS_RING = "#FACC15"
COLOR_PRIMARY = "#1B6B52"
COLOR_PRIMARY_HOVER = "#185F49"
COLOR_DANGER = "#B42318"
COLOR_DANGER_BORDER = "#E0B4AF"
COLOR_WARN_BG = "#FFF1D6"
COLOR_WARN_FG = "#8A4B08"
COLOR_WARN_BORDER = "#D69E2E"
COLOR_SUCCESS_BG = "#ECFDF3"
COLOR_SUCCESS_FG = "#067647"
COLOR_SUCCESS_BORDER = "#C6E7D2"
COLOR_PILL_NEUTRAL_BG = "#EEF2F6"
COLOR_PILL_NEUTRAL_FG = "#5C6975"
COLOR_DISABLED_FG = "#8A969F"
COLOR_DISABLED_BG = "#EDF0F2"
COLOR_ACTIVE_BARCODE = "#1B69D2"
COLOR_LOCKED = "#1E6B52"

# --- Geometry ---
RADIUS_CARD = 18
RADIUS_CONTROL = 12
RADIUS_PILL = 999
RADIUS_INPUT = 10

# --- Typography cues (Qt/Tk approximate salvage eyebrow/metric) ---
FONT_FAMILY = '"Segoe UI", "Segoe UI Variable", sans-serif'
EYEBROW_SIZE_PX = 12
METRIC_SIZE_PX = 34
WEIGHT_SIZE_PX = 72

# Capture status pill labels (text-driven; never color-only)
CAPTURE_PILL_BY_STATE: dict[str, str] = {
    "WAITING_FOR_BARCODE": "Ready",
    "BARCODE_CAPTURED": "Scanned",
    "WAITING_FOR_LOAD": "Waiting",
    "WEIGHING": "Weighing",
    "WAITING_FOR_STABLE_WEIGHT": "Settling",
    "WEIGHT_STABLE": "Stable",
    "MANUAL_CONFIRM": "Locked",
    "RECORD_SAVED": "Saved",
    "RUN_FINISHED": "Finished",
}


def capture_pill_label(state: str) -> str:
    """Return a short text status for the capture pill (accessibility-first)."""
    return CAPTURE_PILL_BY_STATE.get(state, state.replace("_", " ").title() if state else "Idle")


def build_pyside_stylesheet() -> str:
    """Compose APP_STYLE QSS from tokens. Keep Confirm green (primaryAction)."""
    r_card = RADIUS_CARD
    r_ctl = RADIUS_CONTROL
    r_in = RADIUS_INPUT
    r_pill = RADIUS_PILL
    return f"""
/* BBWS SR4 tokens — salvage cite-only; see docs/BBWS_SR4_DESIGN_TOKENS.md */
QWidget {{ color: {COLOR_TEXT}; font-family: {FONT_FAMILY}; font-size: 14px; }}
QMainWindow, QDialog {{ background: {COLOR_BG_APP}; }}
QFrame#topBar, QFrame#card, QGroupBox {{
  background: {COLOR_BG_CARD};
  border: 1px solid {COLOR_BORDER};
  border-radius: {r_card}px;
}}
QDialog#polishDialog {{
  background: {COLOR_BG_APP};
}}
QLabel#appTitle {{
  font-size: 26px; font-weight: 700; letter-spacing: -0.3px; color: {COLOR_TEXT_STRONG};
}}
QLabel#eyebrow {{
  font-size: {EYEBROW_SIZE_PX}px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: {COLOR_TEXT_MUTED};
  padding: 0 0 2px 0;
}}
QLabel#modeBadge, QLabel#statusPill {{
  padding: 6px 10px;
  border-radius: {r_pill}px;
  font-weight: 700;
  font-size: 12px;
  background: {COLOR_PILL_NEUTRAL_BG};
  color: {COLOR_PILL_NEUTRAL_FG};
}}
QLabel#statusPill[pill="ready"], QLabel#statusPill[pill="scanned"] {{
  background: {COLOR_PILL_NEUTRAL_BG}; color: {COLOR_PILL_NEUTRAL_FG};
}}
QLabel#statusPill[pill="stable"] {{
  background: {COLOR_SUCCESS_BG}; color: {COLOR_SUCCESS_FG};
}}
QLabel#statusPill[pill="locked"] {{
  background: {COLOR_SUCCESS_BG}; color: {COLOR_LOCKED};
}}
QLabel#statusPill[pill="saved"] {{
  background: {COLOR_SUCCESS_BG}; color: {COLOR_SUCCESS_FG};
}}
QLabel#statusPill[pill="warn"] {{
  background: {COLOR_WARN_BG}; color: {COLOR_WARN_FG};
}}
QLabel#statusBanner {{
  font-size: 18px;
  font-weight: 700;
  padding: 12px 16px;
  background: {COLOR_BG_CARD};
  border: 1px solid {COLOR_BORDER};
  border-radius: {r_card}px;
  color: {COLOR_TEXT_STRONG};
}}
QLabel#weightDisplay {{
  font-size: {WEIGHT_SIZE_PX}px;
  font-weight: 800;
  padding: 18px;
  background: {COLOR_BG_CARD};
  border: 2px solid {COLOR_BORDER_STRONG};
  border-radius: {r_ctl}px;
  letter-spacing: -1px;
}}
QLabel#metricValue {{ font-size: 18px; font-weight: 700; color: {COLOR_TEXT_STRONG}; }}
QLabel#metricLabel {{
  font-weight: 700; color: {COLOR_TEXT_MUTED}; font-size: {EYEBROW_SIZE_PX}px;
  text-transform: uppercase; letter-spacing: 0.5px;
}}
QLabel#instruction {{ font-size: 16px; font-weight: 600; color: {COLOR_TEXT}; }}
QLabel#lockedMetric {{
  color: {COLOR_LOCKED};
  font-size: {METRIC_SIZE_PX}px;
  font-weight: 800;
  letter-spacing: -1px;
  padding: 4px 0;
}}
QLabel#lastSaved {{
  color: {COLOR_SUCCESS_FG};
  font-weight: 700;
  padding: 10px 12px;
  background: {COLOR_SUCCESS_BG};
  border: 1px solid {COLOR_SUCCESS_BORDER};
  border-radius: {r_ctl}px;
}}
QLabel#dialogTip {{ color: {COLOR_TEXT_SECONDARY}; font-size: 13px; }}
QLabel#dialogStatus {{ font-weight: 600; color: {COLOR_TEXT}; padding: 4px 0; }}
QLineEdit#barcodeInput {{
  min-height: 52px;
  font-size: 20px;
  padding: 4px 12px;
  border: 2px solid {COLOR_BORDER};
  border-radius: {r_in}px;
  background: {COLOR_BG_CARD};
}}
QLineEdit#barcodeInput:focus {{
  border-color: {COLOR_FOCUS};
}}
QPushButton {{
  min-height: 44px;
  font-size: 14px;
  font-weight: 600;
  padding: 6px 14px;
  border: 1px solid #B8C4D0;
  border-radius: {r_ctl}px;
  background: {COLOR_BG_CARD};
}}
QPushButton:hover {{ background: #F0F4F8; }}
QPushButton:focus {{ border-color: {COLOR_FOCUS}; }}
QPushButton#primaryAction {{
  min-height: 58px;
  font-size: 16px;
  color: #FFFFFF;
  background: {COLOR_PRIMARY};
  border-color: {COLOR_PRIMARY};
}}
QPushButton#primaryAction:hover {{ background: {COLOR_PRIMARY_HOVER}; }}
QPushButton#dangerAction {{ color: {COLOR_DANGER}; border-color: {COLOR_DANGER_BORDER}; }}
QPushButton:disabled {{
  color: {COLOR_DISABLED_FG}; background: {COLOR_DISABLED_BG}; border-color: #E1E6EB;
}}
QMenuBar {{ background: {COLOR_BG_CARD}; border-bottom: 1px solid {COLOR_BORDER}; padding: 2px 4px; }}
QStatusBar {{ background: {COLOR_BG_CARD}; border-top: 1px solid {COLOR_BORDER}; color: {COLOR_PILL_NEUTRAL_FG}; }}
QListWidget {{
  border: 1px solid {COLOR_BORDER};
  border-radius: {r_ctl}px;
  background: {COLOR_BG_LIST};
  padding: 4px;
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 12px;
}}
QListWidget::item {{ padding: 4px 6px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{
  background: {COLOR_BG_APP}; width: 12px; margin: 0;
}}
QScrollBar::handle:vertical {{
  background: #C5CED8; border-radius: 6px; min-height: 24px;
}}
""".strip()
