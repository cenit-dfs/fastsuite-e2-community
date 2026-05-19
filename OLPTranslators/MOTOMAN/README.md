# MOTOMAN (Yaskawa) OLP Translators

## Yaskawa.py
Base Yaskawa/MOTOMAN downloader. Outputs INFORM `.jbi` job files.

**Supports:** MOVJ/MOVL/MOVC motion, tool & base frame mapping, speed/accuracy/dwell, controller ports.

## Yaskawa_Arc_Welding.py
Yaskawa arc welding plugin — extends the base downloader with arc welding technology events.

## Dependencies
- ArcWeldingTechnology — see `community/Technologies/ArcWeldingTechnology/Motoman/`
