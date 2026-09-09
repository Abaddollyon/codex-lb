from __future__ import annotations

import pytest

from app.core.runtime_logging import _redact_log_value, redact_rendered_log_text

pytestmark = pytest.mark.unit

_TOKEN = "Qm9iLWludml0ZS10b2tlbi0xMjM0NTY3ODkw_abc-DEF"


def test_invite_path_token_is_redacted_in_rendered_text_at_every_level() -> None:
    line = f'"GET /api/dashboard-auth/invite/{_TOKEN} HTTP/1.1" 404'
    for keyed in (True, False):
        redacted = redact_rendered_log_text(line, keyed_secrets=keyed)
        assert _TOKEN not in redacted
        assert redacted == '"GET /api/dashboard-auth/invite/[REDACTED] HTTP/1.1" 404'


def test_invite_accept_route_and_short_segments_stay_readable() -> None:
    accept = "POST /api/dashboard-auth/invite/accept 422"
    assert redact_rendered_log_text(accept) == accept
    short = "GET /api/dashboard-auth/invite/x 404"
    assert redact_rendered_log_text(short) == short


def test_error_log_field_path_is_redacted() -> None:
    value = _redact_log_value(f"/api/dashboard-auth/invite/{_TOKEN}?x=1")
    assert value == "/api/dashboard-auth/invite/[REDACTED]?x=1"
