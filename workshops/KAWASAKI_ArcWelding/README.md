# Workshop: KAWASAKI Arc Welding Downloader

## Goal

Build a Kawasaki AS-language downloader from scratch using Copilot, guided by reference data and controller documentation.

By the end of this exercise you will have a working Python downloader that produces the same output as the golden files in `golden/`.

## What's in This Folder

| Folder | Content |
|--------|---------|
| `scenarios/` | E2 project file (`.cendoc`) — load this into FASTSUITE E2 |
| `reference/` | Simple Translator tree dump (`.txt`) and legacy CD XML (`.xml`) — shows the E2 object structure and attribute mapping |
| `golden/` | Expected output programs — your downloader should produce these |
| `docs/` | Kawasaki AS language reference — the agent needs this to generate correct robot syntax |

## Prerequisites

- FASTSUITE E2 R2026.1 installed and licensed
- VS Code with Copilot set up (see [Getting Started](https://github.com/cenit-dfs/fastsuite-copilot-starter/blob/master/docs/workshop/getting-started.md))
- Your own clone of the starter repo

## Exercise Steps

### 1. Explore the scenario

- Load `scenarios/*.cendoc` into E2
- Browse the workcell, programs, and operations
- Review `reference/*_tree.txt` to see the OLP object structure as text

### 2. Study the expected output

- Open the files in `golden/` — this is what the downloader should produce
- Review `reference/*_cd.xml` to understand which E2 attributes map to which output constructs
- Read the controller docs in `docs/` to understand Kawasaki AS language syntax

### 3. Create the downloader

- In your starter repo, create `OLPTranslators/KAWASAKI/KAWASAKI_ArcWelding.py`
- Switch to the **E2Downloader** agent mode in Copilot Chat
- Tell Copilot:
  > *"Create a Kawasaki AS language downloader. Use the controller documentation in community/workshops/KAWASAKI_ArcWelding/docs/ and produce output matching the golden files in community/workshops/KAWASAKI_ArcWelding/golden/"*

### 4. Iterate and test

- Run the download in E2 with your new Python downloader
- Compare output against `golden/` using the "Compare Output vs Golden" VS Code task
- Refine with Copilot until the output matches

## Files You Will Provide

> **Workshop facilitator:** Drop the following files into this folder before the workshop:
>
> - `scenarios/*.cendoc` — the E2 arc welding scenario
> - `reference/*_tree.txt` — Simple Translator dump of the scenario
> - `reference/*_cd.xml` — the legacy CustomDefinition XML stylesheet
> - `golden/*.as` — the expected output programs (2-3 files)
> - `docs/kawasaki_as_language.md` — AS language reference (converted from PDF)
> - `docs/kawasaki_touchsensing.md` — touch sensing extension (if applicable)
