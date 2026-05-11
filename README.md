# FASTSUITE E2 — Community Plugins

Community-contributed OLP downloaders, uploaders, technology plugins, and examples for FASTSUITE E2.

This repository is used as a **git submodule** in the [fastsuite-copilot-starter](https://github.com/CBerauer/fastsuite-copilot-starter) template. VS Code Copilot references these files as working examples when helping you build new plugins.

## Contents

### Reference Downloaders

| File | Description |
|------|-------------|
| `OLPTranslators/KUKA/KUKA_KRC5.py` | **Canonical base downloader** — KUKA KRC5 with motion FOLDs, position data, multi-signal event handling |
| `OLPTranslators/ABB/ABB_IRC5.py` | **Advanced multi-plugin** — ABB IRC5 with technology plugin architecture (ArcWelding, Machining, TouchSensing) |
| `OLPTranslators/Simple_Python_Translator.py` | **OLP tree dumper** — downloads the complete E2 object tree as `.txt` for analysis |

### Examples

| Folder | Description |
|--------|-------------|
| `examples/` | Tree dumps, golden files, and test data |

## How to Use

This repo is typically consumed as a submodule:

```bash
# From your fastsuite-copilot-starter project:
git submodule update --init
```

You can also browse the code directly on GitHub for reference.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing new downloaders, uploaders, or examples.

## License

See [LICENSE](LICENSE) for details.
