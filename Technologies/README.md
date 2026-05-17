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
