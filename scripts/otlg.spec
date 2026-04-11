# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for otlg binary

import sys
from pathlib import Path

# Project root is one level up from this spec file
SPEC_DIR = Path(SPECPATH)
PROJECT_DIR = SPEC_DIR.parent

# On Windows, strip can corrupt DLLs; disable it
is_windows = sys.platform == "win32"

a = Analysis(
    [str(SPEC_DIR / 'otlg_entry.py')],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=[
        (str(PROJECT_DIR / 'ontology_explorer' / 'data'), 'ontology_explorer/data'),
    ],
    hiddenimports=[
        'ontology_explorer',
        'ontology_explorer.core',
        'ontology_explorer.core.models',
        'ontology_explorer.core.store',
        'ontology_explorer.core.query',
        'ontology_explorer.cli',
        'ontology_explorer.cli.__main__',
        'ontology_explorer.cli.commands',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'pydoc'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='otlg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=not is_windows,
    upx=not is_windows,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
