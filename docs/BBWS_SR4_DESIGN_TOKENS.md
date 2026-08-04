# BBWS SR4 — Design Tokens

**series_id:** `BBWS_SR4_operator_surface_polish`  
**module:** `app/best_buds_weight_station/ui_tokens.py`

## Salvage cite-only

Tokens are adapted from:

`M:/SALVAGE/CAPSULES/front_end_graphics/aos_ks_frontend_flow_graphics_v0_1_43/repo_scaffold/professional_business_components/professional-business-components.css`

No React components are imported into Best Buds.

| Token group | Salvage cue | BBWS use |
|-------------|-------------|---------|
| Eyebrow | `.aos-business-card__eyebrow` | `QLabel#eyebrow` / Tk uppercase labels |
| Status pill | `.aos-business-card__status` | `QLabel#statusPill` / mode badge |
| Metric | `.aos-business-card__metric` | Locked weight + live weight scale |
| Card | border `#d8dee8`, radius 18 | `QFrame#card` / Tk highlight frames |
| Focus ring | `#facc15` outline | Button/focus border accent (Qt approx.) |
| Success green | `#ecfdf3` / `#067647` | Last-saved receipt + Stable/Locked pills |

## Non-claims

- Tokens are visual only — not legal-for-trade or Metrc compliance
- Status pills always include text labels (not color-only)
- Capture loop remains scan → settle → lock → confirm → reset
