"""Certificate PDF generation for TrAMS first-aid course."""

import csv
import io
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from attest_gen.paths import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SIGNATURE,
    DEFAULT_TEMPLATE,
    FONT_BOLD,
    FONT_REGULAR,
)


def register_fonts():
    """Register Century Gothic fonts for PDF generation."""
    pdfmetrics.registerFont(TTFont("CenturyGothic", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("CenturyGothicBold", FONT_BOLD))


# Default certificate text. Markup, one style per line:
#   "# text"    title (red, fixed position below the logo)
#   "## text"   large bold text
#   "**text**"  bold text
#   "> text"    small text
# Every empty line adds BLANK_LINE_HEIGHT of space. {navn} and {dato} are placeholders.
DEFAULT_CERTIFICATE_TEXT = """\
# DELTAKERBEVIS

Det bekreftes at


## {navn}


har fullført TrAMS førstehjelpskurs.

3 timers kurs i basal livreddende førstehjelp inkludert ABC-drillen og
Basal-HLR-undervisning.


Kurset ble arrangert {dato} av
**Trondheim akuttmedisinske studentforening (TrAMS).**



> Kurset består av undervisning i ABC-drill og basal hjerte-lunge-redning, samt
> mye praktisk trening. Deltakeren har demonstrert sine teoretiske og praktiske
> ferdigheter under casetrening i realistiske omgivelser.
"""

# Title metrics measured from the original template image
TITLE_FONT_SIZE = 40
TITLE_BASELINE_FROM_TOP = 239.3
TITLE_COLOR = (252 / 255, 0, 7 / 255)

TEXT_TOP_FROM_TOP = 320
TEXT_MARGIN = 40
BLANK_LINE_HEIGHT = 10

# style -> (font, size, leading, extra space above, extra space below)
LINE_STYLES = {
    "normal": ("CenturyGothic", 14, 20, 0, 0),
    "large": ("CenturyGothicBold", 18, 20, 0, 0),
    "bold": ("CenturyGothicBold", 14, 20, 5, 7),
    "small": ("CenturyGothic", 12, 18, 0, 0),
}


def _parse_line(line: str) -> tuple[str, str]:
    """Return (style, text) for one line of certificate markup."""
    line = line.strip()
    if line.startswith("##"):
        return "large", line[2:].strip()
    if line.startswith("#"):
        return "title", line[1:].strip()
    if line.startswith(">"):
        return "small", line[1:].strip()
    if len(line) > 4 and line.startswith("**") and line.endswith("**"):
        return "bold", line[2:-2].strip()
    return "normal", line


def _wrap_line(text: str, font: str, size: float, max_width: float) -> list[str]:
    """Wrap a line that is too wide for the page."""
    lines = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}" if line else word
        if line and pdfmetrics.stringWidth(candidate, font, size) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def _draw_title(c: canvas.Canvas, tittel: str, width: float, height: float) -> None:
    max_width = width - 2 * TEXT_MARGIN
    size = TITLE_FONT_SIZE
    text_width = pdfmetrics.stringWidth(tittel, "CenturyGothic", size)
    if text_width > max_width:
        size *= max_width / text_width

    c.setFont("CenturyGothic", size)
    c.setFillColorRGB(*TITLE_COLOR)
    c.drawCentredString(width / 2, height - TITLE_BASELINE_FROM_TOP, tittel)


def create_certificate(
    navn: str,
    dato: str,
    filnavn: str,
    malbilde: str = DEFAULT_TEMPLATE,
    signature_file: str | None = DEFAULT_SIGNATURE,
    tekst: str = DEFAULT_CERTIFICATE_TEXT,
) -> None:
    """Create a single certificate PDF.

    Args:
        navn: Participant name.
        dato: Course date (displayed on certificate).
        filnavn: Output PDF path.
        malbilde: Path to template image (without text).
        signature_file: Path to signature image, or None to omit.
        tekst: Certificate text markup (see DEFAULT_CERTIFICATE_TEXT).
    """
    c = canvas.Canvas(filnavn, pagesize=A4)
    width, height = A4
    max_width = width - 2 * TEXT_MARGIN

    bakgrunn = ImageReader(malbilde)
    c.drawImage(bakgrunn, 0, 0, width=width, height=height)

    y_pos = height - TEXT_TOP_FROM_TOP
    first_line = True
    space_below = 0
    for raw in tekst.splitlines():
        style, text = _parse_line(raw.replace("{navn}", navn).replace("{dato}", dato))
        if style == "title":
            if text:
                _draw_title(c, text, width, height)
            continue
        if not text:
            # Empty lines before the first text line do not move the text down
            if not first_line:
                y_pos -= BLANK_LINE_HEIGHT
            continue

        font, size, leading, space_above, next_space_below = LINE_STYLES[style]
        c.setFont(font, size)
        c.setFillColorRGB(0, 0, 0)
        for i, line in enumerate(_wrap_line(text, font, size, max_width)):
            if not first_line:
                y_pos -= leading + (space_above + space_below if i == 0 else 0)
            first_line = False
            c.drawCentredString(width / 2, y_pos, line)
        space_below = next_space_below

    if signature_file and os.path.exists(signature_file):
        sign_img = ImageReader(signature_file)
        sign_w, sign_h = sign_img.getSize()
        target_w = 180
        scale = target_w / sign_w
        target_h = sign_h * scale
        x = (width - target_w) / 2
        y = 110
        c.drawImage(sign_img, x, y, width=target_w, height=target_h, mask="auto")

    c.save()


def generate_certificates(
    deltagere: list[tuple[str, str]],
    output_dir: str = DEFAULT_OUTPUT_DIR,
    malbilde: str = DEFAULT_TEMPLATE,
    signature_file: str | None = DEFAULT_SIGNATURE,
    tekst: str = DEFAULT_CERTIFICATE_TEXT,
) -> list[str]:
    """Generate certificate PDFs for all participants.

    Returns:
        List of generated PDF file paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generated = []
    for navn, dato in deltagere:
        safe_navn = navn.replace(" ", "_")
        filnavn = os.path.join(output_dir, f"deltakerbevis_{safe_navn}.pdf")
        create_certificate(navn, dato, filnavn, malbilde, signature_file, tekst)
        generated.append(filnavn)
    return generated


def parse_participants_from_file(
    filename: str,
    default_date: str | None = None,
) -> list[tuple[str, str]]:
    """Read participants (name, date) from a CSV file.

    CSV format: Navn,Dato (Dato optional; uses default_date or today if missing).
    """
    default_date = default_date or datetime.now().strftime("%d.%m.%Y")
    deltagere = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            navn = row[0].strip()
            if not navn:
                continue
            dato = row[1].strip() if len(row) > 1 and row[1].strip() else default_date
            deltagere.append((navn, dato))
    return deltagere


def parse_participants_from_string(
    content: str,
    default_date: str,
) -> list[tuple[str, str]]:
    """Parse participants (name, date) from CSV string content."""
    deltagere = []
    reader = csv.reader(io.StringIO(content))
    for row in reader:
        if not row:
            continue
        navn = row[0].strip()
        if not navn:
            continue
        dato = row[1].strip() if len(row) > 1 and row[1].strip() else default_date
        deltagere.append((navn, dato))
    return deltagere
