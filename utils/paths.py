import os
import sys

def get_base_dir() -> str:
    """Returns the base directory for user data, database, resumes, and reports."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_bundle_dir() -> str:
    """Returns the directory containing static bundled resources (assets, models)."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', get_base_dir())
    return get_base_dir()

def get_asset_path(*paths) -> str:
    """Returns absolute path to a bundled static asset."""
    return os.path.join(get_bundle_dir(), *paths)

def get_data_path(*paths) -> str:
    """Returns absolute path to user data/working folder (database, resumes, reports)."""
    return os.path.join(get_base_dir(), *paths)
