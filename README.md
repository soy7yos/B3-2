# AI 커밋/PR 도우미

내가 고친 코드(`git status`·`git diff`)를 읽어 AI(Gemini)가 **커밋 메시지**와 **PR 초안(Why/What/How to Test)** 을 터미널에 써 주는 Python CLI입니다.
명령 한 번에 AI API를 1회 호출하고, 결과는 초안 텍스트까지만 출력합니다. `git commit`·`git push`·PR 생성은 하지 않습니다.

## 설치

- Python 3.10 이상, Git
- 외부 라이브러리 없음(표준 라이브러리만 사용) — `pip install`이 필요 없습니다.

```bash
git clone https://github.com/soy7yos/B3-2.git
cd B3-2
python --version   # 3.10 이상인지 확인 (Mac/Linux는 python3)
```

## 환경변수(API Key) 설정

[Google AI Studio](https://aistudio.google.com/apikey)에서 Gemini API 키를 발급받아 환경변수 `AI_API_KEY`로 설정합니다. 코드나 파일에 키를 적지 않습니다(`.env.example`은 변수 이름만 보여 주는 참고용이며, 프로그램이 `.env`를 읽지는 않습니다).

```bash
# Mac / Linux
export AI_API_KEY=발급받은키

# Windows PowerShell
$env:AI_API_KEY="발급받은키"
```

설정하지 않고 실행하면 API 호출 없이 위 설정 예시와 함께 종료합니다.

## 실행

**변경이 있는 Git 저장소의 루트**에서 실행합니다. 이 도구를 복제한 폴더가 아니라, 커밋 메시지를 받고 싶은 프로젝트 폴더입니다(그 폴더에서 `python <이 repo 경로>/main.py ...`).

```bash
python main.py commit        # 커밋 메시지 생성
python main.py pr            # PR 제목 + 본문 생성
python main.py --help        # 전체 옵션
```

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--model` | `gemini-3.5-flash-lite` | 사용할 Gemini 모델 |
| `--temperature` | `0.3` | 출력 다양성(0.0~2.0). 낮을수록 일관됨 |
| `--max-tokens` | `512` | 응답 최대 토큰. 너무 작으면 답이 잘림 |
| `--safe-mode` | 꺼짐 | diff의 API 키·이메일·전화번호를 가려서 전송 |

```bash
python main.py commit --temperature 0.7 --max-tokens 1024
python main.py pr --safe-mode
```

> 새로 만든(untracked) 파일은 **`git add` 후 실행**하세요. 목록에는 이름만 표시되고, 내용은 `git add`로 추적된 뒤에야 diff에 포함됩니다.

## 출력 예시

### 커밋 메시지

```
[INFO] 현재 브랜치: feat/step-7
[INFO] 변경 파일 3개, diff 45줄 수집
   M main.py
  ?? format_output.py
  ?? logs/step_7_format.txt
[INFO] AI API 호출 1회
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
feat: 커밋 메시지 및 PR 출력 포맷팅 적용

- main.py에 `format_output.py` 모듈을 연동하여 커밋과 PR의 출력 포맷을 개선함
- 후처리 결과 및 경고(`notes`) 메시지 출력 로직을 추가함
- `format_output.py` 및 관련 로그 파일 추가
----------------------
```

### PR 초안

```
[DONE] PR 초안 생성 완료

--- PR Title ---
refactor: AI 응답 후처리를 위한 format_output 모듈 분리 및 적용

--- PR Body ---
## Why
- AI가 생성한 커밋 메시지와 PR 초안의 출력 포맷 검증 및 후처리 로직을 분리하여 코드의 응집도와 가독성을 높이고자 함
- 출력 결과물에 경고 문구가 직접 섞이지 않도록 분리된 경고 시스템을 도입할 필요가 있음

## What
- `format_output.py` 새 모듈을 추가하여 커밋 및 PR 결과물 포맷팅 함수(`format_commit`, `format_pr`) 구현
- `main.py`에 새 포맷팅 함수를 적용하고, 후처리 과정에서 발생한 경고(`notes`)를 별도로 출력하도록 로직 수정

## How to Test
- 아래 명령어로 커밋 메시지 생성 기능을 실행하여 포맷이 정상 출력되는지 확인
`python main.py commit`
- 아래 명령어로 PR 초안 생성 기능을 실행하여 제목과 본문이 올바르게 분리되어 출력되는지 확인
`python main.py pr`
----------------
```

복사할 결과는 구분선 안쪽뿐이고, 후처리로 바뀐 점은 구분선 밖에 `[WARN]`으로 따로 나옵니다.

## 주의사항

**민감정보 — `--safe-mode`**
diff는 그대로 외부 AI 서버로 전송됩니다. 코드에 API 키·이메일·전화번호가 섞여 있을 수 있으면 `--safe-mode`를 켜세요. 전송 전에 `AIza…`·`sk-…` 모양의 키, 이메일, 전화번호를 정규식으로 찾아 `[MASKED_API_KEY]`·`[MASKED_EMAIL]`·`[MASKED_PHONE]` 표시로 바꾸고 마스킹한 건수를 출력합니다. 패턴에 없는 형식(예: `password=`)은 가려지지 않으니 diff를 직접 확인하는 습관은 여전히 필요합니다.

**비용·요청 횟수**
`commit`·`pr`은 각각 **AI API를 1회만** 호출하고, 실행 로그에 `[INFO] AI API 호출 1회`로 표시합니다. 형식이 규칙에서 벗어나도 다시 호출하지 않고 코드로 고칩니다. 기본 모델의 무료 한도는 하루 약 500회입니다(Google 정책에 따라 변동).

**오류 안내**

| 상황 | 동작 |
|---|---|
| Git 저장소가 아님 | `git 저장소가 아닙니다` 안내 후 종료 |
| 변경 없음 | `변경 사항이 없습니다` 후 종료(API 호출 안 함) |
| 키 없음 | 호출 전에 설정 예시와 함께 종료 |
| 틀린 키·한도 초과·서버·네트워크·시간 초과 | 원인을 구분한 `[ERROR]` 메시지 |

## 구현 기능

- `git status`·`git diff HEAD` 수집(`git_utils.py`)
- Gemini REST 호출과 예외 구분(`ai_client.py`)
- 커밋/PR 프롬프트(`prompts.py`), safe-mode 마스킹(`safe_mode.py`)
- 길이·섹션·불릿 검증 후처리(`format_output.py`): 커밋 제목 50자 이내 권장·72자 초과 시 자름, PR 제목 80자 제한, Why/What/How to Test 순서 재조립, 빠진 섹션·불릿은 자리표시자로 채움

## 설계 선택: 왜 이렇게 했나

- **`urllib` 직접 호출**: 설치할 게 없고, 요청에 무엇이 실려 가는지 코드에서 그대로 보입니다.
- **`git diff HEAD`**: `add` 여부와 상관없이 마지막 커밋 이후 변경을 모두 받는 명령 하나로 충분합니다.
- **commit/pr가 수집·마스킹·호출 경로를 공유**: 프롬프트만 갈라 코드 중복을 없앴습니다.
- **마스킹을 수집 직후에**: 이후 어떤 코드도 원문 diff를 만지지 못하게 해 유출 경로를 줄입니다.
- **후처리(재생성 아님)**: 규칙을 어긴 응답을 다시 요청하면 호출이 2회가 됩니다. 코드로 고치면 호출은 1회이고, 결과가 매번 같아 검증하기 쉽습니다.
- **`temperature` 0.3**: 커밋 메시지는 창의성보다 일관성이 중요해 낮게 뒀습니다.
- **`max-tokens` 512**: 초안은 짧습니다. 다만 모델의 생각(thinking) 토큰도 이 상한에 포함되므로, 64처럼 너무 작게 주면 본문이 잘립니다(실험으로 확인, 아래 표).
- **기본 모델 `gemini-3.5-flash-lite`**: 2.5 계열은 신규 키 접근이 제한되고, 3 Flash는 프리뷰에 무료 한도가 작습니다.

## 검증 기록 (`logs/`)

각 단계의 실제 실행 결과를 `logs/`에 남겼습니다.

| 로그 | 확인한 것 |
|---|---|
| `step_1_cli.txt` | `--help`, `commit` 인자 파싱·기본값 |
| `step_2_git.txt` | 변경 있음/없음, 저장소 아님 처리 |
| `step_3_safe_mode.txt` | 가짜 키·이메일 diff의 ON/OFF 비교 |
| `step_4_api.txt` | 키 없음·틀린 키·정상 호출 |
| `step_5_commit.txt` | 제목 1줄 + 본문 불릿 |
| `step_6_pr.txt` | Why/What/How to Test 세 섹션, safe-mode 병행 |
| `step_7_format.txt` | 규칙 위반 샘플 후처리, 실제 실행 |
| `step_8_params.txt` | temperature·max-tokens 값별 비교(9회 실행) |

**파라미터 실험 요약** — 같은 diff로 `pr`을 9회 실행했습니다(temperature 0·1·2 각 2회 @max-tokens 1024, max-tokens 64·256·1024 @temperature 0.3). max-tokens 64에서는 본문이 잘려 후처리가 자리표시자로 채우고 `[WARN]`을 냈고, 256 이상은 정상이었습니다. temperature 간 차이는 `step_8_params.txt`에서 직접 비교할 수 있습니다.
