# OLP Translators

Reference Python downloaders and uploaders shipped with FASTSUITE E2 R2026.1.

> **Read-only reference.** These are the standard E2 translators. For your own vendor customizations, work in `OLPTranslators/<VENDOR>/` in your starter repo.

## Python Translators

| Vendor | Files | Technology | Notes |
|--------|-------|------------|-------|
| [ABB](ABB/) | `ABB_IRC5.py` | Handling + ArcWelding | Multi-plugin reference implementation |
| [DAIHEN](DAIHEN/) | `Daihen_FD19.py`, `Daihen_FD19_Arc_Welding.py`, `Daihen_FD19_ul.py` | ArcWelding | Includes uploader |
| [FANUC](FANUC/) | `Fanuc.py`, `Fanuc_Arc_Welding.py` | Handling + ArcWelding | |
| [KUKA](KUKA/) | `KUKA_KRC5.py`, `KUKA_KRC5_Arc_Welding.py` | Handling + ArcWelding | Canonical base pattern |
| [MOTOMAN](MOTOMAN/) | `Yaskawa.py`, `Yaskawa_Arc_Welding.py` | Handling + ArcWelding | INFORM .jbi format |
| [NEURA](NEURA/) | `NEURA_LARA_specific.py` | Handling | LARA cobot |
| [PANASONIC](PANASONIC/) | `Panasonic.py` | ArcWelding | AJ/AU format, multi-robot sync |
| [PRIMA](PRIMA/) | `PRIMA_XML_ul.py` | LaserCutting | Uploader only; requires numpy |

## Utility Scripts

| File | Purpose |
|------|---------|
| `Simple_Python_Translator.py` | OLP tree dumper — triggers a download that writes a full `.txt` dump of all programs, motions, events, and attributes. Use this to analyze a new workcell before writing a translator. |
| `Simple_Python_Translator_ul.py` | Upload equivalent of the tree dumper. |

## Legacy Translators (not Python)
ABB, CLOOS, DENSO, DÜRR, EPSON, HAITIAN, JARI, KAWASAKI, KOBELCO, LASERDYNE, MITSUBISHI, NACHI, NUKON, REIS, SIASUN, STÄUBLI, TRUMPF, UNIVERSAL — these use the legacy `.pp` PostProcessor format and are not included here.
