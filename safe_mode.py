import re

# 왜: 세 번째 값은 치환 문구다. SECRET은 "password = " 같은 이름 부분은 남기고 값만 가려야 해서 규칙마다 따로 둔다.
# 왜: 순서가 의미 있다. 키·JWT를 먼저 지워야 그 안의 문자열이 뒤 규칙과 겹치지 않고, 주민번호는 전화번호보다 앞에 둔다.
PATTERNS = [
    ("API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}"), "[MASKED_API_KEY]"),
    ("JWT", re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+"), "[MASKED_JWT]"),
    # 왜: 키 모양이 없어도 "이름 = 값" 꼴이면 비밀일 가능성이 높다. (?!\[MASKED_)는 이미 가린 값을 중복 집계하지 않으려는 장치,
    #     [:=](?!=)는 코드의 `token == x` 비교문을 건드리지 않으려는 장치다.
    ("SECRET", re.compile(r"(?i)([\w-]*(?:password|passwd|pwd|secret|token|api[_-]?key)\s*[:=](?!=)\s*)([\"']?)(?!\[MASKED_)[^\s\"',]+"), r"\g<1>\g<2>[MASKED_SECRET]"),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[MASKED_EMAIL]"),
    ("RRN", re.compile(r"\b\d{6}-[1-4]\d{6}\b"), "[MASKED_RRN]"),
    # 왜: 휴대폰은 구분자 선택, 지역번호는 하이픈 필수. 숫자만 긴 값(해시·ID)을 전화번호로 오인하지 않으려는 타협이다.
    ("PHONE", re.compile(r"\b01[016789][-. ]?\d{3,4}[-. ]?\d{4}\b|\b0\d{1,2}-\d{3,4}-\d{4}\b"), "[MASKED_PHONE]"),
]


def mask_sensitive(text):
    """(마스킹된 텍스트, 마스킹한 건수)를 돌려준다."""
    total = 0
    for label, pattern, repl in PATTERNS:
        # 왜: 무슨 종류가 가려졌는지 남겨야 AI가 문맥을 이해하고, 사용자도 확인할 수 있다.
        text, n = pattern.subn(repl, text)
        total += n
    return text, total


def limit_diff(diff, max_files, max_lines):
    """(제한된 diff, 생략한 파일 수, 생략한 줄 수)를 돌려준다."""
    # 왜: 파일 경계("diff --git")에서 먼저 자르면 앞쪽 N개 파일은 온전히 남고, 그다음에 전체 줄 수로 한 번 더 자른다.
    chunks = [c for c in re.split(r"(?m)^(?=diff --git )", diff) if c]
    lines = "".join(chunks[:max_files]).splitlines(keepends=True)
    return "".join(lines[:max_lines]), max(0, len(chunks) - max_files), max(0, len(lines) - max_lines)


if __name__ == "__main__":
    fake = ("+API_KEY = \"AIza" + "A" * 35 + "\"\n"
            "+# 문의: dev.kim@example.com, 010-1234-5678, 02-123-4567\n"
            "+def add(a, b): return a + b\n")
    print("--- OFF (원문) ---")
    print(fake)
    masked, n = mask_sensitive(fake)
    print(f"--- ON (마스킹 {n}건) ---")
    print(masked)
    assert n == 4 and "AIza" not in masked and "@" not in masked and "010" not in masked
    assert "def add" in masked  # 일반 코드는 그대로
    more = ("+password = \"hunter2\"\n+AI_API_KEY=abc123\n+DEFAULT_MAX_TOKENS = 512\n+if token == x: pass\n"
            "+k = \"AKIAABCDEFGHIJKLMNOP\"\n+id 900101-1234567\n")
    m2, n2 = mask_sensitive(more)
    assert n2 == 4 and "hunter2" not in m2 and "abc123" not in m2 and "AKIA" not in m2 and "900101" not in m2
    assert "DEFAULT_MAX_TOKENS = 512" in m2 and "token == x" in m2  # 비밀이 아닌 코드는 그대로
    d = "".join(f"diff --git a/{i} b/{i}\n+a\n+b\n+c\n" for i in range(3))
    out, cf, cl = limit_diff(d, 2, 5)
    assert (cf, cl) == (1, 3) and out.count("diff --git") == 2
    print("OK")