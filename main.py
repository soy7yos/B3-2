import argparse
import sys

from git_utils import GitError, collect_changes

# 왜: 기본값을 상수로 모아 두면 --help와 코드가 같은 값을 쓰고, 8단계 실험 때 바꿀 곳이 한 군데다.
DEFAULT_MODEL = "gemini-2.5-flash"  # 4단계에서 3 Flash와 비교해 확정
DEFAULT_TEMPERATURE = 0.3  # 왜: 커밋 메시지는 창의성보다 일관성이 중요해 낮게 둔다
DEFAULT_MAX_TOKENS = 512  # 왜: 커밋 메시지·PR 초안은 짧아서 비용 절약을 위해 작게 둔다


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
    # 3단계 이후: safe-mode → API 호출로 이어진다. args는 그때 쓴다.


if __name__ == "__main__":
    main()