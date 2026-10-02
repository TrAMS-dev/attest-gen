import os
import tempfile
import zipfile
from datetime import datetime

import streamlit as st

from attest_gen import DEFAULT_CERTIFICATE_TEXT, create_certificate, register_fonts as register_fonts_impl
from attest_gen.email import (
    get_resend_config,
    is_valid_email,
    render_template,
    send_certificates_batch,
)
from attest_gen.paths import DEFAULT_OUTPUT_DIR, DEFAULT_SIGNATURE, DEFAULT_TEMPLATE
from attest_gen.utils import wipe_folder

DEFAULT_EMAIL_SUBJECT = "Ditt TrAMS deltakerbevis"
DEFAULT_EMAIL_BODY = """Hei {navn},

Takk for at du deltok på TrAMS førstehjelpskurs {dato}.

Vedlagt finner du ditt personlige deltakerbevis.

Vennlig hilsen
Trondheim akuttmedisinske studentforening (TrAMS)
"""

# Page configuration
st.set_page_config(
    page_title="TrAMS Attest Generator",
    page_icon="📜",
)


@st.cache_resource
def register_fonts():
    """Register fonts, with Streamlit caching and error handling."""
    try:
        register_fonts_impl()
        return True
    except Exception as e:
        st.error(f"Kunne ikke laste fonter: {e}")
        return False


def _nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_names_only(names_text: str, dato_formatted: str) -> tuple[list[tuple[str, str, str | None]], list[str]]:
    """Return (participants, errors). Participants are (navn, dato, email|None)."""
    names = _nonempty_lines(names_text)
    if not names:
        return [], []
    return [(navn, dato_formatted, None) for navn in names], []


def parse_names_and_emails(
    names_text: str, emails_text: str, dato_formatted: str
) -> tuple[list[tuple[str, str, str | None]], list[str]]:
    """Pair names and emails by line. Return (participants, errors)."""
    names = _nonempty_lines(names_text)
    emails = _nonempty_lines(emails_text)
    errors: list[str] = []

    if not names and not emails:
        return [], []

    if len(names) != len(emails):
        errors.append(
            f"Antall navn ({len(names)}) og e-poster ({len(emails)}) må være likt. "
            "Sjekk at hver linje matcher."
        )
        return [], errors

    participants: list[tuple[str, str, str | None]] = []
    for i, (navn, email) in enumerate(zip(names, emails), start=1):
        if not is_valid_email(email):
            errors.append(f"Linje {i}: ugyldig e-post «{email}»")
            continue
        participants.append((navn, dato_formatted, email))

    if errors:
        return [], errors
    return participants, []


def reset_certificate_text() -> None:
    st.session_state["cert_text"] = DEFAULT_CERTIFICATE_TEXT


def render_certificate_text_editor() -> str:
    """Show the editable certificate text. Returns the current text."""
    with st.expander("Rediger teksten på attesten"):
        st.caption(
            "Bruk {navn} og {dato} som plassholdere. Start en linje med `#` for tittel, "
            "`##` for stor fet tekst og `>` for liten tekst. Skriv `**tekst**` for fet tekst. "
            "Hver tomme linje gir litt ekstra luft."
        )
        tekst = st.text_area(
            "Tekst på attesten",
            value=DEFAULT_CERTIFICATE_TEXT,
            height=480,
            key="cert_text",
        )
        st.button("Tilbakestill til standardtekst", on_click=reset_certificate_text)
    return tekst


