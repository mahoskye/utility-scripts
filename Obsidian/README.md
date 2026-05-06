# Obsidian Utilities

This directory contains an Obsidian Templater template and the user scripts it depends on.

## Layout

- `templates/` — Templater templates (e.g. `Daily Template.md`)
- `scripts/` — Templater user scripts referenced via `tp.user.*` (e.g. `findPreviousNote`, `findNextNote`)

## Usage

In Obsidian, install the [Templater](https://github.com/SilentVoid13/Templater) plugin and point its settings at a vault folder containing copies of these files:

- Set the **Template folder location** to wherever you place the contents of `templates/`.
- Set the **Script files folder location** to wherever you place the contents of `scripts/`.

The daily template uses `tp.user.findPreviousNote` and `tp.user.findNextNote` to build navigation links between dated notes, so both folders need to be configured for the template to work.
