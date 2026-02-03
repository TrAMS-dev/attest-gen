# Heisann TrAMS sekretær!

## Hvordan bruke dette scriptet

Dette scriptet er designet for å lage ferdiglagde TrAMS-attester for HLR kurs. Følg trinnene nedenfor for å komme i gang:

1. **Klon repoet til din lokale maskin**:
   ```bash
   git clone https://github.com/TrAMS/attest-gen.git
    ```
1. **Installer Python**: Sørg for at du har Python installert på din datamaskin. Du kan laste det ned fra [python.org](https://www.python.org/downloads/).

2. **Sett opp et virtuelt miljø**: 
   ```bash
   source venv/bin/activate  # På Windows bruk: venv\Scripts\activate
   ```

3. **Bytt ut signatur med nåværende leder**:  Åpne `signature.png` i en bildebehandler og erstatt den med nåværedne leders signatur.

4. **Legg til deltakerdata i `deltagere.csv` i følgende format**:
   ```
   Navn,Dato
   ```

5. **Kjør scriptet**: Kjør scriptet med `python script.py` i terminalen. Dette vil generere attester for alle deltakere i `deltagere.csv`.

6. **Sjekk utdata**: Attestene vil bli lagret i `attester`-mappen. Denne kan du komprimere til en zip-fil og sende til kursarrangøren.

## Skapere

Peder Brennum <peder.brennum@gmail.com>
Markus Helbæk <markus.helbaek@gmail.com>

Gjerne ta kontakt dersom du har spørsmål eller trenger hjelp!

