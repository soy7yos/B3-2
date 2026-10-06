import argparse
import sys

from ai_client import AIError, call_ai, load_api_key
from git_utils import GitError, collect_changes
from safe_mode import mask_sensitive

# 왜: 기본값을 상수로 모아 두면 --help와 코드가 같은 값을 쓰고, 8단계 실험 때 바꿀 곳이 한 군데다.
# 왜: 2.5 계열은 신규 키 접근이 제한되고 3 Flash는 프리뷰다. 3.5 Flash-Lite는 안정 버전이고 무료 한도가 하루 500회로 가장 넉넉하다.
DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_TEMPERATURE = 0.3  # 왜: 커밋 메시지는 창의성보다 일관성이 중요해 낮게 둔다
DEFAULT_MAX_TOKENS = 512  # 왜: 커밋 메시지·PR 초안은 짧다. 단 thinking 토큰도 이 상한에 포함되므로, 응답이 잘리면(MAX_TOKENS) 이 값을 올린다


def build_parser():
    # 왜: 공통 옵션을 parents로 한 번만 정의해 commit/pr 양쪽에 똑같이 붙인다.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--model", default=DEFAULT_MODEL, help="사용할 AI 모델 (기본: %(default)s)")
    common.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE,
                        help="출력 다양성 0.0~2.0 (기본: %(default)s)")
    common.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                        help="응답 최대 토큰 수 (기본: %(default)s)")
    # 왜: 결정대로 기본 OFF, 플래그를 주면 ON. store_true가 그 의미와 맞는다.
    common.add_argument("--safe-mode", action="store_true",
                        help="diff의 API 키·이메일·전화번호를 마스킹해서 전송")

    parser = argparse.ArgumentParser(prog="main.py", description="AI 커밋 메시지 / PR 초안 도우미")
    # 왜: required=True로 명령 없이 실행하면 argparse가 사용법과 함께 오류를 내준다.
    sub = parser.add_subparsers(dest="command", required=True, metavar="{commit,pr}")
    sub.add_parser("commit", parents=[common], help="변경 사항으로 커밋 메시지 생성")
    sub.add_parser("pr", parents=[common], help="변경 사항으로 PR 제목/본문 초안 생성")
    return parser


def main():
    args = build_parser().parse_args()
    try:
        branch, files, diff = collect_changes()
    except GitError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # 왜: "변경 없음"은 status 기준으로 판정한다. untracked만 있으면 diff는 비어도 변경은 있다.
    if not files:
        print("[INFO] 변경 사항이 없습니다. 파일을 수정한 뒤 다시 실행하세요.")
        return

    print(f"[INFO] 현재 브랜치: {branch}")
    print(f"[INFO] 변경 파일 {len(files)}개, diff {len(diff.splitlines())}줄 수집")
    for line in files:
        print(f"  {line}")
    # 왜: 마스킹은 API 호출 직전이 아니라 수집 직후에 한다. 이후 어떤 코드도 원문 diff를 못 만지게 해 유출 경로를 줄인다.
    if args.safe_mode:
        diff, masked = mask_sensitive(diff)
        print(f"[INFO] safe-mode ON: 민감정보 {masked}건 마스킹")

    # 왜: 키 검사는 git 수집 뒤, API 호출 앞에서 한다. 키가 없으면 호출 없이 바로 끝낸다.
    try:
        api_key = load_api_key()
        # 5·6단계에서 commit/pr 전용 프롬프트로 바꾼다. 4단계는 호출 경로 검증용 임시 프롬프트.
        result = call_ai(f"다음 diff를 한 줄로 요약해줘:\n{diff}", api_key, args.model, args.temperature, args.max_tokens)
    except AIError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    print(result)


if __name__ == "__main__":
    main()