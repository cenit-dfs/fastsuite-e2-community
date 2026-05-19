# PANASONIC OLP Translators

## Panasonic.py
Production-ready PANASONIC downloader. Outputs `.prg` (AJ and AU format) files.

**Supports:** Arc on/off, multi-robot synchronization (Slave Robot 'A', auto slave program download), multiple PANASONIC mechanisms, multiple welding condition sets, AJ output (default) and AU output (controlled by `CENOlpTargetOutputType` robot attribute).

**Does not support:** Touch sensing (any mode), seam search, seam finding, seam tracking.

## Dependencies
- ArcWeldingTechnology — see `community/Technologies/ArcWeldingTechnology/PANASONIC/`
