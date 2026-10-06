import json
import os
import urllib.error
import urllib.request

# 왜: 공식 SDK 대신 urllib로 REST를 직접 호출한다. 설치가 필요 없고, 요청 구성이 코드에 그대로 보여 설명하기 쉽다.
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TIMEOUT_SEC = 30  # 왜: 타임아웃이 없으면 네트워크가 멈췄을 때 프로그램이 영원히 기다린다


class AIError(Exception):
    """API 호출 실패. 메시지에 원인(키 없음·인증 실패·네트워크 등)을 담는다."""


def load_api_key():
    # 왜: 키는 코드가 아닌 환경변수 AI_API_KEY로만 받는다(하드코딩 금지). 변수명은 명세 예시와 같다.
    key = os.environ.get("AI_API_KEY")
    if not key:
        # 왜: 호출 전에 검사해 헛된 요청을 막고, 틀린 키(호출 후 인증 실패)와 원인을 구분한다.
        raise AIError(
            "환경변수 AI_API_KEY가 설정되지 않았습니다.\n"
            "예) export AI_API_KEY=발급받은키        (Mac/Linux)\n"
            '예) $env:AI_API_KEY="발급받은키"        (PowerShell)'
        )
    return key


def call_ai(prompt, api_key, model, temperature, max_tokens):
    url = API_URL.format(model=model)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    # 왜: 키는 URL 쿼리가 아닌 헤더로 보낸다. URL은 로그·오류 메시지에 찍히기 쉬워 유출 위험이 크다.
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    print("[INFO] AI API 호출 1회")  # 명세 권장: 호출 횟수를 로그로 남긴다
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 왜: 400은 키 오류뿐 아니라 모델 ID·파라미터 오타에도 나온다. "인증 실패"로 단정하지 않고 서버가 준 사유를 그대로 보여준다.
        try:
            detail = json.loads(e.read().decode("utf-8"))["error"]["message"]
        except (ValueError, KeyError):
            detail = ""
        if e.code in (401, 403) or "API key" in detail:
            raise AIError(f"인증 실패(HTTP {e.code}): API 키가 올바른지 확인하세요. {detail}") from None
        if e.code == 429:
            raise AIError("요청 한도 초과(HTTP 429): 잠시 후 다시 시도하세요(무료 티어는 분당·일일 한도가 있음).") from None
        raise AIError(f"API 오류(HTTP {e.code}): {detail}") from None
    except urllib.error.URLError as e:
        raise AIError(f"네트워크 오류: {e.reason}") from None
    except TimeoutError:
        raise AIError(f"응답 시간 초과({TIMEOUT_SEC}초)") from None

    # 왜: 응답 구조가 예상과 다르면(안전 필터 차단·토큰 초과 등) KeyError 대신 사람이 읽을 메시지를 낸다.
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        reason = (data.get("candidates") or [{}])[0].get("finishReason", "알 수 없음")
        raise AIError(f"응답에서 텍스트를 찾지 못했습니다(종료 사유: {reason})") from None