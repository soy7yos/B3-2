import re

# 왜: (A) 패턴 마스킹만 구현한다. 명세는 1개 이상이면 충족이고, 보너스 12단계(정규식 확장)도 이 표만 늘리면 된다.
# 왜: 순서가 의미 있다. API 키를 먼저 지워야 키 안의 문자열이 전화번호·이메일 규칙과 겹치지 않는다.
PATTERNS = [
    ("API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}|sk-[A-Za-z0-9_-]{20,}")),  # Gemini·OpenAI 키 모양
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    # 왜: 휴대폰은 구분자 선택, 지역번호는 하이픈 필수. 숫자만 긴 값(해시·ID)을 전화번호로 오인하지 않으려는 타협이다.
    ("PHONE", re.compile(r"\b01[016789][-. ]?\d{3,4}[-. ]?\d{4}\b|\b0\d{1,2}-\d{3,4}-\d{4}\b")),
]


def mask_sensitive(text):
    """(마스킹된 텍스트, 마스킹한 건수)를 돌려준다."""
    total = 0
    for label, pattern in PATTERNS:
        # 왜: 무슨 종류가 가려졌는지 남겨야 AI가 문맥을 이해하고, 사용자도 확인할 수 있다.
        text, n = pattern.subn(f"[MASKED_{label}]", text)
        total += n
    return text, total


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
    print("OK")