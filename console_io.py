from __future__ import annotations

from typing import Callable

from game_constants import (
    EMPTY_INPUT_MESSAGE,
    INPUT_INTERRUPTED_MESSAGE,
    NUMBERS_ONLY_MESSAGE,
    RANGE_MESSAGE_TEMPLATE,
)

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
            output_fn(INPUT_INTERRUPTED_MESSAGE)
            raise SafeExitRequest from None

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
    while True:
        raw_value = prompt_text(input_fn, output_fn, prompt)
        try:
            value = int(raw_value)
        except ValueError:
            output_fn(NUMBERS_ONLY_MESSAGE)
            continue

        if minimum is not None and value < minimum:
            output_fn(RANGE_MESSAGE_TEMPLATE.format(minimum=minimum, maximum=maximum))
            continue

        if maximum is not None and value > maximum:
            output_fn(RANGE_MESSAGE_TEMPLATE.format(minimum=minimum, maximum=maximum))
            continue

        return value
