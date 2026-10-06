"""Replace only this adapter after confirming the actual Daangn API/MCP schema.

No endpoint, tool name or authentication mechanism has been assumed.
The returned structure is OUR internal format, not Daangn's API response.
"""
from datetime import date


def fetch_account(account_id: str, day: date) -> dict:
    """Fetch read-only live data for the KST day and normalize it.

    Implementation requirements:
    - Remote API/MCP access independent of local Chrome.
    - Read credentials from environment / GitHub Secrets.
    - Read operations ONLY. Never alter budget, bids, state, filters or settings.
    - Query day 00:00 KST through current time; exhaust pagination.
    - Join spend and budgets on stable ad-group ID (not display name).
    - Include zero-spend groups; don't drop paused groups that spent today.
    - Match VAT basis for spend AND budget using verified API definitions.
    - Reject lifetime/shared budgets until an explicit allocation rule is defined.
    - Preserve missing values as errors; do not silently substitute zero.
    - `as_of`: upstream data timestamp with timezone, not fabricated freshness.
    - Return `complete: True` only after every page was successfully collected.

    Return example (all money in KRW, both VAT included):
    {
      'account_id': account_id, 'date': day.isoformat(),
      'as_of': '2026-10-06T12:00:00+09:00',
      'currency': 'KRW', 'vat_basis': 'included', 'budget_period': 'daily',
      'complete': True,
      'ad_groups': [
        {'id': 'real-id', 'name': 'real-name', 'spend': '742300', 'budget': '1200000'}
      ]
    }
    """
    raise NotImplementedError('당근 Remote MCP/API 연결 명세 확인 후 구현 필요')
