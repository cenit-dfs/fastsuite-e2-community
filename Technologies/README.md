# Technology Plugins

Community-contributed and reference technology scripts for FASTSUITE E2.

Technology plugins customize the E2 UI — attributes, tabs, events, and workmethods for specific robot vendors and applications.

## Structure

```
Technologies/
└── <TechName>/
    └── <VENDOR>/
        └── Standard/
            └── Scripts/
                ├── PostTechInitAttributes.py
                ├── PostWmSyncPgAttributes.py
                └── ...
```

## Contributing

- Follow the same conventions as `OLPTranslators/` — see [CONTRIBUTING.md](../CONTRIBUTING.md)
- One folder per technology/vendor combination
- Keep scripts general-purpose — no customer-specific logic

---

## E2 Built-in Reference Scripts (R2026.1)

The following are the standard technology scripts shipped with E2 — committed here as read-only reference. They define which events fire, what attributes they carry, and when they appear in the motion stream. Downloaders need this context to handle technology events correctly.

### ArcWeldingTechnology

| Vendor | Scripts | Notes |
|--------|---------|-------|
| [Standard](ArcWeldingTechnology/Standard/) | 13 | Shared: seam finding, touch sensing workmethods |
| [ABB](ArcWeldingTechnology/ABB/) | 26 | |
| [CLOOS](ArcWeldingTechnology/CLOOS/) | 13 | |
| [DAIHEN](ArcWeldingTechnology/DAIHEN/) | 30 | Most complete implementation |
| [FANUC](ArcWeldingTechnology/FANUC/) | 16 | |
| [KAWASAKI](ArcWeldingTechnology/KAWASAKI/) | 28 | |
| [KUKA](ArcWeldingTechnology/KUKA/) | 31 | |
| [Motoman](ArcWeldingTechnology/Motoman/) | 16 | |
| [NEURA](ArcWeldingTechnology/NEURA/) | 13 | |
| [PANASONIC](ArcWeldingTechnology/PANASONIC/) | 13 | |

Key files for downloader development: `ArcWeldingTechnology.py` (event/attribute definitions), `ArcOnEvent.py`, `ArcWeldConditionEvent.py`, `SeamFindingEvent.py`, `TouchSensingEvent.py`.

### TechnologyCommon

| Script | Purpose |
|--------|---------|
| `AuxiliaryCommands/AutoExecute/CycleTimeDelayCalculation.py` | Cycle time with delay |
| `AuxiliaryCommands/DesignChangeProcessGeometry/DesignChangeProcessGeometriesReportScript.py` | Design change report |
| `AuxiliaryCommands/OlpProgram/ToolpathReport.py` | Toolpath PDF report |

### Other Technologies
CavityConservation, Deburring, Drilling, FrictionWelding, Generic, Handling, Inspection, LaserWelding, NailShooting, PlasmaCutting, RemoteLaserWelding, Riveting, Rollerhemming, Routing, Screwing, Sealing, SpotWelding, Spraying, StudWelding, UltrasonicCutting, UltrasonicNdt, WaterjetCutting, and LaserCuttingTechnology ship without Python customization scripts.