def generate_certificates_ui(
    deltagere: list[tuple[str, str, str | None]],
    template_file,
    signature_file,
    tekst: str,
) -> None:
    """Generate PDFs and store paths + participants in session_state."""
    template_path = DEFAULT_TEMPLATE
    tmp_template = None
    tmp_signature = None

    if template_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(template_file.read())
            template_path = tmp.name
            tmp_template = template_path

    if not os.path.exists(template_path) and not template_file:
        st.error(
            "Mal ikke funnet! Last opp en mal eller sørg for at assets/Template.png finnes."
        )
        return

    signature_path = None
    if signature_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(signature_file.read())
            signature_path = tmp.name
            tmp_signature = signature_path
    elif os.path.exists(DEFAULT_SIGNATURE):
        signature_path = DEFAULT_SIGNATURE
    else:
        st.warning("Ingen signatur funnet. Attestene vil bli generert uten signatur.")

    if os.path.exists(DEFAULT_OUTPUT_DIR):
        wipe_folder(DEFAULT_OUTPUT_DIR)
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

    progress_bar = st.progress(0)
    status_text = st.empty()
    generated_files: list[str] = []
    generated_recipients: list[tuple[str, str, str | None, str]] = []

    for i, (navn, dato, email) in enumerate(deltagere):
        status_text.text(f"Genererer attest for {navn}...")
        safe_navn = navn.replace(" ", "_")
        filnavn = os.path.join(DEFAULT_OUTPUT_DIR, f"deltakerbevis_{safe_navn}.pdf")

        try:
            create_certificate(navn, dato, filnavn, template_path, signature_path, tekst)
            generated_files.append(filnavn)
            generated_recipients.append((navn, dato, email, filnavn))
        except Exception as e:
            st.error(f"Feil ved generering av attest for {navn}: {e}")

        progress_bar.progress((i + 1) / len(deltagere))

    status_text.empty()
    progress_bar.empty()

    if tmp_template and os.path.exists(tmp_template):
        os.unlink(tmp_template)
    if tmp_signature and os.path.exists(tmp_signature):
        os.unlink(tmp_signature)

    st.session_state["generated_files"] = generated_files
    st.session_state["generated_recipients"] = generated_recipients
    st.session_state["zip_bytes"] = None
    st.session_state["zip_filename"] = None
    st.session_state["send_results"] = None

    if generated_files:
        zip_filename = f"attester_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in generated_files:
                    zipf.write(file_path, os.path.basename(file_path))
            with open(tmp_zip.name, "rb") as f:
                st.session_state["zip_bytes"] = f.read()
            os.unlink(tmp_zip.name)
        st.session_state["zip_filename"] = zip_filename

    st.success(f"✅ Genererte {len(generated_files)} attester!")
    st.info(f"Attestene er lagret i mappen: `{DEFAULT_OUTPUT_DIR}`")


def render_download_and_email_section() -> None:
    """Show ZIP download and optional email send UI from session_state."""
    generated_files = st.session_state.get("generated_files") or []
    recipients = st.session_state.get("generated_recipients") or []
    if not generated_files:
        return

    zip_bytes = st.session_state.get("zip_bytes")
    zip_filename = st.session_state.get("zip_filename") or "attester.zip"
    if zip_bytes:
        st.download_button(
            label="📥 Last ned alle attester som ZIP",
            data=zip_bytes,
            file_name=zip_filename,
            mime="application/zip",
            use_container_width=True,
        )

    email_recipients = [
        (navn, dato, email, pdf_path)
        for navn, dato, email, pdf_path in recipients
        if email
    ]
    if not email_recipients:
        return

    st.divider()
    st.header("Send attester på e-post")
    st.caption("Bruk {navn} og {dato} som plassholdere i emne og melding.")

    try:
        get_resend_config(st.secrets)
        secrets_ok = True
    except ValueError as e:
        secrets_ok = False
        st.warning(str(e))

    subject = st.text_input("Emne", value=DEFAULT_EMAIL_SUBJECT, key="email_subject")
    body = st.text_area("Melding", value=DEFAULT_EMAIL_BODY, height=180, key="email_body")

    first_navn, first_dato, first_email, _ = email_recipients[0]
    with st.expander("Forhåndsvisning (første mottaker)", expanded=True):
        st.markdown(f"**Til:** {first_navn} <{first_email}>")
        st.markdown(f"**Emne:** {render_template(subject, navn=first_navn, dato=first_dato)}")
        st.text(render_template(body, navn=first_navn, dato=first_dato))
        st.caption(f"Vedlegg: deltakerbevis for {first_navn}")

    send_disabled = not secrets_ok or not subject.strip() or not body.strip()
    if st.button(
        f"✉️ Send e-poster ({len(email_recipients)})",
        type="primary",
        use_container_width=True,
        disabled=send_disabled,
    ):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def on_progress(done: int, total: int, result) -> None:
            status_text.text(
                f"Sender til {result.name} ({result.email})... ({done}/{total})"
            )
            progress_bar.progress(done / total)

        results = send_certificates_batch(
            email_recipients,
            subject_template=subject,
            body_template=body,
            secrets=st.secrets,
            on_progress=on_progress,
        )
        status_text.empty()
        progress_bar.empty()
        st.session_state["send_results"] = results

    results = st.session_state.get("send_results")
    if results:
        ok_count = sum(1 for r in results if r.ok)
        fail_count = len(results) - ok_count
        if fail_count == 0:
            st.success(f"Sendte {ok_count} e-poster.")
        else:
            st.warning(f"Sendte {ok_count} e-poster. {fail_count} feilet.")
        with st.expander("Detaljer"):
            for r in results:
                if r.ok:
                    st.text(f"✓ {r.name} <{r.email}>")
                else:
                    st.text(f"✗ {r.name} <{r.email}> — {r.error}")


