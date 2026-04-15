"""최고 점수와 플레이 히스토리 화면 출력을 담당하는 모듈.

이 파일은 "점수판을 어떻게 보여 줄 것인가"에만 집중한다. history 기록을
만드는 책임은 상위 게임 로직과 `HistoryEntry` 모델이 맡고, 이 모듈은
이미 만들어진 데이터를 콘솔에서 읽기 좋게 출력하는 역할만 담당한다.
"""

from __future__ import annotations

from collections.abc import Sequence

from console_io import OutputFn
from game_constants import (
    ANSWERED_COUNT_LABEL,
    CORRECT_COUNT_LABEL,
    HINT_USED_COUNT_LABEL,
    NO_PLAY_HISTORY_MESSAGE,
    PLAY_COUNT_LABEL,
    PLAY_HISTORY_ENTRY_TITLE_TEMPLATE,
    PLAYED_AT_LABEL,
    SCORE_LABEL,
    SECTION_DIVIDER,
    SELECTED_COUNT_LABEL,
    SUMMARY_BEST_SCORE_LABEL,
)
from history_entry import HistoryEntry


def show_scores(
    output_fn: OutputFn,
    *,
    best_score: int,
    history: Sequence[HistoryEntry],
) -> None:
    """최고 점수와 플레이 기록 전체를 화면에 출력한다.

    전체 히스토리를 플레이한 순서대로 보여 주어, 가장 최근 기록이 화면의
    마지막에 오도록 정리한다.
    """
    output_fn("")
    output_fn(SECTION_DIVIDER)
    output_fn(f"{SUMMARY_BEST_SCORE_LABEL}: {best_score}")
    output_fn(f"{PLAY_COUNT_LABEL}: {len(history)}")
    output_fn(SECTION_DIVIDER)

    if not history:
        output_fn(NO_PLAY_HISTORY_MESSAGE)
        return

    # history는 플레이가 끝날 때마다 뒤에 추가되므로, 그대로 순회하면
    # 오래된 기록부터 최신 기록까지 시간 흐름대로 보여 줄 수 있다.
    for entry_number, entry in enumerate(history, start=1):
        output_fn(PLAY_HISTORY_ENTRY_TITLE_TEMPLATE.format(entry_number=entry_number))
        output_fn(f"{PLAYED_AT_LABEL}: {entry.played_at}")
        output_fn(f"{SELECTED_COUNT_LABEL}: {entry.selected_count}")
        output_fn(f"{ANSWERED_COUNT_LABEL}: {entry.answered_count}")
        output_fn(f"{CORRECT_COUNT_LABEL}: {entry.correct_count}")
        output_fn(f"{SCORE_LABEL}: {entry.score}")
        output_fn(f"{HINT_USED_COUNT_LABEL}: {entry.hint_used_count}")
        output_fn(SECTION_DIVIDER)
