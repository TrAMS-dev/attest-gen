"""TrAMS attest generator – certificate PDFs for first-aid course."""

from attest_gen.certificate import (
    create_certificate,
    generate_certificates,
    parse_participants_from_file,
    parse_participants_from_string,
    register_fonts,
)
from attest_gen.paths import (
    ASSETS_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SIGNATURE,
    DEFAULT_TEMPLATE,
    FONTS_DIR,
)

__all__ = [
    "create_certificate",
    "generate_certificates",
    "parse_participants_from_file",
    "parse_participants_from_string",
    "register_fonts",
    "ASSETS_DIR",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SIGNATURE",
    "DEFAULT_TEMPLATE",
    "FONTS_DIR",
]
