"""TrAMS attest generator – certificate PDFs for first-aid course."""

from attest_gen.certificate import (
    DEFAULT_CERTIFICATE_TEXT,
    create_certificate,
    generate_certificates,
    parse_participants_from_file,
    parse_participants_from_string,
    register_fonts,
)
from attest_gen.email import (
    get_resend_config,
    is_valid_email,
    render_template,
    send_certificate_email,
    send_certificates_batch,
)
from attest_gen.paths import (
    ASSETS_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SIGNATURE,
    DEFAULT_TEMPLATE,
    FONTS_DIR,
)

__all__ = [
    "DEFAULT_CERTIFICATE_TEXT",
    "create_certificate",
    "generate_certificates",
    "parse_participants_from_file",
    "parse_participants_from_string",
    "register_fonts",
    "get_resend_config",
    "is_valid_email",
    "render_template",
    "send_certificate_email",
    "send_certificates_batch",
    "ASSETS_DIR",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_SIGNATURE",
    "DEFAULT_TEMPLATE",
    "FONTS_DIR",
]
