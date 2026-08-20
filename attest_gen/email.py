"""Send certificate PDFs via Resend."""

from __future__ import annotations

import base64
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import resend

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class SendResult:
    """Outcome of sending one certificate email."""

    email: str
    name: str
    ok: bool
    error: str | None = None
    email_id: str | None = None


def is_valid_email(email: str) -> bool:
    """Basic email format check."""
    return bool(EMAIL_RE.match(email.strip()))


def get_resend_config(secrets: object | None = None) -> tuple[str, str]:
    """Resolve Resend API key and from-address from secrets or environment.

    Args:
        secrets: Optional mapping (e.g. ``st.secrets``). Env vars used as fallback.

    Returns:
        ``(api_key, from_address)``.

    Raises:
        ValueError: If either value is missing.
    """

    def _get(key: str) -> str:
        value = None
        if secrets is not None:
            try:
                if hasattr(secrets, "get"):
                    value = secrets.get(key)  # type: ignore[union-attr]
                else:
                    value = secrets[key]  # type: ignore[index]
            except Exception:  # noqa: BLE001 — Streamlit raises if key/file missing
                value = None
        if not value:
            value = os.environ.get(key)
        return (value or "").strip()

    api_key = _get("RESEND_API_KEY")
    from_addr = _get("RESEND_FROM")
    if not api_key:
        raise ValueError(
            "Mangler RESEND_API_KEY. Sett den i .streamlit/secrets.toml eller som miljøvariabel."
        )
    if not from_addr:
        raise ValueError(
            "Mangler RESEND_FROM. Sett den i .streamlit/secrets.toml eller som miljøvariabel."
        )
    return api_key, from_addr


def render_template(template: str, *, navn: str, dato: str) -> str:
    """Replace ``{navn}`` and ``{dato}`` placeholders in a template string."""
    return template.replace("{navn}", navn).replace("{dato}", dato)


def send_certificate_email(
    *,
    to: str,
    subject: str,
    text: str,
    pdf_path: str,
    api_key: str | None = None,
    from_addr: str | None = None,
    secrets: object | None = None,
) -> SendResult:
    """Send one plain-text email with a PDF attachment via Resend.

    Does not raise on Resend failures; returns ``SendResult`` instead.
    """
    name_for_result = Path(pdf_path).stem
    try:
        if not api_key or not from_addr:
            api_key, from_addr = get_resend_config(secrets)
        resend.api_key = api_key

        with open(pdf_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        filename = os.path.basename(pdf_path)
        response = resend.Emails.send(
            {
                "from": from_addr,
                "to": [to],
                "subject": subject,
                "text": text,
                "attachments": [
                    {
                        "filename": filename,
                        "content": content,
                    }
                ],
            }
        )
        email_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        return SendResult(email=to, name=name_for_result, ok=True, email_id=email_id)
    except Exception as e:  # noqa: BLE001 — batch send must continue on failure
        return SendResult(email=to, name=name_for_result, ok=False, error=str(e))


def send_certificates_batch(
    recipients: list[tuple[str, str, str, str]],
    *,
    subject_template: str,
    body_template: str,
    secrets: object | None = None,
    on_progress: Callable[[int, int, SendResult], None] | None = None,
) -> list[SendResult]:
    """Send certificates to many recipients sequentially.

    Args:
        recipients: List of ``(navn, dato, email, pdf_path)``.
        subject_template: Subject with optional ``{navn}`` / ``{dato}``.
        body_template: Plain-text body with optional ``{navn}`` / ``{dato}``.
        secrets: Optional secrets mapping for Resend config.
        on_progress: Optional ``callback(index, total, result)``.
    """
    api_key, from_addr = get_resend_config(secrets)
    results: list[SendResult] = []
    total = len(recipients)

    for i, (navn, dato, email, pdf_path) in enumerate(recipients):
        subject = render_template(subject_template, navn=navn, dato=dato)
        text = render_template(body_template, navn=navn, dato=dato)
        result = send_certificate_email(
            to=email,
            subject=subject,
            text=text,
            pdf_path=pdf_path,
            api_key=api_key,
            from_addr=from_addr,
        )
        # Prefer participant name in the result for UI reporting
        result = SendResult(
            email=result.email,
            name=navn,
            ok=result.ok,
            error=result.error,
            email_id=result.email_id,
        )
        results.append(result)
        if on_progress:
            on_progress(i + 1, total, result)

    return results
