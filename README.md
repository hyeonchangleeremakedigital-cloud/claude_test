# 당근 광고비 → Slack (GitHub Actions 초기 코드)

현재 상태: 계산·Slack 발송·Actions 예약 코드 작성 완료. **당근 실제 수집 어댑터는 미구현**입니다. MCP URL, 읽기 도구 이름/인자, 인증 방식, 응답 구조가 없어 공식 API를 추측하지 않았습니다. 샘플 모드는 지금 실행할 수 있습니다. 외부 서버 연결과 실제 Slack 발송은 검증하지 않았습니다.

## 포함 기능

- 매시 05분 예약. 조회 날짜·표시 시각은 Asia/Seoul.
- 당근DA 1998645 / 4342379, 광고그룹별 당일 누적 비용·현재 일 예산·소진율.
- 비용 / 예산 × 100. 비용과 예산 모두 KRW, VAT 포함으로 정규화한 데이터만 허용.
- 계정별 소계 및 전체 합계. 실패 계정은 금액 미확정 표시, 전체 합계 생략, 실행 실패 처리.
- 누락 금액, 중복 ID, 미완료 페이지, 다른 날짜, 오래된 데이터 검증.
- 광고 설정 변경 없음. 샘플 데이터 Slack 발송 차단.

## 파일

- `.github/workflows/ad-monitor.yml`: 예약 및 수동 실행
- `monitor.py`: 검증, 계산, 보고서, Slack 발송
- `daangn_adapter.py`: 실제 당근 연결 구현 위치와 내부 데이터 계약
- `tests/test_monitor.py`: 계산 및 실패 처리, 모의 Slack 테스트

## 1. GitHub에 코드 넣기

ZIP을 풀어 **daangn-spend-monitor 폴더 안의 내용**을 저장소 루트에 넣으세요. `.github` 숨김 폴더도 반드시 포함해야 합니다. 경로는 저장소 루트 기준 `.github/workflows/ad-monitor.yml`이어야 합니다. 기본 브랜치(main 등)에 커밋하세요.

이미 파일이 있는 저장소는 README, .gitignore 등을 덮어쓰지 말고 병합하세요.

## 2. 샘플 먼저 확인

GitHub → Actions → Daangn spend monitor → Run workflow → mode: demo.

또는 Python 3.12 환경에서:

```bash
python -m unittest discover -s tests -v
python monitor.py --demo
```

외부 Python 패키지는 필요 없습니다. GitHub Ubuntu 실행 환경을 기준으로 합니다.

샘플 계정 소계: 742,300 / 1,200,000 = 61.9%, 384,200 / 700,000 = 54.9%.
샘플 합계: 1,126,500 / 1,900,000 = 59.3%. 실제 광고 데이터가 아닙니다.

## 3. 당근 연결 완성 — 다음 단계

`daangn_adapter.py`의 `fetch_account()`를 실제 읽기 API 또는 Remote MCP 호출로 교체해야 합니다. **현재는 의도적으로 NotImplementedError가 발생합니다.**

필요한 정보:

1. 당근 MCP 서버 주소 또는 사용하는 서비스/저장소 링크
2. 원격 HTTP 방식인지, 로컬 Chrome 의존 방식인지
3. 광고그룹·비용·예산을 읽는 MCP 도구 이름, 인자 명세, 비식별 응답 예시
4. 인증 방식과 토큰 갱신 방법 (비밀값 자체는 채팅에 공유하지 않기)
5. 비용/예산의 VAT 기준, 일 예산 여부, 통계 반영 시각 정의

MCP 주소에 일반 HTTP GET만 보내면 되는 구조가 아닙니다. 해당 전송 방식의 MCP 클라이언트로 초기화·세션·도구 호출을 구현해야 합니다. 인증값은 GitHub Secrets에 넣고 workflow의 env에서 전달하세요. 로컬 Chrome 의존형이면 클라우드에서 사용할 수 있는 API 또는 서버 구성이 먼저 필요합니다.

수집 함수의 내부 반환 구조 예시는 코드 docstring에 있습니다. 이것은 당근 공식 응답 스키마가 아닙니다. 전체 페이지를 수집하고 ID로 조인한 후 반환해야 합니다. 예산이 공유되거나 총예산이면 중복 합산하지 말고 별도 규칙을 정의해야 합니다. 예산 변경이 있으면 소진율의 분모는 조회 시점의 일 예산입니다.

## 4. Slack 연결

Slack 앱에서 Incoming Webhooks를 활성화하고 결과를 받을 채널의 Webhook URL을 생성하세요.

GitHub 저장소 → Settings → Secrets and variables → Actions → Secrets → New repository secret:

| 이름 | 값 |
| --- | --- |
| SLACK_WEBHOOK_URL | 발급받은 https://hooks.slack.com/services/... URL |

Webhook URL은 코드나 공개 저장소에 넣지 마세요. Slack의 채널 선택은 Webhook 생성 시 결정합니다.

## 5. 실데이터 검증 후 예약 활성화

1. 어댑터를 구현하고 필요한 당근 Secrets/env를 연결합니다.
2. Run workflow → preview: 실데이터를 읽어 Actions 로그에서 확인합니다. Slack 발송 없음. 로그에는 광고비가 표시되므로 저장소 접근 권한에 유의하세요.
3. Run workflow → live: 조회 후 실제 Slack 발송. 실패 계정도 실패 상태로 알립니다.
4. Settings → Secrets and variables → Actions → Variables에 `MONITOR_ENABLED` = `true`를 추가하면 예약 실행됩니다.

변수가 없으면 예약 job은 건너뜁니다. 중지하려면 false로 바꾸세요. 기본 제공 상태에서는 예약 발송되지 않습니다.

## 운영상 제한

- Actions 예약은 정확한 05분 실행을 보장하지 않습니다. 부하에 따라 지연 또는 누락될 수 있습니다. 기본 브랜치에 workflow가 있어야 합니다. 공개 저장소는 60일간 활동이 없으면 예약 workflow가 비활성화될 수 있습니다.
- GitHub 호스팅 실행기를 사용하므로 PC가 꺼져도 실행되지만, 당근 연동도 PC에 독립적이어야 합니다.
- 2시간보다 오래된 원천 데이터는 실패 처리합니다. 실제 제공 주기에 맞게 합의 후 조정하세요.
- Slack 메시지는 plain_text 블록입니다. 표 형태의 텍스트이며 Slack에서 Markdown 표가 렌더링되지는 않습니다. 2,900자를 넘으면 조용히 잘라 보내지 않고 실패합니다. 광고그룹이 많으면 파일 업로드 방식으로 확장하세요.
- Webhook 전송 실패 시 Actions가 실패합니다. 중복 발송을 피하려고 POST 자동 재시도는 하지 않습니다. 타임아웃 후 수동 재실행은 기존 메시지 수신 여부를 먼저 확인하세요.
- 워크플로 실행 중복은 직렬화하지만, 재실행에 대한 영구 중복 방지 저장소는 없습니다.
- 초기 버전은 별도의 장애 Slack 알림 채널 없이 Actions 실패 상태로 확인합니다.

## 공식 참고 문서

- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/
