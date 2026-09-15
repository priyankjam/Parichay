"""Shared browser discovery for local UX inspection scripts."""
import os
from pathlib import Path

def chromium_executable():
    configured = os.getenv('CHROMIUM_EXECUTABLE')
    if configured:
        return configured
    mac_chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    return str(mac_chrome) if mac_chrome.exists() else None
