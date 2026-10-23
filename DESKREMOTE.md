# deskRemote (에스에이치원격)

이 저장소는 오픈소스 원격 데스크톱 프로그램 [RustDesk](https://github.com/rustdesk/rustdesk)를 포크하여
이름·아이콘만 변경한 버전입니다. 원본 저작권 고지와 라이선스(`LICENCE`, AGPL-3.0)는 그대로 유지합니다.

- 원본 프로젝트: RustDesk (https://github.com/rustdesk/rustdesk)
- 변경 내용: 앱 이름, 아이콘, Windows 파일 속성, 한국어/영어 UI 문구 (`deskremote/rebrand.py` 참고)
- 빌드: GitHub Actions `deskRemote Windows Build` 워크플로 (빌드 시 `deskremote/rebrand.py` 자동 실행)
- 라이선스: GNU AGPL-3.0 (원본과 동일)

## 설정 바꾸기
`deskremote/config.json`
- `app_name_en` / `app_name_ko`: 앱 이름
- `server_host` / `server_key`: 내 서버 주소와 공개 키 (비워 두면 RustDesk 공개 서버 사용 = 테스트용)

## 빌드 방법
1. 저장소 Settings → Actions → General → Workflow permissions → **Read and write permissions** 선택 후 Save
2. Actions 탭 → `deskRemote Windows Build` → Run workflow
3. 완료 후 Releases 페이지의 `deskremote-test`에서 `deskRemote-<버전>-x86_64.exe` 다운로드
