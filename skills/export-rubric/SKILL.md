---
name: export-rubric
description: Export the assess-rfe scoring rubric to artifacts/rfe-rubric.md in the current working directory.
allowed-tools: Read, Write, Bash
---

## Usage
```
/export-rubric
```

## Instructions

### Plugin Root

When this skill is invoked, resolve the absolute path of the plugin root directory. This SKILL.md is at `<plugin_root>/skills/export-rubric/SKILL.md` — the plugin root is two levels up. Determine this path once at the start.

### Steps

1. Run `python3 {PLUGIN_ROOT}/scripts/export_rubric.py` from the current working directory.
2. Confirm the file was written and print its path.

### Required Permissions

Add to your user or project `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(python3 <PLUGIN_PATH>/scripts/export_rubric.py:*)"
    ]
  }
}
```

`<PLUGIN_PATH>` is a placeholder — replace with the absolute path to this plugin.
