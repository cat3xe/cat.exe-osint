"""Rend le dossier du projet importable depuis tests/ (sans installer quoi que ce soit)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
