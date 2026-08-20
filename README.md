# Heisann TrAMS sekretær!

## Hvordan bruke denne appen

Denne Streamlit-appen er designet for å lage ferdiglagde TrAMS-attester for HLR kurs. Følg trinnene nedenfor for å komme i gang:

1. **Klon repoet til din lokale maskin**:

   ```bash
   git clone https://github.com/TrAMS-dev/attest-gen.git
   ```

2. **Installer Python**: Sørg for at du har Python installert på din datamaskin. Du kan laste det ned fra [python.org](https://www.python.org/downloads/).

3. **Sett opp et virtuelt miljø**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # På Windows bruk: venv\Scripts\activate
   ```

4. **Installer nødvendige pakker**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Kjør Streamlit-appen**:

   ```bash
   streamlit run app.py
   ```

   Appen vil automatisk åpne i nettleseren din. Hvis ikke, gå til `http://localhost:8501`.

6. **Bruk appen**:
   - Velg **kursdato**, last opp signaturbilde (og eventuelt malbilde)
   - Under **Deltakere**, velg **Kun navn** eller **Navn + e-post**
   - **Kun navn**: skriv inn deltakernes navn (ett per linje), generer, og last ned ZIP
   - **Navn + e-post**: lim inn navn og e-poster i hver sin tekstboks (samme antall linjer, linje 1 matcher linje 1). Etter generering kan du sende hver person sitt deltakerbevis på e-post
   - Klikk på "Generer attester" for å lage PDF-ene
   - Last ned alle attester som en ZIP-fil hvis ønskelig

### Sende attester på e-post (Resend)

Appen bruker [Resend](https://resend.com) til å sende e-post med PDF-vedlegg.

1. Opprett en Resend-konto og verifiser domenet du vil sende fra.
2. Kopier eksempel-filen og fyll inn verdier:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   ```toml
   # .streamlit/secrets.toml
   RESEND_API_KEY = "re_..."
   RESEND_FROM = "TrAMS <attester@your-verified-domain.no>"
   ```

3. Restart Streamlit-appen etter at secrets er satt.
4. Velg **Navn + e-post**, generer attester, rediger emne/melding (bruk `{navn}` og `{dato}`), forhåndsvis, og klikk **Send e-poster**.

`secrets.toml` er gitignorert og skal ikke committes.

## Filstruktur

```
attest-gen/
├── app.py              # Streamlit-app (kjør: streamlit run app.py)
├── cli.py              # Kommandolinje (kjør: python cli.py)
├── requirements.txt
├── .streamlit/
│   └── secrets.toml.example
├── attest_gen/          # Pakke med felles logikk
│   ├── __init__.py
│   ├── certificate.py  # PDF-generering og CSV-parsing
│   ├── email.py        # Resend e-postsending med PDF-vedlegg
│   └── paths.py       # Stier til ressurser
└── assets/             # Maler og fonter
    ├── Template.png    # Mal for attestene (kan overstyres i appen)
    ├── signature.png   # Standard signatur (kan overstyres i appen)
    └── fonts/
        ├── centurygothic.ttf
        └── centurygothic_bold.ttf
```

**Kommandolinje (uten Streamlit):** Lag `deltagere.csv` med kolonnene Navn,Dato og kjør `python cli.py`. Attestene lagres i mappen `attester/`.

## Skapere

* Peder Brennum <peder.brennum@gmail.com>
* Markus Helbæk <markus.helbaek@gmail.com>

Gjerne ta kontakt dersom du har spørsmål eller trenger hjelp!
