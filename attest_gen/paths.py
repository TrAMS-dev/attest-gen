"""Resolve project and asset paths regardless of current working directory."""

from pathlib import Path

# Project root: directory that contains the attest_gen package
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = _PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

DEFAULT_TEMPLATE = str(ASSETS_DIR / "Template.png")
DEFAULT_SIGNATURE = str(ASSETS_DIR / "signature.png")
DEFAULT_OUTPUT_DIR = "attester"

# Font files for PDF generation
FONT_REGULAR = str(FONTS_DIR / "centurygothic.ttf")
FONT_BOLD = str(FONTS_DIR / "centurygothic_bold.ttf")
