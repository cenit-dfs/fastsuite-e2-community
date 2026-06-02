# Scenarios

Reference tree dumps and golden files for community downloaders. All files here are small text files — no binaries - except the **.cendoc**.

> **Your own test data** (`.cendoc` scenarios, customer-specific golden files) belongs in your private repo under `OLPTranslators/<VENDOR>/tests/`. See the [starter repo OLPTranslators README](https://github.com/cenit-dfs/fastsuite-copilot-starter/blob/master/OLPTranslators/README.md) for the test folder structure.

**Before committing:** Remove any customer names, proprietary information, or sensitive data from the dump.

## Golden Files

Expected output files that show what a community downloader produces. Organized by technology, vendor and controller:

```
scenarios/<TECHNOLOGY>/<VENDOR>/<CONTROLLER>/
├── Scenario.cendoc          ← specific E2 scenario `.cendoc` file
├── golden/main.src          ← primary output file; hand-edited if needed
├── golden/main.dat          ← data file (if applicable)
└── README.txt               ← brief description of the scenario (optional)
```

## Reference Files (OLP Object Tree Dumps)

Use `OLPTranslators/Simple_Python_Translator.py` in E2 to generate a complete dump of the OLP object tree. This shows all programs, operations, motions, events with their attributes and types.

```
scenarios/<TECHNOLOGY>/<VENDOR>/<CONTROLLER>/
└── reference/main.txt       ← data file (if applicable)
```

**Keep golden files small** — use a minimal scenario (2–3 motions, a tool change, one signal event) to demonstrate the output format. These serve as documentation, not exhaustive test suites.
