import os
import tempfile
import zipfile
from datetime import datetime

import streamlit as st

from attest_gen import create_certificate, register_fonts as register_fonts_impl
from attest_gen.paths import DEFAULT_OUTPUT_DIR, DEFAULT_SIGNATURE, DEFAULT_TEMPLATE
from attest_gen.utils import wipe_folder

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
        help="Hvis du ikke laster opp en mal, brukes malen fra assets/.",
    )

    st.header("Deltakere")

    names_text = st.text_area(
        "Skriv inn navnene (ett per linje)",
        height=200,
        help="Skriv inn navnene til deltakerne, ett navn per linje",
    )

    deltagere = []
    if names_text:
        names_list = [name.strip() for name in names_text.split("\n") if name.strip()]
        deltagere = [(navn, dato_formatted) for navn in names_list]

        if deltagere:
            st.success(f"Fant {len(deltagere)} deltakere")
            with st.expander("Forhåndsvis deltakere"):
                for navn, dato in deltagere:
                    st.text(f"• {navn} - {dato}")

    if deltagere:
        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            generate_button = st.button(
                "🚀 Generer attester",
                type="primary",
                use_container_width=True,
            )

        if generate_button:
            template_path = DEFAULT_TEMPLATE
            if template_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_template:
                    tmp_template.write(template_file.read())
                    template_path = tmp_template.name

            if not os.path.exists(template_path) and not template_file:
                st.error(
                    "Mal ikke funnet! Last opp en mal eller sørg for at assets/Template.png finnes."
                )
                st.stop()

            signature_path = None
            if signature_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
                    tmp_sig.write(signature_file.read())
                    signature_path = tmp_sig.name
            elif os.path.exists(DEFAULT_SIGNATURE):
                signature_path = DEFAULT_SIGNATURE
            else:
                st.warning("Ingen signatur funnet. Attestene vil bli generert uten signatur.")

            if os.path.exists(DEFAULT_OUTPUT_DIR):
                wipe_folder(DEFAULT_OUTPUT_DIR)
            os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

            progress_bar = st.progress(0)
            status_text = st.empty()

            generated_files = []

            for i, (navn, dato) in enumerate(deltagere):
                status_text.text(f"Genererer attest for {navn}...")
                safe_navn = navn.replace(" ", "_")
                filnavn = os.path.join(DEFAULT_OUTPUT_DIR, f"deltakerbevis_{safe_navn}.pdf")

                try:
                    create_certificate(navn, dato, filnavn, template_path, signature_path)
                    generated_files.append(filnavn)
                except Exception as e:
                    st.error(f"Feil ved generering av attest for {navn}: {e}")

                progress_bar.progress((i + 1) / len(deltagere))

            status_text.empty()
            progress_bar.empty()

            st.success(f"✅ Genererte {len(generated_files)} attester!")
            st.info(f"Attestene er lagret i mappen: `{DEFAULT_OUTPUT_DIR}`")

            if template_file and os.path.exists(template_path) and template_path != DEFAULT_TEMPLATE:
                os.unlink(template_path)
            if (
                signature_file
                and signature_path
                and os.path.exists(signature_path)
                and signature_path != DEFAULT_SIGNATURE
            ):
                os.unlink(signature_path)

            if generated_files:
                zip_filename = f"attester_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
                    with zipfile.ZipFile(tmp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for file_path in generated_files:
                            zipf.write(file_path, os.path.basename(file_path))

                    with open(tmp_zip.name, "rb") as f:
                        st.download_button(
                            label="📥 Last ned alle attester som ZIP",
                            data=f.read(),
                            file_name=zip_filename,
                            mime="application/zip",
                            use_container_width=True,
                        )

                    os.unlink(tmp_zip.name)
    else:
        st.info("👆 Legg til deltakere for å generere attester")


if __name__ == "__main__":
    main()
