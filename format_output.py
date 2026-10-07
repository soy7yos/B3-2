# 왜: 검증·후처리를 main.py에서 분리하면 AI 호출 없이 이 파일만 단독으로 테스트할 수 있다.
COMMIT_WARN = 50  # 왜: §4-5 커밋 제목은 50자 이내 권장
COMMIT_MAX = 72   # 왜: §4-5 커밋 제목 최대 72자. 50 초과~72는 경고만, 73+는 자른다
PR_MAX = 80       # 왜: §4-5 PR 제목 최대 80자
SECTIONS = ("Why", "What", "How to Test")  # 왜: §4-4가 정한 섹션 이름 그대로, 출력 순서도 이 순서로 고정한다
FILLER = "- (AI가 내용을 만들지 못함 - 직접 작성 필요)"


def truncate(text, limit):
    # 왜: len()은 한글도 1자로 센다. 글자 수 기준이라 명세의 "N자"와 같다.
    return text if len(text) <= limit else text[:limit - 1] + "…"


def format_commit(result):
    """(정리된 커밋 메시지, 알림 목록)을 돌려준다."""
    lines = result.strip().splitlines()
    title = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip()
    notes = []
    if len(title) > COMMIT_MAX:
        title = truncate(title, COMMIT_MAX)
        notes.append(f"제목이 {COMMIT_MAX}자를 넘어 잘랐습니다")
    elif len(title) > COMMIT_WARN:
        notes.append(f"제목 {len(title)}자: 권장 {COMMIT_WARN}자 초과 (최대 {COMMIT_MAX}자 이내라 유지)")
    # 왜: 커밋 본문은 명세가 강제하지 않는다. 불릿이 없으면 알리기만 하고 내용은 지어내지 않는다.
    if not any(l.strip().startswith("- ") for l in body.splitlines()):
        notes.append("본문에 불릿(- )이 없습니다")
    return (title + "\n\n" + body).strip(), notes


def format_pr(result):
    """(제목, 본문, 알림 목록)을 돌려준다."""
    lines = result.strip().splitlines()
    title = lines[0].strip() if lines else ""
    notes = []
    if len(title) > PR_MAX:
        title = truncate(title, PR_MAX)
        notes.append(f"제목이 {PR_MAX}자를 넘어 잘랐습니다")

    # 왜: `## ` 헤더로 섹션을 쪼갠다(응답은 자유 텍스트로 받고 헤더로 파싱). 대소문자는 무시한다.
    found, current = {}, None
    for line in lines[1:]:
        s = line.strip()
        if s.startswith("## "):
            current = s[3:].strip().lower()
            found.setdefault(current, [])
        elif current and s:
            found[current].append(s)

    # 왜: 섹션을 SECTIONS 순서로 다시 조립해, AI가 순서를 바꾸거나 빠뜨려도 결과 모양이 항상 같다.
    parts = []
    for name in SECTIONS:
        content = found.get(name.lower())
        if content is None:
            notes.append(f"'{name}' 섹션이 없어 추가했습니다")
            content = [FILLER]
        elif not any(c.startswith("- ") for c in content):
            notes.append(f"'{name}' 섹션에 불릿이 없어 추가했습니다")
            content.append(FILLER)
        parts.append(f"## {name}\n" + "\n".join(content))
    return title, "\n\n".join(parts), notes


if __name__ == "__main__":
    # 규칙 위반 샘플로 후처리 동작 확인 (API 호출 없음)
    t, n = format_commit("feat: " + "가" * 80 + "\n\n- 변경")
    assert len(t.splitlines()[0]) == COMMIT_MAX and t.splitlines()[0].endswith("…") and n
    t, n = format_commit("feat: " + "가" * 50 + "\n\n- 변경")  # 56자 → 경고만, 자르지 않음
    assert "…" not in t and len(n) == 1
    t, n = format_commit("feat: 짧은 제목\n\n- 변경")
    assert n == []
    title, body, n = format_pr("feat: " + "나" * 90 + "\n\n## Why\n- 이유\n## What\n설명만 있음")
    assert len(title) == PR_MAX
    assert body.index("## Why") < body.index("## What") < body.index("## How to Test")
    assert body.count("- ") >= 3 and len(n) == 3  # 제목 자름 + What 불릿 추가 + How to Test 추가
    print("[OK] format_output 검증 통과")
    print("- commit 샘플 알림:", format_commit("feat: " + "가" * 80)[1])
    print("- pr 샘플 알림:", n)