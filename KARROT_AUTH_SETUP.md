# 당근 OAuth 연결: 최초 로그인 검증

이 변경은 별도 모니터링 프로그램으로 당근 로그인이 가능한지 검증하는 단계입니다. 광고 조회/변경, Slack 발송, 정기 실행을 하지 않습니다. 기존 Codex 인증값을 추출하지 않습니다.

당근 공개 인증 메타데이터에서 `client_id_metadata_document_supported=true`, PKCE S256, `ads:read`, `offline_access`, refresh_token 지원을 확인했습니다. 따라서 이 저장소의 공개 JSON을 클라이언트 ID로 사용하는 표준 OAuth 흐름을 준비했습니다. **서버의 지원 표시는 이 프로그램의 승인을 보장하지 않습니다. 실제 사용자 로그인 및 토큰 발급은 아직 미검증입니다.**

## 실행

1. `karrot-oauth-setup` 브랜치의 `karrot_login.py`를 PC에 다운로드하거나 해당 브랜치를 체크아웃합니다.
2. Windows의 Python 3.12 환경에서 파일이 있는 폴더를 열고 실행합니다:

```powershell
py -3.12 karrot_login.py
```

Python 3.12가 `python` 명령으로 설정된 환경은 `python karrot_login.py`로 실행할 수 있습니다. 추가 패키지는 필요 없습니다.

3. 열린 당근 로그인 화면에서 앱 이름과 조회 권한을 확인하고 로그인합니다. 이때 PC와 브라우저가 켜져 있어야 합니다. 최초 로그인 준비 단계이며, 이후 클라우드 무인 실행과는 별개입니다.
4. 터미널에서 `OAuth login succeeded`와 `Refresh token present: True/False`를 확인합니다. 결과 문구만 공유하고 인증 JSON 내용은 공유하지 마세요.

브라우저가 안 열리면 터미널에 표시된 로그인 URL을 같은 PC 브라우저에서 여세요. 오류면 표시된 HTTP 코드 또는 브라우저 오류 문구만 전달하세요. 주소창 전체에는 민감한 인증 코드가 있을 수 있으므로 공유하지 마세요.

## 저장과 후속 단계

인증값은 저장소 밖의 사용자 홈 폴더에 `karrot-monitor-auth-<random>.json`으로 저장합니다. Unix는 0600, Windows는 사용자 프로필 폴더의 ACL을 따릅니다. 공개 저장소/채팅/Actions 로그/아티팩트에 올리지 마세요.

로그인 성공 후 할 일:
- 실제 MCP 도구 목록 및 응답 스키마 확인
- `ads:read` 권한으로 두 계정 조회 검증
- 비용/예산의 VAT 기준 및 페이지네이션 처리
- 갱신 토큰 회전 여부와 만료/철회 정책 확인
- 회전된 토큰을 다음 Actions 실행에서도 쓰도록 안전한 영구 저장소 구현
- 이후에만 무인 실행 및 Slack 연결

현재 파일을 GitHub Secret에 넣는 것만으로 자동화가 완성되지 않습니다. 회전된 갱신 토큰을 영구 저장하지 않으면 다음 실행에서 실패할 수 있습니다.

로그인 실패 시 임의로 다른 앱의 client_id나 Codex의 토큰을 복사하지 않습니다. 당근에 자체 OAuth 클라이언트 허용/등록 조건을 확인합니다.

공개 client_id 주소가 이 브랜치를 참조하므로 **인증을 쓰는 동안 해당 브랜치 및 JSON을 삭제하지 마세요.** 안정 운영 전 고정 URL로 옮기면 재로그인이 필요할 수 있습니다.

## 검증 범위

PKCE 공식 테스트 벡터, callback state/issuer 검증, 토큰 저장/덮어쓰기 방지 및 공개 JSON 일치를 로컬에서 테스트했습니다. 당근 로그인·토큰 발급·광고 데이터 조회는 사용자의 로그인 후 검증해야 합니다.

참고: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