def main():
    st.title("📜 TrAMS Attest Generator")
    st.markdown("Generer attester for TrAMS førstehjelpskurs")

    if not register_fonts():
        st.stop()

    dato = st.date_input(
        "Kursdato",
        value=datetime.now().date(),
        help="Datoen kurset ble arrangert",
    )
    dato_formatted = dato.strftime("%d.%m.%Y")

    signature_file = st.file_uploader(
        "Last opp signaturbilde (valgfritt)",
        type=["png", "jpg", "jpeg"],
        help="Last opp signaturbildet som skal brukes på attestene",
    )

    template_file = st.file_uploader(
        "Last opp malbilde (valgfritt)",
        type=["png", "jpg", "jpeg"],
        help="Hvis du ikke laster opp en mal, brukes malen fra assets/. Malen skal være uten tekst.",
    )

    tekst = render_certificate_text_editor()

    st.header("Deltakere")
    input_mode = st.radio(
        "Inndatamodus",
        options=["Kun navn", "Navn + e-post"],
        horizontal=True,
        help="Velg «Navn + e-post» for å sende attester på e-post etter generering.",
    )

    deltagere: list[tuple[str, str, str | None]] = []
    parse_errors: list[str] = []

    if input_mode == "Kun navn":
        names_text = st.text_area(
            "Skriv inn navnene (ett per linje)",
            height=200,
            help="Skriv inn navnene til deltakerne, ett navn per linje",
            key="names_only",
        )
        deltagere, parse_errors = parse_names_only(names_text, dato_formatted)
    else:
        col_names, col_emails = st.columns(2)
        with col_names:
            names_text = st.text_area(
                "Navn (ett per linje)",
                height=200,
                help="Samme antall linjer som e-post-feltet",
                key="names_with_email",
            )
        with col_emails:
            emails_text = st.text_area(
                "E-post (ett per linje)",
                height=200,
                help="Samme antall linjer som navn-feltet",
                key="emails",
            )
        deltagere, parse_errors = parse_names_and_emails(
            names_text, emails_text, dato_formatted
        )

    for err in parse_errors:
        st.error(err)

    if deltagere and not parse_errors:
        st.success(f"Fant {len(deltagere)} deltakere")
        with st.expander("Forhåndsvis deltakere"):
            for navn, d, email in deltagere:
                if email:
                    st.text(f"• {navn} — {email} — {d}")
                else:
                    st.text(f"• {navn} — {d}")

    if deltagere and not parse_errors:
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            generate_button = st.button(
                "🚀 Generer attester",
                type="primary",
                use_container_width=True,
            )

        if generate_button:
            generate_certificates_ui(deltagere, template_file, signature_file, tekst)

        render_download_and_email_section()
    else:
        if not parse_errors:
            st.info("👆 Legg til deltakere for å generere attester")
        # Still show previous results if any
        if st.session_state.get("generated_files"):
            st.divider()
            render_download_and_email_section()


if __name__ == "__main__":
    main()
