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


def create_certificate(
    navn: str,
    dato: str,
    filnavn: str,
    malbilde: str = DEFAULT_TEMPLATE,
    signature_file: str | None = DEFAULT_SIGNATURE,
) -> None:
    """Create a single certificate PDF.

    Args:
        navn: Participant name.
        dato: Course date (displayed on certificate).
        filnavn: Output PDF path.
        malbilde: Path to template image.
        signature_file: Path to signature image, or None to omit.
    """
    c = canvas.Canvas(filnavn, pagesize=A4)
    width, height = A4

    bakgrunn = ImageReader(malbilde)
    c.drawImage(bakgrunn, 0, 0, width=width, height=height)

    text_top = height - 320

    c.setFont("CenturyGothic", 14)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width / 2, text_top, "Det bekreftes at")

    c.setFont("CenturyGothicBold", 18)
    c.drawCentredString(width / 2, text_top - 40, navn)

    c.setFont("CenturyGothic", 14)
    c.drawCentredString(width / 2, text_top - 80, "har fullført TrAMS førstehjelpskurs.")

    kursinfo = (
        "3 timers kurs i basal livreddende førstehjelp inkludert ABC-drillen og",
        "Basal-HLR-undervisning.",
    )
    y_pos = text_top - 110
    for line in kursinfo:
        c.drawCentredString(width / 2, y_pos, line)
        y_pos -= 20

    arrangeringsinfo = f"Kurset ble arrangert {dato} av"
    c.drawCentredString(width / 2, y_pos - 20, arrangeringsinfo)

    c.setFont("CenturyGothicBold", 14)
    c.drawCentredString(width / 2, y_pos - 45, "Trondheim akuttmedisinske studentforening (TrAMS).")

    beskrivelse = (
        "Kurset består av undervisning i ABC-drill og basal hjerte-lunge-redning, samt",
        "mye praktisk trening. Deltakeren har demonstrert sine teoretiske og praktiske",
        "ferdigheter under casetrening i realistiske omgivelser.",
    )
    y_pos -= 100
    c.setFont("CenturyGothic", 12)
    for line in beskrivelse:
        c.drawCentredString(width / 2, y_pos, line)
        y_pos -= 18

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
        create_certificate(navn, dato, filnavn, malbilde, signature_file)
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
