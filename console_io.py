"""콘솔 입력과 공통 입력 검증을 담당하는 모듈.

게임 전체에서 같은 입력 규칙을 재사용할 수 있도록, 숫자 입력 검증과
텍스트 입력 검증을 이 파일에 모아 둔다. 입력 관련 예외를 한 군데로 모으면,
상위 게임 로직은 "무엇을 할지"에 집중하고 "입력을 어떻게 안전하게 받을지"는
이 모듈이 전담하게 된다.
"""

from __future__ import annotations

from typing import Callable

from game_constants import (
    EMPTY_INPUT_MESSAGE,
    INPUT_INTERRUPTED_MESSAGE,
    NUMBERS_ONLY_MESSAGE,
    RANGE_MESSAGE_TEMPLATE,
)

# 콘솔 기반 프로그램이지만, 테스트에서는 입력/출력을 가짜 함수로 바꿔 끼울 수
# 있어야 하므로 함수 시그니처를 타입 별칭으로 명확히 적어 둔다.
InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


class SafeExitRequest(Exception):
    """입력 중단을 상위 로직으로 전달하기 위한 제어용 예외.

    `Ctrl+C`나 EOF를 단순 입력 오류와 다르게 처리하기 위해 사용한다.
    """

    pass


def prompt_text(input_fn: InputFn, output_fn: OutputFn, prompt: str) -> str:
    """빈 입력을 허용하지 않는 텍스트 입력을 반복해서 받는다.

    입력 스트림이 중단되면 `SafeExitRequest`를 발생시켜, 상위 게임 루프가
    저장 후 안전하게 종료할 수 있도록 한다.
    """
    while True:
        try:
            value = input_fn(prompt)
        except (KeyboardInterrupt, EOFError):
            output_fn("")
            # 이 메시지는 실제 사용자에게 보여 주는 안내 문구다.
            output_fn(INPUT_INTERRUPTED_MESSAGE)
            raise SafeExitRequest from None

        # 공백만 입력하는 경우도 "빈 입력"으로 취급해 같은 규칙으로 막는다.
        cleaned_value = value.strip()
        if not cleaned_value:
            output_fn(EMPTY_INPUT_MESSAGE)
            continue

        return cleaned_value


def prompt_int(
    input_fn: InputFn,
    output_fn: OutputFn,
    prompt: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    """정수 입력을 받고 범위까지 검사한다.

    메뉴 번호, 정답 번호, 삭제할 퀴즈 ID처럼 숫자가 필요한 곳에서 공통으로
    사용하기 위해 만든 함수다. 이 함수는 문자열 입력을 정수로 바꾸는 일과,
    허용 범위 안에 드는지 확인하는 일을 함께 맡는다.
    """
    while True:
        # 실제 입력 받기는 prompt_text가 담당하므로, 중단 처리 정책도 그대로 재사용된다.
        raw_value = prompt_text(input_fn, output_fn, prompt)
        try:
            value = int(raw_value)
        except ValueError:
            output_fn(NUMBERS_ONLY_MESSAGE)
            continue

        if minimum is not None and value < minimum:
            # 최소/최대 범위 메시지를 하나의 템플릿으로 통일해 문구 일관성을 유지한다.
            output_fn(RANGE_MESSAGE_TEMPLATE.format(minimum=minimum, maximum=maximum))
            continue

        if maximum is not None and value > maximum:
            output_fn(RANGE_MESSAGE_TEMPLATE.format(minimum=minimum, maximum=maximum))
            continue

        return value
