PS G:\내 드라이브\Codyssey\02_AI_Tools\B3-2> python --version
>> $env:AI_API_KEY="***"
>> python main.py --help
>> python main.py commit
>> python main.py pr
>> python main.py commit --safe-mode
Python 3.14.4
usage: main.py [-h] {commit,pr} ...

AI 커밋 메시지 / PR 초안 도우미

positional arguments:
  {commit,pr}
    commit     변경 사항으로 커밋 메시지 생성
    pr         변경 사항으로 PR 제목/본문 초안 생성

options:
  -h, --help   show this help message and exit
[INFO] 현재 브랜치: feat/step-9
[INFO] 변경 파일 1개, diff 0줄 수집
  ?? README.md
[INFO] AI API 호출 1회
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
docs: README.md 파일 추가

- 프로젝트 설명을 위한 README.md 파일 생성
----------------------
[INFO] 현재 브랜치: feat/step-9
[INFO] 변경 파일 1개, diff 0줄 수집
  ?? README.md
[INFO] AI API 호출 1회
[DONE] PR 초안 생성 완료

--- PR Title ---
docs: README.md 파일 생성

--- PR Body ---
## Why
- 프로젝트에 대한 기본 설명과 사용법을 안내하는 문서가 없어 추가가 필요함.

## What
- 새로운 README.md 파일 생성

## How to Test
- 프로젝트 루트 디렉터리에 `README.md` 파일이 정상적으로 생성되었는지 확인한다.
- `cat README.md` 명령어로 내용을 확인한다.
----------------
[INFO] 현재 브랜치: feat/step-9
[INFO] 변경 파일 1개, diff 0줄 수집
  ?? README.md
[INFO] safe-mode ON: 민감정보 0건 마스킹
[INFO] AI API 호출 1회
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
docs: README.md 파일 추가

- 프로젝트 설명을 위한 README.md 파일 생성
----------------------