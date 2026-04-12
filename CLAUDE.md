# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python 3.8+ project `yunsheng-skills`, managed with [uv](https://github.com/astral-sh/uv) (v0.11.2).
Provides an ontology exploration CLI (`otlg`) and Claude Code Agent Skill.

## Environment

- Virtual environment: `.venv/` (created by uv, CPython 3.8+, macOS ARM)
- Activate with: `source .venv/bin/activate` or prefix commands with `uv run`
- IDE: PyCharm with Black formatter configured

## Commands

```bash
# Generate demo data
uv run python -m ontology_explorer.seed

# Run CLI (after uv sync)
otlg types
otlg type Supplier
otlg instances Supplier --limit 5

# Build binary (PyInstaller)
uv run scripts/build.py

# Sync dependencies
uv sync
```

## Structure

```
ontology_explorer/     # Core package
├── core/              #   models, store, query engine
├── cli/               #   CLI entry point and commands
├── data/              #   ontology.json + instance JSON files
└── seed.py            #   data generation script

skills/                # Skill distribution (for this repo)
.claude/skills/        # Skill auto-discovery (local)
scripts/               # Build scripts (PyInstaller)
```
