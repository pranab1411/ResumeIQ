# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# ── Python 3.14 stdlib path (fixes "Failed to import encodings" on PyInstaller) ──
STDLIB_PATH = r"C:\Users\prana\AppData\Local\Python\pythoncore-3.14-64\Lib"
PYTHON_DLL_DIR = r"C:\Users\prana\AppData\Local\Python\pythoncore-3.14-64"

datas = [('assets', 'assets')]
datas += collect_data_files('en_core_web_sm')

hiddenimports = [
    # ── Critical stdlib: must be explicit for Python 3.14 + PyInstaller ──
    'encodings',
    'encodings.utf_8',
    'encodings.utf_16',
    'encodings.utf_32',
    'encodings.latin_1',
    'encodings.ascii',
    'encodings.cp1252',
    'encodings.cp437',
    'encodings.idna',
    'encodings.aliases',
    'encodings.unicode_escape',
    'codecs',
    'io',
    'abc',
    'os',
    'sys',
    'site',
    '_io',
    '_codecs',
    '_signal',
    '_thread',
    'zipimport',
    'posixpath',
    'ntpath',
    'genericpath',
    'fnmatch',
    'locale',
    # spaCy
    'spacy',
    'spacy.lang.en',
    'spacy.pipeline',
    'spacy.pipeline.tok2vec',
    'spacy.pipeline.ner',
    'spacy.pipeline.tagger',
    'spacy.pipeline.parser',
    'spacy.pipeline.lemmatizer',
    'spacy.kb',
    'en_core_web_sm',
    # Resume parsing
    'pdfplumber',
    'reportlab',
    'matplotlib',
    'docx',
    'pypdfium2',
    'scipy',
    'sklearn',
    # Qt
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]
hiddenimports += collect_submodules('encodings')
hiddenimports += collect_submodules('spacy')
hiddenimports += collect_submodules('en_core_web_sm')
hiddenimports += collect_submodules('google.generativeai')
hiddenimports += collect_submodules('google.ai.generativelanguage')

a = Analysis(
    ['main.py'],
    # ── pathex: include Python 3.14 stdlib so encodings is always found ──
    pathex=[STDLIB_PATH, PYTHON_DLL_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    # ── runtime_hooks: prime sys.path before ANY module loads ──
    runtime_hooks=['rthook_encodings.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ResumeIQ',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX disabled — it corrupts encodings/stdlib on Windows
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('assets', 'app_icon.ico'),
)
