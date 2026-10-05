import subprocess


class GitError(Exception):
    pass


def _run(*args):
    # 왜: 한글 파일명이 status에서 "\355..." 같은 이스케이프로 나오지 않게 quotepath를 끄고,
    #     Windows 기본 인코딩(cp949)으로 diff가 깨지지 않게 utf-8로 읽는다.
    try:
        return subprocess.run(["git", "-c", "core.quotepath=false", *args],
                              capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        raise GitError("git을 찾을 수 없습니다. git을 설치한 뒤 다시 실행하세요.")


def collect_changes():
    """(현재 브랜치, 변경 파일 목록, diff 텍스트)를 돌려준다. 변경이 없으면 파일 목록이 빈 리스트."""
    # 왜: git 원문 에러(fatal: not a git repository)는 비개발자가 원인을 읽기 어려워 따로 안내한다.
    #     returncode로 판정해 git 언어 설정(한글 메시지)에 영향받지 않는다.
    if _run("rev-parse", "--is-inside-work-tree").returncode != 0:
        raise GitError("git 저장소가 아닙니다. 변경 사항이 있는 git 프로젝트 폴더에서 실행하세요.")

    # 왜: --short --branch는 첫 줄이 "## 브랜치...", 나머지가 파일별 한 줄이라 파싱이 쉽고,
    #     추가 git 명령 없이 브랜치명까지 얻는다(§7 status·diff 범위 유지).
    lines = _run("status", "--short", "--branch").stdout.splitlines()
    branch = lines[0][3:].split("...")[0]
    files = lines[1:]

    # 왜: `git diff HEAD`는 add 여부와 무관하게 마지막 커밋 이후 변경 전부를 준다.
    #     untracked 새 파일은 diff에 안 나오므로 이름만 files에 남는다(내용은 보내지 않음).
    diff = _run("diff", "HEAD")
    if diff.returncode != 0:  # 첫 커밋 전 저장소 등
        raise GitError(f"git diff 실패: {diff.stderr.strip()}")
    return branch, files, diff.stdout