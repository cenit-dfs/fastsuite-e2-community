# FANUC OLP Translators

## Fanuc.py
Base FANUC R-30iB downloader. Outputs `.ls` LS format files.

**Supports:** J/L/C motion, tool & base frame mapping, motion events, controller ports (bool), speed/accuracy/dwell events.

**Does not support:** Resource ports.

## Fanuc_Arc_Welding.py
FANUC arc welding plugin — extends `Fanuc.py` with arc welding technology events (arc on/off, weld condition, seam finding, touch sensing).

## Dependencies
- ArcWeldingTechnology (for arc welding events) — see `community/Technologies/ArcWeldingTechnology/FANUC/`
