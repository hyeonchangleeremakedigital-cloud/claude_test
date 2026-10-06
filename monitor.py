"""Python 3.12+, standard library only. Live data adapter is intentionally unconfigured."""
import argparse
import json
import os
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from daangn_adapter import fetch_account

KST = ZoneInfo('Asia/Seoul')
ACCOUNTS = ('1998645', '4342379')


def amount(value):
    if isinstance(value, bool) or value is None:
        raise ValueError('금액 누락 또는 잘못된 금액')
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError('잘못된 금액') from None
    if not number.is_finite() or number < 0:
        raise ValueError('금액은 0 이상이어야 합니다')
    return number


def validate(data, account_id, now):
    """Require complete, daily, VAT-inclusive KRW data; never turn missing into zero."""
    if data['account_id'] != account_id or data['date'] != now.date().isoformat():
        raise ValueError('계정 또는 KST 조회일 불일치')
    if (data['currency'], data['vat_basis'], data['budget_period']) != ('KRW', 'included', 'daily'):
        raise ValueError('KRW / VAT 포함 / 일 예산 데이터만 지원')
    if data['complete'] is not True:
        raise ValueError('페이지 수집 미완료')
    updated = datetime.fromisoformat(data['as_of'])
    if updated.tzinfo is None or not -60 <= (now - updated).total_seconds() <= 7200:
        raise ValueError('데이터 시각 누락 또는 2시간 이상 지연')
    rows = data['ad_groups']
    if not isinstance(rows, list) or not rows:
        raise ValueError('광고그룹 데이터 없음: 빈 결과 확인 필요')
    seen = set()
    normalized = []
    for row in rows:
        group_id = str(row['id'])
        if not group_id or group_id in seen:
            raise ValueError('광고그룹 ID 누락 또는 중복')
        seen.add(group_id)
        if not isinstance(row['name'], str) or not row['name'].strip():
            raise ValueError('광고그룹 이름 누락')
        normalized.append((row['name'], amount(row['spend']), amount(row['budget'])))
    return normalized, updated.astimezone(KST)


def rate(spend, budget):
    return f'{spend / budget * 100:.1f}%' if budget > 0 else '산출 불가'


def safe_name(name):
    # Plain-text Slack block; flatten names to keep each table row intact.
    return ' '.join(name.replace('|', '/').split())[:80]


def render(results, now, demo=False):
    lines = [f"{'[샘플 · 발송 안 함] ' if demo else ''}당근 광고비 | {now:%Y-%m-%d %H:%M} KST",
             '당일 누적 비용 / 현재 일 예산 · KRW · 모두 VAT 포함',
             '계정 | 광고그룹 | 비용 | 일 예산 | 소진율']
    failed = False
    total_spend = total_budget = Decimal(0)
    for account_id, data in results:
        try:
            if isinstance(data, Exception):
                raise data
            rows, updated = validate(data, account_id, now)
            for name, spend, budget in rows:
                lines.append(f'{account_id} | {safe_name(name)} | {spend:,.0f} | {budget:,.0f} | {rate(spend, budget)}')
            spend = sum((r[1] for r in rows), Decimal(0))
            budget = sum((r[2] for r in rows), Decimal(0))
            total_spend += spend
            total_budget += budget
            lines.append(f'당근DA({account_id}) 소계 | {spend:,.0f}원 / {budget:,.0f}원 | {rate(spend, budget)} | 자료 {updated:%H:%M}')
        except Exception:
            failed = True
            lines.append(f'당근DA({account_id}) | 조회/검증 실패 · 금액 미확정')
    if not failed:
        lines.append(f'전체 합계 | {total_spend:,.0f}원 / {total_budget:,.0f}원 | {rate(total_spend, total_budget)}')
    else:
        lines.append('일부 계정 실패: 전체 합계는 제공하지 않습니다. Actions 로그를 확인하세요.')
    return '\n'.join(lines), failed


def send_slack(text):
    url = os.environ.get('SLACK_WEBHOOK_URL', '')
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname != 'hooks.slack.com' or not parsed.path.startswith('/services/'):
        raise ValueError('SLACK_WEBHOOK_URL 설정 오류')
    # Avoid truncating long reports silently; adjust to file upload if > limit.
    if len(text) > 2900:
        raise ValueError('Slack 블록 길이 초과: 그룹별 보고서를 파일 전송 방식으로 확장하세요')
    payload = {'text': '당근 광고비 모니터링 결과', 'blocks': [
        {'type': 'section', 'text': {'type': 'plain_text', 'text': text, 'emoji': False}}
    ]}
    request = Request(url, data=json.dumps(payload, ensure_ascii=False).encode(),
                      headers={'Content-Type': 'application/json'}, method='POST')
    # No automatic POST retry: uncertain delivery could duplicate a message.
    with urlopen(request, timeout=30) as response:
        if response.status != 200 or response.read().strip() != b'ok':
            raise RuntimeError('Slack 전송 실패')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='샘플 데이터, 외부 연결 없음')
    parser.add_argument('--send', action='store_true', help='실제 Slack 발송')
    args = parser.parse_args()
    if args.demo and args.send:
        parser.error('샘플 데이터는 Slack에 발송하지 않습니다')
    now = datetime.now(KST)
    results = []
    for account_id in ACCOUNTS:
        try:
            data = (demo_data(account_id, now) if args.demo else fetch_account(account_id, now.date()))
        except Exception as exc:
            # Do not log exception messages; SDK errors can contain tokens/URLs.
            print(f'{account_id}: 수집 실패 ({type(exc).__name__})', file=sys.stderr)
            data = exc
        results.append((account_id, data))
    text, failed = render(results, now, args.demo)
    if args.send:
        send_slack(text)
    else:
        print(text)
    return 1 if failed else 0


def demo_data(account_id, now):
    first = account_id == ACCOUNTS[0]
    return {'account_id': account_id, 'date': now.date().isoformat(),
            'as_of': now.isoformat(), 'currency': 'KRW', 'vat_basis': 'included',
            'budget_period': 'daily', 'complete': True,
            'ad_groups': [{'id': 'demo-1', 'name': '샘플 광고그룹',
                           'spend': '742300' if first else '384200',
                           'budget': '1200000' if first else '700000'}]}


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'실행 실패 ({type(exc).__name__}). 연결 설정과 데이터 계약을 확인하세요.', file=sys.stderr)
        sys.exit(1)
