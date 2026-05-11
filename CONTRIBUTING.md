# Contributing to FASTSUITE E2 Community

Thank you for contributing to the FASTSUITE E2 community! This guide explains how to add new downloaders, uploaders, technology plugins, or examples.

## How to Contribute

1. **Fork** this repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your changes
4. **Add or modify** files following the guidelines below
5. **Open a Pull Request** against the `main` branch

## What to Contribute

### Downloaders / Uploaders
- Place in `OLPTranslators/<VENDOR>/`
- Follow the coding conventions from the [starter repo](https://github.com/cenit-dfs/fastsuite-copilot-starter)
- Include a brief description in your PR of what robot controller the plugin targets

### Tree Dumps
- Place in `examples/tree_dumps/`
- Use `Simple_Python_Translator.py` to generate the dump
- Remove any sensitive data (customer names, proprietary information) before sharing
- Name files descriptively: `<vendor>_<description>.txt`

### Golden Files
- Place in `examples/golden_files/<VENDOR>/`
- Include both input (tree dump or E2 project description) and expected output

## Coding Guidelines

- **Indentation**: Match the convention of the file you're editing (typically 3 spaces)
- **Logger**: Always use `logger = operator.GetLogOperator()` as a local variable
- **No debugging prints**: Use E2 logger methods
- **Safety**: Never include E2 installation files or proprietary E2 API code

## What NOT to Include

- E2 installation files (`downloadStarter.py`, `downloader.py`, etc.)
- E2 site-packages (`cenpydownload`, `cenpyolpcore`, etc.)
- Customer-specific data or proprietary information
- Large binary files

## Questions?

Open an issue if you have questions about contributing or need guidance on implementing a specific feature.
