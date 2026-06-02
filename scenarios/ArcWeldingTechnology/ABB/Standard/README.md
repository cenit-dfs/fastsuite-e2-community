# Scenarios

Reference tree dumps and golden files for community downloaders. All files here are small text files — no binaries.

> **Your own test data** (`.cendoc` scenarios, customer-specific golden files) belongs in your private repo under `OLPTranslators/<VENDOR>/tests/`. See the [starter repo OLPTranslators README](https://github.com/cenit-dfs/fastsuite-copilot-starter/blob/master/OLPTranslators/README.md) for the test folder structure.

**Before committing:** Remove any customer names, proprietary information, or sensitive data from the dump.

## Golden Files

Expected output files that show what a community downloader produces. Organized by technology, vendor and controller:

```
scenarios/ArcWeldingTechnology/ABB/Standard/
├── ABB_AW_Small.cendoc    ← specific E2 scenario `.cendoc` file
├── golden/ABB001_OP_MOD.MOD         ← up to 3 touchsensing operations composed into one translational offset applied to the actual weld seam operation
├── golden/ABB002_SE_MOD.MOD         ← up to 3 touchsensing operations placed near the seam start point composed into one translational offset, then up to 3 touches near the end point. The two resulting offsets are applied to the actual weld seam operations before the approach point and before the seam's endpoint. This method only works well for seams consisting solely of start- and endpoint.
├── golden/ABB003_3PFR_MOD.MOD       ← 3 to 6 touchsensing operations create a 3-point frame consisting of origin (1-3 touches), local X-axis orientation (1-2 touches) and one touch defining XY-plane. The resulting correction frame is applied to the actual weld seam operations.
├── golden/ABB004_OP_EXP_MOD.MOD     ← Basic arcwelding program using explicit positions
└── README.txt                       ← brief description of the scenario (optional)
```

## Reference Files (OLP Object Tree Dumps)

Use `OLPTranslators/Simple_Python_Translator.py` in E2 to generate a complete dump of the OLP object tree. This shows all programs, operations, motions, events with their attributes and types.

```
scenarios/ArcWeldingTechnology/ABB/Standard/
├── reference/ABB001_OP_MOD.txt      ← OLP object tree dump related to golden/ABB001_OP_MOD.mod
├── reference/ABB002_SE_MOD.txt      ← OLP object tree dump related to golden/ABB002_SE_MOD.mod
├── reference/ABB003_3PFR_MOD.txt    ← OLP object tree dump related to golden/ABB003_3PFR_MOD.mod
└── reference/ABB004_OP_EXP_MOD.txt  ← OLP object tree dump related to golden/ABB004_OP_EXP_MOD.mod
```

**Keep golden files small** — use a minimal scenario (2–3 motions, a tool change, one signal event) to demonstrate the output format. These serve as documentation, not exhaustive test suites.
