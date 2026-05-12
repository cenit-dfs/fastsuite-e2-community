# Contributing to FASTSUITE E2 Community

Thank you for contributing to the FASTSUITE E2 community! This guide explains how to add new downloaders, uploaders, technology plugins, or examples.

## What Makes a Good Contribution

- **General-purpose** — works for any user with the same controller, not tied to a specific customer
- **Works out of the box** — someone should be able to use your downloader with minimal setup
- **Clear code** — meaningful variable names, follows existing patterns
- **Tested** — verified with at least one E2 workcell before submitting
- **Documented** — inline comments for non-obvious logic

## How to Contribute

1. **Fork** this repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your changes (e.g., `feature/add-fanuc-r30ib`)
4. **Add or modify** files following the guidelines below
5. **Open a Pull Request** against the `master` branch

CENIT will review your contribution and either merge it, request changes, or discuss it with you.

## What to Contribute

### Downloaders / Uploaders

Place in `OLPTranslators/<VENDOR>/`:

```
OLPTranslators/
└── <VENDOR>/
    └── <VENDOR>_<CONTROLLER>.py
```

**Naming convention:**
- `<VENDOR>_<CONTROLLER>.py` — base downloader (e.g., `FANUC_R30iB.py`)
- `<VENDOR>_<CONTROLLER>_<specialization>.py` — variant (e.g., `ABB_IRC5_ArcWelding.py`)

**Rules:**
- One folder per vendor — all controllers/variants go in the same folder
- Follow the coding conventions from the [starter repo](https://github.com/cenit-dfs/fastsuite-copilot-starter)
- Set `DOWNLOAD_CLASS_NAME` to match your file name (without `.py`)
- Include a docstring header listing supported features (see `KUKA_KRC5.py` as an example)
- Do not modify CENIT canonical files (`KUKA_KRC5.py`, `ABB_IRC5.py`) without prior discussion

### Golden Files

Place in `examples/golden_files/<VENDOR>_<CONTROLLER>/`:

```
examples/golden_files/FANUC_R30iB/
├── main.ls
└── sub_program.ls
```

These show what your downloader produces for a simple scenario. Keep them small — just enough to demonstrate the output format. Include a brief comment at the top of the folder's files describing the scenario (e.g., "2 LIN + 1 PTP motion, tool change, one digital output").

### Tree Dumps

Place in `examples/tree_dumps/`:
- Use `Simple_Python_Translator.py` in E2 to generate the dump
- Remove any sensitive data (customer names, proprietary information) before sharing
- Name files descriptively: `<vendor>_<description>.txt`

## What NOT to Include

| Content | Why |
|---------|-----|
| E2 installation files (`downloadStarter.py`, `downloader.py`, etc.) | Proprietary, already in E2 |
| E2 site-packages (`cenpydownload`, `cenpyolpcore`, etc.) | Proprietary, already in E2 |
| `.cendoc` scenario files | Binary, 10 MB+, belong in your private repo |
| Customer-specific logic | Keep in your private repo |
| Copilot skills, agent files, docs | Belong in the [starter repo](https://github.com/cenit-dfs/fastsuite-copilot-starter) |
| Large binary files of any kind | Keeps the repo lightweight for submodule use |

## Coding Guidelines

- **Indentation**: 3 spaces (matches E2 convention)
- **Logger**: Always use `logger = operator.GetLogOperator()` as a local variable
- **No debugging prints**: Use E2 logger methods (`logger.LogInfo`, `logger.LogWarning`, `logger.LogError`)
- **Deterministic output**: No timestamps or usernames in generated code unless guarded by a flag
- **Safety**: Never include E2 installation files or proprietary E2 API code

## Questions?

Open an issue if you have questions about contributing or need guidance on implementing a specific feature.
