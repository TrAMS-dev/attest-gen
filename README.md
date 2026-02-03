# Heisann TrAMS sekretær!

## Hvordan bruke dette scriptet

Dette scriptet er designet for å lage ferdiglagde TrAMS-attester for HLR kurs. Følg trinnene nedenfor for å komme i gang:

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

5. **Bytt ut signatur med nåværende leder**:  Åpne `signature.png` i en bildebehandler og erstatt den med nåværedne leders signatur.

6. **Lag en `deltagere.csv` fil i samme mappe som `script.py`**.

7. **Legg til deltakerdata i `deltagere.csv` i følgende format**:

   ```csv
   Navn,Dato
   ```

8. **Kjør scriptet**: Kjør scriptet med `python script.py` i terminalen. Dette vil generere attester for alle deltakere i `deltagere.csv`.

9. **Sjekk utdata**: Attestene vil bli lagret i `attester`-mappen. Denne kan du komprimere til en zip-fil og sende til kursarrangøren.

## Skapere

* Peder Brennum <peder.brennum@gmail.com>
* Markus Helbæk <markus.helbaek@gmail.com>

Gjerne ta kontakt dersom du har spørsmål eller trenger hjelp!

