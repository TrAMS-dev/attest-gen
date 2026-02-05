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
   - I sidepanelet: Velg **kursdato**, last opp signaturbilde (og eventuelt malbilde), og evt. mappe for lagring
   - I hovedområdet: Skriv inn deltakernes navn (ett per linje)
   - Klikk på "Generer attester" for å lage PDF-ene
   - Last ned alle attester som en ZIP-fil hvis ønskelig

## Filstruktur

```
attest-gen/
├── app.py              # Streamlit-app (kjør: streamlit run app.py)
├── cli.py              # Kommandolinje (kjør: python cli.py)
├── requirements.txt
├── attest_gen/          # Pakke med felles logikk
│   ├── __init__.py
│   ├── certificate.py  # PDF-generering og CSV-parsing
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

