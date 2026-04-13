from __future__ import annotations

from typing import Callable

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]


class SafeExitRequest(Exception):
    pass


def prompt_text(input_fn: InputFn, output_fn: OutputFn, prompt: str) -> str:
    while True:
        try:
            value = input_fn(prompt)
        except (KeyboardInterrupt, EOFError):
            output_fn("")
            output_fn("입력이 중단되었습니다. 저장 후 안전하게 종료합니다.")
            raise SafeExitRequest from None

        cleaned_value = value.strip()
        if not cleaned_value:
            output_fn("빈 입력은 허용되지 않습니다. 다시 입력해주세요.")
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
    while True:
        raw_value = prompt_text(input_fn, output_fn, prompt)
        try:
            value = int(raw_value)
        except ValueError:
            output_fn("숫자만 입력해주세요.")
            continue

        if minimum is not None and value < minimum:
            output_fn(f"{minimum}부터 {maximum} 사이의 숫자를 입력해주세요.")
            continue

        if maximum is not None and value > maximum:
            output_fn(f"{minimum}부터 {maximum} 사이의 숫자를 입력해주세요.")
            continue

        return value
