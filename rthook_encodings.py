"""
Runtime hook: Ensure the frozen app can always locate the encodings package.
This hook runs BEFORE any application code, priming sys.path so the bootloader
can resolve 'encodings' even on Python 3.14 where stdlib layout changed.
"""
import sys
import os

# When running as a PyInstaller frozen bundle, _MEIPASS is the temp extraction
# directory. Make sure it is at the very front of sys.path so that the bundled
# encodings package (placed at the root of the archive) is found first.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    meipass = sys._MEIPASS
    if meipass not in sys.path:
        sys.path.insert(0, meipass)
