# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python 3.12 project named `yunsheng-skills`, managed with [uv](https://github.com/astral-sh/uv) (v0.11.2). No dependencies yet.

## Environment

- Virtual environment: `.venv/` (created by uv, CPython 3.12.13, macOS ARM)
- Activate with: `source .venv/bin/activate` or prefix commands with `uv run`
- IDE: PyCharm with Black formatter configured

## Commands

```bash
# Run the project
uv run main.py

# Add dependencies
uv add <package>

# Run a script with uv (no manual activation needed)
uv run python <script.py>
```