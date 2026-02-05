"""CLI: generate certificates from deltagere.csv (run from project root)."""

from attest_gen import generate_certificates, parse_participants_from_file, register_fonts

if __name__ == "__main__":
    register_fonts()
    deltagere = parse_participants_from_file("deltagere.csv")
    generate_certificates(deltagere)
