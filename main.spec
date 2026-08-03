# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [('assets', 'assets')]
datas += collect_data_files('en_core_web_sm')

hiddenimports = [
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
    'pdfplumber',
    'reportlab',
    'matplotlib',
    'docx',
    'pypdfium2',
    'scipy',
    'sklearn',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]
hiddenimports += collect_submodules('spacy')
hiddenimports += collect_submodules('en_core_web_sm')
hiddenimports += collect_submodules('google.genai')
hiddenimports += collect_submodules('google.generativeai')
hiddenimports += collect_submodules('google.ai.generativelanguage')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    upx=True,
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
