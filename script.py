from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import os
import csv


# Register Century Gothic font
pdfmetrics.registerFont(TTFont('CenturyGothic', 'centurygothic.ttf'))
pdfmetrics.registerFont(TTFont('CenturyGothicBold', 'centurygothic_bold.ttf'))

def create_certificate(navn, dato, filnavn, malbilde="Template.png", signature_file="signature.png"):
    c = canvas.Canvas(filnavn, pagesize=A4)
    width, height = A4

    # Legg til bakgrunnsbilde (malen med logo, farger, osv.)
    bakgrunn = ImageReader(malbilde)
    c.drawImage(bakgrunn, 0, 0, width=width, height=height)

    # Tekstinnstillinger (Justerte posisjoner)
    text_top = height - 320  # Juster etter behov

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
        "ferdigheter under casetrening i realistiske omgivelser."
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

# Funksjon som genererer attester for alle deltagere
def generate_certificates(deltagere, output_dir="attester", malbilde="Template.png", signature_file="signature.png"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for navn, dato in deltagere:
        safe_navn = navn.replace(" ", "_")  # erstatt mellomrom med understrek for filnavn
        filnavn = os.path.join(output_dir, f"deltakerbevis_{safe_navn}.pdf")
        create_certificate(navn, dato, filnavn, malbilde, signature_file)

def fetch_names_from_csv(filename="deltagere.csv"):
    deltagere = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            navn = row[0]
            dato = row[1] if len(row) > 1 else datetime.now().strftime("%d.%m.%Y")
            deltagere.append((navn, dato))
    return deltagere

if __name__ == "__main__":
    deltagere = fetch_names_from_csv("deltagere.csv")
    generate_certificates(deltagere)
